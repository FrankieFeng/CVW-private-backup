# 统计与执行预登记（正式数据前）

主矩阵：G0 baseline、G1 C、G2 A+C、G3 历史GetBatchState/PB裁剪+C、G4 A+同一PB补丁+C。只用Step18已构建同源plain，各P重新算A的旧产物，不临时改负载。compute大数10000轮，与24B100轮不可混比；normalCal仍10000000。SDK裁剪只限已覆盖API，不生产兼容。

预检：每case四条G0→G1/G2/G3/G4；每新逻辑WASM G2/G3/G4另做Copy off/on以验证同WASM Gas和S1；每进程一对。任何失败保留STOP，不扩大。先三优先case，正常后才normal。

正式直接对照8条：(G0,G1),(G0,G2),(G0,G3),(G0,G4),(G1,G2),(G1,G3),(G1,G4),(G2,G4)。每条每case3独立批，每批3独立进程×2对=6对，共18对/9进程。所有进程串行，每角色独立Store/Module，最多真实init+2正式Instance，不改变guard/线程/RSS预算。对内交替，Module准备/init顺序按进程交替；批2倒转边和合约顺序，所有样本保留。

完整Invoke沿24B入口到per-Instance defer关闭结束，Module/template/init/账本clone/receipt日志及末尾缓存清理另列。新增exportFunc.Call读取沿用已有B5计时；Go heap在完整Invoke外采样。A0/A1仅本进程左右角色，不代表是否开启Copy；明确doCopy bool决定模块变换/恢复。模板按最终WASM解析，Key绑定WASM/配置/版本，非Data语义不改。

主指标 left.Invoke−right.Invoke 的逐对差中位数；95%CI用预固定seed250027、10000次batch→process聚类bootstrap，保留每个进程2对作为整体。P95采用线性分位数。正向比例按pair计，但18对只有9个独立进程和3批，不当18个独立机器实验。各批/执行先后/Module先后分层另列。多重比较不校正，筛选证据，不做全三因素交互或生产认证。

主PPT每优化组用对应G0直接对照，展示该边实际Baseline/优化分位数、CI、N和批数。增量另用各自独立的直接边，不用前两条配对差的Median相减。不同边绝对中位数不相加。若CI跨零或跨批方向不一致，写证据不足/不稳定；即使正也仅本串行范围。
