# Copy区间源码与实际执行

本实验根目录：`/home/frankie/mygitprojects/.worktrees/cvw-step38/experiments/instance-lifecycle/step-38-copy-range-cost`。source/A是Step38A，并非Arena A。A2、B是冻结的性能二进制；A3-memory与B-clock仅用于后补边界/时钟检查，不替换性能数据。

## 原路径

Step36 `source/vm/step35_static.go:85 prepareStaticMemory`从原WASM Memory/Data Sections生成initial-size零Image，按segment原顺序copy覆盖，:208排序、:209合并重叠/相邻，:220仅丢掉最终全零合并区间，:230 NoData保留其他Sections而去除active Data Section。:235 restore验证Module/配置、:241获取Memory、:245借用Data视图、:249区间循环。实际Step38文件因新增统计字段行号后移，精准索引见audit/SOURCE_FUNCTIONS.csv。

约5万个区间的原因是冻结Go链接器输出约4.6万～5.4万个active segments，原算法只合并重叠/直接相邻，不跨非零距离的零洞。8个真实plain WASM的payload、地址并集、C0 copy字节量相同，说明本批没有净重叠重复复制收益；约0.31～0.36MB零字节位于混合区间内仍会被写入。重叠/显式零覆盖另用native WAT测试，不将人工样本当作真实布局。

实际A2 ELF反汇编`audit/restore-A2.asm`（只读objdump，无新编译）包含循环内`CALL runtime.memmove`及slice边界失败分支`runtime.panicSliceAcap/panicSliceB`。不是每segment一次cgo：native baseline原本在一次wasm_instance_new内部遍历，见native-step35b/lib/vm/src/instance/mod.rs:1490与memory.rs:766/774。

## 新增策略

`source/A/vm/step38_support.go:e38Coalesce`只在缓存模板准备后运行一次；C0保留Ranges，C1/C2/C3按16/64/256B合并，C4覆盖[minBegin,maxEnd)。合并每个gap时逐字节确认Image为零。Image、NoData、原WASM、Gas和Guest全部不改。字段e38CopyBytes在冷准备一次求和，正式调用只读取统计值，没有在热路径额外遍历所有ranges计算bytes。

```go
if n > 0 && r.Begin-out[n-1].End <= gap {
    for _, b := range p.Image[out[n-1].End:r.Begin] {
        if b != 0 { return fmt.Errorf("nonzero uncovered gap") }
    }
    out[n-1].End = r.End
} else { out = append(out, r) }
```

`source/A/vm/step35_node.go:prepare`编译NoData并绑定plan.Module，然后e38Coalesce；每进程策略由启动环境固定，缓存Key未改，**不支持同进程动态切策略**。所有正式策略在独立进程，模块先init/两笔业务预热，目标调用命中缓存。若未来集成支持策略热切换，须做策略版本/缓存失效隔离，不能直接照搬实验环境约定。

Fresh路径仍为NewRuntimeInstance → runtime私有WASM副本 → Invoke验证/Owner.Do → prepare命中 → 新Store(缓存Engine) → WASI builder/Finalize → WASI/CM imports → NewInstanceInStore → restore → WASI Initialize → _start → SetGas/CallMethod → 同步Close。没有旧GetInstance/grow、异步关闭或已执行业务Instance复用。

Memory.Data借用native内存，不分配等长目标；模板Image只读共享于缓存，目标Memory/Store/Instance私有。原Section11初始化被NoData替换，并非原Data全部初始化后再次copy相同数据。native新Memory的零初始化仍存在；显式复制零字节可能重复写已零内存，但没有据此判定某个缓存/页fault机制。
