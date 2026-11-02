# 结果导航与中文研究结论

8个独立业务合约、37个业务方法、四种配置、3个独立批次已完成；1728次有效正式提交，444个窗口。不是540次VM微基准，也没有复用任何历史性能样本。

- E2E_RESULTS.md：全部37行四组P50/P95、直接配对节省与95%CI。
- TPS_RESULTS.md：全部37行四组同步提交TPS。
- STATISTICS.csv：Mean/Median/P50/P95与逐批结果。
- PAIRED_EFFECTS.csv：直接配对、CI、正向比例、三批方向。
- TPS_STATISTICS.csv、TPS_EFFECTS.csv：TPS逐批/合并及三窗口对照。
- ORDER_EFFECTS.csv：先后顺序和首笔分层；3批无法充分分离顺序与批次，不能将信号称为完全消除顺序影响。
- NODE_STAGES.csv、VM_EVENTS.csv：实际关联的节点/VM阶段，不做跨进程绝对时间差。

Copy没有在全部方法上稳定改善端到端。hashCal、fact.saveAndFindByFileHash、erc721.symbol出现三批正向且CI全正的初步信号；erc721.mint出现三批负向且CI全负信号；其余多数CI跨零。A+Copy相对Fresh的局部正向信号为identity.addWriteList、erc721.mint2、hashCal；erc721.balanceOf为反向信号。A+Copy相对Copy仅fact.save出现CI全正，erc721.symbol为CI全负，其余不确定。所有上述信号均未作多重检验校正，不能作为普遍或论文级确定结论。

真实buyNow完成六次真实下游，A+Copy对Fresh配对中位节省11.154ms、CI[-5.623,28.093]ms，不能称为稳定收益。normalCal同样不确定，没有删除这两类负向/波动样本。

本轮已足以作为组会的有限真实节点阶段性证据：能安全执行、能确认提交、能直接复算，VM收益不能自动传递为普遍E2E收益。论文中仍需更充分独立重复、尾延迟样本、日志扰动评估和外部环境复验；本轮不自动扩大样本、并发或多节点研究。
