# 所有权及释放矩阵

|资源|创建/所有者|共享范围|释放/约束|本轮证据|
|---|---|---|---|---|
|Config、Engine|cache scope、native owner|该Module的新Store共用Engine|cache退出最后释放，禁止用户线程析构|兼容性+真实业务|
|编译Store S0、Module、import/export type元数据|e25Prepare；cache scope|同owner缓存Module|预热元数据；排空后关Module/类型/Store/Engine|MODULE_PREPARATION及owner计数|
|运行Store Si|makeE22；instance scope|每个Fresh独立，不clone|其他运行对象清理后删除Store handle|C外Store导入拒绝、store_created事件、CAPI计数|
|WASI配置/环境|Si内创建；配置由native消费|不跨Store freelist|instance scope，WASI env_delete on_exit在Si存活时执行|故障回滚、真实_start|
|Imports、host functions、exports|Si/instance scope|不得逃逸请求|同步显式/逆序scope清理；borrowed类型不重复释放|claimed destructor、实际close测试|
|Instance、Memory、Globals/Table|NewInstanceInStore(M,Si)|Guest运行态不复用|CallMethod返回后同步关闭，Store最后删除|48根+72子调用；Table真实函数身份not_tested|
|Guest函数/Memory借用视图|当前live scope|只在该调用内|关闭后函数/Memory scope/exports检查拒绝；禁止保留Data切片|owner测试post-Close调用拒绝|
|返回值/RWSet/事件|Go宿主对象|可离开owner，不能带native handle|sysCall先make+copy请求body，SuccessResult持有Go bytes|vm_bridge.go:请求body复制；逐次语义对比|
|子Instance|父调用同owner同步创建独立Sj|同cache Module，不共用运行Store|子完成并关闭再返回父；父scope仍存活|buyNow真实六callee/Gas传播|

managedSetFinalizer并非runtime.SetFinalizer：所有native wrapper登记强引用scope，不安装任意Go Finalizer goroutine的native析构。GC不能抢先析构，scope在owner执行。`source/vm/wasmer-go/managed.go:51` 返回是否成功claim，重复Close无二次C删除；`source/vm/wasmer-go/managed.go:75` 在active native call时拒绝关闭，cleanup继续处理其他登记项。没有保留已关闭对象的永久tombstone表。

C API删除计数与Rust最后引用析构分开；未加native Drop探针、不认证长期全部Rc/后台任务。原型以同步C API回收、in-flight=0、scope无登记、资源采样和进程正常退出建立有界证据，不把OS进程退出替代运行期间的所有权协议。
