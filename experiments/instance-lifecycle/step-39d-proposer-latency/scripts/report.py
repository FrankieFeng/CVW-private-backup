"""Generate read-only attribution report from Step39C and the two saved diagnostics."""
from pathlib import Path
import json,csv,hashlib,statistics as st,subprocess
P=Path(__file__).resolve().parents[1];C=P.parent/'step-39c-node-e2e-sha-acopy';N=Path('/home/frankie/mygitprojects/.worktrees/node-step39d');M=Path('/home/frankie/go/pkg/mod/chainmaker.org/chainmaker');TBFT=Path('/home/frankie/mygitprojects/.worktrees/cvw-step17/chainmaker/chainmaker-vm-wasmer/consensus-tbft/v2@v2.4.0')
def rows(f):return list(csv.DictReader(f.open()))
def write(f,s):(P/f).write_text(s.strip()+'\n')
def fmt(x):return f'{float(x):.3f}'
def table(h,rs):return '| '+' | '.join(h)+' |\n|'+'|'.join(['---']*len(h))+'|\n'+'\n'.join('| '+' | '.join(map(str,r))+' |'for r in rs)+'\n'
def q(v,p):
 a=sorted(v);k=(len(a)-1)*p;i=int(k);return a[i]+(a[min(i+1,len(a)-1)]-a[i])*(k-i)
timeline=rows(P/'TIMELINE.csv');windows=rows(P/'WINDOW_ANALYSIS.csv');summ=rows(C/'SUMMARY.csv');diag=rows(P/'DIAGNOSTIC_WINDOWS.csv');byposition=rows(P/'REQUEST_POSITION.csv');names={'compute_hashCal':'hashCal','bigInput_inputSize':'bigInput.inputSize','exchange_buyNow':'buyNow'}
full=[]
for r in summ:
 if r['metric']=='e2e_ms':full.append([names[r['case']],r['group'],r['N'],fmt(r['p50']),fmt(r['p95']),fmt(r['mean']),fmt(r['pooled_tps'])])
contrib=[]
for case in names:
 w=[r for r in windows if r['case']==case];slow=[r for r in timeline if r['case']==case and r['slow_gt_1000ms']=='True']
 if slow:
  contrib.append([names[case],len(slow),f"{st.median(float(r['e2e_ms'])for r in slow):.3f}",f"{st.median(float(r['rpc_to_vm_ms'])for r in slow):.3f}",f"{st.median(float(r['factory_ms'])for r in slow):.3f}",f"{st.mean(float(r['slow_sdk_fraction_of_actual_window'])for r in w)*100:.2f}%",f"{st.mean(float(r['slow_pre_vm_fraction_of_actual_window'])for r in w)*100:.2f}%"])
positions=[]
for pos in range(1,11):
 rs=[r for r in byposition if int(r['request_number'])==pos];z=[pos]
 for case in names:
  r=next(r for r in rs if r['case']==case);z.append(fmt(r['e2e_p50_ms']))
 positions.append(z)
strata=[]
for case in names:
 for kind in ['all_original','slow_only_diagnostic','other_requests_diagnostic']:
  rs=[r for r in timeline if r['case']==case and(kind=='all_original'or(r['slow_gt_1000ms']=='True')==(kind=='slow_only_diagnostic'))]
  if not rs:continue
  z=[names[case],kind,len(rs)]
  for field in ['rpc_to_vm_ms','factory_ms']:
   v=[float(r[field])for r in rs];z.extend([fmt(st.median(v)),fmt(q(v,.95))])
  strata.append(z)
write('README.md','''# Step-39D：短方法固定位置尾延迟归因

**根因已定位为节点启动期 Sync V2 的消息总线背压，不是 VM 第五次调用变慢，也不是 Copy/Artifact 造成秒级执行成本。** Step-39C 的24笔慢交易均是正式第5笔、区块高度6；两次最小诊断保留原TBFT/VM/native参数，抓到实际阻塞栈，并将异常从第5笔移动到第3笔，仍对应高度6。

## 证据链与“第5笔”

1. Sync V2 在初始化 `NewProvideServer` 时就注册 BlockInfo 订阅；RuleManager.newBlockC 容量只有3。节点顺序先启动Consensus，再启动Sync；RPC可用和第一次proposer_ready=true早于整个链启动完成。
2. 单验证节点TBFT.Start显式跳过ListenSyncToIdealHeight等待，节点又异步启动链，因此首次可提案不代表全链就绪。Sync启动先执行Registry.Start，其中已有固定 `time.Sleep(2*time.Second)` 用于等待发现周期；之后才执行Provider.Start→RuleManager.Start→watchNewBlock。**这是原节点代码的启动等待，不是本轮添加的请求Sleep**。
3. Step-39C短方法的部署seed已到高度1。正式前两个Query不提交区块，前三笔正式交易提交高度2、3、4，填满尚无消费者的3格channel。第4笔高度5的BlockInfo通知在RuleManager.NotifyNewBlock发送处阻塞。
4. PublishSafe的消息消费goroutine按订阅者顺序同步调用OnMessage。其阻塞后，后续TBFT高度通知及提案状态无法及时处理；此前Core已经ready=false。SDK的区块事件订阅在前，故第4笔本身还能成功响应；下一笔即第5笔、高度6请求等待进入VM。
5. 两秒启动等待结束后，Provider启动规则消费者、channel排空、消息总线继续投递，TBFT处理新高度并重新sendProposeState(true)，Core恢复提案定时器。旧24笔恢复时间相对第一次ready集中在1995.385～2006.241ms；随后才进入VM。
6. 诊断栈同时显示：msgbus消费线程卡在NotifyNewBlock的chan send；节点启动线程睡在Registry.Start:114；TBFT主循环在select等待，没有正在执行耗时Guest。结合静态控制流与序号移动，这超出了仅凭时间相关性的解释。历史24笔没有保存该栈，不能逐笔声称抓到了同一栈；其高度、时间和状态与诊断机制一致。

不是“每5笔必慢”的业务计数规则，也不是20ms出块间隔突然变成2秒。它是**启动尚未完成时快速提交区块触发有界channel背压**的实现/就绪边界问题；在本轮单节点配置中可触发，并非已证明所有生产网络均出现的常态TBFT缺陷。链版本2040000选Sync V2，不能拿旧module/sync V1的默认3块广播或txpool的2秒flush，仅因数字相同就当根因。

## 原始完整窗口（保持正式口径）

E0 Fresh，E1 Copy，E2 A+Copy，E3 A+Copy+SHA。每行30笔、3批，每批10笔；成功率100%，失败/超时0。单位ms；TPS=30/三批实际窗口秒数之和。下表由Step-39C原CSV重读，未重跑或删除任何慢交易。\n\n'''+table(['方法','组别','N','P50','P95','Mean','同步提交TPS'],full)+'''
## 按正式请求序号分层

每个方法/序号N=12（四组×三批），以下仅描述位置效应，不用于把不同组混合成优化收益。延迟为SDK P50(ms)。REQUEST_POSITION.csv另含P95、Mean、进入VM前及Factory窗口。\n\n'''+table(['正式序号','hashCal','bigInput','buyNow'],positions)+'''
## 慢交易对窗口与VM外耗时的贡献

每个短方法12个原始窗口，每窗只有1笔>1s，均保留在正式分子/分母。表中“窗口占比”是12个窗口各自比例的平均；逐窗口精确分子分母见WINDOW_ANALYSIS.csv。\n\n'''+table(['方法','慢笔数','慢笔SDK P50(ms)','RPC→VM P50(ms)','Factory P50(ms)','慢笔SDK占窗口','慢笔RPC→VM占窗口'],contrib)+'''
慢笔SDK占各自窗口66.02%～71.99%。它们拉高Mean和P95，并占据大部分TPS分母。RPC→VM与Factory并非完全互斥：Factory前段SHA在Owner进入之前，故这些窗口不可直接相加。本报告不通过删除第5笔重算“修正TPS”。

下表为阶段诊断分层，**不能替代正式原始结果**；各层P95不是相加关系。stratum=other_requests不含慢笔，仅帮助定位窗口，不计算该过滤层TPS。\n\n'''+table(['方法','分层','N','RPC→VM P50','RPC→VM P95','Factory P50','Factory P95'],strata)+'''
## 两个必要的最小验证

原日志无TBFT高度接收/栈证据，才运行下述两次诊断。仅新建隔离节点分支，在超过300ms的同步RPC抓一次goroutine栈；timer并行，不阻塞请求、不Sleep、不改共识或Guest。栈采集有扰动，以下仅是机制诊断，不替换正式性能基线。两节点均E0/hashCal；另有1个仅用于部署seed的节点。\n\n'''+table(['诊断运行','窗口N','窗口前真实交易','P50(ms)','P95(ms)','Mean(ms)','实际TPS','慢笔窗口位置','慢笔高度'],[[r['run'],r['N'],r['prelude_count'],fmt(r['p50_ms']),fmt(r['p95_ms']),fmt(r['mean_ms']),fmt(r['submit_tps']),r['slow_window_ordinals'],r['slow_block_heights']]for r in diag])+'''
8笔窗口保留原序号，慢第5笔；12笔窗口前增加两笔真实提交，慢笔移动为窗口第3笔。20笔窗口请求+2笔prelude全部成功提交；没有在第10笔重复出现另一轮固定五次阈值。两次均抓到同一背压/启动睡眠栈；原窗口长度改变会改变单次启动停顿在TPS分母的占比，两个TPS不可解读为性能优化收益。

原始部署seed账本已随/tmp清理而不存在，因此从39C归档配置和原开发证书恢复新的隔离seed；WASM/Host/native/共识参数不变，但不冒充对39C的精确硬件瞬时环境复刻。诊断最大RSS593.902MiB、线程28，Owner接收10/16次均小于32；3节点Store/Instance均配平、退出0。没有提高1536MiB/220线，没有Reset刷新预算、强制GC、过滤慢交易或关闭原日志。

## 对Step-39C公平性与结论的影响

四组/三批均有相同位置的一笔启动尾延迟，所以没有选择性删样或某组缺失；原有限窗口的测量仍可复算。但**相同慢笔数量不等于相同启动残余等待**：优化组可能更早结束冷Query/前四笔，于是更早撞上同一个两秒启动屏障，等待更长。hashCal的E3慢笔比E0早到53～134ms，进入VM前反而多等约47～127ms；bigInput早到24～98ms，多等约27～102ms。它直接干扰Mean、P95、TPS和逐位置配对。

因此39C只保证Module/Artifact已热，不能称为全节点稳态热态。其短方法“P95变差/TPS持平”是该启动期窗口的有效观察，**不足以证明Copy/SHA在稳定节点导致同样退化**，也不能用剔除慢笔宣称稳定TPS提升。buyNow在本轮12次高度6请求到达时已超过启动等待（约2.046秒及以上），没有>1s尾延迟；不意味着跨合约永远不受同一机制影响。

## 最终判断与下一步

- 为什么第5笔：seed高度1+3格未消费通知+第4块通知阻塞，使第5笔等待高度6的提案许可；不是VM调用次数特性。
- 因果证据：控制流、真实堵塞栈、启动睡眠栈、2秒状态恢复、移走两笔后异常序号5→3而高度不变相互吻合。未直接抓取历史24笔的调用栈，也未运行修复版消融；证据边界保留。
- 分类：节点启动订阅/消费者顺序和实验就绪判定共同触发；不是Gas/Store/Artifact身份问题。当前范围无证据要求修改共识超时或区间优化。
- 是否修复：本研究先修正实验就绪屏障，等待真实Sync/Provider/RuleManager启动完成再开始正式窗口。不能简单加固定2秒Sleep，不能只等RPC可连接或首次提案ready。生产是否应统一拒绝未完全启动链的请求，属于后续独立实现评审，本轮未修改。
- Step40：**暂不直接启动全量性能矩阵**。先给出可观测的全模块启动完成信号，并用有限请求验证启动期背压已被排除；保留启动场景为独立结果。机制已清楚，不需要继续扩大本轮诊断。

完整源码证据见SOURCE_TRACE.md，最低准入条件见NEXT_STEP.md。历史360笔始终只读；本轮完成后停止，不自动开始后续实验，不推送远程。
''')
# Freeze decisive sources with line numbering; no private credentials.
specs=[(TBFT/'consensus_tbft_impl.go',394,414),(N/'module/blockchain/chainmaker_server.go',450,464),(M/'sync/v2@v2.4.0/types/watcher.go',10,24),(M/'sync/v2@v2.4.0/provider/provide_server.go',26,61),(M/'sync/v2@v2.4.0/provider/provide_server.go',84,103),(M/'sync/v2@v2.4.0/rule/manager/rule_manager.go',49,61),(M/'sync/v2@v2.4.0/rule/manager/rule_manager.go',80,120),(M/'sync/v2@v2.4.0/noderegistry/registry.go',99,117),(M/'sync/v2@v2.4.0/block_sync_service.go',137,164),(M/'sync/v2@v2.4.0/types/message_bus.go',33,46),(M/'common/v2@v2.4.0/msgbus/message_bus.go',168,184),(M/'common/v2@v2.4.0/msgbus/message_bus.go',214,258),(N/'module/blockchain/blockchain_start.go',28,60),(N/'module/blockchain/blockchain_init.go',59,70),(N/'module/blockchain/blockchain_init.go',103,118),(N/'module/subscriber/subscriber.go',20,26),(N/'module/sync/sync_server_aggregation.go',337,369),(N/'module/sync/sync_server_aggregation.go',86,94),(TBFT/'consensus_tbft_impl.go',551,568),(TBFT/'consensus_tbft_impl.go',1007,1023),(TBFT/'consensus_tbft_impl.go',1830,1848),(TBFT/'consensus_tbft_impl.go',435,444),(N/'module/core/syncmode/proposer/block_proposer_impl.go',216,234),(N/'module/core/syncmode/proposer/block_proposer_impl.go',440,461),(N/'module/core/syncmode/proposer/block_proposer_impl.go',561,571),(N/'module/core/syncmode/core_syncmode_impl.go',169,175)]
source=[]
for f,a,b in specs:
 data=f.read_bytes();lines=data.decode().splitlines();source.append(dict(path=str(f),start=a,end=b,sha256=hashlib.sha256(data).hexdigest(),lines=[str(i)+': '+lines[i-1]for i in range(a,b+1)]))
(P/'evidence/source-excerpts.json').write_text(json.dumps(source,indent=2,ensure_ascii=False))
print('README and source excerpts generated')
