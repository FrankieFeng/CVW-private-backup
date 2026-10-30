# 真实业务夹具

八个独立合约全部进入清单。Step32六方法原样引用，不重复。新增30方法见 inputs/cases.json 和逐方法 *-case.json；逐项真实init与必要的mint/register/save/approve前置调用，不用固定子合约返回值。identity独立调用真实sender推导/管理/白名单。bigInput实际512KiB输入、4×256KiB输入和原默认100次×256B写入。raffle实际注册3人、按原BKDR算法/固定timestamp抽签并检查赢家被删除，未缩短循环。itinerary查询真实写历史。

新增的是内存账本后端功能，不改生产VM：GetHistoryForKey从实际已提交TxRWSet构建历史，SelectObject从实际账本按[start,limit)过滤排序。production SDK/VM iterator与Guest业务仍真实执行。后端不代表真实链数据库或节点吞吐。

首个 accountTokens 预检因后端未实现 SelectObject（嵌入nil接口）返回VM错误；原日志与STOP已归档。资源与owner均正常清空。随后补充真实状态范围迭代器build3，并以backend-v2标签重试；失败样本保留不计主统计。未改变业务、Gas、守卫或资源限制。

identity.callerAddress：源码真实调用自身identity.address，现有已验证串行manager拒绝active-contract reentry。静态blocked，不绕过守卫，不mock。其余Gas接口、init/upgrade、delay/noop/library探针全登记auxiliary，不能将其算作缺失业务而偷偷删除，也不能用空探针提高业务覆盖率。erc721.mint2本身源码只更新latestTxInfo，单列为原型部分mint，不能称完整mint成功路径。

成功配对验证不等于所有输入与异常路径认证。真实Table函数身份及未运行的异常/回滚统一not_tested；Step32 buyNow六次真实子调用的既有证据以来源标识引用，不生成新的buyNow性能。
