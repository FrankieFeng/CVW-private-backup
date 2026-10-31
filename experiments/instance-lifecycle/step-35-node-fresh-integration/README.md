# Step-35：真实节点 Fresh 生命周期接入与 Smoke Test

**已实现并实测真实节点接入；E2E 安全准入暂不签发。** 阻塞收敛为资源问题：六轮请求后 C API 句柄配平，但 RSS/线程尚未证实收敛。没有启动正式性能对照。

基线 Step-34 `9845db9841bc963634c8f7d28d644e8756d5ac22`；工作树 `/home/frankie/mygitprojects/.worktrees/cvw-step35`，分支 `experiment/step35-node-fresh-integration`。节点工作树 `/home/frankie/mygitprojects/.worktrees/node-step35`，节点适配提交 `4dd3ae3`（父 `351b816e`）。本目录 source/vm 是实际编入节点的非测试 VM，实现入口 source/vm/vm_instances_manager.go:53。

已验证：五合约真实部署/初始化，compute.bigNumCal、fact.saveAndFindByFileHash、erc721.mint、exchange.buyNow 真实交易；buyNow 完整六次下游；Module 命中；独立 runtime Store；同步关闭；节点正常关闭/同账本重启；重复 buyNow 失败零写集；真实在途 Stop。Baseline/Copy 独立账本的 Gas、结果、业务读写集、事件和最终业务账本一致（限定元数据归一化，见 CORRECTNESS.md）。

| 记录 | 业务/生命周期 | RSS 峰值 MiB | 线程峰值 | Store CAPI创建/关闭 | Instance CAPI创建/关闭 |
|---|---|---:|---:|---:|---:|
| 原继承配置 | 五部署后触发资源停止 | 1548.410 | 33 | 11/11 | 6/6 |
| 小账本 Baseline | 四业务+查询+重复失败 | 1236.250 | 65 | 27/27 | 22/22 |
| 同账本重启 | 两轮四业务+检查 | 1134.012 | 55 | 34/34 | 29/29 |
| 小账本 Copy | 同 Baseline 业务序列 | 1289.879 | 65 | 27/27 | 22/22 |
| 真实在途 Stop | 进入 VM 后 SIGTERM | 665.047 | 26 | 2/2 | 1/1 |
| 六轮有限请求 | 24笔目标业务+检查 | 1481.109 | 109 | 72/72 | 67/67 |

这是功能 Smoke Test；表中不是性能基准，批次规模、冷热和代码诊断版本不同，不计算 Copy 时延收益。

原继承配置启用 `keys_capacity=1e9` Bloom，按源码分配约1.116GiB位图。触发1536MiB软阈值后立即保留并停止；另建空账本，仅把 Bloom 容量改为1e5，仍启用、同误判率，未提高资源限制。原配置、账本及失败数据不覆盖。小账本减少了大块基础内存，不证明其他资源增长已解决。

六轮末：Go heap 从930.9MiB附近降至521.6MiB，NumGC从8增至9；RSS仍约1473MiB、线程未呈稳定平台。CAPI计数不是Rust最终Drop或物理内存释放计数。**不能凭句柄配平或正常退出宣称长生命周期资源安全。**

运行/复算见 scripts/、SMOKE_TEST.md。Git不包含so；从现有CVW固定库重建可先用 `python3 scripts/restore_native.py`，脚本只接受原SHA，不下载或替换未知库。Node6为最终编译产物；实际节点日志分别关联node2/node4/node5（命令JSON保存精确SHA）；node6仅增加缺失opt-in时拒绝旧池的准入分支，正常opt-in路径不变。所有二进制保留在本地 binaries/ 并记录哈希，不入Git。测试网络配置/测试凭据在 `/tmp/cvw-step35-*`，不打包私钥。

回滚：停止本实验unit并检查PID/cgroup为空，恢复原节点二进制、库路径和原测试配置。**不能**在本实验 managed 绑定二进制里只关 `CM_SAFE_FRESH_NODE` 再走旧后台池：该组合现在直接拒绝启动。关闭Copy仅设 `CM_STATIC_MEMORY_COPY=0`，仍为安全Fresh路径。未改生产代码、原CVW已有修改及历史实验；不推送远程。
