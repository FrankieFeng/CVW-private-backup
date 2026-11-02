# Step-38B：原C0路径成本诊断

以下为time-only版本根调用窗口P50，每方法6次/3批；alloc诊断另列，不混入时间主统计。各列P50**不可相加冒充总耗时**。ROOT_PREPARATION_SHARES.csv提供同次调用可相加的顺序窗口与比例。

| 方法 | NewStore µs | Builder ms | Finalize ms | WASI Imports ms | CM Imports ms | 2×Invoke SHA ms | prepare SHA+key ms | runtime clone ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| bigInput.inputSize | 7.337 | 0.381 | 0.086 | 0.088 | 0.028 | 2.014 | 0.976 | 0.357 |
| compute.bigNumCal | 8.037 | 0.488 | 0.099 | 0.082 | 0.028 | 2.656 | 1.158 | 0.562 |
| compute.hashCal | 7.957 | 0.450 | 0.097 | 0.095 | 0.030 | 2.293 | 1.089 | 1.077 |
| compute.normalCal | 11.716 | 0.622 | 0.119 | 0.101 | 0.030 | 2.401 | 1.661 | 1.163 |
| erc721.mint | 8.505 | 0.456 | 0.105 | 0.084 | 0.028 | 2.428 | 1.186 | 0.530 |
| exchange.buyNow | 5.458 | 0.487 | 0.098 | 0.080 | 0.028 | 2.041 | 1.003 | 0.328 |
| fact.saveAndFindByFileHash | 8.220 | 0.476 | 0.103 | 0.097 | 0.034 | 2.256 | 1.345 | 0.617 |
| identity.address | 8.863 | 0.426 | 0.105 | 0.084 | 0.029 | 2.336 | 1.140 | 0.996 |
| itinerary.save | 8.375 | 0.427 | 0.120 | 0.109 | 0.029 | 2.420 | 1.138 | 1.469 |
| raffle.query | 9.101 | 0.470 | 0.098 | 0.086 | 0.034 | 2.605 | 1.198 | 0.470 |

NewStore本身只含新Store包装及native创建；不是“独立Store相对共享Store的增量”。本轮没有共享Store反事实。NewStore/创建至S1逐笔比率整体中位约0.261%，WASI builder/finalize/两类imports顺序窗口占比整体中位约23.015%，只是当前插桩路径的描述。

Builder源码进入native wasi_config_new并创建Tokio multi_thread Runtime（native6.0.1 wasi/mod.rs:40），Finalize消费config.runtime并绑定目标Store，不是一个便宜Go struct。尚未单独测Tokio build/defaultFS等子窗，所以不能将Builder全部耗时归到某一个子组件。

校准中fact Factory Invoke的B−A中位+1.570ms，CI[0.065,2.453]；观察到明显扰动/队列或环境信号，尚未唯一分离。B数字是诊断版本原始观察，不是无扰动绝对基准。NewStore远小于SHA/Builder的量级判断有依据，但不承诺每个短阶段达到纳秒级准确。
