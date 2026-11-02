# 典型方法：数据自动筛选与源码约束

CASE_SELECTION.csv保存筛选条件。Copy受益/退化等标签均为未经校正探索性CI分类。没有任何方法满足“A+Copy对其余三组全部CI全正”，因此该类别明确none，不强行挑赢家。所有结论分A/B/C/D。

## compute.bigNumCal

| 阶段（ms，中位数） | Fresh | Copy | A-only | A+Copy |
|---|---:|---:|---:|---:|
| Store preparation | not_measured | not_measured | not_measured | not_measured |
| WASI/import preparation | not_measured | not_measured | not_measured | not_measured |
| NewInstance | 1.359 | 0.084 | 1.528 | 0.074 |
| Copy | 0.000 | 0.988 | 0.000 | 0.892 |
| _start | 1.228 | 1.455 | 0.518 | 0.551 |
| S0_to_S1 | 3.841 | 3.363 | 4.120 | 3.720 |
| S1_to_S2 | 1.245 | 1.476 | 0.534 | 0.570 |
| S2_to_S3 | not_measured | not_measured | not_measured | not_measured |
| CallMethod | 13.899 | 13.695 | 14.984 | 13.595 |
| exportFunc.Call | not_measured | not_measured | not_measured | not_measured |
| Close | 0.496 | 0.443 | 0.542 | 0.504 |
| Owner Invoke | 19.914 | 20.107 | 20.345 | 19.705 |
| Factory Invoke | 22.721 | 22.984 | 22.893 | 22.143 |
| VM external remainder | not_measured | not_measured | not_measured | not_measured |
| SDK E2E | 66.981 | 65.973 | 66.964 | 66.082 |

| 直接对照 | E2E节省 ms [95%CI] | Owner Invoke节省 | _start节省 | TPS增量 |
|---|---:|---:|---:|---:|
| G0→G1 | -0.451 [-6.480, 8.080] | 0.105 [-2.098, 1.547] | -0.145 [-0.704, -0.065] | 0.225 |
| G0→G3 | 3.494 [-5.569, 10.738] | -1.722 [-3.090, 2.989] | 0.697 [0.637, 0.748] | 0.749 |
| G0→G2 | -0.276 [-7.192, 7.089] | 0.266 [-1.334, 3.932] | 0.696 [0.654, 0.728] | 0.067 |
| G1→G2 | -1.070 [-4.984, 2.038] | 0.247 [-2.261, 2.784] | 0.911 [0.761, 1.327] | -0.157 |
| G3→G2 | -1.307 [-10.833, 5.029] | 1.529 [-1.959, 2.374] | 0.012 [-0.092, 0.095] | -0.682 |

1. **主要耗时（A/B）**：大整数计算；CallMethod包含guest math/big与参数/host辅助，不能把全部当初始化。Fresh CallMethod/Owner Invoke逐交易比率中位70.6%；这是窗口占比，不是某一guest函数的CPU占比。
2. **Copy节省什么（A/B）**：对同一block直接比较S0→S1、Owner和E2E，表列测得的效应；移除Data Section、恢复约5万范围已由源码/静态产物确认。
3. **Copy新增成本（A/C）**：restore计时包含身份检查、Memory获取及范围循环；它不是纯memcpy。模板一次性容量/构建另计，不算每笔重复准备。
4. **A改变什么（A/C）**：同源padding使init_bloc目标59页，关联arena gap路径；没有跳过_start、改Guest业务或修改Gas。实际Store/WASI时间未分离。
5. **组合解释（B/C）**：表中G1→G2与G3→G2为直接配对；可测_start收益不保证总窗口收益。交互见INTERACTION_ANALYSIS，不由两个Median相加。
6. **直接证据（A/B）**：原始TxID、阶段和四组Gas/状态核对均保存；样本与批次差异在BATCH_ANALYSIS。Holm222项校正无显著，不能宣称已确定该方法受益。
7. **未证实解释（C/D）**：本轮无Reuse组，不能用它判断历史Reuse/Fresh异常。缓存/页fault、guestGC、hash/clone、WASI分配都需额外独立观测。

## compute.hashCal

| 阶段（ms，中位数） | Fresh | Copy | A-only | A+Copy |
|---|---:|---:|---:|---:|
| Store preparation | not_measured | not_measured | not_measured | not_measured |
| WASI/import preparation | not_measured | not_measured | not_measured | not_measured |
| NewInstance | 1.826 | 0.094 | 1.810 | 0.091 |
| Copy | 0.000 | 1.091 | 0.000 | 1.086 |
| _start | 1.768 | 1.702 | 0.654 | 0.685 |
| S0_to_S1 | 4.849 | 4.273 | 4.946 | 3.934 |
| S1_to_S2 | 1.795 | 1.727 | 0.677 | 0.712 |
| S2_to_S3 | not_measured | not_measured | not_measured | not_measured |
| CallMethod | 5.194 | 5.161 | 5.127 | 5.025 |
| exportFunc.Call | not_measured | not_measured | not_measured | not_measured |
| Close | 0.554 | 0.499 | 0.447 | 0.501 |
| Owner Invoke | 12.382 | 12.315 | 11.660 | 10.092 |
| Factory Invoke | 16.286 | 15.901 | 15.311 | 13.923 |
| VM external remainder | not_measured | not_measured | not_measured | not_measured |
| SDK E2E | 61.890 | 58.959 | 55.971 | 56.982 |

| 直接对照 | E2E节省 ms [95%CI] | Owner Invoke节省 | _start节省 | TPS增量 |
|---|---:|---:|---:|---:|
| G0→G1 | 2.325 [0.044, 5.559] | 0.491 [-0.972, 1.296] | 0.007 [-0.094, 0.184] | 0.895 |
| G0→G3 | 4.603 [-2.826, 7.096] | 0.869 [-0.480, 1.204] | 1.106 [0.980, 1.260] | 0.606 |
| G0→G2 | 3.900 [0.291, 6.924] | 2.525 [1.031, 2.811] | 1.055 [0.921, 1.207] | 0.937 |
| G1→G2 | 1.114 [-4.564, 5.157] | 1.797 [0.757, 3.092] | 1.031 [0.920, 1.107] | 0.042 |
| G3→G2 | -1.440 [-3.487, 3.071] | 1.348 [0.790, 2.342] | -0.035 [-0.057, 0.007] | 0.332 |

1. **主要耗时（A/B）**：hash业务与runtime准备共同构成；固定同源输入，没有修改循环来增收益。Fresh CallMethod/Owner Invoke逐交易比率中位42.9%；这是窗口占比，不是某一guest函数的CPU占比。
2. **Copy节省什么（A/B）**：对同一block直接比较S0→S1、Owner和E2E，表列测得的效应；移除Data Section、恢复约5万范围已由源码/静态产物确认。
3. **Copy新增成本（A/C）**：restore计时包含身份检查、Memory获取及范围循环；它不是纯memcpy。模板一次性容量/构建另计，不算每笔重复准备。
4. **A改变什么（A/C）**：同源padding使init_bloc目标59页，关联arena gap路径；没有跳过_start、改Guest业务或修改Gas。实际Store/WASI时间未分离。
5. **组合解释（B/C）**：表中G1→G2与G3→G2为直接配对；可测_start收益不保证总窗口收益。交互见INTERACTION_ANALYSIS，不由两个Median相加。
6. **直接证据（A/B）**：原始TxID、阶段和四组Gas/状态核对均保存；样本与批次差异在BATCH_ANALYSIS。Holm222项校正无显著，不能宣称已确定该方法受益。
7. **未证实解释（C/D）**：E2E局部正向只是未经多重校正的信号。缓存/页fault、guestGC、hash/clone、WASI分配都需额外独立观测。

## compute.normalCal

| 阶段（ms，中位数） | Fresh | Copy | A-only | A+Copy |
|---|---:|---:|---:|---:|
| Store preparation | not_measured | not_measured | not_measured | not_measured |
| WASI/import preparation | not_measured | not_measured | not_measured | not_measured |
| NewInstance | 1.451 | 0.077 | 1.472 | 0.076 |
| Copy | 0.000 | 0.947 | 0.000 | 0.965 |
| _start | 1.270 | 1.276 | 0.508 | 0.551 |
| S0_to_S1 | 3.804 | 3.869 | 4.375 | 4.187 |
| S1_to_S2 | 1.292 | 1.295 | 0.531 | 0.571 |
| S2_to_S3 | not_measured | not_measured | not_measured | not_measured |
| CallMethod | 77.819 | 75.658 | 74.986 | 74.670 |
| exportFunc.Call | not_measured | not_measured | not_measured | not_measured |
| Close | 0.529 | 0.507 | 0.477 | 0.438 |
| Owner Invoke | 83.625 | 81.833 | 80.161 | 81.342 |
| Factory Invoke | 87.231 | 85.683 | 82.929 | 84.076 |
| VM external remainder | not_measured | not_measured | not_measured | not_measured |
| SDK E2E | 130.456 | 128.237 | 123.970 | 129.922 |

| 直接对照 | E2E节省 ms [95%CI] | Owner Invoke节省 | _start节省 | TPS增量 |
|---|---:|---:|---:|---:|
| G0→G1 | -0.133 [-7.983, 9.680] | -2.050 [-4.317, 6.695] | -0.001 [-0.221, 0.160] | -0.083 |
| G0→G3 | 6.626 [-8.962, 14.880] | 2.916 [-6.738, 10.450] | 0.777 [0.723, 0.921] | 0.317 |
| G0→G2 | -0.240 [-11.769, 10.754] | 2.361 [-5.785, 10.501] | 0.732 [0.690, 0.812] | -0.016 |
| G1→G2 | 0.959 [-12.844, 15.907] | -1.519 [-8.581, 11.618] | 0.742 [0.588, 0.893] | 0.067 |
| G3→G2 | -5.370 [-13.845, 2.130] | -0.389 [-5.596, 1.920] | -0.054 [-0.198, -0.003] | -0.333 |

1. **主要耗时（A/B）**：长计算窗口；CallMethod占Owner Invoke约92%，初始化只占其中一部分。Fresh CallMethod/Owner Invoke逐交易比率中位92.4%；这是窗口占比，不是某一guest函数的CPU占比。
2. **Copy节省什么（A/B）**：对同一block直接比较S0→S1、Owner和E2E，表列测得的效应；移除Data Section、恢复约5万范围已由源码/静态产物确认。
3. **Copy新增成本（A/C）**：restore计时包含身份检查、Memory获取及范围循环；它不是纯memcpy。模板一次性容量/构建另计，不算每笔重复准备。
4. **A改变什么（A/C）**：同源padding使init_bloc目标59页，关联arena gap路径；没有跳过_start、改Guest业务或修改Gas。实际Store/WASI时间未分离。
5. **组合解释（B/C）**：表中G1→G2与G3→G2为直接配对；可测_start收益不保证总窗口收益。交互见INTERACTION_ANALYSIS，不由两个Median相加。
6. **直接证据（A/B）**：原始TxID、阶段和四组Gas/状态核对均保存；样本与批次差异在BATCH_ANALYSIS。Holm222项校正无显著，不能宣称已确定该方法受益。
7. **未证实解释（C/D）**：本轮没有独立exportFunc.Call落盘，也没有Reuse组，不能宣称再现或推翻Step27 guest差异。缓存/页fault、guestGC、hash/clone、WASI分配都需额外独立观测。

## fact.saveAndFindByFileHash

| 阶段（ms，中位数） | Fresh | Copy | A-only | A+Copy |
|---|---:|---:|---:|---:|
| Store preparation | not_measured | not_measured | not_measured | not_measured |
| WASI/import preparation | not_measured | not_measured | not_measured | not_measured |
| NewInstance | 1.520 | 0.085 | 1.739 | 0.095 |
| Copy | 0.000 | 1.119 | 0.000 | 1.059 |
| _start | 1.235 | 1.477 | 0.550 | 0.581 |
| S0_to_S1 | 4.517 | 4.146 | 5.580 | 4.324 |
| S1_to_S2 | 1.254 | 1.507 | 0.570 | 0.611 |
| S2_to_S3 | not_measured | not_measured | not_measured | not_measured |
| CallMethod | 0.394 | 0.335 | 0.389 | 0.343 |
| exportFunc.Call | not_measured | not_measured | not_measured | not_measured |
| Close | 0.317 | 0.350 | 0.321 | 0.333 |
| Owner Invoke | 6.536 | 6.538 | 7.174 | 5.628 |
| Factory Invoke | 9.241 | 10.662 | 9.818 | 9.557 |
| VM external remainder | not_measured | not_measured | not_measured | not_measured |
| SDK E2E | 52.706 | 49.326 | 52.005 | 52.355 |

| 直接对照 | E2E节省 ms [95%CI] | Owner Invoke节省 | _start节省 | TPS增量 |
|---|---:|---:|---:|---:|
| G0→G1 | 2.324 [0.866, 6.777] | 0.016 [-0.970, 0.448] | -0.179 [-0.262, -0.070] | 1.324 |
| G0→G3 | 1.943 [-6.425, 7.817] | -0.194 [-2.187, 1.043] | 0.761 [0.637, 1.049] | 0.182 |
| G0→G2 | 2.306 [-2.864, 5.037] | 0.822 [-0.939, 1.685] | 0.711 [0.617, 1.118] | 0.426 |
| G1→G2 | -4.061 [-7.514, 3.653] | 0.749 [-0.026, 1.621] | 0.965 [0.768, 1.224] | -0.898 |
| G3→G2 | -0.811 [-2.977, 0.287] | 0.469 [-0.224, 2.114] | 0.008 [-0.072, 0.069] | 0.244 |

1. **主要耗时（A/B）**：真实保存和查询；host状态调用嵌在CallMethod。Fresh CallMethod/Owner Invoke逐交易比率中位6.0%；这是窗口占比，不是某一guest函数的CPU占比。
2. **Copy节省什么（A/B）**：对同一block直接比较S0→S1、Owner和E2E，表列测得的效应；移除Data Section、恢复约5万范围已由源码/静态产物确认。
3. **Copy新增成本（A/C）**：restore计时包含身份检查、Memory获取及范围循环；它不是纯memcpy。模板一次性容量/构建另计，不算每笔重复准备。
4. **A改变什么（A/C）**：同源padding使init_bloc目标59页，关联arena gap路径；没有跳过_start、改Guest业务或修改Gas。实际Store/WASI时间未分离。
5. **组合解释（B/C）**：表中G1→G2与G3→G2为直接配对；可测_start收益不保证总窗口收益。交互见INTERACTION_ANALYSIS，不由两个Median相加。
6. **直接证据（A/B）**：原始TxID、阶段和四组Gas/状态核对均保存；样本与批次差异在BATCH_ANALYSIS。Holm222项校正无显著，不能宣称已确定该方法受益。
7. **未证实解释（C/D）**：读写/编码的独立成本未记录，不据整体时间认定PB/JSON根因。缓存/页fault、guestGC、hash/clone、WASI分配都需额外独立观测。

## erc721.mint

| 阶段（ms，中位数） | Fresh | Copy | A-only | A+Copy |
|---|---:|---:|---:|---:|
| Store preparation | not_measured | not_measured | not_measured | not_measured |
| WASI/import preparation | not_measured | not_measured | not_measured | not_measured |
| NewInstance | 1.817 | 0.097 | 1.978 | 0.091 |
| Copy | 0.000 | 1.138 | 0.000 | 1.063 |
| _start | 1.571 | 1.563 | 0.628 | 0.586 |
| S0_to_S1 | 4.751 | 4.077 | 5.084 | 4.192 |
| S1_to_S2 | 1.597 | 1.594 | 0.651 | 0.612 |
| S2_to_S3 | not_measured | not_measured | not_measured | not_measured |
| CallMethod | 0.607 | 0.540 | 0.506 | 0.484 |
| exportFunc.Call | not_measured | not_measured | not_measured | not_measured |
| Close | 0.460 | 0.462 | 0.464 | 0.388 |
| Owner Invoke | 7.674 | 6.726 | 6.855 | 5.764 |
| Factory Invoke | 11.556 | 10.834 | 10.671 | 9.832 |
| VM external remainder | not_measured | not_measured | not_measured | not_measured |
| SDK E2E | 55.988 | 58.892 | 56.369 | 53.134 |

| 直接对照 | E2E节省 ms [95%CI] | Owner Invoke节省 | _start节省 | TPS增量 |
|---|---:|---:|---:|---:|
| G0→G1 | -5.643 [-9.833, -0.139] | 0.926 [0.375, 1.286] | 0.064 [-0.014, 0.316] | -1.352 |
| G0→G3 | -3.627 [-10.376, 6.990] | 1.062 [-0.704, 2.055] | 0.932 [0.845, 1.373] | -0.509 |
| G0→G2 | 3.418 [-5.515, 7.300] | 1.466 [1.133, 3.508] | 0.970 [0.906, 1.416] | 0.757 |
| G1→G2 | 5.924 [-1.413, 11.793] | 0.959 [0.422, 2.309] | 0.948 [0.859, 1.137] | 2.109 |
| G3→G2 | 4.706 [-4.473, 11.545] | 1.080 [-0.176, 2.456] | 0.048 [0.023, 0.084] | 1.266 |

1. **主要耗时（A/B）**：真实状态更新与事件；Copy的VM变化和E2E方向可能不同。Fresh CallMethod/Owner Invoke逐交易比率中位8.0%；这是窗口占比，不是某一guest函数的CPU占比。
2. **Copy节省什么（A/B）**：对同一block直接比较S0→S1、Owner和E2E，表列测得的效应；移除Data Section、恢复约5万范围已由源码/静态产物确认。
3. **Copy新增成本（A/C）**：restore计时包含身份检查、Memory获取及范围循环；它不是纯memcpy。模板一次性容量/构建另计，不算每笔重复准备。
4. **A改变什么（A/C）**：同源padding使init_bloc目标59页，关联arena gap路径；没有跳过_start、改Guest业务或修改Gas。实际Store/WASI时间未分离。
5. **组合解释（B/C）**：表中G1→G2与G3→G2为直接配对；可测_start收益不保证总窗口收益。交互见INTERACTION_ANALYSIS，不由两个Median相加。
6. **直接证据（A/B）**：原始TxID、阶段和四组Gas/状态核对均保存；样本与批次差异在BATCH_ANALYSIS。Holm222项校正无显著，不能宣称已确定该方法受益。
7. **未证实解释（C/D）**：负向E2E三批信号保留；未证实Copy引起缓存变坏/GC或提交等待增加。缓存/页fault、guestGC、hash/clone、WASI分配都需额外独立观测。

## exchange.buyNow

| 阶段（ms，中位数） | Fresh | Copy | A-only | A+Copy |
|---|---:|---:|---:|---:|
| Store preparation | not_measured | not_measured | not_measured | not_measured |
| WASI/import preparation | not_measured | not_measured | not_measured | not_measured |
| NewInstance | 1.390 | 0.079 | 1.468 | 0.071 |
| Copy | 0.000 | 0.920 | 0.000 | 0.781 |
| _start | 1.346 | 1.442 | 0.504 | 0.528 |
| S0_to_S1 | 3.935 | 3.604 | 3.884 | 3.093 |
| S1_to_S2 | 1.366 | 1.461 | 0.522 | 0.547 |
| S2_to_S3 | not_measured | not_measured | not_measured | not_measured |
| CallMethod | 71.370 | 66.347 | 64.483 | 62.874 |
| exportFunc.Call | not_measured | not_measured | not_measured | not_measured |
| Close | 0.386 | 0.428 | 0.384 | 0.369 |
| Owner Invoke | 76.552 | 71.956 | 69.695 | 67.582 |
| Factory Invoke | 78.905 | 74.389 | 71.991 | 69.897 |
| VM external remainder | not_measured | not_measured | not_measured | not_measured |
| SDK E2E | 121.992 | 126.220 | 120.962 | 118.216 |

| 直接对照 | E2E节省 ms [95%CI] | Owner Invoke节省 | _start节省 | TPS增量 |
|---|---:|---:|---:|---:|
| G0→G1 | 2.310 [-20.513, 18.291] | 5.300 [-8.799, 15.704] | -0.062 [-0.303, 0.015] | 0.003 |
| G0→G3 | 4.938 [-11.853, 25.437] | 3.337 [-7.494, 15.033] | 0.821 [0.731, 0.951] | 0.482 |
| G0→G2 | 11.154 [-5.623, 28.093] | 8.791 [2.038, 18.368] | 0.834 [0.772, 0.892] | 0.757 |
| G1→G2 | 15.058 [-15.123, 26.282] | 10.794 [-11.891, 17.150] | 0.917 [0.842, 1.130] | 0.754 |
| G3→G2 | 6.608 [-8.278, 10.719] | 4.284 [-6.709, 9.776] | -0.011 [-0.067, 0.108] | 0.275 |

1. **主要耗时（A/B）**：根CallMethod包含identity三次、ERC721三次真实下游及其Fresh生命周期。Fresh CallMethod/Owner Invoke逐交易比率中位91.8%；这是窗口占比，不是某一guest函数的CPU占比。
2. **Copy节省什么（A/B）**：对同一block直接比较S0→S1、Owner和E2E，表列测得的效应；移除Data Section、恢复约5万范围已由源码/静态产物确认。
3. **Copy新增成本（A/C）**：restore计时包含身份检查、Memory获取及范围循环；它不是纯memcpy。模板一次性容量/构建另计，不算每笔重复准备。
4. **A改变什么（A/C）**：同源padding使init_bloc目标59页，关联arena gap路径；没有跳过_start、改Guest业务或修改Gas。实际Store/WASI时间未分离。
5. **组合解释（B/C）**：表中G1→G2与G3→G2为直接配对；可测_start收益不保证总窗口收益。交互见INTERACTION_ANALYSIS，不由两个Median相加。
6. **直接证据（A/B）**：原始TxID、阶段和四组Gas/状态核对均保存；样本与批次差异在BATCH_ANALYSIS。Holm222项校正无显著，不能宣称已确定该方法受益。
7. **未证实解释（C/D）**：7实例不重叠初始化窗口可相加，7个完整Invoke不可相加；Step29夹具clone结果不能直接当本轮真实节点根因。缓存/页fault、guestGC、hash/clone、WASI分配都需额外独立观测。

## erc721.symbol

| 阶段（ms，中位数） | Fresh | Copy | A-only | A+Copy |
|---|---:|---:|---:|---:|
| Store preparation | not_measured | not_measured | not_measured | not_measured |
| WASI/import preparation | not_measured | not_measured | not_measured | not_measured |
| NewInstance | 1.432 | 0.084 | 1.478 | 0.086 |
| Copy | 0.000 | 0.922 | 0.000 | 0.863 |
| _start | 1.191 | 1.258 | 0.507 | 0.503 |
| S0_to_S1 | 4.382 | 3.452 | 3.697 | 3.443 |
| S1_to_S2 | 1.209 | 1.280 | 0.526 | 0.524 |
| S2_to_S3 | not_measured | not_measured | not_measured | not_measured |
| CallMethod | 0.142 | 0.135 | 0.134 | 0.148 |
| exportFunc.Call | not_measured | not_measured | not_measured | not_measured |
| Close | 0.388 | 0.307 | 0.308 | 0.258 |
| Owner Invoke | 6.229 | 5.048 | 4.724 | 4.415 |
| Factory Invoke | 9.124 | 8.044 | 7.455 | 7.430 |
| VM external remainder | not_measured | not_measured | not_measured | not_measured |
| SDK E2E | 52.522 | 48.561 | 52.524 | 54.039 |

| 直接对照 | E2E节省 ms [95%CI] | Owner Invoke节省 | _start节省 | TPS增量 |
|---|---:|---:|---:|---:|
| G0→G1 | 2.888 [0.127, 7.632] | 0.518 [-1.365, 1.563] | -0.003 [-0.258, 0.060] | 1.413 |
| G0→G3 | 0.793 [-10.059, 4.488] | 0.595 [-1.029, 2.019] | 0.694 [0.633, 0.778] | -0.182 |
| G0→G2 | -3.091 [-6.412, 1.126] | 1.507 [-1.171, 3.018] | 0.688 [0.480, 0.785] | -0.677 |
| G1→G2 | -5.902 [-12.023, -1.895] | 0.819 [-0.635, 1.861] | 0.719 [0.544, 0.789] | -2.090 |
| G3→G2 | -3.547 [-8.625, 7.570] | 0.547 [-1.925, 2.627] | -0.011 [-0.162, 0.032] | -0.495 |

1. **主要耗时（A/B）**：读取真实symbol，本轮仍用InvokeContract提交而非Query-only计时。Fresh CallMethod/Owner Invoke逐交易比率中位2.3%；这是窗口占比，不是某一guest函数的CPU占比。
2. **Copy节省什么（A/B）**：对同一block直接比较S0→S1、Owner和E2E，表列测得的效应；移除Data Section、恢复约5万范围已由源码/静态产物确认。
3. **Copy新增成本（A/C）**：restore计时包含身份检查、Memory获取及范围循环；它不是纯memcpy。模板一次性容量/构建另计，不算每笔重复准备。
4. **A改变什么（A/C）**：同源padding使init_bloc目标59页，关联arena gap路径；没有跳过_start、改Guest业务或修改Gas。实际Store/WASI时间未分离。
5. **组合解释（B/C）**：表中G1→G2与G3→G2为直接配对；可测_start收益不保证总窗口收益。交互见INTERACTION_ANALYSIS，不由两个Median相加。
6. **直接证据（A/B）**：原始TxID、阶段和四组Gas/状态核对均保存；样本与批次差异在BATCH_ANALYSIS。Holm222项校正无显著，不能宣称已确定该方法受益。
7. **未证实解释（C/D）**：短业务可见初始化占比，但节点前后窗口与调度波动仍在。缓存/页fault、guestGC、hash/clone、WASI分配都需额外独立观测。

## identity.alterAdminAddress

| 阶段（ms，中位数） | Fresh | Copy | A-only | A+Copy |
|---|---:|---:|---:|---:|
| Store preparation | not_measured | not_measured | not_measured | not_measured |
| WASI/import preparation | not_measured | not_measured | not_measured | not_measured |
| NewInstance | 1.406 | 0.090 | 1.308 | 0.094 |
| Copy | 0.000 | 0.847 | 0.000 | 0.832 |
| _start | 1.185 | 1.205 | 0.532 | 0.547 |
| S0_to_S1 | 3.545 | 3.217 | 3.331 | 3.005 |
| S1_to_S2 | 1.203 | 1.226 | 0.550 | 0.566 |
| S2_to_S3 | not_measured | not_measured | not_measured | not_measured |
| CallMethod | 0.445 | 0.455 | 0.436 | 0.449 |
| exportFunc.Call | not_measured | not_measured | not_measured | not_measured |
| Close | 0.293 | 0.260 | 0.266 | 0.206 |
| Owner Invoke | 5.780 | 5.554 | 4.546 | 4.247 |
| Factory Invoke | 9.018 | 8.475 | 7.186 | 7.092 |
| VM external remainder | not_measured | not_measured | not_measured | not_measured |
| SDK E2E | 57.215 | 57.432 | 56.204 | 45.799 |

| 直接对照 | E2E节省 ms [95%CI] | Owner Invoke节省 | _start节省 | TPS增量 |
|---|---:|---:|---:|---:|
| G0→G1 | -0.217 [-17.075, 26.584] | -0.363 [-0.670, 1.707] | -0.025 [-0.276, 0.005] | 1.148 |
| G0→G3 | 3.587 [-16.399, 13.481] | 1.234 [0.182, 1.889] | 0.653 [0.444, 0.881] | 0.078 |
| G0→G2 | 7.208 [-2.262, 16.216] | 1.355 [1.219, 1.534] | 0.689 [0.625, 0.825] | 2.837 |
| G1→G2 | 7.425 [-10.369, 14.813] | 1.718 [-0.488, 2.204] | 0.714 [0.620, 1.100] | 1.689 |
| G3→G2 | 12.628 [-6.273, 14.137] | 0.300 [-0.669, 1.173] | -0.028 [-0.057, 0.245] | 2.759 |

1. **主要耗时（A/B）**：改管理员后当前签名者权限变化，每批只有1次合法目标调用。Fresh CallMethod/Owner Invoke逐交易比率中位7.7%；这是窗口占比，不是某一guest函数的CPU占比。
2. **Copy节省什么（A/B）**：对同一block直接比较S0→S1、Owner和E2E，表列测得的效应；移除Data Section、恢复约5万范围已由源码/静态产物确认。
3. **Copy新增成本（A/C）**：restore计时包含身份检查、Memory获取及范围循环；它不是纯memcpy。模板一次性容量/构建另计，不算每笔重复准备。
4. **A改变什么（A/C）**：同源padding使init_bloc目标59页，关联arena gap路径；没有跳过_start、改Guest业务或修改Gas。实际Store/WASI时间未分离。
5. **组合解释（B/C）**：表中G1→G2与G3→G2为直接配对；可测_start收益不保证总窗口收益。交互见INTERACTION_ANALYSIS，不由两个Median相加。
6. **直接证据（A/B）**：原始TxID、阶段和四组Gas/状态核对均保存；样本与批次差异在BATCH_ANALYSIS。Holm222项校正无显著，不能宣称已确定该方法受益。
7. **未证实解释（C/D）**：N=3；宽CI典型低功效，不是最有代表性的稳定无效结果。缓存/页fault、guestGC、hash/clone、WASI分配都需额外独立观测。

## identity.addWriteList

| 阶段（ms，中位数） | Fresh | Copy | A-only | A+Copy |
|---|---:|---:|---:|---:|
| Store preparation | not_measured | not_measured | not_measured | not_measured |
| WASI/import preparation | not_measured | not_measured | not_measured | not_measured |
| NewInstance | 1.854 | 0.093 | 1.679 | 0.094 |
| Copy | 0.000 | 1.112 | 0.000 | 1.085 |
| _start | 1.668 | 1.592 | 0.600 | 0.606 |
| S0_to_S1 | 4.967 | 4.154 | 4.701 | 4.247 |
| S1_to_S2 | 1.694 | 1.618 | 0.631 | 0.634 |
| S2_to_S3 | not_measured | not_measured | not_measured | not_measured |
| CallMethod | 0.147 | 0.140 | 0.133 | 0.127 |
| exportFunc.Call | not_measured | not_measured | not_measured | not_measured |
| Close | 0.482 | 0.444 | 0.391 | 0.381 |
| Owner Invoke | 7.572 | 6.348 | 5.957 | 5.499 |
| Factory Invoke | 11.486 | 10.440 | 9.455 | 9.329 |
| VM external remainder | not_measured | not_measured | not_measured | not_measured |
| SDK E2E | 59.890 | 54.847 | 54.207 | 54.271 |

| 直接对照 | E2E节省 ms [95%CI] | Owner Invoke节省 | _start节省 | TPS增量 |
|---|---:|---:|---:|---:|
| G0→G1 | 5.487 [-2.953, 11.633] | 0.901 [0.451, 1.589] | 0.054 [-0.003, 0.234] | 1.805 |
| G0→G3 | 7.173 [1.216, 11.713] | 1.034 [0.375, 2.329] | 1.061 [0.935, 1.360] | 2.160 |
| G0→G2 | 4.950 [0.287, 9.386] | 1.474 [0.280, 2.670] | 1.060 [0.929, 1.333] | 1.822 |
| G1→G2 | 1.452 [-7.588, 5.124] | 0.890 [-0.436, 1.732] | 1.020 [0.905, 1.103] | 0.017 |
| G3→G2 | 0.005 [-4.975, 2.309] | 0.281 [-0.719, 2.373] | -0.008 [-0.112, 0.055] | -0.337 |

1. **主要耗时（A/B）**：独立白名单业务读写，A-only局部有利，组合未必进一步有利。Fresh CallMethod/Owner Invoke逐交易比率中位2.0%；这是窗口占比，不是某一guest函数的CPU占比。
2. **Copy节省什么（A/B）**：对同一block直接比较S0→S1、Owner和E2E，表列测得的效应；移除Data Section、恢复约5万范围已由源码/静态产物确认。
3. **Copy新增成本（A/C）**：restore计时包含身份检查、Memory获取及范围循环；它不是纯memcpy。模板一次性容量/构建另计，不算每笔重复准备。
4. **A改变什么（A/C）**：同源padding使init_bloc目标59页，关联arena gap路径；没有跳过_start、改Guest业务或修改Gas。实际Store/WASI时间未分离。
5. **组合解释（B/C）**：表中G1→G2与G3→G2为直接配对；可测_start收益不保证总窗口收益。交互见INTERACTION_ANALYSIS，不由两个Median相加。
6. **直接证据（A/B）**：原始TxID、阶段和四组Gas/状态核对均保存；样本与批次差异在BATCH_ANALYSIS。Holm222项校正无显著，不能宣称已确定该方法受益。
7. **未证实解释（C/D）**：不能由此得出所有identity方法都适合A-only。缓存/页fault、guestGC、hash/clone、WASI分配都需额外独立观测。
