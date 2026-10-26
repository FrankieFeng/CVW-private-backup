# Step-21B 可恢复进度

2026-10-26 Asia/Shanghai。分支 step-21b-wasmer-store-lifecycle；保留主工作区既有未提交修改，不纳入本实验提交。

- 阶段0完成：独立目录、分支、进度文件已创建。
- 阶段1进行中：已读Step21主报告及Step21A README/POOL_DIFF/NORMALCAL_ANALYSIS/PROGRESS/STOP。
- 尚未执行动态测试；禁止重跑Step21A STOP场景。
- 已执行：git status/branch/switch、rg文件发现、读取上述报告。
- 下一条安全操作：读取实际vm_pool/runtime/wasmer-go及native源码、锁定版本哈希。
- 阻塞：native二进制与源码映射、同Store生命周期约束尚未确认。

恢复时先读本文件及evidence，不重复危险实验。无Copy/Arena/PB改动，不修改生产生命周期、不push。

## 阶段1完成
已冻结当前源码、Step21A守卫源码/失败日志/退出状态及6.0.1分支源码；见evidence/snapshot-manifest.json。源码明确存在Rc共享引用计数及StoreMut无同步入口，关闭等待也不完整。下一步核查二进制和6.0.1对应关系；禁止共享Store并发动态验证。

## 阶段2完成：版本与并发约束
- 当前Go包是ChainMaker vm-wasmer/v2@v2.4.0内置修改版，不是可直接声明版本号的独立wasmer-go依赖。逐文件hash/本地official目录比较已保存。
- packaged头文件6.0.1；so SHA256 dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9；BuildID 69a11e39bb80e3024770895acf2b093aae04b04f。Step21A实际ldd路径的so相同hash。
- 纠正历史线索：7c14de7f是本地main的7.1.0源码，不能认证6.0.1。已改查本地origin/chainmaker/v6.0.1@091074013fa056df0c6502262eae425927272e10；精确build recipe/源码到so可重建映射仍缺失。
- 实际so反汇编wasm_func_call存在非原子inc/dec，instance_delete亦非原子dec；与6.0.1源码Rc路径一致。不能放行同Store并发。
- 官方检索：WebAssembly/wasm-c-api README、wasmerio/wasmer v6.0.1 store/function源码及wasmer-go issue413；不使用latest证明旧版安全。

## 阶段3完成：守卫归因
- 失败日志、事件逐行JSON、guard实现和outcome已保存evidence/step21a及guard-events.json。
- owner=create/requested=execute；业务d29c…与创建ef82…不同；执行在进入native前被拒绝。属于A（生命周期重叠）+E（无实际native冲突观测）；未发现B/C/D现场证据。
- outcome的systemd状态0不能当guest exit86的实测记录；只确认guard源码os.Exit86且日志命中，不补造退出码。
- 下一步安全操作：仅单OS线程C API串行验证，两个独立进程各3次；不启动WASI/业务/同Store并发，不修改VM。并发矩阵均按源码风险跳过。

即将执行串行 same；恢复先查unit step21b-serial-same，已有log时禁止重复运行。

串行 same 结束，passed=True；结果和退出状态见raw_logs/same-outcome.json。

即将执行串行 different；恢复先查unit step21b-serial-different，已有log时禁止重复运行。

串行 different 结束，passed=True；结果和退出状态见raw_logs/different-outcome.json。

## 阶段4完成：最小动态验证
已执行scripts/run_serial.py，gcc编译+两个独立systemd进程（same/different），每进程固定3次C API调用，均结果42、exit0、已停止。运行库自报6.0.1，与头文件一致。没有WASI/Go绑定/业务Gas认证；没有运行任何重叠场景。RSS/线程采样未赶上短进程，记录0表示没有有效样本，报告必须标未测而非零资源。硬cgroup与30秒timeout仍生效。
下一步：写齐八份审计报告并验证链接/hash/退出状态；不再启动native测试。已执行命令与日志见evidence/build.json、raw_logs/*command/launch/resources/outcome。

## 阶段5完成：后续安全方案
八份要求文档已生成，含所有权图、时序图、并发组合证据分类、旧守卫归因、容量行为和Step22准入。建议独立Store+有界固定所有者作为新安全基线；不是原池性能认证。关键阻塞保留：精确native构建映射、全路径所有权/Finalizer、WASI重绑定和资源、shutdown与信号闭环。

## 最终检查进行中
仅做文档链接、快照hash、语法和退出记录检查；不再运行native。下一条安全操作：检查eight docs和manifest，随后仅git add本Step21B目录并提交，不push。已纠正旧guard事件行号和重复Exports.Close的证据边界；重复vector delete不能仅据Go调用次数认定double-free。

## 最终一致性检查完成
- evidence/final-check.json：八份文档、全部源码快照hash、当前生产源码未变、脚本语法、相对链接、两个串行进程结果/退出均通过。
- 本轮实际native场景：仅两个串行进程，共6次；同Store并发场景0；无新业务Gas认证、无TPS。RSS/线程峰值未采中，明确列为未测。
- 既有Step21A outcome未可靠保存86，不能补造；新串行outcome在停止unit前保存退出状态0。
- 已执行：scripts/run_serial.py一次；只读文档/快照验证；未重跑STOP或修改任何VM生命周期/Gas/网络配置。
- 研究阶段1–5均已完成；运行前提仍未满足，见NEXT_STEP。没有尚待自动运行的动态测试。
- 归档：仅本目录提交到step-21b-wasmer-store-lifecycle；提交结果以该分支git log为准，不push。已有主工作区修改保留。
- 恢复后的下一条安全操作：读取README/CONCURRENCY_CONTRACT/NEXT_STEP及git log；不要运行已有run_serial.py或Step21A suite。需新所有权方案后另登记新实验目录。

## 归档命令处理
首次git commit因本机无user.name/email失败（未创建提交）；使用仅本次命令的Codex作者标识，不修改任何Git全局/仓库配置。原始第三方源码/README快照有上游尾空格，保留字节保证hash；本轮撰写文档和脚本的精确文件清单diff --check通过。
