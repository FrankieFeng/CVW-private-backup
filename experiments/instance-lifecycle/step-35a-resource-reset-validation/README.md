# Step-35A：节点资源收敛与Reset生命周期验证

**Reset/Stop阻塞已修正并通过节点验证；Step-36仍不准入，当前明确阻塞是固定native库的WASI线程回收。** 不启动正式Copy E2E矩阵。

基线 `experiment/step35-node-fresh-integration@c48cf907`。独立工作树 `.worktrees/cvw-step35a`，分支 `experiment/step35a-resource-reset-validation`。生产VM、历史数据、Guest、Gas、Go/Wasmer版本不变；native SHA仍为`dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9`。全程1536MiB软RSS/220线程，未提高上限。

已复用Step35的六轮24笔交易进行历史复算；新增仅14笔成功提交的compute/buyNow/Reset期间请求，以及1个在Stop中未确认提交的请求。不是重跑全功能或性能矩阵。新增6次buyNow均有真实六个下游；所有四个测试节点进程正常退出，Store/Instance配平，pending0。

| 本轮结论 | 证据 |
|---|---|
| RSS不能整体判泄漏 | Reset释放正常Module缓存；显式GC降低live heap；单独scavenging使已空闲Go页返回OS |
| 部分RSS来自allocator保留 | resource2 Reset后glibc仍有约380MiB free arena；free不等于已经归还OS |
| 线程未收敛，已定位到native/WASI创建关闭路径 | 24次WASI创建/删除配平后多24个epoll线程；Reset/GC/scavenge不清除 |
| 纯C排除Go/节点干扰 | Store-only四次后线程仍1；WASI四次后静默3s线程5，其中4个epoll；单次WASI残留1个epoll持续10s |
| 真节点Reset通过 |9次实际Manager Reset，含空闲、连续、compute和buyNow在途；后续交易正确提交 |
| Stop/Reset竞态已修复 |Stop改为等待正在进行的Reset完成；两个顺序unit测试和真实节点重叠Stop/Reset通过 |

源代码可直接阅读 `source/vm/step35a_control.go`（0600 Unix socket触发实际Manager）、`step34_owner.go`（最小Stop等待修正）、`wasmer-go/step35a_resources.go`（只读诊断，含固定ELF私有布局探针，禁止作为通用生产ABI）。完整diff在audit/source.diff。

RSS、线程和native剩余问题分别见RSS_ANALYSIS.md、THREAD_ANALYSIS.md、NATIVE_LIFECYCLE.md。Reset证据见RESET_TEST.md。报告不把句柄配平当作所有后台任务已关闭，也不把forced GC/scavenge当正常运行配置或准入条件。

现有native二进制Selector.shutdown反汇编与本地当前源码不一致，旧双waker实现是有证据支持的候选原因；未在本轮重编native或验证补丁，不能声称某个patch已解决。后续最小工作是固定native构建来源，在独立native实验分支验证Selector/WASI线程关闭修复；不继续修改Copy或提高资源阈值。

运行脚本拒绝覆盖旧日志/账本。网络账本由已正常停止的Step35小账本复制到`/tmp/cvw-step35a-diag`，未改存储配置；测试凭据仅存在/tmp，不打包私钥。native/binaries不入Git，使用已有固定库并校验SHA。无远程推送。
