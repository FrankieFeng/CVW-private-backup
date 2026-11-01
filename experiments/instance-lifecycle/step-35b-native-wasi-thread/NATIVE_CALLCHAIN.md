# native 调用链与所有权

以下路径相对 `.worktrees/native-step35b`，基线 `0910740`，补丁仅 selector.rs:34。

| 层次 | 实际函数 / 源码 | 所有权与结束行为 |
|---|---|---|
| C配置 | `lib/c-api/src/wasm_c_api/wasi/mod.rs:48` wasi_config_new | 创建Tokio多线程Runtime，配置暂持有 |
| C环境 | 同文件`:332` wasi_env_new，`:337` StoreRef，`:350` PluggableRuntime::new | 取走配置Runtime；TokioTaskManager持有；WasiFunctionEnv保存在Store对象中，wrapper持StoreRef |
| Runtime | `lib/wasix/src/runtime/mod.rs:276` PluggableRuntime::new，`:280` LocalNetworking::default | host-vnet编译配置每个新Runtime创建LocalNetworking |
| 网络 | `lib/virtual-net/src/host.rs:39` LocalNetworking::new | 持有Arc<Selector>，`:42` Selector::new |
| Selector | `lib/virtual-io/src/selector.rs:26` new，`:45` thread::spawn | poll/registry；线程闭包也持有Arc；后台循环在`:130` run |
| 环境删除 | C API wasi/mod.rs`:376` wasi_env_delete | 调用WasiFunctionEnv::on_exit；释放wrapper的StoreRef；不等于提前销毁所有Store对象 |
| 最后Store/Runtime释放 | `LocalNetworking::drop` host.rs`:57`→Selector::shutdown selector.rs`:53` | 最后网络所有者析构时wake；本例实际触发于wasm_store_delete，实测栈已保存 |
| 线程退出 | selector.rs`:153` token == token_close | return后poll及线程Arc正常drop。原错误token0不能命中token1 |

Go安全节点路径保持：`source/vm/step35_node.go:227` ManagedOpen(fresh) → `:245` NewStore(缓存Engine) → `:246` WASI Finalize → `:250` GenerateImportObject → 同Store实例化 → `:275` Initialize → `:278` _start → CallMethod → scope.Close同步逆序析构。Module缓存没有逐Instance重复编译。

原库线程归属证据见 `audit/thread-identities.json`，其中保存每个Selector TID、名称、等待点和EXIT。Tokio配置线程在C创建phase11，Selector在phase12；C源码phase13/14分别为环境/Store删除。节点剩余11个线程不能全部称为Selector：还包含Go调度/网络等线程。节点TID/comm/wchan原样存于每次snapshot的thread_details，未对每个节点线程符号化，不能宣称其身份全部已确证。

现有关闭接口已经有Selector::shutdown；C API未发现另一个可替代上述正常drop路径的显式Selector join/Runtime统一shutdown函数。本轮没有手工close epoll fd、取消线程或改变资源所有权。
