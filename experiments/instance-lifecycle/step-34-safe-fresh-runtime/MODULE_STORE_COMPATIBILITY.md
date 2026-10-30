# Module / Store兼容性

实际加载6.0.1库SHA256 `dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9`，未替换native。C预检 `source/compat.c`/`compat.wat`、日志raw_logs/native-compat.log、完整命令audit/compat-command.json。dladdr记录实际.so；Go Race进程/proc/maps另确认同一文件。

1. wasm_store_new创建三个Store。缓存Module仅在S0编译一次，S1/S2使用同Engine、同Module实例化成功。
2. S0 Memory当作S1 import时，wasm_instance_new拒绝；换成S1/S2各自Memory后都成功。不是只依据Go指针不同认定独立Store。
3. 两个实例同时存在，Memory1写123，Memory2仍0；实例1真实函数返回123。
4. 3个Store/2个Instance的C API创建和删除平衡；这是handle操作计数，不是Rust Rc最终Drop探针。

实际ABI不导出wasm_store_clone，也没有module_share/module_obtain；不能使用陈航的新接口来替代本库。内部StoreRef.clone在6.0.1候选源码是Rc共享，不等于wasm_store_new。module_serialize/deserialize导出存在，但本轮未调用，无需在每次Invoke反序列化或重复编译。

候选旧native源码wasmer提交3189527eec99cfea7e6991328509e72ed0bec2e0：store.rs调用Store::new(engine.inner.clone())；Module只包编译代码，instance.rs实际使用传入Store并保存该StoreRef。不是6.1分支。未证明候选源码是该.so逐字构建来源；以固定二进制的兼容性运行证据补足API问题，不宣称重建认证。wasm_extern_vec_destroy是现有库扩展，逐函数反汇编归档，未修改ABI。

Go显式入口 `source/vm/wasmer-go/instance.go:33`；原NewInstance仍可委托module.store，独立路径显式传targetStore。WASI Finalize/GenerateImportObject/host imports/Initialize也全用同一targetStore。Module的编译Store保留到cache释放，Module元数据先在cache scope预热；native Module跨Store可用不意味着Go wrapper可跨线程共享。
