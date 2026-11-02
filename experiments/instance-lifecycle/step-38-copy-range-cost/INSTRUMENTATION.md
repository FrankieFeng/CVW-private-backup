# 插桩、窗口与扰动

## 两个独立版本

- A2：只增加冷prepare策略选择、缓存copy bytes及事件元数据；未加入B成本分窗。F0/C0/C1/C2/C3/C4都在这个二进制比较。
- B：原始C0，不合并区间；在独立源码目录加e38Begin/e38End。没有优化SHA、clone、Store、WASI或缓存key。
- A3-memory：只增正确性负对照；B-clock：只增空观察窗测试。原A2/B原件、SHA、构建时source hashes都保存，性能采样后补充测试不覆盖二进制。

## 明确的窗口

| 窗口 | 起止/关系 |
|---|---|
| runtime_bytecode_clone | runtime方法append整份WASM之前/之后；排除返回runtime结构体其他开销；在Factory Invoke外、RunContract内 |
| invoke_two_SHA | 原Invoke身份比较表达式前后；正常调用两个SHA，含比较成本，不是纯单SHA |
| prepare_SHA | 构建原缓存key之前/之后；一个整WASM SHA加字符串拼接/配置处理 |
| module_cache_map_lookup | map取rec前后，排除module_hit日志 |
| module_prepare_inclusive | prepare函数调用前后；含prepare_SHA、map查找与既有日志，不能相加 |
| new_store | NewStore(rec.store.Engine)前后；包含Go包装/native Store创建，不含Module编译 |
| wasi_builder | NewWasiStateBuilder前后，native wasi_config_new创建Tokio Runtime等 |
| wasi_finalize | builder.Finalize前后，绑定目标Store |
| wasi_generate_imports | GenerateImportObject前后 |
| cm_get_imports | VM Bridge GetImports前后 |
| newinstance_inclusive | NewInstanceInStore前后；含imports.intoInner/native创建/Exports包装，未单拆纯wasm_instance_new |
| restore_memory_export / data_view / range_loop | GetMemory、Data()和区间loop前后，嵌套于原copy_ns |
| wasi_initialize | WASI Initialize前后；不等同Finalize |
| _start / CallMethod / Close | 原step35_node.go计时保留；native_scope_close为Close的子窗口，不能重复相加 |
| Owner Invoke | 原begin至defer清理结束，含同步Close；不含入口两个SHA、入Owner前处理和尾日志 |
| Factory Invoke | 原vm_factory.go RuntimeInstance.Invoke前后UnixNano，不含runtime对象clone；仍有墙钟局限 |
| RunContract | 既有fixture RunContract前后单调时间，含runtime建立；不含目标外的准备/账本clone和JSON日志写出 |

S0→S1包含prepare命中与SHA、Store/WASI/import、新实例、restore及既有观测。init_through_s2_ms是同次s2_ns端点，包括Initialize/_start；newinstance_restore_start_ms只相加三个不重叠窗口，不等于全部S2。

## 分配与资源

B time-only不在每阶段读取MemStats；B allocation diagnostic另开进程，每阶段读取Mallocs/TotalAlloc，Ns不当作主要性能基准。分配是**进程Go allocator增量**，可能含其他goroutine，native Rust/C allocator分配量not_measured，不能用Go allocation=0证明native无分配。

目标外层也采样Go Heap及f.run envelope分配，包含输入/收据/JSON等夹具成本，不等于完整VM纯分配。STORE_WASI_BREAKDOWN/WASM_COPY_SHA_BREAKDOWN保留call_id、root_call、TxID、alloc标志；ROOT_COST_SUMMARY只汇总根调用，不能把buyNow七个嵌套完整Invoke相加。

资源观察每25ms采样/proc RSS和线程；sleep仅在外部监视器，不间隔业务。软阈值1536MiB/220线程，保留2GiB systemd硬限、Tasks256及有界超时。所有正常进程Store/Instance配平、managed_pending0、PID退出，WASI单独计数未落盘；Selector线程身份未逐次区分，只验证固定修复库与OS线程界限。

## 扰动校准与限制

独立A/B校准覆盖hash、fact、buyNow，3批交替A/B顺序，每进程两正式目标。INSTRUMENTATION_CALIBRATION.csv：fact Factory B−A中位+1.570ms，CI[0.065,2.453]，另两方法CI跨零。不能声称B完全低扰动，也未唯一分离代码观测/编译布局/环境的贡献。原B整批更晚的数据只作辅助，不能当纯插桩增量。

B-clock在一个独立进程内1000次空begin/end：中位119ns，均值约122ns；这是一个进程的观察器底噪，不是1000次独立实验。e38Mark=5832B，短路径数值保留原观测，不减去另批空窗中位数作“修正”。精确纳秒级成本或下一轮生产收益仍需独立校准。

代码/函数/行号见audit/SOURCE_FUNCTIONS.csv；源码diff与构建命令/依赖图/hash一并保存。不得将B的时间表与A无插桩数据拼成新的配对样本。
