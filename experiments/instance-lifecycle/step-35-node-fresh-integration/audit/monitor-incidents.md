# 监控与启动异常

1. manager-fact-copy0：测试原始日志有PASS/owner_closed pending0；监控读取已退出PID的/proc/status时ProcessLookupError，最初runner未捕获，因此峰值资源未保存。未将缺失峰值编造为0；保留测试数据，runner补捕获后其他测试继续。完整Python traceback只在会话工具输出，磁盘保存原因说明而非冒充原始堆栈。
2. node-baseline-first：缺CM_STEP21A_POOL，包初始化panic，原始stack见node log，MainPID=0；不是Store执行崩溃。
3. node-baseline-configured：RSS触发SIGTERM；第一个业务请求response=None/SDK连接不可用；runner打印response.get时又触发AttributeError，原始客户端行已在打印之前flush保存，finally完成stop/outcome。已修正打印nil响应处理；不把包装脚本错误当作native崩溃。
4. Node工作树首次git commit缺身份；未改用户全局配置，后续命令仅本次使用Codex <codex@local>提交。
