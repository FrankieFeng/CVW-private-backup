from pathlib import Path
import csv,json,statistics as st
P=Path(__file__).resolve().parents[1]
def read(n):return list(csv.DictReader((P/n).open()))
def write(n,s):(P/n).write_text(s.strip()+'\n')
def fmt(v):return f'{float(v):.3f}'
def table(h,rs):return '| '+' | '.join(h)+' |\n|'+'|'.join(['---']*len(h))+'|\n'+'\n'.join('| '+' | '.join(map(str,r))+' |'for r in rs)+'\n'
M=['identity_address','identity_callerAddress','erc721_balanceOf','erc721_tokenLatestTxInfo','raffle_raffle'];G=['G0','G1','G2','G3','G4'];names={m:m.replace('_','.',1)for m in M};S=read('SUMMARY.csv');E=read('PAIRED_EFFECTS.csv');W=read('WINDOWS.csv');R=read('RESOURCE_SUMMARY.csv');X=read('ORDER_CHECK.csv');O=read('ORDER_EFFECTS.csv')
def stat(m,g,metric,key):return next(s[key]for s in S if s['method']==m and s['variant']==g and s['metric']==metric)
def effect(m,left,right,metric):return next(e for e in E if e['method']==m and e['left']==left and e['right']==right and e['metric']==metric)
def delta(e):return f"{fmt(e['paired_saving_median'])} [{fmt(e['ci95_low'])}, {fmt(e['ci95_high'])}]"
vm=[[names[m]]+[fmt(stat(m,g,'factory_invoke_ms','p50'))for g in G]for m in M];e2e=[[names[m]]+[fmt(stat(m,g,'sdk_e2e_ms','p50'))for g in G]for m in M];p95=[[names[m]]+[fmt(stat(m,g,'sdk_e2e_ms','p95'))for g in G]for m in M];tps=[[names[m]]+[fmt(stat(m,g,'sdk_e2e_ms','submit_tps'))for g in G]for m in M];mean=[[names[m]]+[fmt(stat(m,g,'sdk_e2e_ms','mean'))for g in G]for m in M];vmp=[];main=[];detail=[]
for m in M:
 vmp.append([names[m],delta(effect(m,'G3','G4','factory_invoke_ms')),delta(effect(m,'G0','G4','factory_invoke_ms'))])
 z=effect(m,'G0','G4','sdk_e2e_ms');verdict='三批均正，初步支持超过Fresh'if float(z['ci95_low'])>0 and z['all_batches_positive']=='True'else'点估计超过，CI跨零，未确认'
 if m=='erc721_balanceOf':verdict+='；SHA相对G3点回退'
 if m=='raffle_raffle':verdict+='；反序SHA E2E回退0.793ms'
 main.append([names[m],delta(effect(m,'G3','G4','factory_invoke_ms')),delta(effect(m,'G3','G4','sdk_e2e_ms')),delta(z),verdict])
 for l,r in [('G0','G3'),('G3','G4'),('G0','G4')]:
  e=effect(m,l,r,'sdk_e2e_ms');detail.append([names[m],l+'→'+r,fmt(e['p50_difference_ms']),fmt(e['paired_saving_median']),f"{float(e['positive_fraction'])*100:.1f}%",'/'.join(fmt(e['batch'+str(b)])for b in [1,2,3])])
h=['方法','Fresh','Copy','A-only','A+Copy','A+Copy+SHA']
write('RESULTS.md','''# CVW-SHA-NEGATIVE-5 结果

主实验已完成五方法×五方案×三个独立批次，共345笔正式根交易；另有25笔真实预检和6笔单列的raffle反序核查。四个方法每组每批5笔（合计15笔/组）；raffle沿用3人夹具、每批3笔（9笔/组），不增加参与人数/业务计算量以凑样本。无链上失败、超时、资源停止或剔除样本。

G0=Fresh，G1=Copy，G2=A-only，G3=A+Copy，G4=A+Copy+SHA。以下组别P50是该组全部正式调用的描述性中位数；配对效应另定义为同批匹配窗口均值差，不混为一谈。

## 表1：Factory Invoke P50（ms）

'''+table(h,vm)+'''
Factory根窗口已经包含callerAddress的真实address子调用，不重复累加子VM。

### VM直接对照：批次匹配节省中位数 [95%探索性CI]（ms）

'''+table(['方法','A+Copy→A+Copy+SHA','Fresh→A+Copy+SHA'],vmp)+'''
两项VM对照均为5/5三批同向正；不把它解释为所有E2E都稳定变快。

## 表2：SDK真实同步提交 E2E P50（ms）

'''+table(h,e2e)+'''
### E2E P95（ms）

'''+table(h,p95)+'''
### 实际成功确认提交TPS

'''+table(h,tps)+'''
TPS按每个实际串行窗口成功确认的目标交易数/墙钟秒数计算，汇总为总成功数/三个实际窗口秒数之和。不是VM时间倒数、不是节点最大TPS；部署、合法setup、就绪探针及Query预热在窗口外，均保留原始记录。

### E2E Mean（ms）

'''+table(h,mean)+'''
## 表3：SHA是否挽救历史负优化

以下均是批次窗口均值差的配对中位数 [95%探索性CI]，正值为右组更快。

'''+table(['方法','SHA VM增量','SHA E2E增量','Fresh→最终组合 E2E','判断'],main)+'''
**不能把“3/5最终组合初步超过Fresh”说成“SHA单独挽救了3个负例”。** 本轮G3对Fresh的匹配窗口均值效应有4个方法点估计已为正，历史三种优化都负的模式未普遍复现；旧36/37和本轮的就绪协议、统计单位不同。SHA本身的E2E增量多数CI跨零，balanceOf点回退，不能整体归因于SHA。

### P50差值与配对效应分列

'''+table(['方法','对照','独立组P50差值(ms)','匹配窗口Mean差的中位数(ms)','正向批次比例','三个批次窗口Mean差(ms)'],detail)+'''
特别是identity.address的G3 P50略慢于Fresh，但批次窗口Mean差为正；这不是计算错误，而是不同统计量。主效应没有用两个独立Median相减代替。

## 顺序限制与6笔单列反序核查

原始顺序由预设三批轮换产生，完整顺序在audit/order-*.json。复核发现raffle主三批均G4先于G3，故此对照存在相对顺序混杂，不能因三批同向就宣称因果稳定。额外只用原3人夹具做一次G3→G4反序，两节点各3笔，全部保留，未并入主三批统计：

'''+table(['方法','窗口','G3 Mean(ms)','G4 Mean(ms)','反序G3−G4(ms)','独立核查数'],[[names[r['method']],r['metric'],fmt(r['G3_mean']),fmt(r['G4_mean']),fmt(r['window_mean_saving']),r['independent_diagnostic_pairs']]for r in X])+'''
反序VM仍改善3.245ms，E2E反向0.793ms；只能说明E2E正增量未稳定复现，不能仅凭一个反序对确认运行顺序就是根因。未重跑或删除任何主批次。

## 统计口径与边界

每个方案使用独立节点进程，参数在进程启动时固定。VM和SDK只按同一节点、同一TxID关联；没有跨节点拼接一次交易耗时。组间比较的独立匹配单位为同方法、同预定批次、同输入和等价初始状态的完整窗口：

`delta_batch = Mean(左组窗口内目标调用) − Mean(右组窗口内目标调用)`

报告三个delta_batch的中位数、正向比例与27种批次bootstrap组合的经验2.5/97.5百分位。有效独立配对数为3，不是15或9；CI为探索性、未作多重检验校正。P95样本少，P99不报告。补充反序只有1个独立核查，不增加主实验批次数。

## 明日组会可用的三条结论

1. **VM层：五个历史负案例均测得SHA正向Factory增量，批次匹配节省中位数1.685～5.267ms；完整组合比Fresh节省4.610～9.138ms。**
2. **E2E层：最终组合对Fresh为3/5初步正向、2/5未确认；SHA额外E2E收益不普遍，balanceOf点回退，raffle反序核查没有复现正增量。**
3. **不能宣称SHA稳定扭转五个历史负优化案例。** 在新就绪协议下，多数G3点估计已改善；应区分整体组合优势、SHA独立增量和短路径波动。结果可作探索性组会材料，尚不足以作普遍生产收益结论。
''')
write('README.md','''# CVW-SHA-NEGATIVE-5：历史负优化方法快速补测

已完成，停止，不自动扩展到37方法。完整五组VM/E2E/P95/TPS表、匹配效应和三条组会结论在RESULTS.md。

- 使用Step-39E原node-ready、client3二进制及全链就绪协议，没有重新编译或修改节点/VM/native。节点源码c6382c3；Host Go1.25.0，Guest为冻结Go1.24.1 plain/A padding，Selector库SHA56b236ce1772b805819aec7c10eb417cd62bf0c6ee2c9b581e651f746bec17dc。
- 五组主实验345笔；预检25笔；为补足raffle主对照相对顺序的6笔反序单列。每方法三独立批次，普通方法每组15笔，raffle每组9笔；全部保留。启动屏障实际组件完成、消费者配平、双ACK及真实SDK提交探针，不增加Sleep/不改共识。
- callerAddress真实执行一次identity.address子调用；raffle保持原3人/3次抽奖。ERC721合法mint(tokenId1)在窗口前完成。identity真实target probe、ERC/raffle首笔真实setup作为提交探针；Query预热不写入账本。
- SHA方案仅G4启用39B摘要缓存，保留输入SHA和Runtime Clone；Copy固定C0，A-only使用同一Arena二进制但关闭Host Copy。inputs/variants.json含旧Step-36组号字段，本轮组义以inputs/variants-control.json和实际node argv为准。G2/G3/G4的A Guest相同，不把旧产物名G2误当本轮Copy开关。
- 配对单位为3个匹配批次窗口Mean差；同节点TxID连接VM/SDK，不跨Node拼接逐笔数据。独立组P50差值单列，不能替代配对效应。
- 五方法VM SHA增量主三批均正；最终组合对Fresh E2E为三例初步支持、两例CI跨零。SHA E2E独立增量并非普遍有效；raffle反序E2E回退0.793ms，完整结果如实保留。

## 复算

```sh
python3 scripts/analyze.py
python3 scripts/report.py
```

只读取raw_logs并重建派生表。E2E_RESULTS.csv、VM_RESULTS.csv含phase=formal/pre/ordercheck；主性能必须筛formal（345行），不混入预检或6笔反序。SUMMARY/WINDOWS含Mean/P50/P95/TPS；PAIRED_EFFECTS含3批效应、CI、正向比例和独立P50差值；ORDER_CHECK/ORDER_EFFECTS保留顺序复核。

实际执行命令、二进制/源码/Guest/配置身份在audit；六个部署seed和每个节点的SDK原始JSONL、VM日志、提交收据、状态读回及资源退出在raw_logs。失败的初始配置路径准备保留为seed-identity-plain，未启动节点或发送交易；修正后使用新seed-v1目录，不覆盖其现场。

所有节点资源配平，原1536MiB/220线程/32根预算不变；详见RESOURCE_SUMMARY.md、CORRECTNESS.md。历史36/37负值只存在audit/historical-negative5.md参照，不填充本轮统计。未推送远程。
''')
write('CORRECTNESS.md','''# 正确性和计量边界

主345笔、25笔预检和6笔反序目标交易全部成功确认提交。每笔检查SDK成功码、TxID、真实区块高度、GetTxWithRWSet已存结果；所有put_end均不晚于同节点rpc_tx_end。20个五组方法批次（预检5+正式15）精确比较Gas、返回值、事件、完整RWSet、setup及最终业务写键投影，只有集合排序，没有时间/TxID字段归一化。反序G3/G4亦独立核对通过。未声称系统部署WASM不同的全库字节一致。

独立业务预期：identity.address=628aafcf44e1dd25ebb0415e8f1d7026329eebfa；callerAddress为call contract success加该地址，保留真实address子调用。balanceOf=1。tokenLatestTxInfo字段必须精确对应实际mint的TxID/高度、零地址From和冻结To。raffle必须依次Carol、Alice、Bob；正式写键在节点状态库逐项读回，预热Query后也核对setup投影未改变。

**VM日志Gas不等于最终SDK Gas，是原计量边界。** node-step39e/module/core/common/scheduler/run_vm.go:259–287在RunContract返回后追加RWSet和事件费用；gas.go:117–225按非native合约名称/去#分隔符的键/值字节及事件字节计费，固定价格0.1、向上取整。分析按每笔原RWSet独立复算，全部完全相符：balanceOf VM150→SDK156(+6)，tokenLatestTxInfo149→171(+22)，raffle三次355→373(+18)、384→397(+13)、355→363(+8)。identity.address119及callerAddress200263没有额外RW费用。VM和最终Gas都各自跨五组一致；未改Gas规则来配平。

E2E_RESULTS/VM_RESULTS的gas为SDK最终Gas，factory_logged_gas为VM边界，post_vm_rw_event_gas为追加值。最初派生分析误要求两个边界数值相等而失败；已依据源码复算纠正，不是删除样本或修改运行数据。

Factory=root Runtime.Invoke前后，根Clone在Factory之外但在SDK窗口内；Owner=进入安全Owner后的嵌套窗口，含准备/执行/同步Close。NewInstance为既有native实例化子窗口，不代表全部Store/WASI成本；Copy restore、_start、CallMethod、Close均用既有字段。CallMethod含Guest/host及callerAddress子Invoke；根已包含子调用，不重复累加。Close含Guest反分配和native资源关闭，不额外加到完整Invoke。SDK计时为InvokeContract(...,60,true)开始至同步响应，结果经PutBlock→BlockInfo→dispatcher返回，不是AddTx ACK。每个窗口是首SDK开始到末SDK响应；没有窗口内查询、Sleep、setup或重试插入。

正确性覆盖本轮成功业务路径及真实节点正常退出，未重新认证全部异常/回滚路径。SHA命中由G4 registry hits前后增长验证；G0–G3 registry entries0。所有模式Root Instance均Fresh、Store独立，caller父子Store ID同时不同；节点二进制和VM Owner/source没有改变。
''')
write('RESOURCE_SUMMARY.md','''# 资源汇总

'''+table(['实际节点进程','RSS采样峰值MiB','OS线程峰值','Store创建/关闭','Instance创建/关闭','最长正常关闭秒'],[[len(R),fmt(max(float(r['rss_peak_mib'])for r in R)),max(int(r['threads_peak'])for r in R),str(sum(int(r['stores_created'])for r in R))+'/'+str(sum(int(r['stores_closed'])for r in R)),str(sum(int(r['instances_created'])for r in R))+'/'+str(sum(int(r['instances_closed'])for r in R)),fmt(max(float(r['stop_seconds'])for r in R))]])+'''
包含6个部署节点、25个预检节点、75个主实验节点和2个反序节点。均退出码0、PID退出/cgroup空、native managed_pending0、Store/Instance配平。原软限制RSS1536MiB、线程220、Owner根调用32未提高。正式普通方法每节点根预算7，raffle5；caller的子调用不另占根预算，实际Instance数量已计入资源总数。

G4最多单合约Artifact1项，8项/64MiB原限制及满容量拒绝策略保留；关闭后检查entries/bytes归零。RSS为原监控采样值，不是长期无泄漏证明。没有强制GC、后台并发Fresh或异步关闭路径。

最初配置归档路径误写audit而实际在evidence，失败seed未启动节点、没有SDK交易；原空目录、失败JSON和driver traceback保留，未算作成功节点或链上失败。后续六个新seed-v1部署及所有实际实验均成功。
''')
print('Reporttables andcorrectness/resourcesgenerated')
