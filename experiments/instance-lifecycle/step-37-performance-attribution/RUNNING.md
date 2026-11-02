# 复算说明

工作目录为本Step37目录，Python3标准库即可，无需安装依赖。

```bash
python3 scripts/analyze.py
python3 scripts/layout.py
python3 scripts/verify_records.py
python3 scripts/report.py
python3 scripts/supplement.py
python3 scripts/validate.py
```

输入：相邻Step36目录的SHA256SUMS、inputs、raw_logs及原派生CSV。所有历史输入只读。manifest内一个Git忽略packaged so需要仍保存在原Step36工作树；脚本显示fallback并核验其SHA，不复制或加载so。

输出：本目录CSV、audit复算结果和动态报告（README、ALL_METHODS、CASE_STUDIES、E2E_ATTRIBUTION）。静态源码报告不依赖执行native；路径与hash见audit/SOURCE_INDEX.csv。复算只会覆盖本轮可重建派生文件，不写Step36。

原脚本只作为统计方法审阅，没有调用会修改原目录的Step36 analyze.py/report.py。无Go build、wasm构建、go test、节点启动或新benchmark命令。

置信区间与p值解释见STATISTICAL_METHODS.md；不用3批数据宣称确认性普遍收益。SHA256SUMS为交付快照，复算后若有文件内容变化，应重新生成本轮清单，不能把派生文件变化说成原始实验数据变化。
