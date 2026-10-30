# 构建来源

分支 experiment/step33-full-contract-coverage，父7eccc36e。源码家族冻结 Step18 95903a3，P=0，B1禁用。compute/fact/erc721/identity/exchange 四组直接拷贝并核验 Step32 冻结 WASM；bigInput/itinerary/raffle 从95903a3提取原源码/go.mod/go.sum构建。所有哈希和布局在 audit/guest-lineage.json、inputs/variants.json；原命令、日志和padding源在 audit/。

A沿用历史reachable static padding，分别按每个合约、plain/probe基线bloc重新计算 4MiB-bloc-5×64KiB，目标bloc=3866624。不是只增加initial memory，未移动数据或漏改引用。probe只作功能对齐验证，正式只用plain。新增三合约动态probe实测first arena reserve4MiB、skip0、alignment4MiB，日志alignment-*；没有用probe性能代替plain性能。

Copy仍用现有prepareStaticMemory构造最终覆盖模板与noData模块，实例化noData后restore，之后WASI Initialize/_start，未先做原Data再复制。模板与最终WASM匹配；逐组准备缓存、显式owner生命周期，禁止跨二进制复用模板。

host Go1.25.0，guest Go1.24.1，原Wasmer native SHA256 dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9。构建脚本和environment.json固定实际命令/哈希；未升级生产依赖。


本轮源码快照 131915d666a4a233a0ff3307d8b055ed88871244；build3 binary SHA 8434fd73113eba39e326528b5726d9931a6afaad4f69396947846741ab78218f。快照提交发生于正式采样期间，提交前后的所有正式样本均执行同一build3二进制，Go源码哈希逐文件与environment.json一致，不能误称执行时HEAD始终等于该快照。最终结果提交另记。


核心依赖模块沿用Step32的Step21C工作树32d257b62cbaedbefd6112ddf1badb4aee2b413f，目录/状态/关键文件哈希与host二进制buildinfo在audit/。新增Guest SDK v0.1.3（go.mod/go.sum），模块缓存Go源码指纹在SDK_CACHE_HASHES.json，GetBatchState仍存在；没有B1/PB公共API删除。Go工具不能直接读取这些WASM的buildinfo，失败尝试已存GUEST_GO_BUILDINFO_ATTEMPT.json，未把该缺口伪称成功。
