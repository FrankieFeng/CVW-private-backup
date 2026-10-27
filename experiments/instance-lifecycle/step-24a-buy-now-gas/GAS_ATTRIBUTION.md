# Gas归因：确认到JSON编码相关预热，未唯一定位内部缓存

## 历史证据复核

`audit/history/BLOCK_SUMMARY.csv`、`COPY_PARITY.csv`和`audit/recomputed-step23.json`核实Step-23五块R0/R1根Gas为12761395/12765774；5块Fresh/Copy共35对callee记录相等。原始`v2-lifecycle-b1-R0.log`、`v2-lifecycle-b1-R1.log`已经随审计保存。受影响v1不混用。本轮不再执行Copy，Copy相等仅保留为历史证据。

R0的ERC721实例已真实执行init、mint、setApprovalForAll2；R1每次新建。父根R0只执行过init，不能描述成“根buyNow已业务预热”。初始账本和目标参数相等，不等于运行时内存相等，这正是比较变量。

## 第一处分歧与后续传播

三块所有条件共用transferFrom传入累计Gas6374268，目标seq1–36 Gas均相等、宿主调用顺序相同。seq36是**第二个**DeleteState.after，为6378616。seq37是`log_message.before`：

| 边界 | R0/J | R1/S0/U | 两类差值 |
|---|---:|---:|---:|
| DeleteState.after（seq36） | 6,378,616 | 6,378,616 | 0 |
| log_message.before（seq37） | 6,386,180 | 6,390,559 | 4,379 |
| 该窗口增量 | 7,564 | 11,943 | 4,379 |
| transferFrom返回累计值 | 6,386,947 | 6,391,326 | 4,379 |
| 根最终累计Gas | 12,761,395 | 12,765,774 | 4,379 |

seq37后到子调用结束，两侧新增均767。原WACSI路径把子调用累计输出加入进入子调用后的累计6374268，得到12761215/12765594，再原SetGas传回父实例；根末尾各加180。因此根差值没有增加，也不能把每层累计输出当局部成本求和。`GAS_TRACE.csv`提供全部根/子调用/准备期边界（含失败的eligible=False记录），`CALLS.csv`给正式调用的进出Gas与Instance历史。

**log_message.before是桥接函数内的观察点，并非WASM导入调用前的精确PC**：已完成Memory.Data访问和日志字符串读取/宿主拷贝，尚未执行探针后的宿主日志处理。上述读操作不执行Guest计费函数，原只读探针也不改计数。现有记录可排除差额在该探针之后或根结算阶段才新增，但不能据此指定Guest内哪个ConsumeGas最早分叉。

## 实际Guest路径

固定ERC721 SHA `9b6eb47d4ca79f975a9214cc0459d47637ae7d4f1bdc45aa4fd91a0e24c1be1d`，实际WASM反汇编见`audit/selected-disassembly.txt`。

第二个DeleteState（main.setAccountToken，0x337196）返回 → main.transfer → main.setTokenLatestTxInfo[2989] → GetTxId/GetBlockHeight → ParseUint → newobject / 写屏障候选 → encoding_json.Marshal[2146]（0x333e6e，类型89248）→ 字符串转换 → fmt.Sprintf[1950]（0x333fc0）→ SDK.logMessage[2943]（0x33401e）→ 宿主seq37。

后续PutState在0x334291，不在首差窗口。完整动态函数入口、分支和逐guest Gas尚不可直接观察；以上是实际二进制静态路径与成功host trace共同约束，不能声称所有潜在栈增长/GC/错误分支均已排除。参考源码`audit/reference-erc721.go:618`有tokenLatestTxInfo构造、Marshal和格式化日志，但没有精确source→WASM可重建证明，不用源码行号冒充WASM实际PC。

实际typeEncoder[2158]查缓存并有newTypeEncoder[2160] miss路径；cachedTypeFields[2191]也有typeFields[2247] miss路径。原WASM已有编码测试导出使用**相同类型89248**，所以它是有意义的可证伪干预，并非只因函数名字含JSON而猜测。

## 本轮干预证据

预登记和收缩记录见`TRACE_PATH.md`。三块中，S0提前创建不改变差额；U运行既有解码导出、目标实例有过1次业务也不改变；J运行既有编码导出后差额完全消失，目标全部Gas点匹配R0。所有组使用同一模块版本、同一输入、相同初始账本；J/U只恢复账本，不清Guest状态。预热Gas独立保留在`WARM_RECORDS.csv`，没有从root扣除或改Gas规则。

这确认了：**保存于ERC721 Instance中的、可由该编码相关预热改变的运行时状态，足以造成/消除当前4,379差额**。简单的Instance提前创建和“任意执行过一次导出”均不足以解释本轮结果；这并不排除更细的allocator/pool等状态。

这是一个“编码相关预热充分、所选解码对照无效”的干预证据；它支持JSON类型编码首次建模开销这一假设，比时间相关性更强。它**未证明**单一encoderCache/fieldCache根因：编码导出还进行了fmt.Sprintf、字符串转换、分配、日志、3次PutState，且两次Marshal之后还执行一个无Marshal stub。encodeStatePool、fmt printer pool、allocator/栈等状态与缓存共同改变。解码对照也没有完全匹配fmt/分配，因此不能把它当严格等量控制。

## 工具失败及证据限制

首次内部cache读取预检在mint处主动拒绝：`cache key layout/uniqueness mismatch`。静态Go ABI/反汇编推导未能建立可靠运行期键解释；该失败过程目标不完整，不能作为Gas收益。保留旧源码/binary hash、STOP、全部日志，并在新build02固定A24_CACHE_READ=0，全部五条件重新做probe off/on无扰动预检。**没有读取到可靠的运行期JSON cache命中/未命中状态**，缓存预测一律not_tested。

本轮没有修改WASM、Gas、消费权重或底层运行时。没有Guest逐函数入口Gas、缓存内容证明、特定字段编码器建模调用次数，所以**精确根因尚未最终定位**。最接近且重复成立的边界仍为setTokenLatestTxInfo成功路径中seq36→seq37；确切首次不同的Guest函数未确认。

## 下一步最小证据（本轮未执行）

1. 首先用离线解码校验及明确版本布局建立可靠运行期缓存读取，探针off/on分别验证Gas/语义，禁止猜偏移继续运行。
2. 若不能只读定位，则另列**改变二进制的独立诊断**，在同一Go/SDK版本下对Marshal、typeEncoder、newTypeEncoder、cachedTypeFields和fmt入口/出口作低扰动计数，保留原始WASM参照；不能把改后二进制的Gas直接等同原差额。
3. 提供只做同类型编码、只做fmt、以及不同类型编码的匹配干预，拆开原导出的多项预热；任何新增WASM必须记录新hash，不能混入本轮原WASM证据。

这不是本轮的优化实现建议，也不解除R0 Gas不一致或原Store并发限制。
