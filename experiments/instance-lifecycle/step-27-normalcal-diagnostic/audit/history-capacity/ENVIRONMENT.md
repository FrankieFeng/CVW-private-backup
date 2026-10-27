# 环境与版本（容量修复版补充）

测试2026-10-24，整理2026-10-25。源码：c6addbf3ddbc9bb56524b62557a6c52029bb8266；分支experiment/step21-capacity-fix；worktree `/home/frankie/mygitprojects/.worktrees/cvw-step21-fixed`。完整仪表基于原源码474da33，原Step21编译077a8cb，修复父提交dc4d63b。本次只在独立worktree修改grow，不触碰生产源码。

Go go1.25.0 linux/amd64；GOROOT=/usr/local/go，GOTOOLCHAIN=local、GOPROXY=off，不更新依赖。ChainMaker VM/protocol/PB v2.4.0；现有WASM不重编，嵌入SDK精确源码版本不能由宿主go.mod推断，以cases.json WASM SHA为准。模块图沿用父实验modules.jsonl（其中Dir反映原worktree；依赖未修改），实际构建设置见buildinfo-normal/race.txt。

系统Linux 6.18.33.2-microsoft-standard-WSL2 x86_64 GNU/Linux；CPU Intel(R) Core(TM) Ultra 9 285H，16逻辑CPU；WSL31GiB内存/8GiBswap，WSL/Windows版本见wsl-version.txt。未改.wslconfig或重启WSL。

native libwasmer SHA256 `dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9`（packaged Wasmer6.0.1，未改变）。
普通binary SHA256 `0ab673ab49890b56c30aa1e3d03b8be8aa4c9bf93bcfcd8704f564955e553bd0`。
race binary SHA256 `7f7f979f69da3a50c44725699f1acfa2a0e82d30a598c239893eea6ffb172a3f`。
两组用同一普通binary，唯一生命周期开关CM_REUSE_EXPERIMENT=R0/R1。共同CM_STEP21_OBSERVE=1、GOMAXPROCS=4、GOGC=100及同一native library；race单独诊断，不混入主统计。无Copy/A/PB、无全局Store执行锁、无Sleep、无首样本删除。

固定输入与SHA见cases.json及inputs/；R0/R1逐索引输入和返回结果全部一致。fact冻结time=1792827547；mint tokenId1…100。compute bigNum/hash100轮，normal1000万，未更改负载。原入口SnapshotMock和空contractId.Name保持，不宣称真实节点行为。

每组systemd MemoryMax2G、TasksMax256、RuntimeMax60s，RSS软限1536MiB/线程220；Go测试45s；维护排空5s，退出验证；全局MemAvailable≥8GiB、SwapUsed≤1GiB。一次只运行一个测试进程。构建同样单个进行：GOMAXPROCS2、go test -p2 -c、MemoryMax2G/TasksMax192/CPUQuota400%/180s，命令由scripts/build.py重现，原stdout见build-normal/race.log。cgroup构建MemoryPeak异常小，不当作实际进程RSS数据。

boot ID：b91342cd-bf72-4224-b2f3-764116bb6ac3 → b91342cd-bf72-4224-b2f3-764116bb6ac3。全部owned units已停止。资源为离散采样，不认证峰值绝对上界。

InvokeTime原计时起止runtime.go:222及235–237，包含GetInstance/等待、SetGas、CallMethod、Gas读取与defer归还启动；异步Close/grow只在等待造成依赖时影响该窗口，编译/模板（未启用）不在窗内。当前窗使用UnixNano，发现回拨批次已单列。channel耗时在vm_pool.go:674–676用time.Since，GetInstance也用单调时间。

修复代码vm_pool.go:1219–1226，容量10不变。回滚仅弃用实验binary或在实验分支revert c6addbf，不改生产main。无密钥/证书拷贝，不提供含其他PEM夹具的完整runtime_test.go，仅提供最小diff。
