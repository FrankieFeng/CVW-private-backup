# Reset / Stop与异常记录

- candidate-reset：空闲Reset两次返回nil。
- candidate-reset-after：compute后Reset两次，再执行compute和真实buyNow，均成功。
- candidate-reset-stop：在Owner实际清理回调的有界rendezvous暂停Reset，观察Stop已经到VM入口后释放，日志顺序为reset_begin→hold→stop_requested→release→reset_end→stop_finished，证明发生真实重叠。
- candidate-active-reset-stop：compute进入Guest路径后触发Manager Reset，确认resetting，再SIGTERM。已接收同步RPC完成，Reset与Stop正常结束，重启后交易可查。

原Owner的resetDone/closing协调保留，Stop不会与Reset重复释放Native对象。VM Stop现在10秒context，错误传播至节点模块关闭；节点模块错误会fail-fast，避免先返回错误却继续Close账本。失败并非当作“正常排空”，生产级取消/回滚策略未泛化。

重复关闭证据：账本Close的nil/幂等/在途等待单测通过；RPC/Core/Proposer用Once防重复Stop；Owner已有历史幂等验证。未把向已退出节点重复发送信号当作同进程二次Stop测试，完整节点级重复Stop并非另有实测。

保留的失败：
1. obs-held：只观测、不修协议，写已关闭StateDB，exit2，预期证伪旧关闭安全性。
2. fixed3：试用grpc.GracefulStop后当前ServeHTTP transport panic Drain() is not implemented，后续案例停止。没有升级grpc；最终改用HTTP层请求门计数，排空后调用原Stop。
3. restart-v4-active：实验诊断socket未显式关闭，地址残留导致启动panic；尚未进入业务一致性检查。保留原socket/失败日志，最终诊断服务显式Shutdown/join，每次运行独立path；重启验证通过。

这些候选失败均保留在RESOURCE_SUMMARY.csv exploratory_or_failure，未混入冻结候选的8场景和3重启统计。
