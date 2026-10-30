# 同源构建与实现

分支experiment/step32-all-contracts-acopy-matrix，父29950ab1（Step28）。Host Go1.25.0、Guest Go1.24.1、SDK0.1.3完整API、ChainMaker2.4.0、native6.0.1 SHA dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9，max512页、原Gas配置保持。四组均Fresh，不复用业务Instance；Module缓存/Store架构不随组改变。

audit/variants.csv及inputs/variants.json列出最终二进制hash与历史来源。G0/G2原WASM逐字节相同；G1/G3同A布局WASM逐字节相同。A-only直接使用既有A原WASM并关闭Copy，不重写A；Copy使用同一prepareStaticMemory/noData/restore路径，恢复在WASI.Initialize/_start前。A是链接期可达静态padding，非initial memory128页；历史首次arena对齐诊断在Step18/28，不将旧计时并入本轮。

新source/vm仅改实验driver为四组、允许有界分进程，以及在cache_closed输出已成功关闭的Store/Module scope数量（在Invoke外）。不改生产VM/Gas/managed守卫。scope计数不是native StoreRef泄漏检测；owner pending0和进程退出作为本轮有界终点。编译argv/build1-outcome/environment逐文件SHA保留。初次准备发现IDE镜像省略native.so，尚未运行Guest；改从当前CVW已冻结同hash库复制到新实验目录，无版本替换，记录audit/initial-preparation.txt。

只读历史审计：Step18恢复A/P0家族；Step22建立cached Module安全串行Copy；24B提供原件参照但不混入；25包含B1不用于本轮；26仅复算旧样本；27证实Guest波动和同Store协议边界；28提供六方法真实夹具；29说明buyNow子窗口/字节码克隆处于root export；30没有新E2E。对应报告hash见audit/history-manifest.json。
