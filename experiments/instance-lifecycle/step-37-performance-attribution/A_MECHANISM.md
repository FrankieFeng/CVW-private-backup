# A优化的真实实现

## 实际更改（A）

不是更换Go allocator，也不是单独将initial memory调成128页。

`/home/frankie/mygitprojects/CVW/experiments/instance-lifecycle/step-18-combined-cold-start/pipeline.py:72 build`及`:87/88`生成`layout_pad_step18.go`；`/home/frankie/mygitprojects/.worktrees/cvw-step33/experiments/instance-lifecycle/step-33-full-contract-coverage/scripts/prepare_guest.py:24`起补齐bigInput/itinerary/raffle同源构建。核心：

```go
var experimentHeapLayoutPad = [amount]byte{amount-1:1}
var experimentHeapLayoutPadPtr = unsafe.Pointer(&experimentHeapLayoutPad)
func init() { if experimentHeapLayoutPadPtr == nil { panic(...) } }
```

`amount = 4MiB - baseline_init_bloc - 5*65536`，按**每个合约/构建**重新算；重新Go链接修正地址引用。没有手工移动Data再遗漏指针修正。哨兵/引用保证变量保留；因此新增一个很小init行为，不是完全无代码差异。

目标init_bloc=3,866,624（59页），再经历历史已测的5页bootstrap元数据，首次相关heap reservation的bloc接近4MiB arena边界。当前冻结WASM解析的plain/A moduledata及init_bloc与该布局一致。历史probe与Step36不是同一个二进制，不把probe计时混入Step36，也不能仅凭静态init_bloc断言本轮每次运行恰好相同分配序列。

## 作用路径（A/C）

Go1.24.1 `mem_sbrk.go:155 initBloc`从firstmoduledata.end页对齐设置bloc；`malloc.go:252`wasm heapArena为4MiB；`malloc.go:833 sysReserveAligned`转`:838 sysReserveAlignedSbrk`；`mem_sbrk.go:220`对齐bloc，`:241 sbrk`保留范围；若有前缀gap，`:244 memFree`，而`:81/83`memFree清零回收段。A针对这个布局gap及其清零路径，未删除Go Runtime步骤。源码支持“避免/减少某些对齐gap”这一机制；本轮未记录sysReserveAligned每次参数或memclr指令数，精确调用次数/节省字节仍C。

`new(g)`在proc.go:4999为Go goroutine对象分配；A没有patch该函数、mheap.grow、sysReserveAligned或memclr，也未缓存g。历史热点可与上述分配链相连，但不能把函数热点直接叫本轮已定位根因。

## 没有提前执行_start（A）

没有把Go Runtime/package init快照提前到模板，也没有保存业务Instance。所有组都执行NewStore、WASI、_start、SetGas/CallMethod和Close。Copy-only/A+Copy同一host代码路径，差别是最终WASM SHA/布局；两种模板分别生成。A-only没有restore。

## 代价和组合（A/B/C）

冻结8合同plain初始46～52页，A统一74页（4,849,664B）。WASM文件只增加645～787B，Copy字节量只增加约174～445B，不能用“大幅增加WASM文件/Copy字节”解释A组合负收益。模板容量却增加22～28页，约1.375～1.75MiB/缓存项；这是确定的容量代价，不等于同等RSS增长。

A仍保留Go_init、package init、arena实际使用与Memory.grow，可能将运行期gap成本转为较大的初始可访问内存/映射。物理页是否触碰、native分配是否清零、后续缓存局部性变化，没有本轮独立证据。

Step37直接配对复核：A叠加Copy的_start局部改善在37方法中均有探索性CI全正；完整Invoke和E2E并不普遍相同。不能因组合_start更快就认定完整链路一定更快，亦不能把A和Copy两项配对Median相加。

Gas边界补充（A）：step35_node.go:303在_start之后、CallMethod之前设置业务可用Gas，末尾读取Gas用于ContractResult。四组业务Gas一致已经实际验证，但这不能证明_start执行了相同数量的指令；也不能把A减少的初始化指令直接当作业务Gas节省。native/Guest计量规则本轮未改变。
