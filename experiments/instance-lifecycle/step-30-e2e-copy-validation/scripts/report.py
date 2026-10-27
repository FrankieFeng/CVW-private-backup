from pathlib import Path
import csv,json,statistics as st
P=Path(__file__).resolve().parents[1]
def read(n):return list(csv.DictReader((P/n).open()))
S=read('historical/SUMMARY.csv');E=read('PAIRED_EFFECTS.csv');R=read('RESOURCE_SUMMARY.csv');T=read('E2E_SAMPLES.csv');D=read('historical/PAIR_DELTAS.csv')
f=lambda x:f'{float(x):.3f}'
def val(group,metric):return next(x for x in S if x['label']=='low-a'and x['group']==group and x['metric']==metric and x['scope']=='complete_pairs_only')
lines=['# Step-30结果：审计完成，新E2E因安全门槛未执行','','**新增节点启动0、新增RPC请求0、新有效配对区块0、完成新正式批次0。** 下列性能数字全部是对2026-10-23 Step20原始JSONL/VM日志的只读复算，不是Step30新实验，不构成新独立重复证据。','', '## 新三组状态','', '| 组 | 目标 | 新有效区块 | 状态 |','|---|---|---:|---|','| G0 Fresh | 主基线 | 0 | blocked：保存节点未接入已验证Store所有者/回收协议 |','| G1 Fresh+Copy | 主对照 | 0 | 同上 |','| G2 Fresh+A+Copy | 次对照 | 0 | 同上；原件家族A node构建/集成亦未恢复 |','', '不能用Step28/29的安全Go测试夹具冒充SDK→真实节点；本轮也没有临时重写运行时、提高RSS门槛或启用原池后台并发。关键源码/SDK/节点binary及资源停止已核对，见AUDIT。','', '## 历史Step20相同88完整对的复算','', '| 窗口 | G0 Mean / Median / P95 ms | G1 Mean / Median / P95 ms |','|---|---:|---:|']
for m in ['client_elapsed_ns','sum_root_invoke_ns','s1_ns','copy_ns','wasi_plus_start_ns']:
 a,b=val('G0',m),val('G1',m);lines.append('| '+m+' | '+' / '.join(f(a[k])for k in ['mean_ms','median_ms','p95_ms'])+' | '+' / '.join(f(b[k])for k in ['mean_ms','median_ms','p95_ms'])+' |')
lines+=['','P95按原历史nearest rank，均值/中位数严格分开；Copy共89条完成热响应，主配对只用其中88条，但额外1条保留在E2E_SAMPLES，不因未配对删除。cold/warmup也完整保留、分别标记，未当正式热数据。','', '| 同对直接节省（G0−G1） | Median ms | Mean ms | N | 95%CI |','|---|---:|---:|---:|---|']
for e in E:
 if e['label']=='low-a':lines.append('| '+e['metric']+' | '+f(e['paired_save_median_ms'])+' | '+f(e['paired_save_mean_ms'])+' | '+e['n']+' | 未估计：单个资源删失的未完成批次 |')
lines+=['','每一对client节省 = sumRootVM节省 + 未细分残差节省；只对同一对的均值作可加核算。**不能将配对Median相加，也不能将两个组的Median差当配对节省。** 历史客户端配对Median略正而均值反向，P95略变差，均不足以宣称跨批稳定正/负收益。','', '## 历史资源停止','', '| 历史low-a | 首热窗RSS MiB | 峰值RSS MiB | 线程峰值 | Go heap |','|---|---:|---:|---:|---|']
for r in R:
 if r['label']=='low-a':lines.append('| '+r['endpoint']+' | '+f(r['first_warm_rss_mib'])+' | '+f(r['rss_peak_mib'])+' | '+r['threads_peak']+' | 未采集 |')
lines+=['','RSS软限2560MiB/硬限3GiB每节点不变；Copy在2564.707MiB离散采样触发，未等OOM。low-a的1个在途job在管道已写入后中止，SDK开始/TxID/提交未知；另22计划请求未发送。所有207保存响应都成功不等于全部计划请求成功。没有把“pending未完成”填为失败或成功。','', '## 对十个问题的回答','', '1. Copy是否降低客户端延迟？新Step30未测；历史88对的客户端配对Median+0.228ms、Mean−1.148ms，不能确认稳定收益。','2. 是否跨三批？没有。本轮0新批；旧Step20正式首批也未跑完。','3. P95是否改善？旧相同88对G0约49.355ms/G1约49.685ms，未改善；不是本轮新结论。','4. 成功率/超时/提交TPS？历史207已保存响应均成功、Gas106028且有正块高，1个pending未知；独立账本确认窗口/提交TPS缺失，新Step30全部missing。THROUGHPUT只给历史观察窗客户端完成率及锁内VM等效速率，明确不可当节点TPS。','5. VM节省是否传递？旧88对VM平均省0.273ms，但client平均慢1.148ms，未细分残差平均多1.422ms；说明该旧批没有保留均值收益，不能推断Copy造成额外调度等待。','6. AddTx→VM抵消证据？旧2026-10-19两批详细trace报告定位过该窗口；本次复算的旧Step20 low日志没有相应计时，本轮也无新记录，不能据client−VM残差重新命名AddTx时间。','7. clone是否在E2E内？真实节点若在处理该请求时取/拷字节码则客户端总窗覆盖，但本路径未单独测clone。Step29的六次测试Snapshot clone不是Step20 compute无子调用的执行路径；本轮不研究其GC/调度或改实现。','8. 与Step20差异？Step30只完成历史/安全审计，根本没有新的可比较工作负载，不称重现或完成60对；未来安全模型改变须登记受控新E2E。','9. 与王浅秋比较？恢复到顺序N/Σfactory Invoke与并发N/(maxEnd−minStart)两种脚本，历史入口与过滤并未完全确定。客户端延迟/完成率/提交TPS不能直接比较；STEP17锁内timer也不同于factory外层timer。','10. 是否足以证明真实E2E收益？不够。新样本为0，历史完整性/资源/生命周期有明确限制。下一步应先提供符合owner、native回收和长寿命资源门槛的节点实验版本，再按冻结客户端边界做有界G0/G1；原件A缺失则G2继续blocked。','', '## 证据分级','', '- 直接测量的历史事实：SDK elapsed、VM锁内阶段、TxID关联、资源增长与停止；本轮从raw重新计算，不改原件。','- 数据支持的解释：旧同步Fresh初始化处在客户端关键路径，但VM外其他窗口可抵消它；原日志不足以将所有残差归因共识。','- 未证实假设：Copy改变出块相位/GC/调度、模板导致GB增长、Wasmer clone是该节点主因。','- 未完成：新smoke/正式三批/60对、G2节点、独立提交TPS、完整RWSet/event/最终账本、逐笔SDK绝对边界和新AddTx关联。']
(P/'RESULTS.md').write_text('\n'.join(lines)+'\n')
(P/'README.md').write_text('''# Step-30：Copy端到端性能验证——审计与安全阻塞交付

本轮**没有启动新节点、客户端或发送新请求**；新E2E样本/有效配对/独立批次均为0。已完成历史口径、原始日志、二进制/源码与资源停止审计。保存的Step17/20节点未接入后续固定owner/managed-native回收协议，且旧RSS增长未闭合；按任务安全要求停止在新运行之前。未临时重写运行时或通过全局锁/抬限绕过。

先读[AUDIT](AUDIT.md)，再读[RESULTS](RESULTS.md)、[计时边界](TIMING_BOUNDARIES.md)与[正确性/缺口](CORRECTNESS.md)。真实SDK路径是InvokeContract(...60,true)→SendRequestSync→节点提交结果dispatcher返回；不是AddTx ACK，也不等于独立验证全网确认。

交付中的`E2E_SAMPLES.csv`是**历史Step20原始207响应+1个未知在途请求**的复算，每行origin_step=20/is_step30_new=False，不是新实验。PAIRED_EFFECTS、THROUGHPUT明确标注旧描述值与Step30 blocked缺失值；新缺失时延/CI/TPS不填0。原始客户端/VM/资源日志的逐字副本在raw_logs/historical-step20，未复制密钥、证书、账本。historical/目录为额外复算。

分支experiment/step30-e2e-copy-validation，父f1609b80；不修改生产VM、不推送远程、不制作PPT。原e20-e2e-copy-attribution路径未找到，实际已更名为step-20-e2e-performance-attribution。

离线复核（不启动网络/编译/测试）：

```bash
python3 -B scripts/environment_audit.py
python3 -B scripts/check_step17.py
python3 -B scripts/reanalyze.py
python3 -B scripts/report.py
python3 -B scripts/verify.py
```

命令在本实验独立worktree目录运行；绝对历史路径依赖现有CVW环境。IDE镜像用于查看。当前没有可放行的节点运行命令：不要将旧Step20脚本改标签继续跑，也不要重启其他监听端口的既有节点。未来准入与受控新E2E协议见TIMING_BOUNDARIES。

回滚：本轮未启动任何节点/客户端、未改VM/SDK/配置/资源上限；只需保留本目录并切回原分支。没有需要停止的本轮服务，不能误停其他实验/生产进程。
''')
(P/'CORRECTNESS.md').write_text('''# Step-30正确性：新测试未执行，历史核验有限

## 新Step30

G0/G1/G2均blocked，未进行新业务/提交/隔离/回滚验证。所有项不得标pass；EXECUTION_STATUS.csv给出理由。保存的旧node binary缺Store全生命周期owner与native Finalizer收敛，不以单客户端或根Invoke互斥证明安全。没有运行未经验证原池。

## 本轮对旧数据的直接核验

重新读取旧Step20两轮207条响应和四份原始STEP17日志，确认207唯一TxID/207唯一fresh Instance ID，每条有1次根Invoke，返回success bigNumCal:607723520、SDK及VM Gas均106028、code0、正TxBlockHeight。正式资源删失批88完整对的Gas/返回相等；Copy另1条未配对响应和pending未知请求保留，后者不算失败或成功。

客户端未存完整RWSet、独立事件验证/最终账本快照，**not_tested/not_collected**；不能将计算合约“看起来不写状态”当作实际链上写集核对。同步响应表示节点报告该Tx提交结果，独立账本扫描/确认时间和成功提交TPS没有证据。新事务回滚、真实Table身份、跨合约E2E均未在本轮验证。

## 安全与资源

旧low-a Copy RSS峰2564.707MiB触发2560软限，两节点都增长约1GiB；线程27，Go heap未采集。历史停止状态证明自有节点已停，不构成当前长期资源有界证明。没有提高阈值、给新请求降并发凑数据、强制GC、回收池改造或进程轮换续测。

仅临时C-call错误读取的LockOSThread不等于Store固定owner；native Finalizer与NewRuntimeInstance/模块准备不在根Invoke锁内。Step21B已有约束仍适用。Step22/28/29仅有界测试safe路径，当前节点没有相应已验证集成，不能临时替换native对象共享模型绕过。

环境证据保存的是公有源码/文件哈希和非敏感配置字段；没有打包密钥、证书或数据库。所有历史来源文件末尾SHA再核验，分支只新增Step30目录。
''')
print('Step30 blocked-scope reports saved; no new E2E claims')
