# Step-30正确性：新测试未执行，历史核验有限

## 新Step30

G0/G1/G2均blocked，未进行新业务/提交/隔离/回滚验证。所有项不得标pass；EXECUTION_STATUS.csv给出理由。保存的旧node binary缺Store全生命周期owner与native Finalizer收敛，不以单客户端或根Invoke互斥证明安全。没有运行未经验证原池。

## 本轮对旧数据的直接核验

重新读取旧Step20两轮207条响应和四份原始STEP17日志，确认207唯一TxID/207唯一fresh Instance ID，每条有1次根Invoke，返回success bigNumCal:607723520、SDK及VM Gas均106028、code0、正TxBlockHeight。正式资源删失批88完整对的Gas/返回相等；Copy另1条未配对响应和pending未知请求保留，后者不算失败或成功。

客户端未存完整RWSet、独立事件验证/最终账本快照，**not_tested/not_collected**；不能将计算合约“看起来不写状态”当作实际链上写集核对。同步响应表示节点报告该Tx提交结果，独立账本扫描/确认时间和成功提交TPS没有证据。新事务回滚、真实Table身份、跨合约E2E均未在本轮验证。

## 安全与资源

旧low-a Copy RSS峰2564.707MiB触发2560软限，两节点都增长约1GiB；线程27，Go heap未采集。历史停止状态证明自有节点已停，不构成当前长期资源有界证明。没有提高阈值、给新请求降并发凑数据、强制GC、回收池改造或进程轮换续测。

仅临时C-call错误读取的LockOSThread不等于Store固定owner；native Finalizer与NewRuntimeInstance/模块准备不在根Invoke锁内。Step21B已有约束仍适用。Step22/28/29仅有界测试safe路径，当前节点没有相应已验证集成，不能临时替换native对象共享模型绕过。

环境证据保存的是公有源码/文件哈希和非敏感配置字段；没有打包密钥、证书或数据库。所有历史来源文件末尾SHA再核验，分支只新增Step30目录。
