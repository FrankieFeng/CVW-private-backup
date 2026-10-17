# 三合约 pilot：完整 VM Invoke（ms）

单线程 VM + mock TxSimContext，包含同步 fresh 创建、业务和关闭；不是节点延迟。40 次/有效组，单批探索性结果。P=1 缺可恢复源码。

| A | P | C | compute Median / P95 | ERC721 Median / P95 | fact Median / P95 |
|---|---|---|---|---|---|
| 0 | 0 | 0 | 31.600 / 35.227 | 6.212 / 7.808 | 5.951 / 7.316 |
| 0 | 0 | 1 | 31.073 / 35.245 | 4.919 / 7.833 | 4.784 / 6.280 |
| 0 | 1 | 0 | blocked（PB 源码缺失） | blocked（PB 源码缺失） | blocked（PB 源码缺失） |
| 0 | 1 | 1 | blocked（PB 源码缺失） | blocked（PB 源码缺失） | blocked（PB 源码缺失） |
| 1 | 0 | 0 | 30.280 / 34.132 | 4.674 / 6.849 | 4.163 / 5.288 |
| 1 | 0 | 1 | 28.282 / 32.964 | 3.816 / 6.514 | 3.133 / 3.816 |
| 1 | 1 | 0 | blocked（PB 源码缺失） | blocked（PB 源码缺失） | blocked（PB 源码缺失） |
| 1 | 1 | 1 | blocked（PB 源码缺失） | blocked（PB 源码缺失） | blocked（PB 源码缺失） |
