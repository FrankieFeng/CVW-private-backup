# 正确性与安全范围

下表仅Step18主矩阵家族；原24B参考独立列于REFERENCE_EFFECTS。目标方法真实执行，所有成功/失败均保留；不是仅用Go进程PASS判定。

| 方法 | G0 | G1 | G2 | G3 | G4 |
|---|---:|---:|---:|---:|---:|
| bigNumCal（10,000轮） | [120027] | [120027] | [120027] | [120027] | [120027] |
| fact | [154] | [154] | [154] | [154] | [154] |
| ERC721.mint | [235] | [235] | [235] | [235] | [235] |
| normalCal | [100000019] | [100000019] | [100000019] | [100000019] | [100000019] |

已完成662个有效配对的Gas/业务对照。逐对比较实际返回码/消息/返回字节、root RWSet（含读集和写集）、事件、业务输入、初始/最终账本及每层调用记录；bigNum返回607723520，normal返回666，fact检查JSON字段与实际写入，mint检查owner。相同输入、固定TxID和初始账本，mint tokenId=1，每次从相同init账本开始，Instance完全Fresh。

四种最终逻辑WASM各自Copy off/on经过preflight：原版与对应noData+restore S1全Memory SHA各与其模板相等，同逻辑二进制Gas/业务相等。A/B1跨二进制不能要求S1字节相等，但本次观测Gas仍严格相等；未隐去跨二进制差异。所有实测合同的A/B1新布局也可被原Copy parser支持。

未测试：真实Table函数身份（不是以非空证明身份）、全部异常/OOG/回滚、真实跨合约、长期Store回收/共享Store并发、原池背景补充及节点共识。没有这些场景的PASS。B1删除GetBatchState公共接口，只对不使用该API的当前方法给出结果。

Gas是原Getter/ContractResult的业务计费结果，不额外证明native fuel、计费插桩覆盖或未测路径一致。

两角色Module/Store独立，owner/ManagedScope守卫保持；每次business fresh，逐次close后native对象数恢复到创建前，最终created=closed、managed/pending=0，进程及cgroup退出。独立Instance隔离来自新建、相等初始账本与重复业务结果检查；本轮没有新增同时保留两个Instance互写的隔离压力试验，不把未做的测试冒充通过。RSS/线程有界只覆盖单进程2对，Store存活期间线程增长仍存在。
