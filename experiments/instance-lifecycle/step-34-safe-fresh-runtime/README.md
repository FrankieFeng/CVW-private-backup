# Step-34 安全Fresh源码原型

已实现并真实执行，尚非生产替换。独立分支experiment/step34-safe-fresh-runtime，父963b47b4。未修改生产、未推送、未启动节点E2E。

|最终问题|结果|
|---|---|
|真正独立Store？|是：wasm_store_new；跨Store错误导入拒绝和Memory隔离实测，不是Go/Rc clone|
|保留Module缓存？|是：缓存Module，同Engine不同Store，无逐Fresh重复编译/反序列化|
|Fresh完整路径？|是：新Store→WASI/imports→NewInstanceInStore→原Copy→Initialize/_start→CallMethod/Gas→同步回收|
|错误/Finalizer？|Go故障、真实业务回滚、GC、幂等Close、Reset/Stop/poison通过；native OOM/析构失败未强制制造|
|buyNow六下游？|三轮四组12根/72真实子调用正确|
|Gas/状态？|四合约48根四组一致，逐收据与Step32语义复核通过|
|生命周期固定成本？|同代码控制直接配对见下表；N3探索性，不能给通用固定常数|
|可直接开始节点E2E？|否；可进入最小节点适配接线验证，仍须完成生命周期smoke|
|最小阻塞？|节点manager/缓存/回调/Reset/Stop未路由新owner，当前业务适配仍是测试入口|

|方法|共享Store控制Median ms|独立Store Median ms|直接额外耗时 Median [95% CI] ms|对数|
|---|---:|---:|---|---:|
|compute|22.277|19.173|-2.896 [-3.424, -2.332]|3|
|fact|6.466|5.038|-1.074 [-1.826, -0.086]|3|
|erc721|5.934|6.290|+0.325 [-1.102, 0.729]|3|
|exchange|75.541|45.731|-29.810 [-34.737, -20.928]|3|

正值为新路径额外成本，负值为更快；三对bootstrap区间仅探索。控制组也是同owner/同补丁的安全串行共享Store，不是默认池或原生产版本；Module/模板准备均在外。exchange三对更快仅归属于此Store架构对照，不归因Copy或预设线程/GC原因。

独立路径已通过进程观测峰值RSS 525.6MiB、线程48，创建/删除计数平衡；含控制组及失败的所有记录在RESOURCE_SUMMARY.csv。计数是C API handle操作，非最终Rust Rc Drop测量。

入口：ARCHITECTURE、OWNERSHIP_MATRIX、IMPLEMENTATION、MODULE_STORE_COMPATIBILITY、LIFECYCLE_TESTS、CORRECTNESS、SAFETY_GATE、NEXT_STEP。原始命令/资源/收据在raw_logs；CODE_INDEX.csv给函数行号。

复算：python3 scripts/analyze.py；python3 scripts/report.py。构建：scripts/build.py使用新标签避免覆盖，固定本地native so与go.work依赖；运行：scripts/validate.py（已完成标签会跳过，不构成新实验）。完整参数见逐进程command.json。native兼容性完整编译命令仍应使用source/compat.c/WAT，原C API命令见audit；共享代码diff在audit。

回滚：停止state.json所列自有step34 unit、核对PID/cgroup清空，保留分支/目录即可；没有生产部署需回滚，不reset/clean原工作区。归档不含so或.test，固定哈希原件仍在原隔离工作树。
