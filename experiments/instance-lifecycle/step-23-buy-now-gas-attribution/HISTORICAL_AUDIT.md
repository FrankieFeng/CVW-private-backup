# Step-23 历史条件审计

只读冻结Git提交507310c与394d291中的原CSV、trace、命令和receipt，hash见audit/history_hashes.json。下面条件根据实际源代码和原始记录，不直接采用报告推测。

| 条件 | Step21E R0 | Step21E R1 | Step22 A0 | Step22 A1 | 本轮计划 |
|---|---|---|---|---|---|
| Instance | 每合约从init开始保留；下游同合约继续用 | 每次包括子调用均Fresh | 每调用Fresh | 每调用Fresh | R0/R1同缓存模型仅Instance历史不同；再独立测R1/C1 |
| Store/Module | 首次每合约创建，随后复用 | 每次调用重建/编译 | 每合约/变体预先缓存 | 同左，noData Module | 同Step22缓存，不每Invoke编译；与21E R1有明确区别 |
| Copy | 无 | 无 | 无 | S1前静态区间Copy | 只在C1启用已有方案 |
| 根调用次数/进程 | 1 | 1 | 1（exchange分进程） | 1 | 每进程最多1根、六真实callee |
| 初始化 | identity→ERC721→exchange | 同左 | ERC721→exchange→identity | 同左 | 固定使用21E初始化顺序和TxID |
| 目标TxID | step21c-buy-001 | 同左 | step22-exchange-000 | 同左 | 两阶段全固定step21c-buy-001 |
| 业务参数 | 固定from/to/tokenId1/metadata | 相同 | 与21E相同 | 相同 | 完全固定；原JSON已冻结 |
| 初始账本 | a27f2d1e… | 相同 | 相同 | 相同 | 真实init后hash必须与21E匹配 |
| 根Gas | 12761395 | 12765774 | 12767294 | 12767294 | 待实测，不预设 |
| 并发/池 | 固定owner、无原后台池 | 同左 | 同左 | 同左 | 保留全部所有权与资源边界 |

三个实际依赖WASM的SHA完全相同，见inputs/manifest.json及21E gas-slots：identity213d4d2b…、ERC7219b6eb47d…、exchange9387cb4e…。都使用真实VmManager/TxSimContext/合约业务，非子合约成功Mock。Gas映射/runtime limit沿用既有代码。完整构建版本和native hash在各提交源码及Step22 environment中。

**历史比较对象**：21E只有一次根buyNow，不是先后两根冷/热。R0根Instance此前只init，但ERC721同一Instance在transferFrom前已init、mint、setApprovalForAll2；R1的每个子Instance都新建。因此复用历史与局部guest冷热相关，但不能把概念等同。21E的fact/ERC独立重复业务另属于等账本的首次/后续调用比较，不替换buyNow条件。

**第六次**：按真实子调用进入顺序（排除3次init），1 identity.addWriteList；2、3 identity.isApprovedUser；4 ERC721.mint；5 ERC721.setApprovalForAll2；6 ERC721.transferFrom。历史Instance ID：R0第六次仍为ERC721 ID2，R1为新ID10；根R0 ID3、R1 ID4。深度均1，不是递归第六层。完整调用原始记录保留在audit/history/step21e/call_records.csv。

原Gas是GetGas返回的registry累计计数。R0/R1前五个子Gas入/出相等，第6入参6374268相等、返回6386947/6391326；本地增量12679/17058；根差4379。原trace最后相同DeleteState.after=6378616，首个不同log_message.before=6386180/6390559。仅能把差异缩在transferFrom的两host边界间，不能认定JSON缓存为已证实根因。

Step22与21E不同TxID也进入guest日志、写集、事件；因此绝对Gas/最终账本不同不直接说明Copy或计量错误。本轮固定TxID消除此差异，若新Store模型无法复现，也会明确报告。

采样接口复核：GetTxRWSet会releaseAllUsedIters，中途禁止使用。最初v1把GetTxRWMapByContractName误判只读；深审sim_context_rwset_cache.go:36/46发现merge函数写第一个dst，而该API直接传入内部map，因此v1的26进程全部标为受观测器副作用影响并完整保留，不作为最终readonly证据。

最终v2在SimContext业务host接口上透明转发原Get/Put/Del一次，记录输入/实际返回，不调用RWMap采样API。已静态审计GetState/PutState/DeleteState分别通过这三个原方法；子调用仍走真实TxSimContext.CallContract，每次dRuntime建立相应只记录代理。框架元数据内部读写未冒充完整callee RWSet；根最终真实RWSet只在原事务结束时取得。v2重新进行了off/on预检及全部独立块。
