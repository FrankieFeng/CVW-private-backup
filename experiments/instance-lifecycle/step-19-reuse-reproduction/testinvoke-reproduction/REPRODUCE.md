# 给王浅秋的最小复现材料

本包未经发送。它记录当前CVW上的直接TestInvoke对照，不声称是历史四节点PPT原件。结果和风险先读README.md；每组100次，3个独立批次，不能当成100次独立实验。

## 固定源码

公开基础：`https://github.com/wqqkakuiii/CVW.git`，commit `c3e8f2cc1479a11450d61e342a93c3b2416b7cff`。

实际测试工作树commit：`9caf9d2da13eef64363ad39e84a3a19eb2957bbf`（未推送的实验分支）；source-vs-github.patch是该源码相对公开基础的完整chainmaker代码差异。原始runtime_test.go与公开基础逐字相同，哈希在environment.json，包内仅摘录本次入口，避免分发文件里其他方法的内嵌证书/私钥测试夹具。

在新的检出中准备，勿在原账本或脏工作区执行：

```bash
git clone https://github.com/wqqkakuiii/CVW.git cvw-testinvoke-repro
cd cvw-testinvoke-repro
git checkout --detach c3e8f2cc1479a11450d61e342a93c3b2416b7cff
git apply /absolute/path/to/material/source-vs-github.patch
# 若源码检出自带的WASM与下面哈希不同，使用包中compute-go.wasm替换新检出中的同名文件。
```

不是从本地Git commit推断GitHub已更新；基础commit经本轮git ls-remote确认。全量模块版本在modules.jsonl，工作区go.mod/go.work/sum快照为workspace-*；没有升级依赖。若按固定依赖初次下载，应使用保存的sum校验，不应自动升级。

## 固定产物与配置

- WASM：compute-go.wasm，SHA256 `e8b1fe3648b9f731f90352aff1796195f9f1efd1c4043bafec966fac53952507`，4,628,317 Bytes，bigNumCal 100轮原版；业务参数为空，内置mock基础参数见parameters.json。
- Go1.25.0、CGO=1、Linux amd64；详细WSL内核、CPU见environment.json。本机默认go的GOROOT推断失败，构建实际显式设置GOROOT=/usr/local/go，仍是已安装同一版本。
- 原packaged native库SHA256 `dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9`，在固定GitHub检出中提供。包不重复携带so或测试binary；请先校验库，不替换成其他Wasmer版本。
- R0：CM_REUSE_EXPERIMENT=R0；R1：CM_REUSE_EXPERIMENT=R1；两组同一binary、GOMAXPROCS=4、无Copy/A/PB。
- 默认空业务池、首次等待触发grow，后台补池保持原状；没有预填池、预热排除、间隔、根锁或同步fresh。

## 编译与实际执行方式

先在新检出中把包中compute-go.wasm放到`chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0/testdata/compute-go.wasm`。设置以下变量为实际绝对路径：

```bash
export STEP19_VM_DIR=/absolute/path/to/cvw-testinvoke-repro/chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0
export STEP19_OUTPUT_DIR=/absolute/path/to/new-empty-results
mkdir -p "$STEP19_OUTPUT_DIR"
export GOROOT=/absolute/path/to/installed/go1.25.0
export GOTOOLCHAIN=local
export GOWORK=/absolute/path/to/cvw-testinvoke-repro/go.work
export LD_LIBRARY_PATH="$STEP19_VM_DIR/wasmer-go/packaged/lib/linux-amd64"
cd "$STEP19_VM_DIR"
"$GOROOT/bin/go" test -c -o "$STEP19_OUTPUT_DIR/testinvoke.test"
"$GOROOT/bin/go" test -race -c -o "$STEP19_OUTPUT_DIR/testinvoke-race.test"
```

本机已缓存构建使用GOPROXY=off；在其他机器如依赖未缓存，先按固定版本准备依赖，不要把下载/编译纳入InvokeTime。

**原始入口的直接命令**为`go test -count=1 -run '^TestInvoke$' -v . -args -invoke_contract_name compute -invoke_contract_method bigNumCal -invoke_contract_type go -invoke_test_time 100`，切换R0/R1环境变量。实际先编译一次、再各起独立测试进程，避免go test结果缓存。普通版每组实际完整命令都保存在a/b/c-*-command.json，安全封装如下：

```bash
# 先做独立诊断，-race耗时不计入性能结果；发现race/资源异常就停止。
python3 /absolute/path/to/material/run_guarded.py --label check-r0 --policy R0 --race
python3 /absolute/path/to/material/run_guarded.py --label check-r1 --policy R1 --race
# 原始入口存在未完成回收及native并发局限；阅读README后再决定是否仅作隔离短时复核。
# 若复核，不扩展并发或其他合约，保留有界保护。
python3 /absolute/path/to/material/run_guarded.py --label a-r0 --policy R0
python3 /absolute/path/to/material/run_guarded.py --label a-r1 --policy R1
python3 /absolute/path/to/material/run_guarded.py --label b-r1 --policy R1
python3 /absolute/path/to/material/run_guarded.py --label b-r0 --policy R0
python3 /absolute/path/to/material/run_guarded.py --label c-r0 --policy R0
python3 /absolute/path/to/material/run_guarded.py --label c-r1 --policy R1
```

run_guarded.py需要可用的systemd用户服务与cgroup；没有时不要删除保护后冒充相同执行环境。每进程2GiB/256任务/90秒，软阈值RSS1536MiB/220线程，测试超时60秒，停止超时5秒。脚本拒绝覆盖已有同名日志。R0/R1不会同时运行。

## 统计公式与必要限制

`successCnt / Σsuccessful InvokeTime.executionTime`。标签TPS(callMethod only)有误，不能按callMethodTime子窗口重算或把数值称为提交TPS。平均耗时=`Σsuccessful executionTime/successCnt`。本次600次均成功；有失败时必须单列数量与错误，不丢失失败日志。

samples.csv从原始startTime/endTime纳秒重建，并与原始汇总总时长及打印TPS逐组核对。Gas分布包括每次返回值；本方法均105920。原始日志、每批CSV、race诊断、资源及完整命令都在包内。诊断200次与普通版600次分开。

原始close不等待worker退出，普通版记录有未完成清理；Go race没有覆盖native Store竞争。这里只复核短时性能参考，不据此认证Instance复用或生产安全；未运行ERC721。请协助确认历史实际WASM哈希、bigNumCal循环、入口/配置和原统计公式，以判断为什么历史bigNumCal仅1.4倍而本次连续调用约10倍。

## 包内容与敏感信息排除

白名单只含报告、补丁、非敏感源文件/摘录、参数/环境/模块清单、WASM、统计脚本、运行命令、原始测试日志和CSV。没有node/SDK配置、证书、密钥、账本、Shell历史或环境变量全量转储；没有发送给任何人。runtime_test.go中其他方法的PEM夹具未拷入本包。manifest.sha256可校验每个包内文件。
