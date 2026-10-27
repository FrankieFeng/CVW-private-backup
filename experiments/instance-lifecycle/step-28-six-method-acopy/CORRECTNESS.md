# Step-28正确性与边界

六方法三组均完成新的功能预检；每个正式三组区块逐对严格比较根Gas、返回值、状态码、完整根读写集、事件、初始/最终账本摘要。对buyNow还对root和六个真实子调用逐次核对contract/method/order/depth/TxID/Gas/code/result/message，不能仅凭Go测试PASS判成功。

| 方法 | 有效正式区块 | 独立批 | 根Gas（三组一致） | 真实调用/根交易 |
|---|---:|---:|---:|---:|
| compute.bigNumCal | 30 | 3 | 120027 | 1 |
| compute.hashCal | 30 | 3 | 120019 | 1 |
| compute.normalCal | 30 | 3 | 100000019 | 1 |
| fact.saveAndFindByFileHash | 30 | 3 | 154 | 1 |
| erc721.mint | 30 | 3 | 235 | 1 |
| exchange.buyNow | 30 | 3 | 12612158 | 7 |

每次完整账本另存`raw_logs/*-receipts/target-Gx-ledger.json`：由实际init/目标RW写集重放，并逐阶段复核进程内snapshot.hash()的SHA256；CHAIN_CONFIG值直接取真实setup-identity读集，非手填。三组重建的完整最终账本逐键/值相等。未成功的交易不提交写集。原始回执包含返回bytes(base64)、所有读写、事件和根/子调用记录，保留可复核数据。

## buyNow真实与失败路径

init顺序identity→ERC721→exchange；真实调用顺序exchange.buyNow→identity.addWriteList→identity.isApprovedUser(from)→identity.isApprovedUser(to)→erc721.mint→erc721.setApprovalForAll2→erc721.transferFrom。每次新建目标token1的等价初始账本，验证最终owner=to和buyNow success。G2对root、identity和ERC721全部应用各自A+Copy。

空参数在root拒绝；重复token预置已有owner，使第4个子调用mint失败，此前identity写入不得提交。两条路径每组三个独立进程之一，各G0/G1/G2一次，均真实运行并核对Gas/结果/读写/事件/最终账本。它们是小样本功能证据，不是覆盖所有异常。
- empty：三组根Gas 142、root+child调用数1，失败且最终账本等于初始；原始对照通过。
- duplicate：三组根Gas 3002833、root+child调用数5，失败且最终账本等于初始；原始对照通过。

## 不得标为通过的范围

- 真实Table元素函数身份：**not_tested**。Data变换保留Table/element字节与成功间接调用，不等于逐元素身份验证。
- 所有其他业务异常、深层trap、Gas耗尽、节点级回滚、共识/持久化/签名：**not_tested**。夹具使用公钥身份/真实VM状态，并非完整节点认证。
- 实例隔离：已验证每次fresh、uses_before=0、同步销毁、S1预检与各自静态模板一致、每次账本独立克隆；未做同时存活实例互写Memory压力测试，不把它标为本轮已通过。
- Store owner/生命周期：本轮有界串行guard与回收计数通过；长期Store内WASI线程/native资源完全回收仍未证明，不称生产安全。
- A跨二进制Gas不是默认假设，本轮实测三组及所有下游一致。B1未纳入，公共API未删除。
