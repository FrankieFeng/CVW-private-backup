# 正确性与安全边界

已验证：

- TestStep39Artifact（source/vm/step39_artifact_test.go:13）：拥有权Copy；调用方随后写源不改变内部内容/摘要；同version换内容失效；version/chain/config/contract隔离；8并发读者各20次核对。独立-race进程通过，仅限纯Go Artifact。
- TestStep39Reject（:69），A/B/C/D分别执行：错误字节、错误version在进入Owner前拒绝；没有用缓存绕过实际输入校验。
- TestStep39ModuleIdentity（:88）：合成小WAT同名同version不同内容分配不同Module；回到旧内容命中旧Module；Reset后清Module并重编译；native模块/Store全部释放。
- 12个真实业务预检进程：所有初始化后Memory逐字节与原Image一致，包含buyNow所有子Instance。旧Copy边界测试沿用Step-38，本轮没有改Ranges/restore。
- audit/parity-*.json比较四组及补充组的TxID、完整Result（含Gas/事件）、RWSet和初始/最终账本hash。全部相同；每个phase的所有调用层级Gas序列一致，见CHILD_GAS_PARITY.csv。buyNow根Gas12612158在本轮四组一致，不与历史不同上下文的12765774直接比较。
- 原step34_owner.go、step21d_compile.go、step35_static.go及wasmer-go managed/store/instance/wasi逐文件SHA与Step-38一致。未改安全Fresh生命周期、Gas、Guest或Copy策略。
- 所有受监控进程Store/Instance配平，pending=0，独立Store!=编译Store，已退出。真实六次下游调用保持执行。

未验证/限制：

- 不允许调用者在读期间并发写原输入；Race只覆盖只读缓存访问，不覆盖native并发/不合法输入并发修改。
- 真正生产部署升级、长时间缓存治理、Manager生命周期外引用、真实节点E2E尚未执行。
- registry容量8、Reset保留Go快照而清native Module；功能正确但生产淘汰政策尚未实现。需要有限额/可回收的管理器策略，不可做无界全局WASM缓存。
- 真实Table函数身份、业务全部异常/回滚未因本轮而宣称新增通过；未注入native危险错误。
- 夹具固定BlockVersion=1、gasUsed=0、内存账本，与真实节点输入上下文不等同；本轮只证明同一夹具内部方案一致。
- 没有发现本轮业务语义差异或资源守卫异常；这不等于全面生产认证。

失败记录保留：build-main工作区路径生成错误；build-main-r1链接阶段找不到本隔离目录的libwasmer（Git历史不含此忽略产物）；在核实已知库SHA后放入规定链接路径，main-r2成功。identity首轮缺少显式CM_REUSE_EXPERIMENT，包init退出2，没有创建native对象；补全原守卫要求后identity-r1通过。没有放宽或跳过守卫。所有失败日志仍在audit/raw_logs。
