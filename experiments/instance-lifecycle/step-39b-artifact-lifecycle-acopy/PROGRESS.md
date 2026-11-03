# Step-39B 已完成

基线0dd9f76e；experiment/step39b-artifact-lifecycle-acopy。

1. 审计及独立工作树完成；Go1.24.1 reachable padding、P0、C0及原native SHA核实，未重编Guest。
2. 单一Manager有界缓存治理完成：8项/64MiB、满拒绝、Reset清理、Stop关闭、prepare失败条件删除；原Owner不改。
3. 实际VM生命周期、自然GC可回收、读并发Race、失败回滚、旧Runtime替换/Reset及Stop中真实buyNow6子调用通过。54条新生命周期check，另有继承身份拒绝/隔离新执行记录。
4. 四组12进程功能预检通过，逐字节初始Memory相等。
5. 3方法×4组×3批×2正式调用=72新正式调用；每进程2预热/2正式。另6诊断进程，不混入主统计。三批完整保存，未删反向样本。
6. 统计/中文报告/源码diff/精确编译时测试快照及资源校验完成。67个受监控进程已退出，60个native Owner计数配平，未触发守卫。

失败/准备纠正：首个诊断编译未用变量，保留build-diag.log；测试源码复制路径曾写错，diag-r2仍为旧测试文本，未用于性能或补充新检查。修正后用独立diag-r3/r4/r5标签，旧日志/二进制身份保留。没有覆盖失败现场。

复算：python3 scripts/analyze.py；python3 scripts/report.py；python3 scripts/finalize.py。不重复有效实验。

结论：有限VM范围生命周期闭环通过，建议下一轮有限节点Smoke/E2E，尚未运行节点。G2→G3三方法正向探索CI；G0→G1的hashCal CI跨零，保留不确定性。遵守原Owner32根调用预算、1536MiB/220线程，禁止自动扩样本。

本轮停止，等待确认；不启动Step-39C、不推送。初始截断消息的笔记保存在旧step-39b-sha-artifact-lifecycle目录（只读预审），正式成果以当前指定目录为准。
