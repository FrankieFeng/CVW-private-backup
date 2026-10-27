# Step-26：A+Copy及A+B1+Copy增量确认

分支`experiment/step26-ab-copy-incremental`，父Step25 `be88d9a`。**本轮只审计和复算已有有效数据，新增VM/Guest运行0、编译0、新独立批次0；没有制作PPT。** 没有为了达到30对而重复已有实验，不修改生产VM/Gas/合约，不推送。

## 结论

- Step24B原件的匹配A/B1构建未可靠恢复，blocked。Step18同源plain产物、补丁、构建记录和SHA可恢复，沿此家族内比较；没有将原件的时间/Gas混入。
- A叠加到Copy：compute/fact/ERC分别直接节省0.711/0.957/0.966ms，总体95%CI均为正，原3批中位数均为正。
- B1在A+Copy上：分别直接节省1.090/0.328/0.498ms，总体CI均为正，原3批中位数均为正。
- 完整组合相对Copy：分别直接节省1.799/1.128/1.089ms，原3批和已采样顺序分层均为正。
- 这是原Step25协议下的跨批支持，不是新增重复验证。compute/fact部分顺序分层CI跨零，不能写成不受顺序影响或所有环境下稳定。
- B1仍删除GetBatchState公共API。完整组合在这里更快，但保留SDK接口的A+Copy更适合优先继续；B1仅作明确适用条件下的研究候选。数据不足以认证生产或原池并发节点收益。

详细数值、P95、CI、正向比例、每批/顺序及阶段见[RESULTS.md](RESULTS.md)；构建来源与API限制见[BUILD_LINEAGE.md](BUILD_LINEAGE.md)；正确性见[CORRECTNESS.md](CORRECTNESS.md)。

## 编号映射（避免混淆）

| Step26 | 实际配置 | Step25原编号 |
|---|---|---|
| G1 | Copy | G1 |
| G2 | A+Copy | G2 |
| G3 | A+B1+Copy | G4 |

原Step25 G3是“B1+Copy”，不等于本轮G3。raw_logs不改写旧编号；导出表同时保留old_left/old_right。MATRIX保存完整WASM/模板/执行Module哈希及原配置。

## 为什么不新增实验

原始日志、command、receipt及配对标识已经能构成三条直接边：oldG1→oldG2、oldG2→oldG4、oldG1→oldG4。每方法每边18对=原3批×6对=9个独立进程×2对，每process各角色真实init、同输入/TxID和相同init账本后Fresh执行。

本轮从raw sample与receipt重建，不直接抄summary。严格检查Gas/返回/实际根RWSet/事件/账本、call错误、fresh唯一ID、created=closed、owner清零及进程退出；重新计算CI/P95并与原汇总逐字段交叉核对，全部一致。原有15个相关功能/S1/Copy off-on预检也完整保留并复核。因此现有数据足以回答限定协议内的直接增量问题，无需为凑30对重复。它不能消除未来环境或顺序不确定性。

共保留81个原正式+15个相关预检进程、162正式配对及15预检配对。ALL_STEP25_RUNS清单记录原全部347进程及本次提取理由；未选择的原件参考、normalCal和其他边仍保存在不可变Step25提交，未删除或筛除反向时间样本。原347进程均成功，没有隐去失败组。所有来源文件以原提交manifest SHA校验，见audit/ORIGIN_FILES.csv。

## 数据和计时

TIMING逐样本保留NewInstance、Copy/字节/范围、_start、S0/S1/S2/S3、CallMethod/export.Call、Close/完整Invoke和对应资源；PAIRED_SAMPLES保留每对直接差。PAIRED_EFFECTS为配对差中位数及批次→process聚类bootstrap95%CI，不是两个独立Median相减。MODULE_PREPARATION单列一次性模板/Module准备及cache关闭，不放入目标Invoke。

宿主代码及环境与原Step25一致：Go1.25.0、Guest构建记录Go1.24.1、VM/protocol2.4.0、原native6.0.1；原binary/配置/源码hash见audit/original_step25/environment.json。Copy发生在noData实例化后、WASI.Initialize/_start前，无原Data重复初始化。当前是独立Store、固定owner的串行参考管理器，不是原池或真实客户端调用。

## 离线复算与恢复

```bash
cd /home/frankie/mygitprojects/.worktrees/cvw-step26/experiments/instance-lifecycle/step-26-ab-copy-incremental
python3 -B scripts/analyze.py
python3 -B scripts/report.py
```

以上仅用Python标准库读本目录冻结文件，不启动Guest/native运行时。`scripts/extract.py`重新核验/提取时需要父Step25目录与Git对象，已有文件逐字核对不覆盖；`scripts/lineage.py`只读wasm-validate/wasm-objdump和原仓库zip，需现有CVW材料，不能在缺源时伪造恢复。它们也不会构建或实例化。

中断先读PROGRESS与verification，不重新启动原测试命令。本轮无需任何动态恢复。回退为离开本分支/worktree即可，无生产服务或配置需回滚；不删除历史数据，不push。所有统计仅针对明确适用家族，未测项不标通过。
