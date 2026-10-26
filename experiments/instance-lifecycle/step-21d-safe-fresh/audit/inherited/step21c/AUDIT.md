# Step-21C 历史、调用链、状态和Gas审计

## 范围与版本

用户已确认Step21B仅规划、未执行；不再查找不存在的报告。当前安全边界继承Step21A的Store创建/执行/关闭粗粒度区间重叠记录。Step21C只准备源码、编译和静态检查，无guest运行。所有源码路径以.worktrees/cvw-step21c为根；依赖生产源码相对fc3e90d不变，仅新增step21c_fixture_test.go。

## 三份实际产物与历史参照

当前测试件为vm-wasmer/v2@v2.4.0/testdata中的exchange、identity、erc721，完整SHA/Bytes见audit/artifact-inventory.json，冻结输入见fixture-manifest.json及inputs/exchange-buyNow.json。没有重编/变换合约。根SHA9387cb4e…、identity213d4d2b…、ERC7219b6eb47d…；toolkit候选根72ef5f1c…/identitya6590321…/ERCa692e438…不同，不能标为9月PPT精确用件。881.2/57.7和15.27只作用户历史参考。

实际恢复的toolkit入口parallel/Init.go:105–132的InitBeforeTest在exchange前先Install identity、erc721，再安装exchange；:506–523中identity/exchange无初始化参数，ERC721初始化name=huanletoken、symbol=hlt、tokenURI=https://chainmaker.org.cn。:214–217保存buyNow参数，RandParams将tokenId递增。不能证明该现存文件逐字等于9月PPT实际配置，未找到完整历史部署状态/逐笔Gas/工作负载记录。

## 调用链：三合约，六个下游调用

chainmaker/testdata/exchange/exchange.go:48、57、65、77、88、101：

```text
exchange.buyNow（根，depth0）
  1 identity.addWriteList(from,to)                 depth1
  2 identity.isApprovedUser(from)                depth1
  3 identity.isApprovedUser(to)                  depth1
  4 erc721.mint(to=from, tokenId, metadata)       depth1
  5 erc721.setApprovalForAll2(approvalFrom=from)  depth1
  6 erc721.transferFrom(from,to,tokenId)          depth1
  → buyNow事件 → buyNow success
```

当前根WASM反汇编有6个sdk.CallContract静态调用点，见audit/current-buynow-disassembly.txt与static-call-sites.json；分支可能提前返回，不能把6个静态点写成实测6个成功子调用。三份WASM必需导出已检查，见audit/artifact-exports.json。

选定identity addWriteList/isApprovedUser及ERC721路径没有额外用户合约调用，源码预期最大depth1；identity的另一个callerAddress方法:205会自调用identity.address，但不在本buyNow路径。完整动态深度仍not_tested，协议最大depth5未改。正常成功预期7个Runtime Invoke记录，只有1个根交易，不能计7笔TPS。R1若严格不复用，源码上预期每成功根交易消耗7个Fresh业务Instance（根1+子6）；验证实例、预建库存和额外grow另计，不能将7写成实测创建数或TPS倍数。

## 原TestInvoke夹具缺失

runtime_test.go:369–402通过prepareFile/prepareContract/newVmPool直接建根池；prepareFunc/getMethodParams只有业务参数，不安装callee、不初始化合约、不维护跨交易账本。prepareContract使用包级ContractName，存在空Name；prepareTxSimContext每笔新VmManager/InstancesManager，SnapshotMock.GetBlockchainStore/GetLastChainConfig未实现，GetKey只读未初始化cache。先前失败还没有进入真实callee，不能拿其耗时比较完整buyNow。

ParametersValueMaxLength在protocol/vm_interface.go:159–161为未赋值全局uint32，初值0。标准赋值存在vm/v2/wasi_test.go:33–35的测试init；构建vm-wasmer测试时依赖包_test.go不参与，因而不会执行这段赋值。wasi.go:573拒绝首次81字节address参数。本轮夹具在未来构造时显式设默认10MiB并用t.Cleanup恢复；不是改Gas或guest逻辑。此次constructor未执行，当前全局运行状态未修改。

## 恢复的真实夹具与验证边界

step21c_fixture_test.go实现：

- 三合约元数据/字节码注册；一个InstancesManager在进程内共享，避免每根交易重建子池。
- 内存Snapshot与账本只提供真实状态读写；使用原vm.NewTxSimContext、CallContract的深度/RWSet合并/回滚逻辑；根成功才提交真实TxWrites，失败不提交。
- 原vm.NewVmManager/RunContract负责实际成员参数及调用分发；observedRuntime只调用实际RuntimeInstance.InvokeTime并返回原Result，绝无callee答案表、空业务函数或Mock成功。
- 仅测试身份上下文：公开固定P256公钥、真实解析与SKI UID；成员提供器只识别该身份，签名/节点ACL未覆盖且不返回伪造认证成功。沿用Step21 BlockVersion1，不能宣称现代节点授权/交易签名验证通过。
- 真正调用三合约init_contract后再验证白名单、NFT owner、授权、事件、错误路径；三次成功/重复token/非法地址等断言已编译，但全部未执行。
- identity现存源码对非空adminAddress参数的处理有疑点，夹具沿原toolkit无参初始化，让真实guest走配置公钥的GetSenderAddress，且准备非空admin状态断言；不直接写入假管理员。

root/callee的Gas、返回值、读写集、事件和before/after状态hash会由真实调用收集。当前只有代码，没有任何业务receipt，不得将“断言已准备”标为通过。原源码中ERC721 mint/transferFrom若干权限拒绝分支被注释；本轮不更改，也不把业务成功当作标准ERC721授权安全认证。

## Instance生命周期与Store边界

原InstancesManager.getVmPool会newVmPool并同步grow(defaultMinSize=5)后缓存，三个合约各有Module/Store/池；原TestInvoke手工根池初始空，二者冷态边界不同，未来正式统计需重新明确，不能直接混用。GetInstance非阻塞借出，空则发apply并阻塞；runtime.go的根/子路径都GetInstance并defer RevertInstance。R0归还；R1 vm_pool.go:696–705异步Close→remove→add，worker触发grow，Close包含guest CallDeallocate及native删除。

连续identity3次、ERC7213次可使前次异步回收/新建与下次同Store执行重叠，即使只顺序发根交易也不能规避。Step21A容量补丁和CAS粗粒度守卫均不构成完整Store线程安全证明。本轮不添加全局执行锁、不逐callee排空伪装原负载，也不绕过守卫；guest入口无条件Skip。三个池的WASI线程/RSS总预算还需Step21B验证，不能抬高原220线程/1536MiB软限。

## Gas及计时路径（均未修改）

1. Runtime.InvokeTime按runtimeGasLimit−传入gasUsed设置可用Gas；CallMethod后通过导出函数读剩余值，runtime.go:329–341报告GasUsed。
2. SDK CallContractLen→bridge.callContractCore读取根当前GasUsed→wacsi.CallContract；wasi.go:583加CallContractGasOnce，再传入实际TxSimContext.CallContract→VmManager→子Invoke。
3. wasi.go:596在返回时加result.GasUsed，bridge:406回写根Gas。旧BlockVersion1中callee.GasUsed是否包含传入累计量需要单独核对；不能手工求和或默认R0/R1必相等。
4. bridge:396取得wacsi err后，:406复用err变量可能覆盖原错误，原Step16已记录。本轮不修生产错误处理；准备同时核对每个真实callee Code/Message与根结果，避免仅根字符串误判成功。
5. 子调用失败时BlockVersion<2300的TxSimContext仍合并到上一层，根失败的GetTxRWSet(false)及fixture不提交提供整笔失败保护；准备负向状态hash/写集断言，现代块版本语义未覆盖。

时长记录只包实际InvokeTime的原begin/end；根为inclusive，包含子合约工作及嵌套VM管理开销；子inclusive单列，禁止再次累加到根，主N只计成功根交易。RunContractWallNS含外层管理器/首次编译和观测日志，单独命名，不与InvokeTime或节点客户端延迟混用。原vm_factory计时还包adapter外层日志，因此未来不能自动声称与Step19 factory INFO逐字同边界。当前未生成任何性能数字。
