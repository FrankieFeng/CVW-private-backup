# 最小后续工作

1. 独立节点适配分支中，将NewRuntimeInstance/合约缓存准备、根Invoke、嵌套回调、Reset/Stop全部路由到SafeFreshOwner；缓存按合约版本+WASM SHA+native/compiler/Gas/config键验证，固定部署时禁止未匹配二进制和在线升级。不接回原pool后台grow/freelist/async close。
2. 复用现有固定库、Guest和四组原件，只选Baseline/Copy恢复一个隔离节点。先启动→单根真实交易→在途Stop→正常退出，核对/proc maps、Gas/写集/事件/账本、CAPI计数及RSS/线程；这一步是接线验证，不是E2E性能结论。
3. 接线smoke通过后才进入有限SDK开始到同步响应的配对E2E。两组同新生命周期；编译/模板和owner排队另列；保留TxID/重复Invoke/提交语义。每owner外部job预算≤32，按有限实验计划配置，不解除守卫、不通过重启掩盖持续增长。

不再等待陈航、不换native ABI、不引入B1、不研究新Copy或Module编译优化。精确native构建来源、长期服务、多owner并行和Table身份作为后续认证问题，不能在当前有限原型上宣称已解决。
