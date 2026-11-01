# RSS与Go Heap归因

## 历史复算

HISTORICAL_WAVES.csv复用了Step35原始六轮24笔交易；未把它们计为本轮新独立样本。每轮结束Go heap为705.399、780.591、855.771、930.934、521.580、597.088MiB。第5轮发生GC，NumGC从8至9，HeapSys仍约994.6MiB、HeapReleased仅约6MiB；live heap下降不要求RSS同步下降。

原资源轮询只有`monotonic_s`，VM日志为`wall_ns`，没有保存可审计的历史转换偏移。逐轮RSS/线程、goroutine、WASI计数和静默快照缺失；不能用后来时钟校准伪造精确轮末数据。整体RSS峰值1481.109MiB仍有效。新同步快照补齐本轮测量，不能冒充原六轮记录。

## 新有界诊断（resource2，四个缓存合约，非Step35五合约全集）

| 阶段 | RSS MiB | Go heap MiB | HeapReleased MiB | glibc in-use MiB | glibc free MiB |
|---|---:|---:|---:|---:|---:|
| 3轮compute/buyNow后静默 |1214.35|750.75|5.56|238.68|352.32|
| 实际Manager Reset后 |1052.85|750.92|5.34|22.74|380.30|
| 单独诊断GC后 |1053.12|477.74|5.00|22.74|380.30|
| 单独诊断Go scavenge后 |781.41|477.61|276.86|22.74|380.30|

直接支持：

1. Reset清除4个Module缓存后native glibc in-use减少约216MiB，属于正常长期缓存释放；缓存不是业务Instance复用。
2. GC回收约273MiB live Go对象，但还在Go heap保留页中；scavenging后RSS下降约272MiB，HeapReleased相应增加。这部分并非不可释放的native线性内存。
3. glibc仍报告约380MiB空闲arena，表明部分已free内存没有立即归还OS；mallinfo2不是Rust/Wasmer专用计量，不覆盖全部mmap，也不能把全部free arena视为全部resident。
4. 进程RSS包含Go页、native allocator、代码/文件映射和线程等，不能仅凭RSS斜率给出统一“内存泄漏”结论。

resource1独立诊断观察到同方向：Go heap739→478MiB，RSS1016MiB基本不随单次GC下降，scavenge后749MiB。没有改GOGC=100、GOMAXPROCS=2，没有malloc_trim，没有把强制回收插入业务请求之间。

边界：自然观察窗只有有限3轮和约1秒静默；RSS未证明长驻平台。本轮峰值最高1214.668MiB，低于1536MiB，但不能用forced scavenge后的低RSS宣称正常服务准入。已直接发现native线程持续残留，对应栈/selector资源也可能贡献内存，尚未完整量化。
