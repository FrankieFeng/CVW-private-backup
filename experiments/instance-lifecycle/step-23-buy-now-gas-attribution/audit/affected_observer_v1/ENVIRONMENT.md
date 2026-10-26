# Step-23 环境与版本

- 2026-10-26开始，2026-10-27收尾，Asia/Shanghai。独立worktree /home/frankie/mygitprojects/.worktrees/cvw-step23；父394d2914289caace077349dd99677f430005ab6c，历史507310cb391de666cfadf5d3712dcebee13de885；源码冻结提交pending。
- 分支experiment/step23-buy-now-gas-attribution。生产工作区原在step-21b-wasmer-store-lifecycle/620650d，已有脏文件保留；本轮仅新增Step23实验及IDE镜像。
- Host Go1.25.0，GOMAXPROCS2/GOGC100，Go test -p2 -c，GOPROXY=off/GOTOOLCHAIN=local；当前WSL/CPU信息与完整source hashes见environment.json。
- build02 binary SHA `834e7028c15ba0a6bfa8406f51e48e889e19cbf51e17e8cc39af5481f0d21170`，所有26个进程相同。build01因遗漏占位Go包而编译失败，未执行guest；修复只恢复Step22实际source_hashes绑定的6个原Go文件。
- native6.0.1 SHA `dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9`；实际动态加载路径audit/ldd.txt；未编译或修改runtime。精确native构建源码映射仍未认证。
- 原dCompile/opcode/fn Gas映射原字节与Step22相同，max_pages512，原module metering初始1e19、runtimeGasLimit2^31−1。E23不是Gas规则开关。
- 固定三个原WASM SHA在inputs/manifest.json，GetGas槽在inputs/gas-slots.json。source与noData/template hash及Module缓存key在MODULES/preparation.csv，每进程六Module仅准备一次，实际使用三个，不逐子调用编译。
- inputs/business.json冻结root TxID、参数、初始/最终ledger hash和init顺序。BlockVersion1、ETHEREUM地址、固定公开P256公钥与逻辑member、内存账本/真实TxSimContext；不是生产ACL/节点共识验证。
- 原来WASM的精确SDK/compiler构建来源未重新认证；本轮没有重编译或改SDK，A0/A1使用完全相同逻辑source artifact，C1仅按既有方案移除active data。
- 五生命周期块：R0→R1、R1→R0、R0→R1、R1→R0、R0→R1；每条件独立进程1根。五Copy块同样交替R1/C1。每模式probe off/on各一个预检。共26进程、260含init Invoke，非100次/轮，更非TPS实验。
- 上限MemoryMax2GiB/RSS软1536MiB，TasksMax256/线程软220，Go45秒/进程60秒，全机available8GiB/swapUsed1GiB；未提高。合并峰值763.61MiB/177线程。所有进程退出、owner最终登记0、WSL boot ID未变。
- 完整原始执行命令、环境、binary SHA在每个raw_logs/*-command.json；构建命令在audit/build02-command.json。scope、Store与Module实际ID在CALLS及原事件中。每进程本地单调时钟只用于事件排序，不跨进程相减；不以诊断时延作性能主张。
