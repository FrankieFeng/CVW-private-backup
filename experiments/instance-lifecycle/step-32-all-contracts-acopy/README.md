# Step-32：A / Copy / A+Copy全方法四组评估

独立分支experiment/step32-all-contracts-acopy-matrix，父Step28 29950ab1。只使用既有受控串行Fresh协议，不修改生产VM、不加入B1/新Store架构、不运行节点/E2E、不推送、不制作PPT。

本轮实际完成180正式四组block、720根调用；每方法见RESULTS，不把预检/异常/下游重复算为根样本。新数据未与旧批次拼接。六重点方法均预检通过；其他候选合约及未纳入原因见CONTRACT_INVENTORY.csv。

| 方法 | N/组 | 批 | Fresh Median/P95 | A Median/P95 | Copy Median/P95 | A+Copy Median/P95 |
| --- | --- | --- | --- | --- | --- | --- |
| compute.bigNumCal | 30 | 3 | 17.991 / 19.778 | 16.912 / 20.470 | 17.135 / 19.825 | 16.509 / 18.711 |
| compute.hashCal | 30 | 3 | 8.047 / 9.751 | 6.951 / 7.913 | 7.445 / 8.234 | 6.613 / 7.520 |
| compute.normalCal | 30 | 3 | 78.309 / 83.434 | 78.407 / 84.054 | 78.298 / 82.461 | 76.478 / 81.995 |
| fact.saveAndFindByFileHash | 30 | 3 | 4.412 / 5.040 | 3.760 / 5.025 | 4.107 / 5.335 | 3.191 / 3.775 |
| erc721.mint | 30 | 3 | 4.539 / 5.777 | 3.910 / 4.940 | 4.057 / 5.018 | 3.348 / 4.117 |
| exchange.buyNow | 30 | 3 | 61.002 / 76.370 | 48.430 / 66.044 | 63.142 / 75.945 | 57.004 / 68.097 |


完整直接收益、CI、批次、顺序与阶段见[RESULTS](RESULTS.md)。交互原公式的符号与“额外收益”相反，两个方向同时保留INTERACTION_ANALYSIS.csv，不强行标所有组合有效。资源/业务/Gas与限制见CORRECTNESS.md。

## 复现和恢复

在独立worktree的本目录执行：

```bash
python3 scripts/experiment.py preflight
python3 scripts/experiment.py formal
python3 scripts/analyze.py
python3 scripts/report.py
python3 scripts/verify.py
```

有outcome/有效block时跳过，不覆盖；存在STOP或日志无outcome时先读PROGRESS和实际unit，禁止重复启动。准备WASM为同源冻结产物，不需要重编Guest；SHA见audit/variants.csv。Host完整build argv/build1-outcome/environment保留；脚本有本机绝对路径，迁移机器须登记新配置，不能直接宣称精确复现。

回退：等自有unit结束，离开本worktree即可；生产没有改动。保留所有历史与本轮数据，无远程推送。原始模块/模板/计时/回执/资源日志均在raw_logs，TIMING含初始化、预检、异常、root/child及valid_block标识。

主要判断：hash/fact/ERC的组合及增量较稳定；bigNum/normal组合对Fresh正向但增量未确认；buyNow A-only有收益、组合对Fresh未确认，Copy叠到A反向。交互CI均跨零。完整证据/限制见RESULTS。
