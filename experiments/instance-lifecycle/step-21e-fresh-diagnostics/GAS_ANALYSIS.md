# Gas差异：排除账本变化，定位guest首次分歧窗口

**已证实Instance执行历史会影响当前WASM的Gas结果，即使业务输入与账本初始状态相同。** 尚未把差值逐条归因到JSON缓存或某条guest指令；不能写成Gas规则已被证明错误，亦不能通过改业务或Gas表消除差异。

## 实验与观测方法

同WASM/hash见[audit/wasm-manifest.json](audit/wasm-manifest.json)。fact/ERC721各进程先真实init，复制初始化后账本；每次目标调用还原完全相同快照、固定TxID `step21e-equal-000`、blockheight111、原夹具固定时间、相同参数。R0保留同一Instance的guest状态，R1每次新Engine/Store/Module/WASI/Instance；不改变合约代码。输入冻结见[audit/gas-inputs.json](audit/gas-inputs.json)。

读取的Gas是原Runtime真正使用的guest导出GetGas（registry.gasPtr->Remain），不是把native metering API或CPU指令数当成Gas。五个实际WASM的GetGas反汇编得到指针槽，按逐件hash绑定[audit/gas-slots.json](audit/gas-slots.json)，只读native memory、校验边界，不额外调用guest GetGas、不写guest内存。每次在Runtime原有Getter处核对只读值一致。syscall前后、业务入口/返回及原有日志调用读取计数器；probe-on/off独立fact调用Gas均1585，输入/状态/RWSet/结果/事件一致。此检查不意味着探针对时延零影响，**Gas日志批不用于性能主张**。

记录见[gas_timeline.csv](gas_timeline.csv)、[call_records.csv](call_records.csv)与每进程`raw_logs/*-receipts/*.json`，包含Gas入参/累计结果、真实返回值、全部读写集/事件、调用深度、Instance ID。逐调用完整Gas和语义比较在[audit/gas-equivalence.json](audit/gas-equivalence.json)。

## 等状态结果

| 方法 | R0三次Gas | R1三次Gas | 冷−热 |
|---|---|---|---:|
| fact.saveAndFindByFileHash | 1585, 991, 991 | 1585, 1585, 1585 | 594 |
| erc721.mint | 15449, 11070, 11070 | 15449, 15449, 15449 | 4379 |

六次之间输入、前后账本hash、RWSet、事件和返回值均完全相同（同方法内比较）；R0同Instance，R1三个新Instance。冷R0与Fresh R1 Gas相同。ERC721绝对值不同于旧Step21的14469/10090，因为本次使用固定TxID及真实等状态夹具；同一4379差值能够复现，不能混用不同夹具的绝对数值。旧tokenId增加到两位还会改变Gas，本轮固定tokenId1排除这一因素。

fact返回文件JSON，但实际入账fact_bytes是`{}`（原Fact字段未导出），新旧模式的写值一致；不为了改善夹具而改业务。完整receipt保留base64原值，不能只看返回文本推断写入正确内容。

## 首次差异窗口

以同一R0进程第一/第二次对齐，所有先前观测点相同；[逐点原始边界](audit/first-gas-divergence.json)保留准确序号与实例。

| 路径 | 最后相同点 | 首个不同点（冷/热累计Gas） | 界定 |
|---|---|---|---|
| fact | business.before均0 | 首次EmitEvent.before 931/337 | guest入口至第一次host调用，差594已存在，早于事件宿主实现和后续读写 |
| erc721.mint | PutState.after均2965 | latestTxInfo日志.before 15060/10681 | 两host边界之间guest代码，差4379；日志内容相同 |
| buyNow第6 transferFrom | DeleteState.after均6378616 | latestTxInfo日志.before R0 6386180 / R1 6390559 | 子调用Gas入参也相同；差4379在子guest内产生 |

本地对应业务源码分别在[audit/guest-reference/fact.go](audit/guest-reference/fact.go)与[erc721.go](audit/guest-reference/erc721.go)，反汇编在audit/*-selected-disassembly.txt。fact在首EmitEvent前构造Fact并json.Marshal；ERC721对应setTokenLatestTxInfo构造结构、json.Marshal和fmt.Sprintf再日志。实际WASM含encoding_json.typeEncoder/newTypeEncoder及Load/Store缓存路径。**JSON反射编码器首次构建缓存是有源码与窗口支持的候选解释**，但窗口还包含参数处理、分配与其他SDK/runtime代码；没有内部逐函数计数和干预对照，不能把594/4379完整等同某个缓存成本。本地源码不是可重建WASM来源认证，真正执行的是固定hash的既有WASM。

R0账本恢复但guest历史保留、R1反复冷态，已将“差异仅因账本变化/参数长度”的解释排除于此夹具；仍不能仅靠R0/R1区别细分Store历史与Instance私有堆/栈状态。后者是下一步更窄的因果问题。

## buyNow：真实六次下游，累计Gas不能求和

两个独立进程从同样三合约真实init开始，root前后状态hash、读写集、事件、返回值一致。根Gas R0 **12761395**，R1 **12765774**，差4379。每根严格6次真实VmManager下游，深度1，无Mock成功返回；R0 identity/erc721分别复用各自实例，R1六个子调用六个新bundle。

| 次序 | 下游 | 相同Gas入参 | R0累计返回 | R1累计返回 | R0/R1本地增量 |
|---:|---|---:|---:|---:|---|
| 1 | identity.addWriteList | 100276 | 101804 | 101804 | 1528/1528 |
| 2 | identity.isApprovedUser | 302309 | 302538 | 302538 | 229/229 |
| 3 | identity.isApprovedUser | 705088 | 705317 | 705317 | 229/229 |
| 4 | erc721.mint | 1510668 | 1525965 | 1525965 | 15297/15297 |
| 5 | erc721.setApprovalForAll2 | 3136862 | 3137143 | 3137143 | 281/281 |
| 6 | erc721.transferFrom | 6374268 | 6386947 | 6391326 | 12679/17058 |

这里本地增量=累计返回−Gas入参。根最终Gas也包括原有bridge/root继续执行的算法；不能把六个累计返回相加，也不能简单把根减六个累计结果叫“根自身Gas”。本轮按根整笔、各callee入/出/本地增量分别记录，保留bridge的原Gas传播规则。第6调用之前入参相同，因此首差不是从根早先传播进来的差。

## 对Step22的约束

R0热态Gas不是Fresh R1应追平的真值。Copy若复制已执行Instance的运行时缓存，即使业务读写相同也可能降低Gas；不能以Gas规则调整或忽略差值通过一致性门槛。应把**相同起点的冷Fresh与待验证Copy**作为主功能对照，逐层检查Gas、事件/读写集/调用深度，再单列热R0的状态差异。当前已能定位差值发生在哪一层/哪两个host边界之间；精确编码器缓存归因仍未闭合。
