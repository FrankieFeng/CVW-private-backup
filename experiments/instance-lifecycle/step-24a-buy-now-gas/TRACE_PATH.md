# Step-24A 静态TRACE_PATH（动态运行前冻结）

2026-10-27。基线ba57368。Step23有效v2的BLOCK_SUMMARY、GAS_TRACE和35行COPY_PARITY已逐项复算（audit/recomputed-step23.json），不是照抄提示。五块R0/R1根12761395/12765774、差4379；目标第6callee seq36为6378616共同、seq37为6386180/6390559。Gas均是原GetGas的累计已用值，不加六个累计返回；该窗口增量7564/11943，差4379。

## 实际WASM与源码路径

固定ERC721 SHA9b6eb47d…，producers明确go1.24.1；没有DWARF（完整sections证据已存），name和code section存在。未重编译/修改WASM。reference-erc721.go仅为候选源码，不冒充逐字重建来源；函数索引/调用点以实际反汇编为准。

根buyNow→identity三次→ERC721 mint、setApprovalForAll2、transferFrom，深度1；目标transferFrom为第6callee。它的成功路径是：main.transferFrom[2986]→main.transfer[2987]→…→main.setAccountToken[2998]→第二个SDK.DeleteState（0x337196，SDK函数2959）→返回setAccountToken/transfer→main.setTokenLatestTxInfo[2989]→SDK.GetTxId[2949](0x333a9b)→SDK.GetBlockHeight[2948](0x333bed)→strconv.ParseUint[1470](0x333d4b)→runtime.newobject[264](0x333d88，struct type214464)→可能的gcWriteBarrier3→encoding_json.Marshal[2146](0x333e6e，传入*tokenLatestTxInfo类型89248)→runtime.slicebytetostring/convTstring→fmt.Sprintf[1950](0x333fc0)→SDK.logMessage[2943](0x33401e)→宿主log_message.before。

后面的SDK.PutState在0x334291，**不在首差窗口内**；错误/栈增长/panic路径在实际WASM也存在，不能仅根据静态call表声称运行了全部分支。主成功路径由Step23实际host调用/返回/状态结果约束。目标DeleteState是账户token索引删除；更早还有token授权删除，不能混淆两个DeleteState。

候选源码位置：transferFrom457、transfer495，setAccountToken803，setTokenLatestTxInfo618–655；该函数构造TxId/BlockHeight/From/To结构后Marshal，再格式化日志。SDK取TxId/高度使用本次参数，无对应节点I/O调用。此处仍可能有Go分配、写屏障、GC/栈路径；尚无逐guest函数入口计数，不预先排除。

## JSON缓存可观测依据

实际typeEncoder[2158]在0x21e409调用HashTrieMap.Load[1553]；全局地址2267392。miss路径包含newobject/WaitGroup、LoadOrStore[1551]、newTypeEncoder[2160](0x21e77c)、Swap[1548]。cachedTypeFields[2191]使用另一个map2267456，miss调用typeFields[2247]。这不是时间/CPU缓存推测，而是实际代码中的Go类型缓存；但本轮尚未动态证明其命中情况或Gas贡献。

Go1.24.1参考hashtriemap.go与实际Load/entry.lookup的assembly共同约束读取布局：map.root+16；节点tag0；indirect.children+24、16个8byte指针；entry.overflow+8、key(itab,data)+16/+24、value+32/+40。static Data重建及ABI元数据核实*tokenLatestTxInfo=89248、struct=214464，struct大小56，四字段TxId@0、BlockHeight@16、From@24、To@40；不是猜偏移。详情inputs/cache-layout.json。没有DWARF，不能据此声称可观测任意Go局部变量。

## 不改原WASM的最小可证伪设计

原WASM已经导出testgasJSONMarshal[3022]和testgasJSONUnmarshal[3021]。实际Marshal诊断函数的两个stub在0x334a3b/0x3352e4调用同一个encoding_json.Marshal，并传入同一个类型89248；第三stub没有Marshal。Unmarshal诊断只解空结构，不是目标类型编码。此事实由实际WASM验证，不仅依赖附近源码。

预登记5组，每块同WASM、相同目标buyNow输入/TxID、同初始账本，所有模块仅缓存原版，无Copy或noData编译：

- R0：保持Step23原真实复用历史（init→mint→approval→transfer），不清其状态。
- R1：所有业务Instance新建，Step23 Fresh原版。
- S0：额外提前准备一个未执行业务的ERC721 Instance，只把它用于transfer。从而检验提前创建/年龄/选择效应；仍无业务复用。
- J：仅对该专属Instance先执行原有testgasJSONMarshal，恢复账本到真实init后的副本，保留该Instance运行时状态；其余子调用Fresh，目标transfer才使用预热Instance。
- U：同J流程，但执行已有testgasJSONUnmarshal，作为无目标类型编码的负对照。

J/U是**有意预热并保留Instance的诊断组**，不是Fresh优化方案或生产正确性方案；不改root业务路径/参数，不把准备Gas并入root，不通过清缓存追平。预热会影响fmt/分配等其他状态，故即使J消除差额，也不能单靠这一对照宣称某一个cache条目是唯一原因。

可证伪预测：若目标JSON类型缓存机制是候选主因，R0/J在DeleteState.after前已有目标encoder条目，R1/S0/U尚无；之后R1等在log前建立条目；J应减少4379，而S0/U应保留冷态差值。若状态/数值不符，必须记录假设不成立或证据不足。将读取全部cache键和函数值、字段cache键，不凭根指针变化宣称命中。读取只用原Memory.Data视图，所有指针/节点/长度有界核对；解码失败立即停止，不能猜测继续。

先每组probe off/on各1根，验证Gas/结果/实际root RWSet/事件无扰动。通过后3独立块×5组，每条件独立进程、每进程1根（最多10个WASI实例），交错组顺序。沿用固定OS owner/Scope全部守卫与1536MiB/220软限、2GiB/256task硬限、Go45s/进程60s，不放宽，不并发，不加100ms。若现有导出或布局无法可靠使用，停止该动态方案并报告工具边界。

状态观察沿用Step23有效v2的透明Get/Put/Del转发，**不使用会写内部map的GetTxRWMapByContractName**，不在中途GetTxRWSet。最终真实root RWSet、业务操作、返回、事件仍分别对照。Step23已有Table真实身份/异常、native精确构建及长期资源问题本轮不自动宣称解决。


## 动态预检后的方案收缩（主实验前登记）

首次原始R1 off通过，cache reader on在ERC721.mint处因cache key layout/uniqueness mismatch主动拒绝。该过程已退出、登记清零、资源正常，无Store/native并发守卫触发；业务因探针异常失败，因此整组计费不可用。STOP和源码保存audit/unsupported-cache-reader-build01，原日志不覆盖。

**撤销动态内部cache命中状态的验证计划**：即使静态偏移看似匹配，也未建立可靠的运行期键表示/布局解释。不能报告成员存在或缺失，不再猜偏移重试。最终build02把A24_CACHE_READ固定0，只执行Step23已验证的边界Gas/状态操作探针和已有export预热对照。所有Native/OS owner/资源和Fresh守卫仍保留。恢复仅限这个已知探针失败、指定新binary与safe-*标签；任何新资源/语义/所有权失败立即重新停止。

原R0/R1/S0/J/U条件和相同账本/根输入设计不变；cache状态预测标为not_tested。J若减少差额，仅证实该JSON编码相关预热的充分效果；仍可能耦合fmt、编码状态池、分配等，不能唯一归因encoderCache/fieldCache。原读取器相关结果不得并入有效组。

## 2026-10-27 实际结果回填

build02五条件off/on全部通过；三块正式×五条件也全部通过。R0/J根12761395、其余12765774；J与R0全部已观察Gas点相等；S0/U与R1相等。各组真实业务语义对照一致。编码相关预热充分效果已证实；内部缓存命中与确切首次Guest函数仍未验证，不能恢复使用前述未通过的动态布局解释。报告以GAS_ATTRIBUTION.md为准，完整失败保留。
