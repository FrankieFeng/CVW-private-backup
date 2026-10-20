# Step-19：9月reuse/no_reuse入口、产物与指标定向审计

仅只读检查源码、Git、Shell历史、配置、二进制元信息和反汇编，未启动节点、执行合约、编译或修改生产代码。

## 结论

**无法确认给定9月PPT各行与Step-19完全同口径。** 已有证据支持一套本地Go SDK压测工作流，包含两个不同统计入口；7/8月存在明确的并发入口日志，6月存在明确的顺序入口日志，但没有找到9月对应PPT行的参数、入口选择和完整四节点日志。

当前Step-19按用户允许采用的统一N/ΣInvokeTime口径计算，这是一项已确定的当前协议；不能倒推王浅秋PPT必定用该公式。最重要的新发现：**工具目录现存WASM与Step-19全部不同，compute.bigNumCal和hashCal循环上限分别为10000 vs100**。这些工具目录产物属于可恢复候选，尚未证实就是9月PPT用件。

## 1. 入口追踪与证据强度

| 证据 | 直接支持什么 | 不能证明什么 |
|---|---|---|
| toolkit根目录readme.txt:23–35 | 名为“cmc测试”的流程实际运行go run test.go，并使用build_release/cluster_quick脚本 | 不等于使用cmc parallel CLI，更不证明某9月参数 |
| 本地.bash_history:438–443、660–662、776、825 | ./test、在example目录go run test.go、test4gas等确实被输入过 | 无时间戳；是本地frankie记录，不能归为王浅秋某次9月执行 |
| history:663–664及proposing报告20260908100913 | 本地曾查看9月8日报告；该报告四节点均“未找到proposing/commit日志” | 不能当作成功四节点负载或PPT原始TPS证据 |
| example/test.go:25–43 | main→ProcessPressureTest(i) | 文件当前形态不能倒推历史版本 |
| process_pressure.go:37–40 | ThreadNum>0走ClaimTPSCTPSWithSub，否则normalTPSTest | 9月ThreadNum原始值缺失 |
| Init.go:293 | 当前ThreadNum=配置thread_num/Clientslen，整数除法 | 旧版本是否同样整除未确认 |
| 6月23日汇总 | ThreadNum0、LoopNum100、SleepTime0、顺序banner、1600条/总执行时间口径 | 不是9月PPT各行 |
| 7月27日、8月9/25日汇总 | ThreadNum4、并发banner、parallel_claim.go:701/703输出；8月25日ERC mint LoopNum10、SleepTime10 | 不能直接代替9月每节点1000笔参数 |

因此最有证据的**候选程序族**是`chainmaker-performance-test/example/test.go → ProcessPressureTest → 两种入口`，不是仅凭“cmc”名称选择CLI。邻近7/8月的已保存运行支持并发分支是一个较强候选；**9月具体入口仍未知，不能写成已确认并发，也不能确认顺序公式。**

本地toolkit是解压目录，没有.git；CVW/chainmaker-go的Git历史没有找到对应9月PPT参数提交或R0/R1双版本。部分VM文件在早期通过gitlink保存，不能把当前平铺文件当作早期逐字源码。Shell没有`#epoch`时间记录，文件mtime只入清单，不作运行日期或作者证明。

## 2. 两种统计及过滤的实际区别

`parallel_claim.go`：

| 项目 | normalTPSTest（730、805–809行） | ClaimTPSCTPSWithSub（553、693–697行） |
|---|---|---|
| 分子 | 各节点目标方法日志条数相加 | 同左 |
| 分母 | 各节点Invoke纳秒差之和/1e9 | 全节点最大结束−最小开始，再/1e9 |
| 平均含义 | 平均VM窗口成本的倒数 | VM执行事件跨节点发生速率 |
| 请求间空闲 | 不直接计入分母 | 计入首尾跨度 |
| 四节点同TxID | 不去重 | 不去重，不能当唯一交易提交TPS |

两者都调用`getLastTimestamp`而非Map版本。它固定匹配vm_factory.go:438，跳过每文件第一条匹配；按合约与方法筛分子，但179行在方法筛选前累加分母；成功过滤被注释。另一`getLastTimestampMap`固定417行、开启成功过滤并按TxID保留一条，但不在这两个现用调用链中。

各节点都读取当前小时日志，不按本批TxID/时间隔离；旧日志残留、多个方法、重执行可污染结果。代码只归档最后结束节点的system.log，无法从单快照恢复全部四节点聚合。不能将注释“执行成功交易数”当作实际成功过滤。

现存旧工具binary `test`/`test4gas`编译信息为Go1.24.1、SDK v2.3.2等；文件mtime为6月，现有源文件到9月仍有修改。binary同时包含两种入口符号，不能仅以符号存在确定曾选哪条路径。当前Step-19客户端SDK为另一固定环境，不能假定所有客户端版本相同。

## 3. 恢复的WASM候选和业务输入

`generateByteCodePath`在Init.go:423–430指向`contract/claim_demo/<name>-go.wasm`，所以该目录是强关联候选。它没有相应Go源码或可重建补丁，无法以当前CVW源码冒充其精确构建源。

| 合约 | toolkit候选SHA前12位 / Bytes | Step-19 SHA前12位 / Bytes |
|---|---|---|
| compute | f5998558da98 / 4,629,936 | e8b1fe3648b9 / 4,628,317 |
| ERC721 | a692e438748b / 5,178,387 | 4fbad3f2c1d0 / 5,054,538 |
| fact | 9d1953c4b159 / 4,873,088 | 02d64cbced7c / 4,871,418 |

完整SHA/路径见wasm_inventory.csv。静态反汇编，没有执行WASM：

| compute方法 | toolkit compute-go | Step-19原始产物 |
|---|---:|---:|
| bigNumCal循环比较上限 | 10000 | 100 |
| hashCal循环比较上限 | 10000 | 100 |
| normalCal循环比较上限 | 10000000 | 10000000 |

bigNumCal证据是各自`main.bigNumCal`中`i64.const 上限 → i64.lt_s`；同样识别了toolkit的compute-go-origin和compute-modify2两个候选均为10000。反汇编片段按文件保存，不能据今天的源码注释认定历史WASM工作量。WASM哈希不同、循环不同是确定事实，**这些候选是否就是PPT用件仍缺hash/原始部署记录**。

Init.go当前候选参数：

- compute：空业务参数。
- ERC721 mint：同一收件地址，metadata=`http://chainmaker.org.cn/`，tokenId在RandParams中用互斥递增big.Int生成；当前实现虽叫RandomNumberString，实际不是随机字符串，也不使用传入length。
- fact：固定长file_hash、file_name=`aoteman.jpg`；`time`被RandParams改为发送时秒时间戳；不自动生成唯一file_hash。
- Step-19：ERC metadata=`step15`、tokenId从190000递增；fact每次独立file_hash、file_name=`s15file`、time固定1700000000。

这些参数差异可能改变状态访问与分配；尚无证据量化它们造成多少ms，不能认定为311→1416的原因。现有代码还会在getMethodParams中覆盖部分YAML params，后续不能只存配置而不保存最终发送payload。

## 4. 恢复的节点二进制行为

对现存9月8日发布目录的node binary只读Go反汇编：

- Invoke的root和child路径均调用GetInstance，没有在这些路径发现改用同步NewInstance；证据见release-Invoke.asm.txt。
- RevertInstance不走正常归还队列分支，启动goroutine；其闭包先CloseInstance，再发送两个控制信号。现存该发布物是后台补池的no_reuse候选，而不是同步fresh。证据见release-RevertInstance*.asm.txt。
- 该binary与native库完整SHA、Go buildinfo已保存。没有找到与它成对的历史reuse binary；不能将此发布目录自动标为PPT R1。

这里缩小了候选，但不解决9月PPT源码/产物对应问题。当前仓库也没有找到CM_WASMER_POOL_POLICY的Go消费实现，不能以start.sh导出的变量证明历史切换生效。

## 5. ERC721约311 vs当前约1416：哪些能解释、哪些还不能

当前200条样本已验证原始纳秒起止；ERC mint每组20条：R0平均0.524081ms、R1平均0.706078ms，N/Σ分别1908.10/1416.27。所有借出后队列快照为4，零空池等待；R1替补在下次100ms间隔请求前完成。这是当前差距较小的直接证据。

如果PPT的311.4也用N/Σ，它条件上对应约3.211ms平均窗口，和本轮0.706ms不同；如果PPT来自并发首尾跨度入口，则不能这样换算。不能先假定前一种再将约2.5ms差全部归为创建。

| 因素 | 证据等级 |
|---|---|
| 本轮低负载库存充足、创建主要在窗口外 | 已证实 |
| 工具目录ERC WASM与Step-19不同 | 已证实；PPT是否用该候选未知 |
| 当前可恢复工具参数与Step-19不同 | 已证实代码差异；9月参数仍未知 |
| 本地存在两种公式和有局限的筛选 | 已证实；9月采用哪个未知 |
| 高压导致GetInstance等待、创建/关闭CPU争用 | 合理假设，缺历史等待/创建利用率证据 |
| 高压或旧WASI实现导致线程/RSS压力 | 合理假设，缺PPT对应资源曲线 |
| 精确SDK/WASM布局变化造成多大差值 | 未验证 |

当前R0无创建的窗口也增长约141–148MiB RSS，不能把R1全部增长归于新实例。历史旧原始log中有ERC N/Σ约310.06的7月20条样本，但时间、次数、reuse标记与PPT不对应，**数值接近不构成历史311.4已恢复的证据**。

## 6. 当前是否可直接复现并发负载

有工作流组件：四节点release配置/证书、cluster脚本、Go SDK压力工具、日志解析与可用cgroup资源限制。**没有已验证的、隔离且安全的一键历史复现命令**：

- example/test.go在结束后调用`cluster_quick_stop.sh clean`，接着重启原release；多个路径硬编码到当前工作区，原样执行会清理/影响旧账本。不能直接运行。
- 当前toolkit源码/旧binary版本不一致，test4gas源文件已缺失；完整编译兼容性未重新测试，本轮不编译或更新依赖。
- 需要同Store的native创建/关闭/Call/WASI/exports所有权与同步；实际so的非原子Store引用及容器修改风险已在four-node-tps-preflight保存，不用仅保护日志的锁代替。
- 需要处理池退休、在途关闭与remove/add、容量预留、创建失败及等待取消。当前close/reset存在控制loop相互等待的源码路径；资源回收尚未证明有界。
- R0存在fact Gas变化，仅隔离性能参考；四节点结果/状态分歧立即停止，不能认证生产正确性。

最小下一步是隔离路径和退出机制、完整Store访问同步/回调重入设计、关闭在途生命周期及资源计数验证；安全补丁三组相同并记录差异。不能偷偷加根Invoke锁、同步fresh或资源轮换后仍叫历史原版。

## 7. 下一轮怎样做到可直接比较

分两条证据线，不跨线直接计算优化收益：

1. 历史候选复现：冻结toolkit候选原始WASM及完整SHA，R0/R1用同一文件、固定payload序列、相同四节点配置和客户端版本；标记“当前可恢复候选”，而不是已确认PPT原件。取同一轮四节点全部原始日志，不只归档最后节点。
2. 优化增量：选可重建的同源baseline/A产物（例如已验证的Step-18 P=0系列），R0与R1均用该baseline，R1+A+Copy用其同源A变体及按最终WASM重算的模板。不能拿toolkit原件的R1与另一SDK/业务版本的A+Copy比较；不能沿用Step-19的100轮基线对比10000轮优化版。

当前工具语义下，node_num=4、thread_num=4意味着每客户端worker=1、总发送worker=4；loop_num=1000、sleep_time=0、climb_time=0、add_option=no，才是每endpoint发送1000笔的一个明确新配置。它不是恢复出的历史参数。若需要每endpoint4个worker，则配置thread_num=16、loop_num=250，仍是每endpoint1000笔；两者压力量不同，不可混为一组。

安全门槛通过后先loop_num=8做每endpoint8笔的短批、无100ms等待、逐步增加；计数预算包含全节点执行/验证重试，不只客户端发送数。每组独立账本/进程、相同预热，交换顺序并至少两批；触及内存/线程/等待/状态异常即停止，不自动扩成1000笔。模板准备与首次pool创建单列成本，不混入热业务窗。

同批同时输出：

- **主指标**：已选定的根业务N/ΣInvokeTime，成功/失败分开报告，分母分子同样本；部署、init、预热明确排除；四节点先各自统计再按总N/总时间合并，不相加TPS。
- **历史入口对照**：完全记录getLastTimestamp原规则及N/(maxEnd-minStart)；展示原样选择与按RunID/TxID批次选择的差异，不能暗中修正旧筛选。
- **辅助指标**：成功唯一提交TPS、客户端延迟、VM Mean/Median/P95、池等待/队列/创建/关闭、每提交的root attempts、CPU/RSS/Threads/Gas/状态一致性。

结论：时间窗口来源相同，不等于统计公式、输入和负载同口径。当前不能将历史311与1416直接解释为某项优化加速4.55倍。下一轮必须在一个固定产物族、同负载和同筛选协议下同时跑各组，才可直接比较。

## 本目录交付

wasm_inventory.csv完整hash/循环；run_log_inventory.csv历史汇总参数；shell_evidence.csv任务相关命令摘录（无时间戳、不归属王浅秋）；artifact_inventory.csv源码/二进制hash及仅供参考mtime；toolkit和release buildinfo；函数级WASM和node反汇编。未复制整份Shell历史、私钥或凭证。原始日志和代码均未覆盖。
