# CVW-SHA-NEGATIVE-5：历史负优化方法快速补测

已完成，停止，不自动扩展到37方法。完整五组VM/E2E/P95/TPS表、匹配效应和三条组会结论在RESULTS.md。

- 使用Step-39E原node-ready、client3二进制及全链就绪协议，没有重新编译或修改节点/VM/native。节点源码c6382c3；Host Go1.25.0，Guest为冻结Go1.24.1 plain/A padding，Selector库SHA56b236ce1772b805819aec7c10eb417cd62bf0c6ee2c9b581e651f746bec17dc。
- 五组主实验345笔；预检25笔；为补足raffle主对照相对顺序的6笔反序单列。每方法三独立批次，普通方法每组15笔，raffle每组9笔；全部保留。启动屏障实际组件完成、消费者配平、双ACK及真实SDK提交探针，不增加Sleep/不改共识。
- callerAddress真实执行一次identity.address子调用；raffle保持原3人/3次抽奖。ERC721合法mint(tokenId1)在窗口前完成。identity真实target probe、ERC/raffle首笔真实setup作为提交探针；Query预热不写入账本。
- SHA方案仅G4启用39B摘要缓存，保留输入SHA和Runtime Clone；Copy固定C0，A-only使用同一Arena二进制但关闭Host Copy。inputs/variants.json含旧Step-36组号字段，本轮组义以inputs/variants-control.json和实际node argv为准。G2/G3/G4的A Guest相同，不把旧产物名G2误当本轮Copy开关。
- 配对单位为3个匹配批次窗口Mean差；同节点TxID连接VM/SDK，不跨Node拼接逐笔数据。独立组P50差值单列，不能替代配对效应。
- 五方法VM SHA增量主三批均正；最终组合对Fresh E2E为三例初步支持、两例CI跨零。SHA E2E独立增量并非普遍有效；raffle反序E2E回退0.793ms，完整结果如实保留。

## 复算

```sh
python3 scripts/analyze.py
python3 scripts/report.py
```

只读取raw_logs并重建派生表。E2E_RESULTS.csv、VM_RESULTS.csv含phase=formal/pre/ordercheck；主性能必须筛formal（345行），不混入预检或6笔反序。SUMMARY/WINDOWS含Mean/P50/P95/TPS；PAIRED_EFFECTS含3批效应、CI、正向比例和独立P50差值；ORDER_CHECK/ORDER_EFFECTS保留顺序复核。

实际执行命令、二进制/源码/Guest/配置身份在audit；六个部署seed和每个节点的SDK原始JSONL、VM日志、提交收据、状态读回及资源退出在raw_logs。失败的初始配置路径准备保留为seed-identity-plain，未启动节点或发送交易；修正后使用新seed-v1目录，不覆盖其现场。

所有节点资源配平，原1536MiB/220线程/32根预算不变；详见RESOURCE_SUMMARY.md、CORRECTNESS.md。历史36/37负值只存在audit/historical-negative5.md参照，不填充本轮统计。未推送远程。
