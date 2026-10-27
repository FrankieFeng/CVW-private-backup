# 正确性复核及安全边界

本轮无新Guest执行，以下为对Step25冻结原始证据的重新核验，不是新功能/安全测试。

## 核验内容和结果

- 原81个正式进程×2对=162对，以及15个相关预检进程×1对，共177个配对全部通过严格JSON逐项对照。
- 对照字段包含实际状态码、返回码/消息、返回字节、Gas、business_input、TxID、初始/最终账本hash、实际根RWSet（读集/写集）、事件及原调用记录，不仅检查Go测试PASS。
- 相同方法所有提取进程的初始账本hash只有1个，双方每次从同一个init副本开始，业务参数/TxID固定；mint tokenId=1在每笔前恢复等价账本，绝不是在同一账本重复非法mint。
- compute返回`success bigNumCal: 607723520`，fact逐字段检查JSON与真实写入，ERC返回`mint success`并核对token owner；配对raw receipt完整保存。
- 同一方法各组返回Gas相等：compute120027、fact154、ERC235。Gas来自原Getter/ContractResult，不据此推断native fuel或所有计费覆盖相等。没有修改Gas规则或事后补偿Gas。
- 从原profile读取的Gas和receipt实际Gas一致，CallMethod观察错误均`<nil>`，所有原结果码0。原实现会覆盖CallMethod错误的历史行为未改，但这里额外核对保留的实际错误，避免仅靠返回码误判。
- 每进程所有init和business Instance ID均唯一，数量与created一致；正式各角色init+2正式实例，原Fresh guard未发现业务Instance复用。每次关闭后Managed对象数恢复创建前，末尾created=closed、in_flight=0、owner managed/pending=0，PID/cgroup退出。

## S1与Copy

相关预检包括每方法G0→旧G1/旧G2/旧G4及旧G2/旧G4各自Copy off/on。原测试在WASI.Initialize/_start之前把实际S1全Memory SHA与其逻辑WASM的静态模板SHA核对，成功后原profile保留s1_hash。不同A/B1逻辑二进制的S1布局本来就不同，不要求跨二进制整页hash相等。

同一逻辑WASM的标准Data和noData+Copy在原预检Gas/返回/状态/事件一致，Copy真正替代active Data初始化。缓存绑定最终WASM/配置/版本以及Module，不跨不同产物借模板。TIMING同时保留old_group、group和Copy实际开关；预检左侧可能是某逻辑变体的Copy关闭控制，不能将其计入正式Copy性能。

## 跨家族不能混用

Step25两家族在相同TxID/业务输入/初始账本下仍有不同Gas，详见BUILD_LINEAGE和audit/lineage-findings。原Step24B参考ERC15981与更早历史15677还另有TxID格式差异。这些都不是当前同源配对中的Gas不一致；也不能以业务状态相等补齐原件构建来源缺口。

## 未验证项

| 项目 | 状态 | 限制 |
|---|---|---|
| 当前原成功路径的Gas/返回/根RWSet/事件/账本 | 原样本复核通过 | 无新增动态验证，不外推所有输入 |
| Fresh身份及逐次同步关闭 | 原样本复核通过 | 固定owner串行预算内，不认证原池 |
| S1全Memory和同逻辑Copy off/on | 原预检复核通过 | 非不同二进制状态hash等同证明 |
| 真实Table函数身份 | not_tested | 保留section/结构不等于验证元素函数身份 |
| 异常/OOG/回滚全路径 | not_tested | 本轮不执行异常扩展 |
| 真实跨合约 | not_tested | 三个目标方法为本地业务 |
| 同时存活Instance互写压力隔离 | not_tested | 未把唯一ID/重复结果冒充同时互写测试 |
| 长寿命Store资源回收 | not_tested | 已知WASI线程随Store存活累积未解决 |
| 原池背景Fresh/异步关闭/共享Store并发 | not_tested | 原风险边界不解除，无全局锁绕过 |
| 真实节点/客户端/TPS | not_tested | 串行参考管理器不是节点数据 |
| B1公共SDK兼容 | 限制已确认 | GetBatchState被删除，非通用兼容方案 |

原安全阈值不变：单合约RSS768MiB/线程125软限，2GiB/256task硬限，45s Go/60s进程超时，全局available8GiB/swap1GiB。所选原进程观测峰RSS418.39MiB、Go heap Alloc66.73MiB、线程109，未触发保护；这些是历史资源样本，本轮不声称新测资源。原进程均已退出，无需恢复长任务。
