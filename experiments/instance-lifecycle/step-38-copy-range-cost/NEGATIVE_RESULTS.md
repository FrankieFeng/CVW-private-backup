# 负向、失败与未完成边界

1. C2≤64B和C3≤256B明显减少区间，却没有任何restore对照CI全正；部分方法CI全负。完整表保留C1/C2/C3/C4慢样本与batch反向。
2. buyNow单span对C0的Factory Invoke配对中位-4.868ms、CI[-5.826,-2.670]；根restore方向不确定，不把反向结果删掉或归成已证实缓存问题。
3. B校准fact出现额外完整Invoke成本；分窗只是诊断，不作为无扰动基准。SHA与WASI相对Store的量级差大，但不能把全部插桩差归成已定位机制。
4. 首次build-A因独立module依赖版本未缓存且GOPROXY=off失败。保留audit/build-A.log；后用Step36现有node模块依赖图工作空间构建A2/B，没有下载/升级依赖或修改原node go.mod。
5. 首次memory-A缺CM_STEP21A_POOL配置，在Go init guard panic，退出2；没有进入Native Owner。修正环境后用memory-A-r1运行成功，原文件不覆盖。唯一失败进程不混入正式性能。
6. 新增负对照确认非Fresh脏洞不会被restore清理。当前所有正式调用构造新的Store/Instance；没有把不适用目标偷偷清零后当作通过。
7. 本轮没有同字节量、仅改变range个数的正交对照，故不能量化“纯loop vs纯字节流量”各占多少。coalescing同时改变二者，不能强行分摊。
8. 3批×每批2笔，P95只是小样本插值；cluster翻转最小p=.25，80项事后Holm敏感性不显著。CI跨零表示不确定，不是无效/等效证明。
9. VM夹具BlockVersion1、gasUsed0、公开测试成员和内存账本不同于真实节点；不直接对比Step36绝对Gas/完整Invoke/客户端TPS。真实Table身份、全部业务异常、native每阶段allocation、长期资源收敛未验证。
