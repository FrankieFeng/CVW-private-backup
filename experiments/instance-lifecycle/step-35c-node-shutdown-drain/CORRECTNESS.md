# 业务正确性与边界

冻结8场景均exit0，3次原账本重启成功。candidate-normal与35B patched-node使用相同部署WASM、token输入和等价账本种子：四笔compute/buyNow的Gas、返回、事件、提交读写集全部相等；TxID及业务latestTxInfo的TxId/BlockHeight仅用于规范化，原始数据不删除。结果见audit/parity.json。

compute根Gas120135，buyNow根Gas12620048；每次成功buyNow含六次真实下游调用，非Mock。它们是节点上下文数据，不与其他串行WASM家族/夹具的绝对Gas混算。

重启后核对：restart-candidate-active、writer、active-reset-stop分别查到停机前TxID，返回/Gas一致。重复buyNow真实执行失败，失败交易可查、写集为空、NFT owner前后相等。未改变错误返回或Gas使测试通过。

所有候选相关Store/Instance计数配平，pending0；Core/Put/DB-write/WAL首尾计数配平；archive_workers_drained、diagnostic_stopped均出现，PID/cgroup退出。资源表包括Go heap/goroutine快照在原始snapshot/VM事件中；没有把进程退出自动写成每个全局goroutine都已逐一证明安全。

限制：未导出整个账本状态树/全量hash；读写集和关键业务状态验证不能替代全账本逐键证明。未做电源故障/磁盘故障耐久验证，DB写入返回与重启可读不自动等于每层设备已强制fsync。真实Table函数身份、所有异常分支、RPC断网后的结果重试、异步业务提交、其他共识和Quick模式not_tested。未扩大并发或做race性能结论。

Gate取消/重复释放/排空单测，以及账本nil Close、重复Close、在途租约等待单测通过。最初直接在Store模块单独运行测试因离线依赖图缺少protocol2.4而失败；使用节点已有replace依赖图测试通过，没有下载或替换未知版本。
