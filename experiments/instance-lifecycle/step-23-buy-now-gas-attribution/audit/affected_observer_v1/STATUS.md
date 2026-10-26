# Rejected observer v1

2026-10-27复核发现GetTxRWMapByContractName调用mergeTx*Set(dst,src)会向内部map写入，不是纯读取。此26进程全部原日志/receipt/命令/outcome按原标签保留；本目录保存原源码、分析及当时报告，均为受影响诊断，不能作为最终readonly探针证据。

SDK/Gas/WASM未被改动，原Gas结果仍恰与历史相符，但不足以排除观察副作用。后续v2必须不用此API，真实状态操作透明转发记录，并重做on/off及正式对照。原始数据不删除、不混入v2有效样本。
