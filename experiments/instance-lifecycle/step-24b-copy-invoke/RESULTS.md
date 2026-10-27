# Step-24B 结果：有界串行完整Invoke

2026-10-27 Asia/Shanghai。先审计、预登记、预检及先导，再完成135个单合约正式进程（每合约45进程、3批各15进程×2对），另3预检及8个buyNow进程。不是同Store连续30对；线程累积限制下没有扩大单进程预算。A0/A1只比较Baseline Fresh与静态Memory Copy，没有A段/PB等优化。

## 完整Invoke主结果

| 合约 | 对数/独立批 | A0 Median/P95 ms | A1 Median/P95 ms | 配对节省Median [95%CI] ms | 正向比例 |
|---|---:|---:|---:|---:|---:|
| compute.bigNumCal | 90/3 | 5.020/6.758 | 4.290/5.981 | 0.670 [0.468, 1.014] | 74/90 (82.2%) |
| fact.saveAndFindByFileHash | 90/3 | 5.178/6.895 | 4.590/5.962 | 0.750 [0.654, 0.967] | 72/90 (80.0%) |
| erc721.mint | 90/3 | 5.360/7.474 | 4.692/6.241 | 0.711 [0.485, 0.957] | 75/90 (83.3%) |

三个合约各批完整Invoke配对节省中位数均为正，整体95%聚类bootstrap区间均在零以上：**本轮条件支持静态初始化收益传递到完整Invoke**。这不是每次都更快；270个单合约正式配对有49对反向，全部保留，未剔除异常值。不能扩大为所有合约、长寿命Store或真实节点稳定收益。

配对节省是逐对A0−A1的中位数，不是两组Median相减。P95最近秩；每合约90对、45进程聚类、仅3批，置信区间是固定本机/本时段有界进程模型下的探索性估计，不认证长期稳定性。预检、init、Module/模板准备与最终缓存关闭不计入表中Invoke；每次Instance/WASI关闭计入。详见AUDIT.md。

## 初始化收益及阶段传递

纯静态初始化窗口NewInstance+Copy：

| 合约 | 对数/独立批 | A0 Median/P95 ms | A1 Median/P95 ms | 配对节省Median [95%CI] ms | 正向比例 |
|---|---:|---:|---:|---:|---:|
| compute.bigNumCal | 90/3 | 1.705/2.747 | 0.992/1.721 | 0.748 [0.693, 0.886] | 87/90 (96.7%) |
| fact.saveAndFindByFileHash | 90/3 | 1.768/2.741 | 1.048/1.736 | 0.680 [0.580, 0.779] | 84/90 (93.3%) |
| erc721.mint | 90/3 | 1.898/3.080 | 1.156/1.769 | 0.744 [0.620, 0.867] | 89/90 (98.9%) |

这里每条样本先求newinstance_ns+copy_ns再配对，不把不同中位数混加。Invoke级S0→S1还包含WASI/imports准备，因此不等于纯Data初始化；S0=Invoke入口，S1=NewInstance/Copy后，S2=WASI.Initialize/_start后，S3=业务/Gas结果后关闭前。全部阶段有嵌套，不可把CallMethod再次加到S2→S3。TIMING.csv资源值为每根调用返回后的实际RSS/线程边界，子行仅引用所属根边界；没有声称获得每callee瞬时资源。

| 合约 | 阶段 | 配对节省Median [95%CI] ms |
|---|---|---:|
| compute.bigNumCal | NewInstance | 1.643 [1.562, 1.900] |
| compute.bigNumCal | Copy（A0为0，故节省为负成本） | -0.918 [-0.976, -0.876] |
| compute.bigNumCal | WASI/imports | -0.037 [-0.124, 0.026] |
| compute.bigNumCal | S0→S1 | 0.598 [0.465, 0.823] |
| compute.bigNumCal | S1→S2 | 0.042 [0.016, 0.077] |
| compute.bigNumCal | S2→S3 | 0.019 [-0.002, 0.048] |
| compute.bigNumCal | CallMethod | 0.019 [-0.001, 0.042] |
| compute.bigNumCal | Close | 0.002 [0.000, 0.004] |
| fact.saveAndFindByFileHash | NewInstance | 1.683 [1.619, 1.852] |
| fact.saveAndFindByFileHash | Copy（A0为0，故节省为负成本） | -0.971 [-1.156, -0.929] |
| fact.saveAndFindByFileHash | WASI/imports | 0.075 [-0.112, 0.172] |
| fact.saveAndFindByFileHash | S0→S1 | 0.756 [0.485, 1.007] |
| fact.saveAndFindByFileHash | S1→S2 | 0.007 [-0.036, 0.067] |
| fact.saveAndFindByFileHash | S2→S3 | 0.043 [-0.009, 0.104] |
| fact.saveAndFindByFileHash | CallMethod | 0.040 [-0.013, 0.101] |
| fact.saveAndFindByFileHash | Close | 0.001 [-0.002, 0.003] |
| erc721.mint | NewInstance | 1.813 [1.731, 2.048] |
| erc721.mint | Copy（A0为0，故节省为负成本） | -1.069 [-1.170, -1.010] |
| erc721.mint | WASI/imports | -0.014 [-0.142, 0.119] |
| erc721.mint | S0→S1 | 0.744 [0.471, 0.875] |
| erc721.mint | S1→S2 | 0.012 [-0.048, 0.061] |
| erc721.mint | S2→S3 | 0.042 [0.009, 0.062] |
| erc721.mint | CallMethod | 0.039 [0.009, 0.063] |
| erc721.mint | Close | 0.000 [-0.001, 0.002] |

主要可解释节省位于NewInstance静态Data初始化；A1另支付Host区间Copy成本，净初始化省约0.68–0.75ms。A1在Copy timer后还有Ranges字节计数记账循环，该观测开销计入S0→S1/Invoke，未算入pure static_init；本轮按22原样保留。后续准备/执行/关闭存在噪声，不能用各阶段中位数相加解释整笔中位数。对阶段均值可作线性核算，但本轮不把其他窗口偶发差异归因于Copy。

## 每批与顺序

| 合约 | 批次 | 有效对 | Invoke节省Median ms | 正向比例 |
|---|---:|---:|---:|---:|
| compute.bigNumCal | 1 | 30 | 0.946 | 86.7% |
| compute.bigNumCal | 2 | 30 | 0.548 | 83.3% |
| compute.bigNumCal | 3 | 30 | 0.605 | 76.7% |
| fact.saveAndFindByFileHash | 1 | 30 | 0.939 | 80.0% |
| fact.saveAndFindByFileHash | 2 | 30 | 0.696 | 80.0% |
| fact.saveAndFindByFileHash | 3 | 30 | 0.711 | 80.0% |
| erc721.mint | 1 | 30 | 0.782 | 86.7% |
| erc721.mint | 2 | 30 | 0.528 | 83.3% |
| erc721.mint | 3 | 30 | 0.828 | 80.0% |

### 顺序分层（补充离线分析）

| 合约 | 配对中先运行 | n | Invoke节省Median [95%CI] ms | 正向比例 |
|---|---|---:|---:|---:|
| compute.bigNumCal | A0 | 45 | 0.230 [0.097, 0.406] | 68.9% |
| compute.bigNumCal | A1 | 45 | 1.197 [0.829, 1.400] | 95.6% |
| erc721.mint | A0 | 45 | 0.292 [0.186, 0.593] | 75.6% |
| erc721.mint | A1 | 45 | 0.983 [0.866, 1.316] | 91.1% |
| fact.saveAndFindByFileHash | A0 | 45 | 0.142 [-0.113, 0.488] | 60.0% |
| fact.saveAndFindByFileHash | A1 | 45 | 1.053 [0.841, 1.254] | 100.0% |

收益幅度明显依赖先后顺序，不能把平衡设计下总体中位数解释为顺序无关常数；尤其fact在A0先分层的95%CI为[-0.113,0.488]ms，跨零；不能称该顺序已确认收益。这是事后分层，未用于挑选/剔除样本或触发继续运行。完整Invoke的强结论限于预登记的平衡顺序总体。

每个单合约进程两配对恰好一对A0先/一对A1先，整体45对/顺序。Module准备顺序也按进程交替（45进程不能完全二等分，23/22），未根据耗时选种子/样本。ORDER_SENSITIVITY.csv同时保存两种因素；有顺序/时期敏感性但未删样本。统计固定seed240027，10000次先抽batch再抽process的配对bootstrap，同进程两对整体保留；没有把180条单独Invoke当独立配对。

## buyNow扩展：根与六callee

| 合约 | 对数/独立批 | A0 Median/P95 ms | A1 Median/P95 ms | 配对节省Median [95%CI] ms | 正向比例 |
|---|---:|---:|---:|---:|---:|
| exchange.buyNow | 3/3 | 76.630/83.117 | 57.600/73.932 | 6.628 [2.698, 28.385] | 3/3 (100.0%) |

只有3独立对，3/3为正时bootstrap区间正值很大程度受小样本支持集限制；**不能据此声称buyNow稳定收益**。三组正式Full Invoke节省为6.628、28.385、2.698ms；正式样本未重复22的A1慢15.765ms，但宿主准备/启动波动仍明显。

| 批次/阶段 | 根Full Invoke节省 ms | 全7调用纯静态初始化节省 ms | 六callee WASI/imports节省 ms | 全7 _start节省 ms |
|---|---:|---:|---:|---:|
| preflight 0 | -1.351 | 4.821 | -6.000 | -0.330 |
| formal 1 | 6.628 | 4.304 | 2.629 | 0.886 |
| formal 2 | 28.385 | 8.861 | 11.344 | 4.943 |
| formal 3 | 2.698 | 3.774 | 0.734 | -2.258 |

预检反向1.351ms仍保留，其六callee准备A1多5.9995ms；该过程含S1全Memory SHA，不混入正式性能。正式第2批A0六callee准备反而多11.344ms，连同启动/其他窗口导致更大正向值；不能把28.385ms全部认作Copy。实际六子调用逐窗口见BUY_NOW_STAGE_EFFECTS.csv；BUY_NOW_DECOMPOSITION.csv只加互不嵌套的创建/start/close子阶段，不把根与子Invoke重复相加。未测每窗口owner线程CPU/调度/分配器因果，不宣称准备波动一定由调度造成。

旧22第三批两原log重算Full Invoke A0−A1=-15.764944ms，六callee WASI/imports=-19.732278ms（audit/historical-buyNow-recompute.json），说明历史反向确实主要发生在准备窗口。新样本出现不同方向的大准备差；证据支持它能掩盖或放大Copy净收益，尚不能证明某一反向机制稳定存在。

## Module/模板成本与复制量

| 合约 | 模板准备Median ms | A0 Module准备Median ms | A1 Module准备Median ms | 每次Copy Bytes |
|---|---:|---:|---:|---:|
| compute | 12.258 | 611.835 | 583.727 | 1167957 |
| fact | 12.788 | 650.962 | 623.192 | 1209635 |
| erc721 | 12.735 | 689.159 | 659.881 | 1273888 |
| exchange | 6.182 | 539.236 | 518.234 | 1080586 |
| identity | 9.833 | 633.583 | 609.359 | 1216964 |

Module准备含config/Engine/Store/Validate/compile及metadata，不是纯编译器函数；各缓存只准备一次，无不对称逐调用编译。每个独立进程重建缓存的真实总成本全数保存在MODULE_PREPARATION.csv；本轮Invoke收益不含这些一次性成本，不能用于估计进程级端到端收益/摊销或原生产池性能。

## 正确性、资源与可推广性

共146个测试进程正常退出，277对成功路径语义检查相同（含预检），最终native包装登记0，所有PID/cgroup结束。单合约正式90对/合约与buyNow3对，全部Fresh，Gas/返回/根读写集/事件/初始最终账本一致。最高RSS采样/边界763.01MiB，线程176；无STOP、阈值未放宽。

Store期内线程仍随WASI累积，单合约边界通常57→74→91→108，进程最终释放；没有解决长期Store生命周期。真实Table函数身份、动态Globals、异常/OOG、完整callee内部RWMap、并发和真实节点继续not_tested。原始记录与计时范围见CORRECTNESS.md、RESOURCE_SUMMARY.csv、raw_logs和AUDIT.md。

本结果足以支持进一步设计**有界、隔离的节点功能验证**，但不足以直接启动真实节点并发Fresh性能实验或生产启用。必须先补Table/异常语义、长期WASI/Store供给与回收协议和节点路径等价性；不能把进程隔离下的90对写成同Store连续90对或默认池TPS。精确native构建来源仍未闭合。本轮不部署节点、不新增优化、不push。
