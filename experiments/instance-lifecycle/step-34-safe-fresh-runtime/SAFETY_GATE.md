# 准入决定

**有界串行独立Store原型通过；真实节点E2E仍未准入，未启动节点或压测。**

|条件|本轮状态|
|---|---|
|独立Store，不是Rc clone|PASS：固定so外Store导入拒绝，实际跨Store同Module/Memory隔离|
|缓存Module/Engine/API契约|PASS于同owner同Engine；未认证跨线程wrapper共享|
|Fresh创建/执行/同步关闭|PASS：四组真实业务三轮|
|错误回滚、失效访问、重复关闭|PASS于列明的Go故障与真实业务错误；native OOM/析构失败not_tested|
|Finalizer/显式Close冲突|PASS于scope协议：不安装Go native finalizer，owner claim一次，GC与重复Close测试|
|Reset/Stop与在途job|PASS于SafeFreshOwner；不等于已修好原pool.reset/空StopVM|
|真实跨合约/Gas/状态|PASS于12 buyNow根/72子调用及其他三合约|
|有限资源|PASS于当前有界测试，非长期native Drop/线程join证明|
|节点实际NewRuntimeInstance/缓存/回调/Stop接线|NOT_IMPLEMENTED_AND_NOT_VALIDATED|

最小剩余阻塞是节点适配接线及其生命周期smoke，而非“本库不支持独立Store或缓存Module”。当前完整业务路径在测试适配器中；将其当成可替换节点实现会遗漏锁外Module准备、原manager reset/Stop与回调归属。不得直接替换Instance创建一行后启动E2E。

不把尚未证明安全写成已发生内存损坏；本轮没有观察到native资源损坏。没有因为GetRace通过就认证native安全。正式生产节点保持原样。
