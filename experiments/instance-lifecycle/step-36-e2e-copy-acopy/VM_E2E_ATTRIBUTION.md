# VM 与端到端收益

| 方法 | Copy VM节省 | Copy E2E节省 | A+Copy VM节省 | A+Copy E2E节省 |
|---|---:|---:|---:|---:|
| bigInput.inputSize | 0.078 | -1.702 | 0.673 | 3.931 |
| bigInput.inputSizeMulti | -0.114 | 1.839 | 0.836 | 0.690 |
| bigInput.ioHeavy | -0.221 | 0.922 | 0.249 | 2.678 |
| identity.addWriteList | 0.901 | 5.487 | 1.474 | 4.950 |
| identity.alterAdminAddress | -0.363 | -0.217 | 1.355 | 7.208 |
| identity.removeWriteList | 0.368 | 0.044 | 2.697 | -2.478 |
| identity.isApprovedUser | 1.409 | 2.786 | 2.513 | 3.336 |
| identity.address | 0.422 | -2.587 | 1.189 | -4.326 |
| itinerary.save | 0.242 | -0.478 | 0.945 | 2.164 |
| itinerary.queryHistory | 4.407 | 10.971 | 3.312 | 4.571 |
| itinerary.saveAndQueryHistory | 0.965 | 1.873 | 0.528 | -6.442 |
| raffle.registerAll | 0.885 | 4.526 | 0.800 | 1.933 |
| raffle.query | 1.652 | -0.390 | 1.725 | 5.282 |
| raffle.raffle | 0.589 | -1.710 | -0.281 | -4.872 |
| raffle.registRaffle | 1.250 | -2.049 | 0.666 | 1.605 |
| fact.save | 0.667 | -5.286 | 1.351 | 2.206 |
| fact.findByFileHash | -0.171 | -2.808 | 0.296 | -0.344 |
| erc721.balanceOf | 0.521 | -3.209 | 0.634 | -5.281 |
| erc721.ownerOf | 0.818 | -1.146 | 1.523 | 1.364 |
| erc721.getApproved | 0.584 | 2.477 | 1.321 | -1.287 |
| erc721.tokenURI | 0.388 | 1.765 | -0.289 | -3.117 |
| erc721.tokenMetadata | 0.753 | 1.779 | 1.077 | 0.679 |
| erc721.accountTokens | 1.985 | 0.475 | 2.652 | 1.473 |
| erc721.tokenLatestTxInfo | 0.290 | -3.155 | 0.964 | -3.151 |
| erc721.name | 0.831 | 0.882 | 1.278 | 2.074 |
| erc721.symbol | 0.518 | 2.888 | 1.507 | -3.091 |
| erc721.setApprovalForAll2 | -0.934 | 1.177 | 1.220 | 4.911 |
| erc721.approve | 0.439 | 0.770 | 0.571 | -3.563 |
| erc721.transferFrom | -1.223 | 0.288 | 0.986 | 2.958 |
| erc721.mint2 | 0.324 | -0.138 | 2.250 | 6.094 |
| compute.bigNumCal | 0.105 | -0.451 | 0.266 | -0.276 |
| compute.hashCal | 0.491 | 2.325 | 2.525 | 3.900 |
| compute.normalCal | -2.050 | -0.133 | 2.361 | -0.240 |
| fact.saveAndFindByFileHash | 0.016 | 2.324 | 0.822 | 2.306 |
| erc721.mint | 0.926 | -5.643 | 1.466 | 3.418 |
| exchange.buyNow | 5.300 | 2.310 | 8.791 | 11.154 |
| identity.callerAddress | 0.858 | -1.534 | 1.969 | -1.995 |

VM列为同一TxID全部根invoke_end单调计时之和的配对节省；E2E为SDK窗口。1728笔中1584笔观察到1次根执行，144笔观察到2次：erc721.accountTokens、itinerary.queryHistory、itinerary.saveAndQueryHistory各48笔。不能把这些交易只算一次VM执行；没有仅凭计数判定重执行原因。buyNow每次观察到六次真实下游调用，子调用嵌套于根Invoke，未重复加到根时长。

NewInstance、Copy、_start、S0→S1、CallMethod、Close原始分段见VM_EVENTS.csv；NewInstance不含随后Copy，S0→S1包含创建Store、WASI/import、NewInstance与Copy，_start和Close嵌于完整Invoke。首次Module准备含模板/编译，单列MODULE_PREPARATION.csv，正式前Query已加载缓存，但每次业务仍创建独立Instance。

本轮VM节省并未普遍转化为稳定客户端收益；多数E2E CI跨零。PutBlock、RPC通知、排队及其他宿主开销位于真实路径内，但本轮没有对全部VM外耗时作无重叠的细分，不能认定某个组件是负收益根因。禁止跨进程绝对时间直接相减。外层REUSE_VM日志使用UnixNano，保留其墙钟局限；Owner内部与客户端分别使用本进程单调时钟。

保留既有诊断日志（含ReadMemStats）；各组相同，但其扰动未单独量化，本结果不是低插桩生产基准。

## 额外可测量窗口（已有事件复算）

NODE_STAGES.csv逐笔用同一节点的CLOCK_MONOTONIC记录关联RPC TxID及PutBlock区块高度，1728笔全部匹配。全体样本仅作窗口量级描述：PutBlock中位16.710ms、PutBlock结束至RPC处理结束中位0.170ms、RPC处理开始至首次VM事件中位28.899ms；这些跨方法汇总不是某一组的优化收益或因果估计。节点事件边界含ReadMemStats/日志开销，不能当作纯队列等待。

分段配对证据：A叠加到Copy后37/37方法的`_start`节省CI全正，但完整Owner Invoke只有9/37的CI全正，客户端仅1/37。Copy相对Fresh的完整Owner Invoke6/37 CI全正，客户端3/37。说明本轮可以测得部分VM窗口改善，却不足以证明普遍的E2E改善；不能把剩余方法均写成优化无效或确定退化。

未归因的VM外窗口、诊断日志扰动和三批环境/顺序影响仍存在。没有进行WASM克隆内部机制研究；字节码/宿主准备在真实路径中保留，不额外设计优化。
