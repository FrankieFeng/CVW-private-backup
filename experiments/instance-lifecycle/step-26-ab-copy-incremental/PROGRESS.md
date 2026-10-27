# Step-26 可恢复进度
2026-10-27。独立分支experiment/step26-ab-copy-incremental，父be88d9a。
当前：构建审计、原样本配对复核、统计与报告完成；新增Guest/编译0，无动态计划。以下保留原进度。
现有Step25三条所需直接边：oldG1→oldG2、oldG2→oldG4、oldG1→oldG4；各方法18对/3批/9进程。Step26 G3=Step25 G4，保留原标识不改raw。
原24B匹配A/B1构建仍待核实；zip候选hash不同，不能当恢复。优先复用已有有效样本，若输入/账本/Gas/进程证明失败再决定是否需新预检。本轮不制作PPT，不改变生产、不push。
下一步：冻结来源、逐raw receipt/command/profile交叉检查，再复算CI和顺序分层。

## 已完成：构建来源与提取
Step24B匹配A/B1未可靠恢复；只恢复Step18已有同源plain产物及原SDK/padding补丁，不重写旧构建。zip候选不匹配原件；现有通用instrumenter与build.sh无法唯一绑定原件计费构建。BINARY_LINEAGE和实际反汇编重新核实100 vs10000循环，跨家族相同TxID/输入/初始账本仍有不同Gas；未推定具体插桩根因。
三条指定边及对应预检按预登记条件提取：81正式process/162对，15预检process/15对。保留原编号、raw bytes和原提交manifest SHA；ALL_STEP25_RUNS列出原全部347个过程/提取理由，无性能方向筛选，原源实验无失败进程。

## 已完成：复算和交叉核验
已执行（均无Guest）：scripts/extract.py、scripts/lineage.py、scripts/analyze.py、scripts/report.py、scripts/verify.py。
直接差中位数/总体CI/P95与Step25一致；顺序/阶段复算也一致。最初verify字段别名把旧paired_median_ms与新paired_saving_median_ms误作同名，已修正核验器后通过；没有改样本/统计值，也不是VM测试失败。
全部177配对业务/返回/Gas/根RWSet/事件/账本对照通过；初始账本每方法只有一个hash；fresh唯一ID、created=closed、owner managed/pending0、原PID/cgroup退出均复核。9总体CI全部正、原3批中位数全正；7/36顺序分层CI跨零，不认证顺序无关。Module准备顺序3/6或6/3进程，明确不是完全平衡。
来源/source/template/cache key、Code和binary SHA与原MATRIX对应，资源数据明确为复用的原样本；无新增VM资源记录，无Table/异常/并发/节点PASS。

## 交付与恢复
README、RESULTS、BUILD_LINEAGE、CORRECTNESS、MATRIX、TIMING、PAIRED_SAMPLES/EFFECTS、BATCH/ORDER/STAGE、RESOURCE/MODULE_PREPARATION、原日志及所有脚本已生成。不制作PPT。
下一条可执行命令仅为python3 -B scripts/verify.py或analyze.py→report.py，完全离线；不应重复启动任何历史Guest命令。无动态阻塞等待。原件匹配构建与未测安全项列为限制，不用新猜测替代。
正在本实验独立分支提交、IDE同步；不push、不覆盖历史。新增独立批次0，不能把复算当成新时间维度重复验证。
