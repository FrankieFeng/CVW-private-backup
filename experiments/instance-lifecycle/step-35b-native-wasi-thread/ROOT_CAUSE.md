# 根因：关闭唤醒被识别为孤立事件

## 已直接观测

1. 原始库 `dcdfa716…` 的 pthread 创建栈落在 `virtual_mio::selector::Selector::new`，而非凭 epoll 等待名称猜测身份。单次环境的创建ID17/TID192059，发生在 `wasi_env_new` 阶段；Tokio worker 均退出，Selector 未退出。
2. 四环境的 Selector ID17/34/51/68 分别对应 TID193267/193284/193301/193318，删除 Store/Engine、静默3秒后仍存在。每个环境新增一个，属于逐环境累积，不是固定数量的全局常驻线程。
3. `original-fd-wake`：TID195008 在 epoll_wait(fd10)；epoll注册的 eventfd12 数据为 **0**。Store删除阶段，`Selector::shutdown` 经 `LocalNetworking` 析构实际向 eventfd12 写入唤醒。原始 `wasi_env_delete` 调用已存在；不是 Go 漏调 delete，也不是 shutdown 完全没有执行。
4. 恢复的6.0.1源码 `lib/virtual-io/src/selector.rs:34` 注册 `Token(0)`，`:35` 保存 `token_close=Token(1)`；`:153` 只有 token相等才return，其他未登记token走 orphaned event。通知已发生，但不能走退出分支。
5. 同一 Rust1.81/Cargo.lock/features 的未修复重建库重现同样4个残留；仅改注册值为Token1后，4个创建点相同的线程均有EXIT记录，静默期只余主线程。此单行对照支持因果定位。

原始库符号偏移：Selector::new `0xabec00`，创建栈帧 `+533`；shutdown `0xabf070`，实际wake栈帧 `+11`；run `0xabfb90`。原始反汇编存于 `audit/original-selector-*.asm`，创建/写入栈与符号映射见原始 pthread 日志、`audit/*-frames.json`。

## 为什么 WASI delete 后没有退出

WASI函数环境还持有Store侧对象；`wasi_env_delete` 执行on_exit并丢弃wrapper，不保证立即销毁全部Store对象。本例真正的 LocalNetworking析构发生在后续 `wasm_store_delete`。它已调用shutdown；错误Token让 Selector继续poll。线程闭包持有Selector的Arc，线程不退出，poll/registry及这份Arc也不能释放。Tokio任务管理器和Selector是不同的生命周期，不能把所有残留笼统叫Tokio线程。

## 证据边界

原始so的完整历史构建清单/精确源码提交未恢复。6.0.1 fork的相关组件源码、原始ELF符号/事件及对照行为互相支持；不声称重建库与原始so逐字节一致。补丁并未添加join或带超时的native关闭API：仍使用已有异步wake/线程return协议。已测有界等待内线程退出；不能将观察上界写成任意调度条件下的硬实时保证。

共享LocalNetworking由Arc持有，补丁保持最后所有者Drop才shutdown的时机；未引入每个wrapper额外强制shutdown。共享网络Runtime/socket长寿命复杂场景本轮未动态覆盖，不能标为通过。
