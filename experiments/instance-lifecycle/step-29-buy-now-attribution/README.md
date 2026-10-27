# Step-29：exchange.buyNow A+Copy性能归因

完成历史审计与新的同期plain/trace对照，每套30三组区块/3批，真实六次下游调用，原始数据全部保留。

新的**未插桩**完整Invoke直接配对节省：

| 对照 | Median [95%CI] ms | 判断 |
|---|---:|---|
| G0→G1 | -4.466 [-9.283, 5.393] | CI跨零，未确认稳定收益 |
| G1→G2 | 3.385 [-3.426, 12.430] | CI跨零，未确认稳定收益 |
| G0→G2 | 2.549 [-2.296, 8.937] | CI跨零，未确认稳定收益 |

主要定位：trace中根export残余集中在子VM Invoke进入之前的cross准备；其中夹具GetContractBytecode会每次分配并复制整份WASM。JSON日志和可测Gas getter/setter另列，不能将未分离的成本都称为JSON或Gas。插桩可能影响执行，定位结果不等于已因果解释旧数据全部残余。详见[BUY_NOW_ANALYSIS](BUY_NOW_ANALYSIS.md)、[历史审计](HISTORICAL_AUDIT.md)、[正确性](CORRECTNESS.md)。

运行与恢复：原独立worktree `.worktrees/cvw-step29`。先读PROGRESS/state/outcome并确认无活动unit；现有outcome保留，严禁删后重跑覆盖。`python3 -B scripts/analyze.py`、`python3 -B scripts/report.py`仅离线复算；`scripts/continue.py`为实际有界执行入口。每个group独立进程，三个进程才是一个三组区块，不能称单Store连续30次。

版本：父29950ab；原binary与新build3的SHA/源码hash/完整构建命令在environment.json、audit与逐进程command.json；Guest来自inputs/variants.json所指Step28已保存WASM，所有SHA再次核对，Gas/SDK/输入不变，MaxPages512/GOMAXPROCS2/GOGC100。独立分支experiment/step29-buy-now-attribution，未修改生产VM、未push、无PPT。

回滚：停止state.json中具体step29 unit并核对PID/cgroup为空，保留现场；本实验只有目录副本与分支，无生产部署需回滚。IDE镜像仅用于阅读，运行使用原worktree及固定依赖；不带Git忽略的.so/host binary时按校验哈希从原环境恢复。

限制：只适用于独立Store、有界串行夹具。真实节点字节码获取路径可能不同，不能用本轮clone成本宣称生产Copy负收益；Table身份、长期Store及原池并发问题仍未解决。
