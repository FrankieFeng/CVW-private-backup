# Step-21环境和构建

日期：2026-10-24，Asia/Shanghai。生产主分支未修改；旧Step-19/19A/20结果未覆盖。

- 源码基线：`474da33eebc85fd8c1d9fe77232611aebf573fef`。
- 实际构建源码：`077a8cbd52aca2a1a4fc39f2d3f8c5e574730a2e`；分支`experiment/step21-instance-reuse-loss`。
- worktree：`/home/frankie/mygitprojects/.worktrees/cvw-step21`。
- 差异：source.patch。原runtime.go/InvokeTime计时边界未改；vm_pool.go增加等待观测和窗口外维护追踪；原TestInvoke增加冻结参数、结果输出及计时后排空。两模式同一binary，无额外Store全局锁。
- Go：go1.25.0 linux/amd64，GOROOT=/usr/local/go，GOTOOLCHAIN=local，CGO开启；合约未重编，合约构建来源不以宿主Go版本代替。
- WSL/kernel：Linux 6.18.33.2-microsoft-standard-WSL2 x86_64 GNU/Linux；完整WSL/Windows应用版本见wsl-version.txt。
- CPU：Intel(R) Core(TM) Ultra 9 285H。
- WSL MemTotal：32573072 kB；SwapTotal：8388608 kB。
- native libwasmer SHA256：`dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9`，沿用packaged Wasmer6.0.1。
- 普通binary SHA256：`03b8ee6a35e4891133c8168c698ccc2c4180b3b77f1c7d669e6a421ccd4926da`。
- race binary SHA256：`8bcf4f4a7f39f701748fce44ceb00f8b76783b9ea2ca87441cb78edbfc906fa4`。

## WASM固定产物

使用基线已提交的TestInvoke/testdata文件，没有为了历史倍率更换成toolkit候选，也没有变换内存、PB或计算循环。

| 合约 | Bytes | SHA256 |
|---|---:|---|
| compute | 4628317 | `e8b1fe3648b9f731f90352aff1796195f9f1efd1c4043bafec966fac53952507` |
| erc721 | 5176627 | `9b6eb47d4ca79f975a9214cc0459d47637ae7d4f1bdc45aa4fd91a0e24c1be1d` |
| fact | 4871418 | `02d64cbced7c34b02b0d90ba78668458bdfc97d0db6068750d81077357b28dcd` |
| exchange | 4283547 | `9387cb4e1ff393652862d25911e721095141924651c890a4de6236327369b74a` |

compute.bigNumCal/hashCal沿用100轮产物，normalCal沿用1000万循环，与此前恢复toolkit候选前两者10000轮不同。历史PPT精确WASM未确认，所以只比较参考数值，不宣称工作量已对齐。当前ERC721 SHA9b6e也不同于Step-19节点用过的4fbad和候选a692，未将它们视作同一二进制。

## 固定运行条件

R0/R1唯一生命周期开关为CM_REUSE_EXPERIMENT=R0/R1；共同CM_STEP21_OBSERVE=1、GOMAXPROCS=4、GOGC=100、同一LD_LIBRARY_PATH。SnapshotMock、无节点/账本/RPC、空业务池min5/max10/grow5，默认refresh为12小时，无人为Sleep、无预热删除、无CPU绑核或OS cache清空。已有WASI environment freelist为共同基线，未在本轮新增；不能假定它与历史WASI实现相同。

每组独立systemd用户单元，2GiB硬内存/256任务/60秒，RSS1536MiB和线程220软阈值；Go测试45秒；退出排空5秒。监测包含启动、JIT、业务及退出，RSS/线程为离散采样，不把cgroup MemoryPeak当成进程RSS。

## 构建命令

未更新依赖，使用现有workspace与模块缓存，完整模块图见modules.jsonl，实际buildinfo见两个buildinfo文本。

```bash
cd /home/frankie/mygitprojects/.worktrees/cvw-step21/chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0
export GOROOT=/usr/local/go GOTOOLCHAIN=local GOPROXY=off
export GOWORK=/home/frankie/mygitprojects/.worktrees/cvw-step21/go.work
/usr/local/go/bin/go test -c -o /ABS/OUTPUT/step21.test
/usr/local/go/bin/go test -race -c -o /ABS/OUTPUT/step21-race.test
```

实际完整启动命令和环境在raw_logs/*-command.json。参数文件100行、SHA见cases.json；fact时间在experiment起点冻结，ERC721 tokenId=1…100。原入口的默认参数会先生成但被文件逐次覆盖，实际输入以冻结文件和STEP21 sample哈希为准。没有采集敏感环境变量、密钥或证书；完整runtime_test.go包含其他测试PEM夹具，不另行复制，只提供最小diff。

## 停止与来源解释

本轮退出检查暴露满队列阻塞，正式矩阵未完成；不用-race样本的耗时补正式数据。ExecMainStatus在失败unit被collect后可能显示默认0，以Go日志FAIL和worker退出事件为准。所有自启进程均停止；原始日志、失败、未运行组全部保留。
