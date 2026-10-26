# Step21E 运行前方案

只用21D单OS线程所有者、独立Store/Module/WASI和显式scope清理，不允许并发C API或100次。所有新代码在本目录source/vm。

Gas：同WASM、同固定业务参数/TxID/时间；每调用前还原真实初始化后的账本快照。R0保留Instance内状态，R1每次新建，刻意隔离账本变化与Instance历史。fact/ERC721各模式最多3次；buyNow每模式只1根，三个真实init和六真实callee不变。记录输入/账本hash、RWSet、事件、Gas入参/结果、深度和Instance ID。

不插入额外GetGas到Guest执行路径。对固定hash WASM从main.GetGas反汇编提取registry.Gas指针槽，只读memory取得Remain；运行时在原有GetGas处核对一致、指针边界必检，无法核对即停用/失败，不猜地址、不写内存。syscall入口/返回及业务前后记录该值。额外静态GetGas代码无ConsumeGas调用，但仍用probe-off对照检验最终Gas/业务无扰动。

normalCal：不改WASM；先1对预检。之后至多两进程，各预建R0一个及R1三个独立Store bundle（总量4，无后台补池），R0固定预热1次，R1不执行过业务。测量按ABBAAB/BAABBA交替顺序（每模式3次），编译/创建全部在测量前完成，避免R1每次前编译造成直接热态偏差。日志/receipt保留固定，记录CallMethod、exportFunc.Call单调时长、owner线程CPU、host GC与RSS/线程。Guest GC没有公开导出/调试元信息时明确未测，不加导出或改业务。

继续沿用2GiB硬限、RSS1536MiB、Tasks256、Threads220、45秒Go/60秒进程限、MemAvailable8GiB、SwapUsed1GiB；已有失败不覆盖，遇资源/所有者保护停止。Module Serialize/Deserialize只查源码/库符号，不扩展成优化benchmark。

附加API能力预检：实际so导出serialize/deserialize，但没有module_share/obtain符号。只对一个本机生成的常量42微型Module做一次可信序列化→同Engine独立目标Store反序列化→实例化结果核对；同Module另串行实例化两次。没有WASI、并发、真实业务替换或编译优化性能研究。
