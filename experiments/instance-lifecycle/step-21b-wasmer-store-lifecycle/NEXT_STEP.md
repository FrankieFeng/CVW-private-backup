# Step21/Step22前的安全边界和后续方案

当前结论是**共享Store的无同步并发不能放行**，并有关闭等待环；没有发现Step21A已造成native破坏的证据。精确构建来源未闭合。现阶段继续保留Step21/21A原始结果及STOP，不进行默认Fresh+Copy压测。

## 必须解决的事项

1. **锁定运行库**：取得so对应commit、patch、Cargo.lock、Rust/LLVM版本、features、构建命令和产物hash，或生成一个可重建的新基线。当前6.0.1分支只是候选。更新native后必须重新测baseline，不能继续沿用旧倍率。
2. **所有者覆盖全生命周期**：Store/Instance/exports/functions/memory/Gas/WASI创建、执行和销毁全部归固定所有者；包括Go Finalizer及错误路径。只锁new/call、单次LockOSThread、只锁日志都不充分。
3. **受控退场**：拒绝新Invoke→取消/唤醒等待获取→等待活跃调用结束→停止新补池→收束已接受创建→所有已借出对象归还或在所有者关闭→完成close事件及计数→确定性释放WASI/imports/exports/module/store→join所有worker。控制loop等待库存时必须还能处理归还/完成事件；shutdown不能依赖已停止的消费者/信号接收者。
4. **供给预算与错误处理**：worker持有有界的请求/在建/库存/借出/待关闭计数，用需求票据去重apply和add，发送有取消；创建失败回滚预留，不入nil。语义变化必须同时用于所有对照，并记录改变了什么。不能把新的去重算法假称原版容量补丁。
5. **WASI资源**：不能跨Store复用WasiEnvironment；确认同Store重复Initialize、on_exit及Store对象表保留、Tokio线程实际释放。freelist cap仅是切片上界。异步Finalizer改为所有者队列回收时，队列也必须有界且不会在关闭后调用native。
6. **回调与重入**：guest→host→跨合约调用需明确Store归属与返回，检查同合约递归、持有parent借用时重新借Store、多个所有者互等；不要只靠一把不可重入锁。Go注册表、ctxIndex、全局统计与cached wrapper另行审计。

## 最小修正候选及对性能机制的影响

| 候选 | 修正范围 | 创建/执行/供给并行度 | 可报告的性质 |
|---|---|---|---|
| 每Store固定所有者，所有操作串行 | 可最小化生命周期同步范围；不共享native handle到其他线程；显式销毁并禁用/重定向危险Finalizer | 同池Store内创建/执行/关闭串行；跨池可并行；改变原重叠机制 | 功能和生命周期诊断基线，**不能称原始实例池性能** |
| 每Fresh Instance独立Store及固定所有者 | 改造Instance构造API、相关imports/WASI和Module绑定；严格有界owner数量；所有者接收业务/关闭命令，避免迁移native对象 | 可使A创建/B执行/C关闭分别在独立Store重叠；协调器仍限制同池一次创建一个，保留后台供给方向 | 优先研究方向，但新安全基线，分配/调度/内存成本必须量化 |
| 有界独立进程slot | 每进程Store完全私有，业务参数/结果经IPC；每slot串行创建/执行/关闭 | slot间可重叠；IPC与调度改变成本，不能跨进程移动native Instance | 隔离验证/故障定位环境，不直接替代VM日志原性能 |
| 修改C API为真正并发Store | 不止Rc换Arc，还要解决StoreMut别名/对象表/VM内存/回调和销毁 | 潜在保留更多原并行；实现及认证范围大 | 本轮不建议作为最小修正，也未实施 |

独立Store构造要注意：当前Go `NewInstance(module,imports)`固定用`module.store`，仅新建另一个Go Store变量没有作用。需要显式目标Store构造接口；先验证native Module跨Store/Engine的合法方式，必要时独立反序列化/编译，准备成本单列。`wasm_store_clone`的Rc clone不是隔离。

可以先设计2–3个有界所有者槽位，每个Store从创建到销毁始终由同一OS线程处理，统一协调器限制并行创建为1；业务线程只传命令/收结果。跨槽位后台创建与执行仍可重叠，但必须证明传递的是所有者令牌而非共享native调用权。Store随每次Fresh销毁会阻止对象表无限保留，却可能造成WASI runtime积累；因此先做独立进程短批及资源计数，尚不具备直接实施该性能方案的前提。

## 如何恢复连续负载对照

若以后有**针对该二进制/修正版的充分证据**支持默认共享Store并发，可在生命周期退场问题解决后恢复原空池、min5/max10/grow5、单creator、连续Invoke、异步回收的实验协议；不能仅关闭guard即放行。目前没有这份证据，不能无条件承诺“原机制完全不变且安全”。

选择独立Store时，登记新的安全基线，保留有限队列和后台供给，不在两次Invoke间等待、不预填或丢首样本；明确新增所有者/Store与旧模式的差异。R0在同一安全架构下仅作隔离参考，R1不复用执行过的Instance。先少量确定输入核对结果、Gas、实例唯一性和完整退场；有失败即停，不因赶100次而扩大。全部通过后才登记连续小批，再考虑原Step21三批配对；实际节点高并发仍需单独过门。

容量original/capacity比较也必须使用同一安全架构、同一binary、同一计时边界和输入，准确标出供给策略。原版已存在可证明的满队列路径，不为比较再次强行触发；可以做不进入native的有界状态机分析，但不能将其模拟值当实际TPS。

## Step22 Fresh+Copy准入

本轮不实现Copy。准入需：安全基线来源固定、所有权及回调审计通过、每Instance资源确定关闭且退场可join、RSS/线程在边界内、连续小批无异常、业务/Gas对齐。再在**同一新安全架构**上只切Fresh/Fresh+Copy，保持并行创建数、补池需求、WASI生命周期、计时和输入一致。

Copy须使用可重建同源WASM及匹配模板，保留Fresh业务Instance，不额外加入Arena/PB因素；单列模板准备、初始化和复制成本，同时观测GetInstance等待。若独立Store策略本身改变了供给能力，就以它作为两组共同基线，不能拿旧容量修复版TPS当Copy增益分母。

交付环境当前可信之处在于版本/源码/失败证据已冻结、运行范围有界且可恢复；**安全并行Fresh性能环境仍待实现与验证**。这项阻塞不能用本轮6次成功、Go race通过或新增全局VM锁消除。
