# 非guest开发错误记录

1. 初次准备时packaged/lib/linux-amd64未创建导致so copy失败；尚未构建/执行guest，创建目录并从同hash源恢复。后续shell相对路径错误也只发生在准备阶段。
2. 首版run.py压缩表达式写成else125/else768，Python语法检查在任何systemd-run前拒绝执行；修正空格、静态compile通过后才启动preflight-compute。
3. formal suite门槛对init的protobuf省略零Gas字段直接取下标，离线KeyError；完整错误保留formal-driver-attempt1.log。改为默认0，仅从已有receipt复算，原进程不重跑、不覆盖。

这些不是guest失败或有效性能样本。全部guest进程日志/outcome保留，无native崩溃/资源STOP被隐瞒或删除。
