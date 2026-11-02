# 夹具状态

8个独立部署业务合约、37个业务方法均PASSED；状态和每组实测N在METHOD_COVERAGE.csv。identity.callerAddress已通过真实独立节点、自合约下游执行，不沿用Step33旧blocked。exchange保留六次真实子调用。大输入按冻结配置执行512KiB/1MiB，ioHeavy原100×256，不缩减输入。

扫描2590个Go/WASM文件、40个export源码、617份WASM（含历史/重复）。清单121行包含重复源码、辅助模块和非业务exports，不等于121个独立合约。八个业务家族的生命周期/Gas/库预热/人为延迟探针登记为未纳入业务性能；不是PASSED。构建来源95903a3及Step33冻结A产物；完整路径、哈希见清单与inputs/variants.json。

首轮raffle夹具失败及revision原因见CORRECTNESS.md；所有其他方法无需改写Guest。
