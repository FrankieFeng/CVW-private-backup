# Step-39C 真实节点 Smoke

安全准入已通过。SMOKE_COMPLETE.json 在正式实验开始前生成：121 项检查通过，formal_executed_before_gate=0。随后只执行计划内 360 笔正式根交易，没有因负收益追加采样。

| 检查 | 实际证据 | 结果和边界 |
|---|---|---|
| 启动/加载 | raw_logs/seed-*-seed.json；六个 plain/A 独立部署账本 | 单验证节点 TBFT，loopback 27535/28535，Common 写入 |
| 三方法×四组 | raw_logs/pre-*-case.json；pre-*-parity.json | 每组冷 Query、热 Query、1 笔真实提交；buyNow 六次真实子调用 |
| 首次登记/热命中 | case.json artifact_initial/after_cold/before/after | E3 从空登记后命中；E0/E1/E2 entries=0。冷/热 Query 在 COLD_WARM.csv 独立保存 |
| 满容量 | cap-full-capacity.json | 8 项时第九项明确拒绝，未创建业务 Instance；Reset 清空后可登记。未改变 8 项/64MiB 上限；本轮没有实际构造超64MiB的单项，字节上限实现沿用39B |
| 真实升级 | smoke-upgrade-r2-upgrade.json、r3、restart | v1 plain→v2 A，经3份合法开发管理员签名确认提交；新 SHA/新 Module 生效，Reset后及重启后仍为v2 |
| 同版本换码 | smoke-upgrade-r2-upgrade.json | SDK提交v2不同WASM，被合约管理层拒绝 `contract version exist`，原缓存身份未变化。该证据覆盖真实节点入口拒绝路径，不冒充缓存强行接受同版本换码的测试；registry内部内容隔离由39B验证 |
| Reset/预算 | smoke-budget-reset-upgrade.json | Manager实际入口Reset，accepted不变、limit32；正式进程未通过Reset刷新预算 |
| 在途Reset+Stop | smoke-inflight-inflight.json、restart | 观察真实invoke_begin后触发Reset与SIGTERM；已接收交易返回成功、排空退出，重启查到同TxID并可继续业务 |
| 错误与回滚 | smoke-rollback-*-postcheck.json | 三方法调用不存在的export，失败交易可查、写集为空，已验证业务KV投影不变；未穷举所有Guest异常 |
| 退出资源 | *-outcome.json、*-loaded-maps.txt、*-resources.jsonl | 全部107次节点运行exit0、PID退出/cgroup空、Store/Instance配平、managed_pending0、Artifact Stop后0项0字节 |
| 正式后持久化 | restart-formal-*-postcheck.json 共36份 | 全部360笔TxID/高度/结果在正常关闭重启后查回，并检查业务写键最终值 |

正式每进程只接受 12 次根调用（2 Query+10正式交易），小于32预算。buyNow 每进程实际84个业务Instance、87个Store（包括3个编译Store），关闭均配平；不能把根预算误解为只允许32次嵌套子调用。

## 保留的失败与修正

cap-seed0/1：RWSet读取成功的对象在transaction字段，旧辅助断言错误要求response；原先已提交的部署未重做，只补缺少的别名。smoke-upgrade：单管理员不满足升级权限；改用原策略允许的3份开发签名，没有改权限规则。smoke-upgrade-r1：恢复分支选错，健康查询v1后退出。r2升级实际成功；随后把Go map遍历顺序当成缓存值变化，辅助断言失败；只对items排序，原记录保留为false，r3接续成功状态，不重做已提交升级。以上五个false记录全部留存，不当作360笔正式交易失败，也不删去。

初始SDK配置字段名修正、派生分析脚本语法错误及所有修正均不改变已运行节点或正式原始记录。node3是早期构建，未用于节点；107个实际节点均为node4。早期Smoke使用client2，增加管理升级功能后使用client3；全部正式实验为client3。原client2源码保存在audit/client2-source.go.txt。harness中的旧错误提示“Solo”是历史文案，实际配置/enum已核对为TBFT。

## 复现入口（本轮已完成，不自动重跑）

构建入口：scripts/build.py，实际参数及编译日志在 audit/node4-command.json、client3-command.json。隔离配置与源码路径依赖必须先按 audit/configuration-identity.json 恢复；开发凭据仅从原环境引用，交付不含私钥/证书。冻结Guest来源及SHA见inputs/variants.json、audit/wasm-identity.json。

准备/预检使用 scripts/study.py seeds、pre，容量、升级、Reset/Stop分别用capacity.py、upgrade.py、inflight.py；每次实际 argv/home 留在 audit/*-orchestration.json 或 raw_logs/*-command.json。scripts/smoke_gate.py 只应在新的尚未正式执行的目录运行；不要在现有已完成目录重写准入时间证据。正式入口是 `python3 scripts/study.py formal`，逐进程命令、环境、顺序均保留；现有结果存在时脚本不重复有效运行。

资源软阈值1536MiB/220线程未提高；systemd硬限制2GiB、Tasks256、180秒是最后兜底，不能替代原软阈值。正式阶段CM39C_DIAGNOSTIC=0，保留与各组相同的35C/Owner阶段日志；不是完全无插桩的生产性能。
