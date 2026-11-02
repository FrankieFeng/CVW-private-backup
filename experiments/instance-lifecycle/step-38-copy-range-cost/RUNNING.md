# 可恢复运行与复算

已完成实验，**不要为复算重启进程**。

```bash
python3 scripts/analyze.py
python3 scripts/supplement.py
python3 scripts/report.py
python3 scripts/validate.py
```

仅读取raw_logs并重建本目录CSV/报告；无节点、编译或新增样本。主要代码与窗口见COPY_RANGE_SOURCE/INSTRUMENTATION、audit/SOURCE_FUNCTIONS.csv。

实际构建：scripts/build.py A A2，scripts/build.py B。A第一次失败保留；A3-memory/B-clock是补充unit control。每个build command/outcome/source_hashes完整保存，native .so和测试二进制不入Git。

实际主运行：scripts/experiment.py，调用scripts/run.py；已有成功outcome会跳过，失败或孤立log必须人工审阅不能覆盖。所有业务init、预热与目标收据存在*-receipts目录。资源监视器只监视step38自己unit/pid，无Clash/VSCode配置修改，无全局kill。

使用现有Node依赖图的A.work/B.work避免下载缺失旧module；实际Go buildinfo归档。原node workspace只被读取，未改其go.mod。需要本机原冻结WASM与依赖路径、patched native库；不是零依赖分发包。

本轮没有真实节点AddTx/PutBlock、客户端确认或TPS；VM夹具BlockVersion1/gasUsed0边界必须随数据说明。
