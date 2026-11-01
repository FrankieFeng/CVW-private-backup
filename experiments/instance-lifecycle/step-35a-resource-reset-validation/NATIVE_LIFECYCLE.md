# Native生命周期：计数、实际析构与剩留任务

固定实际库SHA为dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9（Step35相同，版本6.0.1），未重编/升级。节点加载maps、纯C RUNPATH/ldd及systemd loader环境在audit/raw_logs；不存在LD_PRELOAD替换。

- Go Store.Close -> wasm_store_delete。实际ELF @0x2ce610取Rc块并dec strong；仅减至0才调用StoreInner drop。CAPI调用计数本来不能单独证明Drop。
- 本轮只读探针固定上述ELF布局，在Owner线程、有效Store删除前读取strong，不写native内存、不改变ABI。resource2的24个runtime Store加4个compile Store全部strong=1，shared=0；调用返回且反汇编分支支持最后引用析构已执行。该私有布局不是生产接口，换库必须撤销/重新审查，不能拿它作为独立Store隔离证明。
- Instance.Close先清export/import vector，再wasm_instance_delete；Memory借用跟随Instance/Store。源码候选StoreObjects持有memory/table/function arena，Mmap::drop对系统映射munmap。精确整个native构建来源仍未锁定，不把候选源码每一行当实际二进制。
- WASI env delete调用on_exit并删除环境引用。新增计数显示空闲快照WASI与Imports容器全部配平，host函数登记归零；ImportObject计数是Go容器生命周期，不能称为每个native extern的物理释放计数。
- Module/Engine/compile Store在缓存有效期长期保留；实际Manager Reset关闭它们，native in-use显著下降，属于预期缓存。
- glibc arena free增多但RSS未同步释放，属于已free仍保留的资源；Go heap idle/released证据另见RSS_ANALYSIS.md。

关键反证：即使Store进入最后strong析构分支，pure-C的WASI环境与Engine也关闭，仍遗留epoll线程。因此Store析构、Instance配平和WASI API delete不等于所有native后台任务退出。问题已收敛至WASI/native网络运行时关闭路径。

候选实现LocalNetworking.Drop调用Selector.shutdown；实际二进制也有对应析构和shutdown符号，后者仅wake。旧双waker与当前单waker修复的关系有静态证据，尚未通过原生补丁验证。不得直接编译本地当前全量源码替换so以宣称通过，因为这会引入不可审计的其他差异。

本轮Go源码只做Stop/Reset同步修正、Unix诊断入口和只读计数/观测；不改Guest、Gas、A/Copy或native ABI。未来最小native实验需恢复构建来源，仅修复Selector/WASI关闭，先重复本轮C对照，再验证节点Reset，最后才考虑E2E。
