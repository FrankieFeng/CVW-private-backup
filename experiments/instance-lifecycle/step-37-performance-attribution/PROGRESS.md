# Step-37 可恢复进度

仅只读Step-36及历史源码；新增分析文件，不运行节点/编译/基准。

1. 已创建独立工作树`.worktrees/cvw-step37`，分支experiment/step37-performance-attribution，父abc2ce35。
2. 主CVW存在用户未提交变更，未切换、覆盖或修改。
3. 当前阶段：Step36原始数据完整性、独立配对复算、多重校正设计；随后源码、案例和候选方案。
4. 统计计划：同block/槽位直接差；3批聚类bootstrap复核原CI；以批均值的8种符号翻转作保守双侧检验，Holm对37×(5对照+交互)=222项整体校正。只有3批，最小双侧p=0.25，校正不显著不代表无效。
5. 交互符号：同时输出cost interaction与saving synergy，避免将正成本交互误称协同。
6. 下一步读取冻结Copy/A/Go/native源码，独立生成CSV。无待执行性能测试。

## 完成：审计、复算、机制分析与验证

- Step36 CVW abc2ce35、节点c28bfa8固定；8779项SHA通过；一个ignored packaged so从原Step36目录只读校验，缺失/来源明确记录。
- scripts/analyze.py：925项配对CI/中位数/正向比例复现差0；新增37交互，主Holm家族222项，全部未达显著；三批检验功效限制已说明。
- scripts/layout.py：16冻结plain/A布局、NoData/Image/range派生hash、静态区间粗化计数；没有编译或输出新WASM。
- scripts/verify_records.py：1728提交receipt与111四组block业务/Gas/状态规范化复核通过；Copy fallback0。
- scripts/report.py：37方法全表、9典型案例、分阶段not_measured边界、README必答10问。
- scripts/supplement.py：逐批各组Mean/P50/P95、TPS窗口CI与buyNow七实例不重叠初始化统计。
- scripts/validate.py：111block实际组次序与记录一致，CSV行数/交互符号/必交文件核查；py_compile全部通过。
- 源码路径/hash共31项，Guest源码从95903a3只读提取供审计；无生产代码、WASM、native改动。
- 已完成SOURCE_TRACE、COPY/A/Go机制、E2E归因、9候选方向、Renew调研及下一轮建议。
- 剩余仅提交独立分析分支和镜像新目录供IDE阅读，不推送。
- 下一条可执行命令（仅复算）：python3 scripts/analyze.py && python3 scripts/layout.py && python3 scripts/verify_records.py && python3 scripts/report.py && python3 scripts/supplement.py && python3 scripts/validate.py
- 没有待执行性能实验；本轮结束，不自动启动Step38/39。
