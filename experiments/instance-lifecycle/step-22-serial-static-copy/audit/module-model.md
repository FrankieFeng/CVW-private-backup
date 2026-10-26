# Step22登记的串行缓存模型

父Step21D 87eb925。每A0/A1/合约分别一个固定owner Store+Module，不跨Store传Module，不跨线程调用。Module的Imports/Exports懒缓存须在持久scope预先 materialize，禁止被首个Instance的临时scope回收。每个Instance、WASI、imports与memory view在独立短scope，同步关闭后下一实例；WASI不复用。

这选择了D设计表方案A的有界串行参考（非默认后台池）。Step22明确登记这一新模型，不能称原池性能。管理器缓存Module而不缓存业务Instance。一次性准备/缓存清理分开计时；每Invoke包含完整Instance创建、Copy、WASI/start、业务与关闭。

先小标量模块重复创建/销毁scope、owner拒绝及内存隔离；再bigNum/fact 1对预检（S1 hash/结果/Gas/写集/事件）；通过后每独立进程最多3对×3批（保留首样本、交错随机顺序）。资源阈值不变。样本小，P95与CI必须注明有限精度。ERC721/真实exchange只在前两者通过后评估，资源不允许则not_tested。
