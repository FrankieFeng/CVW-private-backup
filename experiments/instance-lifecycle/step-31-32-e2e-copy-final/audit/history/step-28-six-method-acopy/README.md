# Step-28：六方法A+Copy独立收益确认

本轮已完成六方法功能预检、3批×10个三组配对区块/方法：**180区块、540次正式根调用**，另有buyNow的540次真实下游业务执行，未混入历史样本。所有有效区块完成Gas/结果/读写集/事件/完整最终账本对照；buyNow包含六次真实子调用。详细数据与限制见[RESULTS](RESULTS.md)、[CORRECTNESS](CORRECTNESS.md)、[构建来源](BUILD_LINEAGE.md)。

| 方法 | Copy相对Fresh | A叠加Copy | A+Copy相对Fresh |
|---|---|---|---|
| compute.bigNumCal | 0.072ms；CI跨零，未确认稳定收益 | 0.478ms；CI跨零，未确认稳定收益 | 0.696ms；CI跨零，未确认稳定收益 |
| compute.hashCal | 0.958ms；三批同向、总体CI>0 | 0.792ms；三批同向、总体CI>0 | 1.625ms；三批同向、总体CI>0 |
| compute.normalCal | 0.946ms；CI跨零，未确认稳定收益 | 0.869ms；CI跨零，未确认稳定收益 | 1.153ms；三批同向、总体CI>0 |
| fact.saveAndFindByFileHash | 0.580ms；三批同向、总体CI>0 | 0.802ms；三批同向、总体CI>0 | 1.465ms；三批同向、总体CI>0 |
| erc721.mint | 0.768ms；三批同向、总体CI>0 | 0.819ms；三批同向、总体CI>0 | 1.450ms；三批同向、总体CI>0 |
| exchange.buyNow | -2.870ms；CI跨零，未确认稳定收益 | 5.077ms；三批同向、总体CI>0 | -0.058ms；CI跨零，未确认稳定收益 |

正值为优化组节省，直接配对统计，非独立中位数相减。30区块/方法，只有3个时间批；短期单机串行证据，不是节点并发或生产收益。normalCal/buyNow不利样本全部保留。

运行：先检查PROGRESS/state/outcome及活跃unit，再按BUILD_LINEAGE命令恢复；`python3 -B scripts/analyze.py`、`python3 -B scripts/report.py`、`python3 -B scripts/children.py`、`python3 -B scripts/verify.py`可只读原始测量复算汇总。不要删除outcome重跑后覆盖原记录。

回滚：本实验仅改本目录副本/独立分支，无生产开关需回退。停止具体`step28-<label>.service`并核对PID/cgroup为空；保留日志，切回原分支即可。禁止通配杀其他实验进程。不推送远程、不制作PPT。

交付：TIMING.csv包括init/preflight/正式/异常及children，`phase`、`depth`、`valid_block`区分；主表仅formal+depth0+目标方法+完整有效区块。SUMMARY、PAIRED_EFFECTS、STRATIFIED_EFFECTS、STAGE_EFFECTS、MODULE_PREPARATION、RESOURCE_SUMMARY及原始日志完整保留。PROGRESS注明失败构建，性能样本没有静默排除。
