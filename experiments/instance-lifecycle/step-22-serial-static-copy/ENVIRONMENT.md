# Step-22 环境

- 日期2026-10-26（Asia/Shanghai），WSL boot ID前后一致，未发生本轮可观察的WSL重启。
- 父commit87eb9256d5617b1ea07e7ea23e820f4720ff819b；实验代码冻结提交4160b271fda1bba587dd0098d7069e9e74b5a907；独立分支experiment/step22-serial-static-copy，执行工作树/home/frankie/mygitprojects/.worktrees/cvw-step22。
- go version go1.25.0 linux/amd64；Linux 6.18.33.2-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Thu Jun 18 21:54:43 UTC 2026 x86_64 GNU/Linux；CPU Intel Core Ultra 9 285H，16逻辑核；WSL可见约31GiB内存/8GiB swap，测试未用swap。未固定CPU亲和/频率，未采GC暂停或逐线程调度事件。
- 固定GOMAXPROCS2/GOGC100；同binary同时运行A0/A1，无100ms Sleep。
- native6.0.1 SHA dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9；动态加载位置核对audit/ldd.txt；精确源码/构建映射缺失仍保留。
- 最终build4 SHA f83ff5524108f56290767d2b23426f8de4b78454f27f69b5b09db3f9ae89fbc7；早期build3 SHA 4e62f95282266f50fb9e17d234d8bad17496dc429b2629a9da47b14447f6e063，仅探索预检。
- config SHA be15625a9e49480e79b0ffeafdd76579e64ff3d07f4428c2e260208ed6cfee0f；Gas map/MaxPages固定，runtimeGasLimit2^31−1，Module初始meter1e19。
- source.diff相对父D私有模块；仅四文件变化，两新测试文件、D运行器实验分派、fixture放行fact。managed.go/dCompile以及其余绑定全部保持D版；哈希见audit/source_hashes.json。
- 原WASM、noData与Image SHA逐合约见variants.csv；所有A0/A1逻辑source hash相同。ERC与Step16旧artifact不同（9b6e vs4fba），另外四个相同；audit/step16_artifact_identity.json保留核对。
- 附近合约源声明SDK v0.1.3，但既有WASM精确原始构建来源未独立重新证明；未重编译或改SDK。
- 依赖本地Step21C worktree/module cache，不更新版本；go.mod/go.sum/go.work/source/native hashes已存。
- ResourceMax2GiB、RSS软1536MiB；TasksMax256、线程软220；Runtime60s/Go timeout45s；全机MemAvailable最少8GiB、swapUsed最多1GiB；未提高阈值。
- 主实验和补充共33个测试进程均退出，后检查无Step22活动unit。详见audit/final-health.json与resource_summary.csv。

完整可机读环境environment.json；原执行命令raw_logs/*-command.json。build4完整手工orchestrator命令未另存原始JSON，但保留构建输出、binary/source hash；scripts/build.py提供同编译设置的重建命令，不能把重建命令伪称原始launcher逐字记录。
