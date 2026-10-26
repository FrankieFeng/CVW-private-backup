# Gas首差与传播：已定位到窗口，尚未定位具体函数

所有五块有相同整数结果，首次分歧原事件完整保存在audit/first_divergences.json；GAS_TRACE可按run_label + tx_id + call_sequence + point_sequence复算。没有以exportFunc.Call耗时推导Gas。

## 调用与状态

外部→exchange.buyNow（深度0、根序号0），依次六个真实VmManager下游（深度1）：identity.addWriteList、两次isApprovedUser、ERC721.mint、setApprovalForAll2、transferFrom。R0三个Instance分别ID1 identity、ID2 ERC721、ID3 exchange，从真实init一直保留；R1/C1初始化各一个，业务根ID4，六个callee为ID5–10。新建模式的uses_before全部0。

R0根在本轮只init过，没有预热第二根buyNow；ERC721到第6callee已走init/mint/approval。冷/热是具体执行历史描述，不是对reuse/fresh的同义替换。新模型把R1的Store/Module也缓存，在同Store上连续创建不同Fresh Instance后依然复现差值；不能把历史“每调用编译”当必要根因。仍未单独隔离Instance私有guest状态与其WASI bundle状态。

## 最早当前调用计数差

| 观测边界 | R0 | R1 | 解释 |
|---|---:|---:|---|
| root原SetGas后已用Gas | 0 | 0 | 旧Instance Gas与Fresh初值差异已由原SetGas覆盖 |
| 第6子调用Gas入参/SetGas后 | 6374268 | 6374268 | 更早调用没有把差额带入 |
| transferFrom DeleteState.after，seq36 | 6378616 | 6378616 | 最后相同的计费点 |
| 下一log_message.before，seq37 | 6386180 | 6390559 | 首个已采样不同点，差4379 |
| 该窗口增量 | 7564 | 11943 | 由同一个上一点逐条相减，非不同批次 |
| callee最终GetGas累计已用 | 6386947 | 6391326 | 后续各增加767，差值不再扩大 |
| callee本地边界增量 | 12679 | 17058 | 累计返回−相同入参 |

seq37的相同文本为`setTokenLatestTxInfo to {"TxId":"step21c-buy-001",...}`。它在日志宿主实际处理前已经携带不同计数。先前读写快照、输入、全部已采样ChainMaker host调用形状和前五callee计数均相同。

这是**两个已采样ChainMaker host边界之间的guest执行窗口**，包括未细分的Go runtime行为；WASI imports没有逐项采样，不能据此排除未观测WASI行为或声称逐guest指令路径完全一致。源码参考`setTokenLatestTxInfo`包含构造对象、json.Marshal、格式化与日志；WASM含encoding/json相关函数。这只支持JSON缓存候选，没有逐函数/指令Gas和受控干预，不能把4379完整归给某个编码器、GC、分配或缓存。

## 传播到父与最终Gas

| 阶段 | R0 | R1 |
|---|---:|---:|
| root第6次before_wacsi已用 | 6274268 | 6274268 |
| 原跨合约基础费 | 100000 | 100000 |
| 传给子调用的累计Gas | 6374268 | 6374268 |
| 子返回累计Gas | 6386947 | 6391326 |
| WACSI返回gas | 12761215 | 12765594 |
| 原parent SetGas后已用 | 12761215 | 12765594 |
| root最后GetGas/ContractResult | 12761395 | 12765774 |

本fixture为BlockVersion1，保留既有`WacsiImpl.CallContract`：先`gasUsed += CallContractGasOnce`，子调用接收此累计值，返回后`gasUsed += result.GasUsed`。因此本实现的WACSI值为6374268+子累计返回；不能把子结果误当“纯本地Gas”。这里只复核现存公式和相同计量边界，**不据此认证收费公式全局正确，也没有改它**。

`after_wacsi`时父registry仍是调用前相同值6274268，但WACSI返回已含差额；原`setGasByExport`之后父计数才带上4379差额。root之后均再增加180，故根差完整由该callee带回，末尾Getter/结算没有新增差额。36个桥接快照（12次core调用×3阶段）及每次原Getter读数核对支持这一定位。

为什么是12次core却只有6个callee：每个SDK跨调用的is_len=true会真实执行一次子合约；is_len=false只读取缓存结果。原wasi.go有明确分支，实际dRuntime Invoke记录始终为根+6，不把取结果当额外业务执行。

当前Gas是runtime原GetGas的registry Remain：`runtimeGasLimit - Remain`，不是native fuel、指令数、CPU周期或时间。GasOut是业务后、CallDeallocate/销毁前的原Getter结算值；关闭阶段不读取已销毁memory，也不重定义原Gas范围。

## Copy单独判断

五块Fresh/Copy根/六子返回相等，各147个原gas点及36桥接快照相等；同WASM/source SHA、原Gas规则和等状态输入，无模块升级或SDK替换。35对CALL/STATE复核与Memory hash独立进行，所以不是通过hash推断Gas。R0热态少4379不构成Cold Copy必须追平的目标。

未验证的Table函数身份、内部Globals全量动态比较、异常/OOG/回滚、真实节点及长期Store并发/回收仍not_tested。根因只定位到上述窗口，不能用假设替代尚缺证据。
