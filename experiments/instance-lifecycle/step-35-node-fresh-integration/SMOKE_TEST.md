# 执行与结果

6种配置、7个实际InstancesManager夹具进程通过（包含最终compute生命周期回归）：compute(0/1 Copy)、fact(0)、ERC721(0)、exchange(0/1)。每个测试执行真实初始化、目标、等价账本Reset后重执行、missing方法失败、在途Go job Stop等待和重复Stop。fact首次monitor在进程退出时读/proc发生ProcessLookupError，测试原日志PASS但资源峰值标未记录，未重跑覆盖原始结果。准入测试覆盖缺失config、R0和最后缺失opt-in的拒绝（最终日志见admission-final2.log）。

真实节点：1节点TBFT，隔离链step35，RPC 127.0.0.1:27535/P2P 28535；同一测试网络开发凭据，非生产账本。SDK v2.4.0同步响应后另GetTxWithRWSetByTxId确认上链；query不计提交交易。日志Op=rwset为原始提交结果及写集。

- node-baseline-first：漏传继承的CM_STEP21A_POOL，包初始化拒绝，无native执行。
- node-baseline-configured：继承Bloom容量1e9，5笔部署已提交；第一个bigNumCal进入并完成VM，但客户端连接因资源SIGTERM关闭，未认定该业务提交成功。峰值1548.410MiB超过1536MiB软阈值；node exit0、owner配平。
- node-small-baseline：新空账本，仅Bloom容量1e5；5部署+四目标业务+ownerOf两次+重复buyNow失败。所有已取到TxInfo的交易确认，重复失败零写集。
- node-small-restart-converge：同账本正常重启，两轮连续四业务、唯一token3001/3002及3011/3012；4次owner查询和重复失败检查。
- node-small-copy：另一个等价空账本、同小账本配置、Copy=1，重复Baseline完整序列。18条对照检查（含部署RW/业务结果RW及最终业务账本）通过。
- node-small-inflight：同账本重启，观察到真实invoke_begin后SIGTERM；StopVM入口inflight=1，等invoke_end和同步Close后释放缓存；客户端未收到成功响应，不算成功提交。不是人为Sleep或持有业务锁制造等待。
- node-small-six-waves：6轮四目标业务，共24笔成功提交目标交易；owner查询两次和duplicate失败。5个Module准备、62次命中，67次Instance new/delete，72次Store new/delete，停止时pending0。RSS/线程增长尚未证实收敛，停止扩大。

脚本无100ms业务Sleep；25ms资源轮询和RPC启动探测间隔是监控/就绪检测，非请求之间等待。单客户端顺序请求；节点自身共识/调度路径保留，所有Wasmer操作进同一个Owner。不是原池高并发测试。

已执行命令存 raw_logs/*command.json、audit/*command.json。示例（不应在本轮资源门槛未通过时自动续跑）：
```bash
python3 scripts/build.py <新构建名> node
STEP35_HOME=/tmp/cvw-step35-small-ledger python3 scripts/node_smoke.py <新日志标签> repeat 0
python3 scripts/analyze.py
```
setup.py及small_ledger.py拒绝覆盖已有账本。source客户端为Step17同源SDK入口；client编译单独记录。运行时凭据在/tmp，不进入Git。

未执行：正式E2E性能对照、节点级chain-config触发Reset、任意native OOM/析构故障、长期运行、并发Owner/原池、真实Table函数身份、生产崩溃恢复。不得把这些记为通过。
