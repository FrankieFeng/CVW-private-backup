# 已执行生命周期测试

|场景|证据|范围|
|---|---|---|
|真实独立Store+同Module|native-compat.log|三Store，两活Instance；foreign Memory拒绝，自有Memory通过且隔离|
|Fresh/WASI/_start/业务/关闭|verify-*三批|4合约×4组×3轮=48根；buyNow12根、72真子调用|
|Module准备失败|TestStep34Owner bad-module|真实畸形WASM拒绝；新Store部分资源scope回滚，缓存随后可调用|
|Store/WASI/Instance/Initialize失败|freeze-fault-*|Go安全检查点注入；不冒称实际OOM或C错误被制造|
|执行失败及回滚|fault-execute与business-error-*|Go Guest后故障、真实ERC空输入、真实buyNow重复token、缺失方法；账本未提交|
|故障后恢复|recovery-G0.json|同缓存Module，下一Fresh实际成功|
|关闭失败/取消关闭|fault-close/cancel-close|先真正清理再注入Go返回错误；native void析构失败不可安全强制注入|
|取消创建|cancel-wasi、Do取消|创建Store后取消，scope回滚；队列取消不启动native业务|
|Reset、Stop在途等待|TestStep34Owner|channel barrier定位job，不使用Sleep；Stop超时不释放在途资源，释放任务后Stop完成|
|重复Close、GC、失效函数|TestStep34Owner|重复Instance/Store close、强制GC、关闭后函数拒绝|
|Reset失败|TestStep34Poison|poison拒绝新请求，Stop正常且可重复|
|Go Race|v9-race-owner/v9-race-poison|通过，仅Go协议诊断，不能认证native race不存在|

结构化记录239进程，成功238；失败owner-configured是诊断在ManagedEndOwner后读取ManagedCount触发守卫，build3及冻结版已修正。另保留build1编译参数错误和owner-preflight缺环境变量的package-init拒绝；未执行Guest，未隐藏。任何资源阈值均未提高，失败进程已结束。

保护：普通合约RSS768MiB/125线程，exchange1536MiB/220线程，硬MemoryMax2GiB/TasksMax256/60s，Go45s；宿主可用内存至少8GiB、swap不超过1GiB。owner C兼容性预检另更小边界。每进程至多2组/目标，exchange1组。无后台池、无100ms业务Sleep，无长期压测。
