# Go WASM Runtime路径与内存层次

Guest为Go1.24.1/wasip1/wasm，源码`/usr/local/go-version/go1.24.1/src/runtime`；host节点和SDK二进制Go1.25.0。不得把host Go heap/GC当guest heap/GC。

## _start至业务前

- `rt0_wasip1_wasm.s:8 _rt0_wasm_wasip1`设置wasm栈，`:12`进入rt0_go。
- `asm_wasm.s:10 rt0_go`，`:22 schedinit`，后续启动runtime main。
- `proc.go:798 schedinit`进行Runtime初始化，包括mallocinit、随机种子、mcommoninit等；`malloc.go:373 mallocinit`、`:461 mheap_.init`。
- runtime main执行module/package init（`proc.go`中doInit(m.inittasks)）；业务导出在后续CallMethod。A没有裁剪PB/package init，本轮没有B1。

这里只追踪源码执行结构，不把所有Runtime步骤归入同一个可单独测量的“A段”。Step36只有_start窗口，无法从中独立分出Runtime A与package B1。

## 真实分配链

`mheap.go:1478 grow`按palloc块请求；`:1497`h.sysAlloc → `malloc.go:718`及`:833 sysReserveAligned` → wasm的`mem_sbrk.go:220 sysReserveAlignedSbrk`。新保留首先尝试free list，后按arena对齐bloc→sbrk；跳过gap可经memFree清零（:83）。`mem_wasm.go:9 sbrk`将逻辑break按页增长；越过blocMax才调用`:26 growMemory`（native wasm memory.grow），随后刷新视图。

`os_wasm.go:16`记录初始linear size；`mem_sbrk.go:155 initBloc`与firstmoduledata.end相关。`sysFreeOS:167`在尾部减bloc并清零或进入free list，**不会将WASM Memory物理size缩小回原页数**。`memclr_wasm.s:9 memclrNoHeapPointers`是guest零填充实现，和native新建零Memory是不同层次。

## 四种内存不能混为一谈

| 对象 | 所有者/边界 | 本轮可见量 |
|---|---|---|
| Go host heap | 节点Go runtime | nodeEvent.ReadMemStats的HeapAlloc/GC，非guest |
| guest Go heap | 每个独立WASM Memory内 | 无独立GC计数/heap边界动态探针 |
| WASM linear memory | native Store/Instance私有 | 初始pages静态声明，后续memory.grow未逐次计数 |
| 模板Image | host Go plan，Module缓存生命周期 | initial pages×64KiB，可由冻结WASM静态精确重建 |

Copy优化的是_start前Data初始化，不会省去Go堆创建和业务对象分配；A改变Go链接布局，针对部分arena对齐路径，不省去所有清零。两者不是对同一热点的重复修复，也不能默认加性：改变初始页数可能改变native准备/页触碰，模板和cache容量也变。现有数据没有单独测量guestGC、页fault、memory.grow次数或memclr累计字节，不能据此认定“缓存预热”是收益/退化根因。

## 当前native分配边界

实际native`/home/frankie/mygitprojects/.worktrees/native-step35b/lib/vm/src/memory.rs:34 WasmMmap`记录memory definition；grow路径可能扩可访问映射或重新分配并copy（:103）。这些条件分支的源码存在不代表每个Step36交易都走了重分配。Store::new单独计时缺失；不能由Close或RSS倒算创建成本。没有同一计时/相同Guest的共享Store反事实对照，因此不能测出“Store独立化额外成本”的净值。
