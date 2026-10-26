# 实际验证与可复现边界

12个独立进程，全部退出0、owner登记0、单owner_tid、停止后MainPID0；详见[processes.csv](processes.csv)、[verification.json](verification.json)。没有并发Fresh、Copy、Arena/PB、100次或生产VM修改。

| 独立场景 | 执行量 | 结果 |
|---|---|---|
| fact只读Gas探针开/关 | 各init1＋目标1 | Gas1585，输入/账本/RWSet/事件/结果一致 |
| normal安全预检 | R0预热1＋R0/R1各1 | 正确结果/Gas、全部bundle回收 |
| Module能力 | 同Module两Instance＋独立目标Store反序列化Instance | 三次实际answer=42，可信产物3888字节，回收完成 |
| fact固定初态 | 两模式各init1＋目标3 | Gas冷/热差594，业务语义相同 |
| ERC721固定初态 | 两模式各init1＋目标3 | Gas冷/热差4379，业务语义相同 |
| 真实exchange.buyNow | 两模式各init3＋根1＋子6 | 每次六callee全部真实VM执行，首次Gas分歧第6次 |
| normal交替顺序 | 两进程各R0预热1＋测量6 | 每模式每批3次，固定输出/Gas，尚未解释小幅时延差 |

试验前登记见[PLAN](PLAN.md)，两次构建日志/退出在audit/build-01/02-*。前3个预检进程使用build01，其余使用追加Module入口后的build02；各command.json保存实际binary SHA256。相关probe及normal逻辑两版本一致。不同历史attempt不覆盖，本轮无失败guest进程；分析脚本开发时的路径/窗口断言失败仅是离线分析错误，修正后从既有日志重算，没有为此重跑guest。

沿用保护：cgroup MemoryMax2GiB/Tasks256，进程60秒/Go45秒，监控RSS1536MiB、Threads220、MemAvailable至少8GiB、SwapUsed至多1GiB。监控每约20ms采样；峰值为采样值，可能漏掉短瞬态。最高本轮采样750.85MiB/74线程，硬限未触发。每进程command、launch、resource JSONL、log、outcome及receipt完整保存；native失败只能进程隔离，不能声称可被Go recover修复。

执行环境见[audit/runtime-artifacts.json](audit/runtime-artifacts.json)。复现入口：

```bash
# 在本目录，先读PROGRESS、已有outcome及unit，禁止覆盖label或直接重复尝试。
python3 scripts/build.py build-NEW
python3 scripts/run.py NEW Gas R1 fact 1
# 离线重算全部已保存证据，不运行guest
python3 scripts/analyze.py
```

build使用离线已有Go依赖、GOWORK和固定packaged so。native库与test ELF不入Git；在新机器必须取得相同hash库、相同WASM/输入与依赖，将go.work、go.mod/manifest的本机绝对路径明确重定位，再构建。不能从缺库状态自动下载“最新版”代替。具体本次命令已在每个command.json中，主机现有路径可直接复核。预登记的完整短矩阵已经完成，示例命令不是要求额外测试。

这一验证建立的是**固定owner、有限预算、独立进程的功能诊断环境**。单Store并行仍禁止；不同Store并行及长期连续100次没有放行。Native内部WASI线程/allocator是否能长期平稳回收，不能由Go wrapper登记归零、一次GC或进程成功退出证明。
