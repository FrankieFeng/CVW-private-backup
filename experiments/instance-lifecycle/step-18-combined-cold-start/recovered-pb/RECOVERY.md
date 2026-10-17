# PB 裁剪恢复审计（2026-10-18）

历史记录确实留存。此前只检查工作区、Git和源码文件名，未追到历史会话里的具体补丁，因此“无法恢复”的判断过早。本次修正为：临时源码目录当前不存在，但可从原实验会话恢复补丁和构建命令。

证据链：

1. `pb-trim-artifacts/trimmed/compute-go.wasm` 的内嵌构建信息含 `github.com/TKOTKCh/contract-sdk-go-wasm => /tmp/contract-sdk-go-wasm-pb-trim (devel)`。
2. `/home/frankie/.codex/sessions/2026/09/25/rollout-2026-09-25T23-20-38-01a0d927-7b11-7180-ac0a-9cccbdc15c03.jsonl` 第1181行创建该SDK副本，第1188行保存完整SDK补丁；第1640行再次恢复SDK补丁及Go诊断插桩；第1649行构建持久化的四合约original/trimmed WASM。选定证据和历史文件SHA见 `recovery-evidence.json`。
3. SDK0.1.3缓存与原下载zip逐文件一致。恢复只在本目录 `sdk/` 私有副本上应用原补丁，原module cache、Go和ChainMaker生产文件不改。补丁原文 `original-sdk-patch.txt`，可审查统一diff `sdk.diff`，可重复恢复脚本 `restore.py`。
4. 旧构建使用Go1.24.1的独立B1诊断工具链、`-trimpath`，前四个合约来自 `b-probe/contracts/*.go`，其余四个来自原合约源文件。历史WASM是诊断产物，不能直接当成本次plain组合产物；本次使用原版Go1.24.1重新构建，A/B1诊断另做副本。
5. 第1476行保存八合约各192对的历史汇总输出，已提取为 `historical-eight-contract-summary.txt`。原始JSONL当时在 `/tmp/b1-pb-real/paired-*`，当前本机未找回；不能把恢复的汇总冒充原始样本，不能确认临时目录消失的原因。

## 补丁的真实语义

它删除 `sdk/chainmaker.go` 的 PB import、`SimContext.GetBatchState` 接口方法、`SimContextImpl.GetBatchState` 实现及 `batchKeysLimit`，而不是保留完整SDK API的透明裁剪。删除后，目标合约的实际编译依赖不再包含pb-go/gogo-protobuf；SDK go.mod中原有间接require不做升级/改写。

8个现有合约源码未发现GetBatchState/BatchKey引用，全部P1构建成功，逐合约依赖清单和源码检查见 `eight_contract_build_checks.csv`。这是构建/直接引用兼容性检查，不是八合约的业务安全认证。使用该API、依赖SDK反射方法集合或其他未覆盖行为的合约不能无条件使用P1。

## 本次补测

在既有step-18独立worktree恢复同一P，不换成新SDK实现。对每个P0/P1分别校准A、生成最终WASM、重算C模板、独立首次编译/Serialize；三合约完整8组各40次，plain和probe独立采样。原4组pilot及blocked记录保留，完整8组用新批次内的配对比较，绝不拼接旧4组时序。

新报告在step-18根目录和 `full-pilot/`，P=1的当前状态已从blocked更新为built及tested_scope_pass（限已覆盖路径）。Table真实身份、真实跨合约、全部trap/OOG仍not_tested，所有组合safe均未认证。
