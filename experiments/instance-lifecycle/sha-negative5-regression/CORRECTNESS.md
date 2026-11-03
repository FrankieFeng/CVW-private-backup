# 正确性和计量边界

主345笔、25笔预检和6笔反序目标交易全部成功确认提交。每笔检查SDK成功码、TxID、真实区块高度、GetTxWithRWSet已存结果；所有put_end均不晚于同节点rpc_tx_end。20个五组方法批次（预检5+正式15）精确比较Gas、返回值、事件、完整RWSet、setup及最终业务写键投影，只有集合排序，没有时间/TxID字段归一化。反序G3/G4亦独立核对通过。未声称系统部署WASM不同的全库字节一致。

独立业务预期：identity.address=628aafcf44e1dd25ebb0415e8f1d7026329eebfa；callerAddress为call contract success加该地址，保留真实address子调用。balanceOf=1。tokenLatestTxInfo字段必须精确对应实际mint的TxID/高度、零地址From和冻结To。raffle必须依次Carol、Alice、Bob；正式写键在节点状态库逐项读回，预热Query后也核对setup投影未改变。

**VM日志Gas不等于最终SDK Gas，是原计量边界。** node-step39e/module/core/common/scheduler/run_vm.go:259–287在RunContract返回后追加RWSet和事件费用；gas.go:117–225按非native合约名称/去#分隔符的键/值字节及事件字节计费，固定价格0.1、向上取整。分析按每笔原RWSet独立复算，全部完全相符：balanceOf VM150→SDK156(+6)，tokenLatestTxInfo149→171(+22)，raffle三次355→373(+18)、384→397(+13)、355→363(+8)。identity.address119及callerAddress200263没有额外RW费用。VM和最终Gas都各自跨五组一致；未改Gas规则来配平。

E2E_RESULTS/VM_RESULTS的gas为SDK最终Gas，factory_logged_gas为VM边界，post_vm_rw_event_gas为追加值。最初派生分析误要求两个边界数值相等而失败；已依据源码复算纠正，不是删除样本或修改运行数据。

Factory=root Runtime.Invoke前后，根Clone在Factory之外但在SDK窗口内；Owner=进入安全Owner后的嵌套窗口，含准备/执行/同步Close。NewInstance为既有native实例化子窗口，不代表全部Store/WASI成本；Copy restore、_start、CallMethod、Close均用既有字段。CallMethod含Guest/host及callerAddress子Invoke；根已包含子调用，不重复累加。Close含Guest反分配和native资源关闭，不额外加到完整Invoke。SDK计时为InvokeContract(...,60,true)开始至同步响应，结果经PutBlock→BlockInfo→dispatcher返回，不是AddTx ACK。每个窗口是首SDK开始到末SDK响应；没有窗口内查询、Sleep、setup或重试插入。

正确性覆盖本轮成功业务路径及真实节点正常退出，未重新认证全部异常/回滚路径。SHA命中由G4 registry hits前后增长验证；G0–G3 registry entries0。所有模式Root Instance均Fresh、Store独立，caller父子Store ID同时不同；节点二进制和VM Owner/source没有改变。
