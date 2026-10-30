# Step-34进度

父963b47b4，独立worktree /home/frankie/mygitprojects/.worktrees/cvw-step34。阶段1：实际native ABI与跨独立Store缓存Module预检；随后实现有界owner生命周期与真实业务。未启动节点。

启动 owner-configured，unit=step34-owner-configured，pairs=one split block chunk, max2 targets；命令已保存。

结束 owner-configured：passed=False，reason=exited，peak_threads=5，RSS_KiB=45152，PID/cgroup结束=True。

预检build1因测试NewModule漏logger参数编译失败；build2编译通过。第一次owner启动漏CM_REUSE_EXPERIMENT在package init拒绝，未执行native。配置补全后owner测试清理时日志在ManagedEndOwner后调用ManagedCount触发守卫；现场保留owner-configured。修复仅在End前读取清理计数，守卫不变、资源不放宽，build3新标签重测。

启动 owner-fixed，unit=step34-owner-fixed，pairs=one split block chunk, max2 targets；命令已保存。

结束 owner-fixed：passed=True，reason=exited，peak_threads=5，RSS_KiB=43796，PID/cgroup结束=True。

启动 compute-smoke，unit=step34-compute-smoke，pairs=one split block chunk, max2 targets；命令已保存。

结束 compute-smoke：passed=True，reason=exited，peak_threads=27，RSS_KiB=369680，PID/cgroup结束=True。

启动 fact-smoke，unit=step34-fact-smoke，pairs=one split block chunk, max2 targets；命令已保存。

结束 fact-smoke：passed=True，reason=exited，peak_threads=22，RSS_KiB=369016，PID/cgroup结束=True。

启动 erc721-smoke，unit=step34-erc721-smoke，pairs=one split block chunk, max2 targets；命令已保存。

结束 erc721-smoke：passed=True，reason=exited，peak_threads=22，RSS_KiB=397620，PID/cgroup结束=True。

启动 exchange-smoke-G0，unit=step34-exchange-smoke-G0，pairs=one split block chunk, max2 targets；命令已保存。

结束 exchange-smoke-G0：passed=True，reason=exited，peak_threads=46，RSS_KiB=524660，PID/cgroup结束=True。

启动 exchange-smoke-G2，unit=step34-exchange-smoke-G2，pairs=one split block chunk, max2 targets；命令已保存。

结束 exchange-smoke-G2：passed=True，reason=exited，peak_threads=46，RSS_KiB=495604，PID/cgroup结束=True。

启动 owner-final，unit=step34-owner-final，pairs=one split block chunk, max2 targets；命令已保存。

结束 owner-final：passed=True，reason=exited，peak_threads=5，RSS_KiB=45628，PID/cgroup结束=True。

启动 fault-store，unit=step34-fault-store，pairs=one split block chunk, max2 targets；命令已保存。

结束 fault-store：passed=True，reason=exited，peak_threads=24，RSS_KiB=289588，PID/cgroup结束=True。

启动 fault-wasi，unit=step34-fault-wasi，pairs=one split block chunk, max2 targets；命令已保存。

结束 fault-wasi：passed=True，reason=exited，peak_threads=22，RSS_KiB=285968，PID/cgroup结束=True。

启动 fault-instance，unit=step34-fault-instance，pairs=one split block chunk, max2 targets；命令已保存。

结束 fault-instance：passed=True，reason=exited，peak_threads=23，RSS_KiB=297504，PID/cgroup结束=True。

启动 fault-initialize，unit=step34-fault-initialize，pairs=one split block chunk, max2 targets；命令已保存。

结束 fault-initialize：passed=True，reason=exited，peak_threads=22，RSS_KiB=296484，PID/cgroup结束=True。

启动 fault-execute，unit=step34-fault-execute，pairs=one split block chunk, max2 targets；命令已保存。

结束 fault-execute：passed=True，reason=exited，peak_threads=24，RSS_KiB=288924，PID/cgroup结束=True。

启动 fault-close，unit=step34-fault-close，pairs=one split block chunk, max2 targets；命令已保存。

结束 fault-close：passed=True，reason=exited，peak_threads=23，RSS_KiB=307488，PID/cgroup结束=True。

启动 fault-cancel-wasi，unit=step34-fault-cancel-wasi，pairs=one split block chunk, max2 targets；命令已保存。

结束 fault-cancel-wasi：passed=True，reason=exited，peak_threads=24，RSS_KiB=306036，PID/cgroup结束=True。

启动 fault-cancel-close，unit=step34-fault-cancel-close，pairs=one split block chunk, max2 targets；命令已保存。

结束 fault-cancel-close：passed=True，reason=exited，peak_threads=22，RSS_KiB=294416，PID/cgroup结束=True。

启动 owner-freeze，unit=step34-owner-freeze，pairs=one split block chunk, max2 targets；命令已保存。

结束 owner-freeze：passed=True，reason=exited，peak_threads=5，RSS_KiB=38736，PID/cgroup结束=True。

启动 poison-freeze，unit=step34-poison-freeze，pairs=one split block chunk, max2 targets；命令已保存。

结束 poison-freeze：passed=True，reason=exited，peak_threads=5，RSS_KiB=42456，PID/cgroup结束=True。

启动 freeze-fault-store，unit=step34-freeze-fault-store，pairs=one split block chunk, max2 targets；命令已保存。

结束 freeze-fault-store：passed=True，reason=exited，peak_threads=22，RSS_KiB=285660，PID/cgroup结束=True。

启动 freeze-fault-wasi，unit=step34-freeze-fault-wasi，pairs=one split block chunk, max2 targets；命令已保存。

结束 freeze-fault-wasi：passed=True，reason=exited，peak_threads=22，RSS_KiB=290392，PID/cgroup结束=True。

启动 freeze-fault-instance，unit=step34-freeze-fault-instance，pairs=one split block chunk, max2 targets；命令已保存。

结束 freeze-fault-instance：passed=True，reason=exited，peak_threads=22，RSS_KiB=293164，PID/cgroup结束=True。

启动 freeze-fault-initialize，unit=step34-freeze-fault-initialize，pairs=one split block chunk, max2 targets；命令已保存。

结束 freeze-fault-initialize：passed=True，reason=exited，peak_threads=22，RSS_KiB=281228，PID/cgroup结束=True。

启动 freeze-fault-execute，unit=step34-freeze-fault-execute，pairs=one split block chunk, max2 targets；命令已保存。

结束 freeze-fault-execute：passed=True，reason=exited，peak_threads=25，RSS_KiB=276412，PID/cgroup结束=True。

启动 freeze-fault-close，unit=step34-freeze-fault-close，pairs=one split block chunk, max2 targets；命令已保存。

结束 freeze-fault-close：passed=True，reason=exited，peak_threads=22，RSS_KiB=302840，PID/cgroup结束=True。

启动 freeze-fault-cancel-wasi，unit=step34-freeze-fault-cancel-wasi，pairs=one split block chunk, max2 targets；命令已保存。

结束 freeze-fault-cancel-wasi：passed=True，reason=exited，peak_threads=24，RSS_KiB=295416，PID/cgroup结束=True。

启动 freeze-fault-cancel-close，unit=step34-freeze-fault-cancel-close，pairs=one split block chunk, max2 targets；命令已保存。

结束 freeze-fault-cancel-close：passed=True，reason=exited，peak_threads=22，RSS_KiB=294360，PID/cgroup结束=True。

启动 business-error-erc721，unit=step34-business-error-erc721，pairs=one split block chunk, max2 targets；命令已保存。

结束 business-error-erc721：passed=True，reason=exited，peak_threads=24，RSS_KiB=291172，PID/cgroup结束=True。

启动 business-error-exchange，unit=step34-business-error-exchange，pairs=one split block chunk, max2 targets；命令已保存。

结束 business-error-exchange：passed=True，reason=exited，peak_threads=44，RSS_KiB=523668，PID/cgroup结束=True。

启动 verify-b1-compute-c0，unit=step34-verify-b1-compute-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 verify-b1-compute-c0：passed=True，reason=exited，peak_threads=27，RSS_KiB=381344，PID/cgroup结束=True。

启动 verify-b1-compute-c1，unit=step34-verify-b1-compute-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 verify-b1-compute-c1：passed=True，reason=exited，peak_threads=26，RSS_KiB=361836，PID/cgroup结束=True。

启动 verify-b1-fact-c0，unit=step34-verify-b1-fact-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 verify-b1-fact-c0：passed=True，reason=exited，peak_threads=22，RSS_KiB=414420，PID/cgroup结束=True。

启动 verify-b1-fact-c1，unit=step34-verify-b1-fact-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 verify-b1-fact-c1：passed=True，reason=exited，peak_threads=23，RSS_KiB=376440，PID/cgroup结束=True。

启动 verify-b1-erc721-c0，unit=step34-verify-b1-erc721-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 verify-b1-erc721-c0：passed=True，reason=exited，peak_threads=23，RSS_KiB=398272，PID/cgroup结束=True。

启动 verify-b1-erc721-c1，unit=step34-verify-b1-erc721-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 verify-b1-erc721-c1：passed=True，reason=exited，peak_threads=22，RSS_KiB=393232，PID/cgroup结束=True。

启动 verify-b1-exchange-c0，unit=step34-verify-b1-exchange-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 verify-b1-exchange-c0：passed=True，reason=exited，peak_threads=30，RSS_KiB=520768，PID/cgroup结束=True。

启动 verify-b1-exchange-c1，unit=step34-verify-b1-exchange-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 verify-b1-exchange-c1：passed=True，reason=exited，peak_threads=48，RSS_KiB=529616，PID/cgroup结束=True。

启动 verify-b1-exchange-c2，unit=step34-verify-b1-exchange-c2，pairs=one split block chunk, max2 targets；命令已保存。

结束 verify-b1-exchange-c2：passed=True，reason=exited，peak_threads=29，RSS_KiB=498292，PID/cgroup结束=True。

启动 verify-b1-exchange-c3，unit=step34-verify-b1-exchange-c3，pairs=one split block chunk, max2 targets；命令已保存。

结束 verify-b1-exchange-c3：passed=True，reason=exited，peak_threads=45，RSS_KiB=495708，PID/cgroup结束=True。

启动 cost-b1-compute-control，unit=step34-cost-b1-compute-control，pairs=one split block chunk, max2 targets；命令已保存。

结束 cost-b1-compute-control：passed=True，reason=exited，peak_threads=41，RSS_KiB=277048，PID/cgroup结束=True。

启动 cost-b1-compute-new，unit=step34-cost-b1-compute-new，pairs=one split block chunk, max2 targets；命令已保存。

结束 cost-b1-compute-new：passed=True，reason=exited，peak_threads=22，RSS_KiB=282616，PID/cgroup结束=True。

启动 cost-b1-fact-control，unit=step34-cost-b1-fact-control，pairs=one split block chunk, max2 targets；命令已保存。

结束 cost-b1-fact-control：passed=True，reason=exited，peak_threads=40，RSS_KiB=297584，PID/cgroup结束=True。

启动 cost-b1-fact-new，unit=step34-cost-b1-fact-new，pairs=one split block chunk, max2 targets；命令已保存。

结束 cost-b1-fact-new：passed=True，reason=exited，peak_threads=23，RSS_KiB=292324，PID/cgroup结束=True。

启动 cost-b1-erc721-control，unit=step34-cost-b1-erc721-control，pairs=one split block chunk, max2 targets；命令已保存。

结束 cost-b1-erc721-control：passed=True，reason=exited，peak_threads=40，RSS_KiB=306748，PID/cgroup结束=True。

启动 cost-b1-erc721-new，unit=step34-cost-b1-erc721-new，pairs=one split block chunk, max2 targets；命令已保存。

结束 cost-b1-erc721-new：passed=True，reason=exited，peak_threads=23，RSS_KiB=310476，PID/cgroup结束=True。

启动 cost-b1-exchange-control，unit=step34-cost-b1-exchange-control，pairs=one split block chunk, max2 targets；命令已保存。

结束 cost-b1-exchange-control：passed=True，reason=exited，peak_threads=176，RSS_KiB=553648，PID/cgroup结束=True。

启动 cost-b1-exchange-new，unit=step34-cost-b1-exchange-new，pairs=one split block chunk, max2 targets；命令已保存。

结束 cost-b1-exchange-new：passed=True，reason=exited，peak_threads=48，RSS_KiB=530344，PID/cgroup结束=True。

最终build6验证批1完成：四合约四组正确性与同代码Store架构成本，所有区块/配对已落盘。

启动 verify-b2-compute-c0，unit=step34-verify-b2-compute-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 verify-b2-compute-c0：passed=True，reason=exited，peak_threads=25，RSS_KiB=370696，PID/cgroup结束=True。

启动 verify-b2-compute-c1，unit=step34-verify-b2-compute-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 verify-b2-compute-c1：passed=True，reason=exited，peak_threads=26，RSS_KiB=377116，PID/cgroup结束=True。

启动 verify-b2-fact-c0，unit=step34-verify-b2-fact-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 verify-b2-fact-c0：passed=True，reason=exited，peak_threads=23，RSS_KiB=366476，PID/cgroup结束=True。

启动 verify-b2-fact-c1，unit=step34-verify-b2-fact-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 verify-b2-fact-c1：passed=True，reason=exited，peak_threads=23，RSS_KiB=414420，PID/cgroup结束=True。

启动 verify-b2-erc721-c0，unit=step34-verify-b2-erc721-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 verify-b2-erc721-c0：passed=True，reason=exited，peak_threads=22，RSS_KiB=391908，PID/cgroup结束=True。

启动 verify-b2-erc721-c1，unit=step34-verify-b2-erc721-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 verify-b2-erc721-c1：passed=True，reason=exited，peak_threads=22，RSS_KiB=419116，PID/cgroup结束=True。

启动 verify-b2-exchange-c0，unit=step34-verify-b2-exchange-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 verify-b2-exchange-c0：passed=True，reason=exited，peak_threads=48，RSS_KiB=496012，PID/cgroup结束=True。

启动 verify-b2-exchange-c1，unit=step34-verify-b2-exchange-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 verify-b2-exchange-c1：passed=True，reason=exited，peak_threads=44，RSS_KiB=486668，PID/cgroup结束=True。

启动 verify-b2-exchange-c2，unit=step34-verify-b2-exchange-c2，pairs=one split block chunk, max2 targets；命令已保存。

结束 verify-b2-exchange-c2：passed=True，reason=exited，peak_threads=48，RSS_KiB=528252，PID/cgroup结束=True。

启动 verify-b2-exchange-c3，unit=step34-verify-b2-exchange-c3，pairs=one split block chunk, max2 targets；命令已保存。

结束 verify-b2-exchange-c3：passed=True，reason=exited，peak_threads=44，RSS_KiB=528516，PID/cgroup结束=True。

启动 cost-b2-compute-new，unit=step34-cost-b2-compute-new，pairs=one split block chunk, max2 targets；命令已保存。

结束 cost-b2-compute-new：passed=True，reason=exited，peak_threads=22，RSS_KiB=271768，PID/cgroup结束=True。

启动 cost-b2-compute-control，unit=step34-cost-b2-compute-control，pairs=one split block chunk, max2 targets；命令已保存。

结束 cost-b2-compute-control：passed=True，reason=exited，peak_threads=40，RSS_KiB=287584，PID/cgroup结束=True。

启动 cost-b2-fact-new，unit=step34-cost-b2-fact-new，pairs=one split block chunk, max2 targets；命令已保存。

结束 cost-b2-fact-new：passed=True，reason=exited，peak_threads=23，RSS_KiB=293612，PID/cgroup结束=True。

启动 cost-b2-fact-control，unit=step34-cost-b2-fact-control，pairs=one split block chunk, max2 targets；命令已保存。

结束 cost-b2-fact-control：passed=True，reason=exited，peak_threads=40，RSS_KiB=293660，PID/cgroup结束=True。

启动 cost-b2-erc721-new，unit=step34-cost-b2-erc721-new，pairs=one split block chunk, max2 targets；命令已保存。

结束 cost-b2-erc721-new：passed=True，reason=exited，peak_threads=23，RSS_KiB=303352，PID/cgroup结束=True。

启动 cost-b2-erc721-control，unit=step34-cost-b2-erc721-control，pairs=one split block chunk, max2 targets；命令已保存。

结束 cost-b2-erc721-control：passed=True，reason=exited，peak_threads=40，RSS_KiB=304496，PID/cgroup结束=True。

启动 cost-b2-exchange-new，unit=step34-cost-b2-exchange-new，pairs=one split block chunk, max2 targets；命令已保存。

结束 cost-b2-exchange-new：passed=True，reason=exited，peak_threads=48，RSS_KiB=521224，PID/cgroup结束=True。

启动 cost-b2-exchange-control，unit=step34-cost-b2-exchange-control，pairs=one split block chunk, max2 targets；命令已保存。

结束 cost-b2-exchange-control：passed=True，reason=exited，peak_threads=176，RSS_KiB=575148，PID/cgroup结束=True。

最终build6验证批2完成：四合约四组正确性与同代码Store架构成本，所有区块/配对已落盘。

启动 verify-b3-compute-c0，unit=step34-verify-b3-compute-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 verify-b3-compute-c0：passed=True，reason=exited，peak_threads=26，RSS_KiB=393708，PID/cgroup结束=True。

启动 verify-b3-compute-c1，unit=step34-verify-b3-compute-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 verify-b3-compute-c1：passed=True，reason=exited，peak_threads=26，RSS_KiB=366692，PID/cgroup结束=True。

启动 verify-b3-fact-c0，unit=step34-verify-b3-fact-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 verify-b3-fact-c0：passed=True，reason=exited，peak_threads=26，RSS_KiB=410736，PID/cgroup结束=True。

启动 verify-b3-fact-c1，unit=step34-verify-b3-fact-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 verify-b3-fact-c1：passed=True，reason=exited，peak_threads=24，RSS_KiB=373044，PID/cgroup结束=True。

启动 verify-b3-erc721-c0，unit=step34-verify-b3-erc721-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 verify-b3-erc721-c0：passed=True，reason=exited，peak_threads=23，RSS_KiB=416280，PID/cgroup结束=True。

启动 verify-b3-erc721-c1，unit=step34-verify-b3-erc721-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 verify-b3-erc721-c1：passed=True，reason=exited，peak_threads=25，RSS_KiB=386540，PID/cgroup结束=True。

启动 verify-b3-exchange-c0，unit=step34-verify-b3-exchange-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 verify-b3-exchange-c0：passed=True，reason=exited，peak_threads=28，RSS_KiB=524004，PID/cgroup结束=True。

启动 verify-b3-exchange-c1，unit=step34-verify-b3-exchange-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 verify-b3-exchange-c1：passed=True，reason=exited，peak_threads=47，RSS_KiB=541532，PID/cgroup结束=True。

启动 verify-b3-exchange-c2，unit=step34-verify-b3-exchange-c2，pairs=one split block chunk, max2 targets；命令已保存。

结束 verify-b3-exchange-c2：passed=True，reason=exited，peak_threads=46，RSS_KiB=503492，PID/cgroup结束=True。

启动 verify-b3-exchange-c3，unit=step34-verify-b3-exchange-c3，pairs=one split block chunk, max2 targets；命令已保存。

结束 verify-b3-exchange-c3：passed=True，reason=exited，peak_threads=27，RSS_KiB=474640，PID/cgroup结束=True。

启动 cost-b3-compute-control，unit=step34-cost-b3-compute-control，pairs=one split block chunk, max2 targets；命令已保存。

结束 cost-b3-compute-control：passed=True，reason=exited，peak_threads=40，RSS_KiB=276536，PID/cgroup结束=True。

启动 cost-b3-compute-new，unit=step34-cost-b3-compute-new，pairs=one split block chunk, max2 targets；命令已保存。

结束 cost-b3-compute-new：passed=True，reason=exited，peak_threads=24，RSS_KiB=267872，PID/cgroup结束=True。

启动 cost-b3-fact-control，unit=step34-cost-b3-fact-control，pairs=one split block chunk, max2 targets；命令已保存。

结束 cost-b3-fact-control：passed=True，reason=exited，peak_threads=40，RSS_KiB=290444，PID/cgroup结束=True。

启动 cost-b3-fact-new，unit=step34-cost-b3-fact-new，pairs=one split block chunk, max2 targets；命令已保存。

结束 cost-b3-fact-new：passed=True，reason=exited，peak_threads=22，RSS_KiB=287472，PID/cgroup结束=True。

启动 cost-b3-erc721-control，unit=step34-cost-b3-erc721-control，pairs=one split block chunk, max2 targets；命令已保存。

结束 cost-b3-erc721-control：passed=True，reason=exited，peak_threads=40，RSS_KiB=315532，PID/cgroup结束=True。

启动 cost-b3-erc721-new，unit=step34-cost-b3-erc721-new，pairs=one split block chunk, max2 targets；命令已保存。

结束 cost-b3-erc721-new：passed=True，reason=exited，peak_threads=23，RSS_KiB=297956，PID/cgroup结束=True。

启动 cost-b3-exchange-control，unit=step34-cost-b3-exchange-control，pairs=one split block chunk, max2 targets；命令已保存。

结束 cost-b3-exchange-control：passed=True，reason=exited，peak_threads=176，RSS_KiB=574596，PID/cgroup结束=True。

启动 cost-b3-exchange-new，unit=step34-cost-b3-exchange-new，pairs=one split block chunk, max2 targets；命令已保存。

结束 cost-b3-exchange-new：passed=True，reason=exited，peak_threads=31，RSS_KiB=526860，PID/cgroup结束=True。

最终build6验证批3完成：四合约四组正确性与同代码Store架构成本，所有区块/配对已落盘。

启动 race-owner，unit=step34-race-owner，pairs=one split block chunk, max2 targets；命令已保存。

结束 race-owner：passed=True，reason=exited，peak_threads=6，RSS_KiB=88952，PID/cgroup结束=True。

启动 race-poison，unit=step34-race-poison，pairs=one split block chunk, max2 targets；命令已保存。

结束 race-poison：passed=True，reason=exited，peak_threads=6，RSS_KiB=82128，PID/cgroup结束=True。

常规go build暴露继承的sim_context.go依赖step27_test诊断函数。保留build6原文，将同一诊断实现移至step27_diagnostic.go；算法、Gas和计时边界不改。build6数据保留，当前build7重新验证，不混合性能统计。

启动 v7-owner-freeze，unit=step34-v7-owner-freeze，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-owner-freeze：passed=True，reason=exited，peak_threads=5，RSS_KiB=43936，PID/cgroup结束=True。

启动 v7-poison-freeze，unit=step34-v7-poison-freeze，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-poison-freeze：passed=True，reason=exited，peak_threads=5，RSS_KiB=39612，PID/cgroup结束=True。

启动 v7-freeze-fault-store，unit=step34-v7-freeze-fault-store，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-freeze-fault-store：passed=True，reason=exited，peak_threads=22，RSS_KiB=291560，PID/cgroup结束=True。

启动 v7-freeze-fault-wasi，unit=step34-v7-freeze-fault-wasi，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-freeze-fault-wasi：passed=True，reason=exited，peak_threads=24，RSS_KiB=292080，PID/cgroup结束=True。

启动 v7-freeze-fault-instance，unit=step34-v7-freeze-fault-instance，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-freeze-fault-instance：passed=True，reason=exited，peak_threads=22，RSS_KiB=299784，PID/cgroup结束=True。

启动 v7-freeze-fault-initialize，unit=step34-v7-freeze-fault-initialize，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-freeze-fault-initialize：passed=True，reason=exited，peak_threads=23，RSS_KiB=296372，PID/cgroup结束=True。

启动 v7-freeze-fault-execute，unit=step34-v7-freeze-fault-execute，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-freeze-fault-execute：passed=True，reason=exited，peak_threads=23，RSS_KiB=291656，PID/cgroup结束=True。

启动 v7-freeze-fault-close，unit=step34-v7-freeze-fault-close，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-freeze-fault-close：passed=True，reason=exited，peak_threads=25，RSS_KiB=298328，PID/cgroup结束=True。

启动 v7-freeze-fault-cancel-wasi，unit=step34-v7-freeze-fault-cancel-wasi，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-freeze-fault-cancel-wasi：passed=True，reason=exited，peak_threads=24，RSS_KiB=282344，PID/cgroup结束=True。

启动 v7-freeze-fault-cancel-close，unit=step34-v7-freeze-fault-cancel-close，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-freeze-fault-cancel-close：passed=True，reason=exited，peak_threads=23，RSS_KiB=288752，PID/cgroup结束=True。

启动 v7-business-error-erc721，unit=step34-v7-business-error-erc721，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-business-error-erc721：passed=True，reason=exited，peak_threads=23，RSS_KiB=310396，PID/cgroup结束=True。

启动 v7-business-error-exchange，unit=step34-v7-business-error-exchange，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-business-error-exchange：passed=True，reason=exited，peak_threads=46，RSS_KiB=502380，PID/cgroup结束=True。

启动 v7-verify-b1-compute-c0，unit=step34-v7-verify-b1-compute-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-verify-b1-compute-c0：passed=True，reason=exited，peak_threads=26，RSS_KiB=389620，PID/cgroup结束=True。

启动 v7-verify-b1-compute-c1，unit=step34-v7-verify-b1-compute-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-verify-b1-compute-c1：passed=True，reason=exited，peak_threads=25，RSS_KiB=362312，PID/cgroup结束=True。

启动 v7-verify-b1-fact-c0，unit=step34-v7-verify-b1-fact-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-verify-b1-fact-c0：passed=True，reason=exited，peak_threads=26，RSS_KiB=407796，PID/cgroup结束=True。

启动 v7-verify-b1-fact-c1，unit=step34-v7-verify-b1-fact-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-verify-b1-fact-c1：passed=True，reason=exited，peak_threads=22，RSS_KiB=370348，PID/cgroup结束=True。

启动 v7-verify-b1-erc721-c0，unit=step34-v7-verify-b1-erc721-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-verify-b1-erc721-c0：passed=True，reason=exited，peak_threads=23，RSS_KiB=421968，PID/cgroup结束=True。

启动 v7-verify-b1-erc721-c1，unit=step34-v7-verify-b1-erc721-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-verify-b1-erc721-c1：passed=True，reason=exited，peak_threads=23，RSS_KiB=399736，PID/cgroup结束=True。

启动 v7-verify-b1-exchange-c0，unit=step34-v7-verify-b1-exchange-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-verify-b1-exchange-c0：passed=True，reason=exited，peak_threads=48，RSS_KiB=541008，PID/cgroup结束=True。

启动 v7-verify-b1-exchange-c1，unit=step34-v7-verify-b1-exchange-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-verify-b1-exchange-c1：passed=True，reason=exited，peak_threads=43，RSS_KiB=523764，PID/cgroup结束=True。

启动 v7-verify-b1-exchange-c2，unit=step34-v7-verify-b1-exchange-c2，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-verify-b1-exchange-c2：passed=True，reason=exited，peak_threads=43，RSS_KiB=507264，PID/cgroup结束=True。

启动 v7-verify-b1-exchange-c3，unit=step34-v7-verify-b1-exchange-c3，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-verify-b1-exchange-c3：passed=True，reason=exited，peak_threads=46，RSS_KiB=490996，PID/cgroup结束=True。

启动 v7-cost-b1-compute-control，unit=step34-v7-cost-b1-compute-control，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-cost-b1-compute-control：passed=True，reason=exited，peak_threads=40，RSS_KiB=280796，PID/cgroup结束=True。

启动 v7-cost-b1-compute-new，unit=step34-v7-cost-b1-compute-new，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-cost-b1-compute-new：passed=True，reason=exited，peak_threads=22，RSS_KiB=276660，PID/cgroup结束=True。

启动 v7-cost-b1-fact-control，unit=step34-v7-cost-b1-fact-control，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-cost-b1-fact-control：passed=True，reason=exited，peak_threads=40，RSS_KiB=288224，PID/cgroup结束=True。

启动 v7-cost-b1-fact-new，unit=step34-v7-cost-b1-fact-new，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-cost-b1-fact-new：passed=True，reason=exited，peak_threads=22，RSS_KiB=299296，PID/cgroup结束=True。

启动 v7-cost-b1-erc721-control，unit=step34-v7-cost-b1-erc721-control，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-cost-b1-erc721-control：passed=True，reason=exited，peak_threads=40，RSS_KiB=302444，PID/cgroup结束=True。

启动 v7-cost-b1-erc721-new，unit=step34-v7-cost-b1-erc721-new，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-cost-b1-erc721-new：passed=True，reason=exited，peak_threads=23，RSS_KiB=301248，PID/cgroup结束=True。

启动 v7-cost-b1-exchange-control，unit=step34-v7-cost-b1-exchange-control，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-cost-b1-exchange-control：passed=True，reason=exited，peak_threads=176，RSS_KiB=567116，PID/cgroup结束=True。

启动 v7-cost-b1-exchange-new，unit=step34-v7-cost-b1-exchange-new，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-cost-b1-exchange-new：passed=True，reason=exited，peak_threads=45，RSS_KiB=517688，PID/cgroup结束=True。

最终build6验证批1完成：四合约四组正确性与同代码Store架构成本，所有区块/配对已落盘。

启动 v7-verify-b2-compute-c0，unit=step34-v7-verify-b2-compute-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-verify-b2-compute-c0：passed=True，reason=exited，peak_threads=26，RSS_KiB=349976，PID/cgroup结束=True。

启动 v7-verify-b2-compute-c1，unit=step34-v7-verify-b2-compute-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-verify-b2-compute-c1：passed=True，reason=exited，peak_threads=25，RSS_KiB=375480，PID/cgroup结束=True。

启动 v7-verify-b2-fact-c0，unit=step34-v7-verify-b2-fact-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-verify-b2-fact-c0：passed=True，reason=exited，peak_threads=22，RSS_KiB=371816，PID/cgroup结束=True。

启动 v7-verify-b2-fact-c1，unit=step34-v7-verify-b2-fact-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-verify-b2-fact-c1：passed=True，reason=exited，peak_threads=23，RSS_KiB=400680，PID/cgroup结束=True。

启动 v7-verify-b2-erc721-c0，unit=step34-v7-verify-b2-erc721-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-verify-b2-erc721-c0：passed=True，reason=exited，peak_threads=22，RSS_KiB=400508，PID/cgroup结束=True。

启动 v7-verify-b2-erc721-c1，unit=step34-v7-verify-b2-erc721-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-verify-b2-erc721-c1：passed=True，reason=exited，peak_threads=23，RSS_KiB=409668，PID/cgroup结束=True。

启动 v7-verify-b2-exchange-c0，unit=step34-v7-verify-b2-exchange-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-verify-b2-exchange-c0：passed=True，reason=exited，peak_threads=28，RSS_KiB=479924，PID/cgroup结束=True。

启动 v7-verify-b2-exchange-c1，unit=step34-v7-verify-b2-exchange-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-verify-b2-exchange-c1：passed=True，reason=exited，peak_threads=28，RSS_KiB=493212，PID/cgroup结束=True。

启动 v7-verify-b2-exchange-c2，unit=step34-v7-verify-b2-exchange-c2，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-verify-b2-exchange-c2：passed=True，reason=exited，peak_threads=30，RSS_KiB=515188，PID/cgroup结束=True。

启动 v7-verify-b2-exchange-c3，unit=step34-v7-verify-b2-exchange-c3，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-verify-b2-exchange-c3：passed=True，reason=exited，peak_threads=47，RSS_KiB=530980，PID/cgroup结束=True。

启动 v7-cost-b2-compute-new，unit=step34-v7-cost-b2-compute-new，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-cost-b2-compute-new：passed=True，reason=exited，peak_threads=22，RSS_KiB=268120，PID/cgroup结束=True。

启动 v7-cost-b2-compute-control，unit=step34-v7-cost-b2-compute-control，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-cost-b2-compute-control：passed=True，reason=exited，peak_threads=40，RSS_KiB=282956，PID/cgroup结束=True。

启动 v7-cost-b2-fact-new，unit=step34-v7-cost-b2-fact-new，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-cost-b2-fact-new：passed=True，reason=exited，peak_threads=24，RSS_KiB=272396，PID/cgroup结束=True。

启动 v7-cost-b2-fact-control，unit=step34-v7-cost-b2-fact-control，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-cost-b2-fact-control：passed=True，reason=exited，peak_threads=40，RSS_KiB=296340，PID/cgroup结束=True。

启动 v7-cost-b2-erc721-new，unit=step34-v7-cost-b2-erc721-new，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-cost-b2-erc721-new：passed=True，reason=exited，peak_threads=23，RSS_KiB=291752，PID/cgroup结束=True。

启动 v7-cost-b2-erc721-control，unit=step34-v7-cost-b2-erc721-control，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-cost-b2-erc721-control：passed=True，reason=exited，peak_threads=40，RSS_KiB=300520，PID/cgroup结束=True。

启动 v7-cost-b2-exchange-new，unit=step34-v7-cost-b2-exchange-new，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-cost-b2-exchange-new：passed=True，reason=exited，peak_threads=46，RSS_KiB=522156，PID/cgroup结束=True。

启动 v7-cost-b2-exchange-control，unit=step34-v7-cost-b2-exchange-control，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-cost-b2-exchange-control：passed=True，reason=exited，peak_threads=176，RSS_KiB=551732，PID/cgroup结束=True。

最终build6验证批2完成：四合约四组正确性与同代码Store架构成本，所有区块/配对已落盘。

启动 v7-verify-b3-compute-c0，unit=step34-v7-verify-b3-compute-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-verify-b3-compute-c0：passed=True，reason=exited，peak_threads=25，RSS_KiB=374476，PID/cgroup结束=True。

启动 v7-verify-b3-compute-c1，unit=step34-v7-verify-b3-compute-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-verify-b3-compute-c1：passed=True，reason=exited，peak_threads=26，RSS_KiB=365420，PID/cgroup结束=True。

启动 v7-verify-b3-fact-c0，unit=step34-v7-verify-b3-fact-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-verify-b3-fact-c0：passed=True，reason=exited，peak_threads=22，RSS_KiB=412408，PID/cgroup结束=True。

启动 v7-verify-b3-fact-c1，unit=step34-v7-verify-b3-fact-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-verify-b3-fact-c1：passed=True，reason=exited，peak_threads=22，RSS_KiB=380996，PID/cgroup结束=True。

启动 v7-verify-b3-erc721-c0，unit=step34-v7-verify-b3-erc721-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-verify-b3-erc721-c0：passed=True，reason=exited，peak_threads=26，RSS_KiB=422364，PID/cgroup结束=True。

启动 v7-verify-b3-erc721-c1，unit=step34-v7-verify-b3-erc721-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-verify-b3-erc721-c1：passed=True，reason=exited，peak_threads=26，RSS_KiB=384872，PID/cgroup结束=True。

启动 v7-verify-b3-exchange-c0，unit=step34-v7-verify-b3-exchange-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-verify-b3-exchange-c0：passed=True，reason=exited，peak_threads=30，RSS_KiB=533604，PID/cgroup结束=True。

启动 v7-verify-b3-exchange-c1，unit=step34-v7-verify-b3-exchange-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-verify-b3-exchange-c1：passed=True，reason=exited，peak_threads=47，RSS_KiB=531704，PID/cgroup结束=True。

启动 v7-verify-b3-exchange-c2，unit=step34-v7-verify-b3-exchange-c2，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-verify-b3-exchange-c2：passed=True，reason=exited，peak_threads=29，RSS_KiB=504692，PID/cgroup结束=True。

启动 v7-verify-b3-exchange-c3，unit=step34-v7-verify-b3-exchange-c3，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-verify-b3-exchange-c3：passed=True，reason=exited，peak_threads=34，RSS_KiB=478920，PID/cgroup结束=True。

启动 v7-cost-b3-compute-control，unit=step34-v7-cost-b3-compute-control，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-cost-b3-compute-control：passed=True，reason=exited，peak_threads=41，RSS_KiB=275984，PID/cgroup结束=True。

启动 v7-cost-b3-compute-new，unit=step34-v7-cost-b3-compute-new，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-cost-b3-compute-new：passed=True，reason=exited，peak_threads=23，RSS_KiB=284412，PID/cgroup结束=True。

启动 v7-cost-b3-fact-control，unit=step34-v7-cost-b3-fact-control，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-cost-b3-fact-control：passed=True，reason=exited，peak_threads=40，RSS_KiB=308048，PID/cgroup结束=True。

启动 v7-cost-b3-fact-new，unit=step34-v7-cost-b3-fact-new，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-cost-b3-fact-new：passed=True，reason=exited，peak_threads=23，RSS_KiB=288184，PID/cgroup结束=True。

启动 v7-cost-b3-erc721-control，unit=step34-v7-cost-b3-erc721-control，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-cost-b3-erc721-control：passed=True，reason=exited，peak_threads=40，RSS_KiB=312292，PID/cgroup结束=True。

启动 v7-cost-b3-erc721-new，unit=step34-v7-cost-b3-erc721-new，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-cost-b3-erc721-new：passed=True，reason=exited，peak_threads=24，RSS_KiB=312208，PID/cgroup结束=True。

启动 v7-cost-b3-exchange-control，unit=step34-v7-cost-b3-exchange-control，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-cost-b3-exchange-control：passed=True，reason=exited，peak_threads=176，RSS_KiB=551288，PID/cgroup结束=True。

启动 v7-cost-b3-exchange-new，unit=step34-v7-cost-b3-exchange-new，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-cost-b3-exchange-new：passed=True，reason=exited，peak_threads=46，RSS_KiB=534276，PID/cgroup结束=True。

最终build6验证批3完成：四合约四组正确性与同代码Store架构成本，所有区块/配对已落盘。

启动 v7-s1-compute-c0，unit=step34-v7-s1-compute-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-s1-compute-c0：passed=True，reason=exited，peak_threads=25，RSS_KiB=375924，PID/cgroup结束=True。

启动 v7-s1-compute-c1，unit=step34-v7-s1-compute-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-s1-compute-c1：passed=True，reason=exited，peak_threads=26，RSS_KiB=357028，PID/cgroup结束=True。

启动 v7-s1-fact-c0，unit=step34-v7-s1-fact-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-s1-fact-c0：passed=True，reason=exited，peak_threads=26，RSS_KiB=407756，PID/cgroup结束=True。

启动 v7-s1-fact-c1，unit=step34-v7-s1-fact-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-s1-fact-c1：passed=True，reason=exited，peak_threads=22，RSS_KiB=360080，PID/cgroup结束=True。

启动 v7-s1-erc721-c0，unit=step34-v7-s1-erc721-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-s1-erc721-c0：passed=True，reason=exited，peak_threads=26，RSS_KiB=418408，PID/cgroup结束=True。

启动 v7-s1-erc721-c1，unit=step34-v7-s1-erc721-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-s1-erc721-c1：passed=True，reason=exited，peak_threads=22，RSS_KiB=381388，PID/cgroup结束=True。

启动 v7-s1-exchange-c0，unit=step34-v7-s1-exchange-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-s1-exchange-c0：passed=True，reason=exited，peak_threads=32，RSS_KiB=517116，PID/cgroup结束=True。

启动 v7-s1-exchange-c1，unit=step34-v7-s1-exchange-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-s1-exchange-c1：passed=True，reason=exited，peak_threads=47，RSS_KiB=529672，PID/cgroup结束=True。

启动 v7-s1-exchange-c2，unit=step34-v7-s1-exchange-c2，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-s1-exchange-c2：passed=True，reason=exited，peak_threads=46，RSS_KiB=495888，PID/cgroup结束=True。

启动 v7-s1-exchange-c3，unit=step34-v7-s1-exchange-c3，pairs=one split block chunk, max2 targets；命令已保存。

结束 v7-s1-exchange-c3：passed=True，reason=exited，peak_threads=30，RSS_KiB=513636，PID/cgroup结束=True。

普通构建已修复。错误路径复查原dRuntime继承CallMethod错误被gasErr覆盖的逻辑，build8修复为保留原CallMethod错误（Gas计算不改）；新增缺失方法与真实unreachable trap用例，当前资料全部保留，最终统计单列build8。

启动 v9-owner-freeze，unit=step34-v9-owner-freeze，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-owner-freeze：passed=True，reason=exited，peak_threads=5，RSS_KiB=44064，PID/cgroup结束=True。

启动 v9-poison-freeze，unit=step34-v9-poison-freeze，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-poison-freeze：passed=True，reason=exited，peak_threads=5，RSS_KiB=41596，PID/cgroup结束=True。

启动 v9-freeze-fault-store，unit=step34-v9-freeze-fault-store，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-freeze-fault-store：passed=True，reason=exited，peak_threads=23，RSS_KiB=286380，PID/cgroup结束=True。

启动 v9-freeze-fault-wasi，unit=step34-v9-freeze-fault-wasi，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-freeze-fault-wasi：passed=True，reason=exited，peak_threads=23，RSS_KiB=292108，PID/cgroup结束=True。

启动 v9-freeze-fault-instance，unit=step34-v9-freeze-fault-instance，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-freeze-fault-instance：passed=True，reason=exited，peak_threads=23，RSS_KiB=294696，PID/cgroup结束=True。

启动 v9-freeze-fault-initialize，unit=step34-v9-freeze-fault-initialize，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-freeze-fault-initialize：passed=True，reason=exited，peak_threads=22，RSS_KiB=292512，PID/cgroup结束=True。

启动 v9-freeze-fault-execute，unit=step34-v9-freeze-fault-execute，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-freeze-fault-execute：passed=True，reason=exited，peak_threads=23，RSS_KiB=293980，PID/cgroup结束=True。

启动 v9-freeze-fault-close，unit=step34-v9-freeze-fault-close，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-freeze-fault-close：passed=True，reason=exited，peak_threads=24，RSS_KiB=290016，PID/cgroup结束=True。

启动 v9-freeze-fault-cancel-wasi，unit=step34-v9-freeze-fault-cancel-wasi，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-freeze-fault-cancel-wasi：passed=True，reason=exited，peak_threads=23，RSS_KiB=300008，PID/cgroup结束=True。

启动 v9-freeze-fault-cancel-close，unit=step34-v9-freeze-fault-cancel-close，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-freeze-fault-cancel-close：passed=True，reason=exited，peak_threads=25，RSS_KiB=286948，PID/cgroup结束=True。

启动 v9-business-error-erc721，unit=step34-v9-business-error-erc721，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-business-error-erc721：passed=True，reason=exited，peak_threads=23，RSS_KiB=303096，PID/cgroup结束=True。

启动 v9-business-error-exchange，unit=step34-v9-business-error-exchange，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-business-error-exchange：passed=True，reason=exited，peak_threads=47，RSS_KiB=517496，PID/cgroup结束=True。

启动 v9-business-error-fact，unit=step34-v9-business-error-fact，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-business-error-fact：passed=True，reason=exited，peak_threads=23，RSS_KiB=289372，PID/cgroup结束=True。

启动 v9-verify-b1-compute-c0，unit=step34-v9-verify-b1-compute-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-verify-b1-compute-c0：passed=True，reason=exited，peak_threads=26，RSS_KiB=382688，PID/cgroup结束=True。

启动 v9-verify-b1-compute-c1，unit=step34-v9-verify-b1-compute-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-verify-b1-compute-c1：passed=True，reason=exited，peak_threads=26，RSS_KiB=359016，PID/cgroup结束=True。

启动 v9-verify-b1-fact-c0，unit=step34-v9-verify-b1-fact-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-verify-b1-fact-c0：passed=True，reason=exited，peak_threads=23，RSS_KiB=394056，PID/cgroup结束=True。

启动 v9-verify-b1-fact-c1，unit=step34-v9-verify-b1-fact-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-verify-b1-fact-c1：passed=True，reason=exited，peak_threads=22，RSS_KiB=374100，PID/cgroup结束=True。

启动 v9-verify-b1-erc721-c0，unit=step34-v9-verify-b1-erc721-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-verify-b1-erc721-c0：passed=True，reason=exited，peak_threads=23，RSS_KiB=420516，PID/cgroup结束=True。

启动 v9-verify-b1-erc721-c1，unit=step34-v9-verify-b1-erc721-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-verify-b1-erc721-c1：passed=True，reason=exited，peak_threads=23，RSS_KiB=381892，PID/cgroup结束=True。

启动 v9-verify-b1-exchange-c0，unit=step34-v9-verify-b1-exchange-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-verify-b1-exchange-c0：passed=True，reason=exited，peak_threads=43，RSS_KiB=535824，PID/cgroup结束=True。

启动 v9-verify-b1-exchange-c1，unit=step34-v9-verify-b1-exchange-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-verify-b1-exchange-c1：passed=True，reason=exited，peak_threads=47，RSS_KiB=535032，PID/cgroup结束=True。

启动 v9-verify-b1-exchange-c2，unit=step34-v9-verify-b1-exchange-c2，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-verify-b1-exchange-c2：passed=True，reason=exited，peak_threads=46，RSS_KiB=503304，PID/cgroup结束=True。

启动 v9-verify-b1-exchange-c3，unit=step34-v9-verify-b1-exchange-c3，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-verify-b1-exchange-c3：passed=True，reason=exited，peak_threads=46，RSS_KiB=511212，PID/cgroup结束=True。

启动 v9-cost-b1-compute-control，unit=step34-v9-cost-b1-compute-control，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-cost-b1-compute-control：passed=True，reason=exited，peak_threads=40，RSS_KiB=283512，PID/cgroup结束=True。

启动 v9-cost-b1-compute-new，unit=step34-v9-cost-b1-compute-new，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-cost-b1-compute-new：passed=True，reason=exited，peak_threads=22，RSS_KiB=283096，PID/cgroup结束=True。

启动 v9-cost-b1-fact-control，unit=step34-v9-cost-b1-fact-control，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-cost-b1-fact-control：passed=True，reason=exited，peak_threads=40，RSS_KiB=305788，PID/cgroup结束=True。

启动 v9-cost-b1-fact-new，unit=step34-v9-cost-b1-fact-new，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-cost-b1-fact-new：passed=True，reason=exited，peak_threads=22，RSS_KiB=295760，PID/cgroup结束=True。

启动 v9-cost-b1-erc721-control，unit=step34-v9-cost-b1-erc721-control，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-cost-b1-erc721-control：passed=True，reason=exited，peak_threads=40，RSS_KiB=304020，PID/cgroup结束=True。

启动 v9-cost-b1-erc721-new，unit=step34-v9-cost-b1-erc721-new，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-cost-b1-erc721-new：passed=True，reason=exited，peak_threads=23，RSS_KiB=297560，PID/cgroup结束=True。

启动 v9-cost-b1-exchange-control，unit=step34-v9-cost-b1-exchange-control，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-cost-b1-exchange-control：passed=True，reason=exited，peak_threads=176，RSS_KiB=581000，PID/cgroup结束=True。

启动 v9-cost-b1-exchange-new，unit=step34-v9-cost-b1-exchange-new，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-cost-b1-exchange-new：passed=True，reason=exited，peak_threads=46，RSS_KiB=508440，PID/cgroup结束=True。

最终build6验证批1完成：四合约四组正确性与同代码Store架构成本，所有区块/配对已落盘。

启动 v9-verify-b2-compute-c0，unit=step34-v9-verify-b2-compute-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-verify-b2-compute-c0：passed=True，reason=exited，peak_threads=26，RSS_KiB=368752，PID/cgroup结束=True。

启动 v9-verify-b2-compute-c1，unit=step34-v9-verify-b2-compute-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-verify-b2-compute-c1：passed=True，reason=exited，peak_threads=26，RSS_KiB=383068，PID/cgroup结束=True。

启动 v9-verify-b2-fact-c0，unit=step34-v9-verify-b2-fact-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-verify-b2-fact-c0：passed=True，reason=exited，peak_threads=24，RSS_KiB=373512，PID/cgroup结束=True。

启动 v9-verify-b2-fact-c1，unit=step34-v9-verify-b2-fact-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-verify-b2-fact-c1：passed=True，reason=exited，peak_threads=25，RSS_KiB=401860，PID/cgroup结束=True。

启动 v9-verify-b2-erc721-c0，unit=step34-v9-verify-b2-erc721-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-verify-b2-erc721-c0：passed=True，reason=exited，peak_threads=22，RSS_KiB=375576，PID/cgroup结束=True。

启动 v9-verify-b2-erc721-c1，unit=step34-v9-verify-b2-erc721-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-verify-b2-erc721-c1：passed=True，reason=exited，peak_threads=23，RSS_KiB=425056，PID/cgroup结束=True。

启动 v9-verify-b2-exchange-c0，unit=step34-v9-verify-b2-exchange-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-verify-b2-exchange-c0：passed=True，reason=exited，peak_threads=47，RSS_KiB=495060，PID/cgroup结束=True。

启动 v9-verify-b2-exchange-c1，unit=step34-v9-verify-b2-exchange-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-verify-b2-exchange-c1：passed=True，reason=exited，peak_threads=48，RSS_KiB=496832，PID/cgroup结束=True。

启动 v9-verify-b2-exchange-c2，unit=step34-v9-verify-b2-exchange-c2，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-verify-b2-exchange-c2：passed=True，reason=exited，peak_threads=45，RSS_KiB=525388，PID/cgroup结束=True。

启动 v9-verify-b2-exchange-c3，unit=step34-v9-verify-b2-exchange-c3，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-verify-b2-exchange-c3：passed=True，reason=exited，peak_threads=45，RSS_KiB=522244，PID/cgroup结束=True。

启动 v9-cost-b2-compute-new，unit=step34-v9-cost-b2-compute-new，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-cost-b2-compute-new：passed=True，reason=exited，peak_threads=24，RSS_KiB=276040，PID/cgroup结束=True。

启动 v9-cost-b2-compute-control，unit=step34-v9-cost-b2-compute-control，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-cost-b2-compute-control：passed=True，reason=exited，peak_threads=40，RSS_KiB=280528，PID/cgroup结束=True。

启动 v9-cost-b2-fact-new，unit=step34-v9-cost-b2-fact-new，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-cost-b2-fact-new：passed=True，reason=exited，peak_threads=24，RSS_KiB=286360，PID/cgroup结束=True。

启动 v9-cost-b2-fact-control，unit=step34-v9-cost-b2-fact-control，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-cost-b2-fact-control：passed=True，reason=exited，peak_threads=40，RSS_KiB=293648，PID/cgroup结束=True。

启动 v9-cost-b2-erc721-new，unit=step34-v9-cost-b2-erc721-new，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-cost-b2-erc721-new：passed=True，reason=exited，peak_threads=24，RSS_KiB=299080，PID/cgroup结束=True。

启动 v9-cost-b2-erc721-control，unit=step34-v9-cost-b2-erc721-control，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-cost-b2-erc721-control：passed=True，reason=exited，peak_threads=40，RSS_KiB=313172，PID/cgroup结束=True。

启动 v9-cost-b2-exchange-new，unit=step34-v9-cost-b2-exchange-new，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-cost-b2-exchange-new：passed=True，reason=exited，peak_threads=43，RSS_KiB=517588，PID/cgroup结束=True。

启动 v9-cost-b2-exchange-control，unit=step34-v9-cost-b2-exchange-control，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-cost-b2-exchange-control：passed=True，reason=exited，peak_threads=176，RSS_KiB=537120，PID/cgroup结束=True。

最终build6验证批2完成：四合约四组正确性与同代码Store架构成本，所有区块/配对已落盘。

启动 v9-verify-b3-compute-c0，unit=step34-v9-verify-b3-compute-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-verify-b3-compute-c0：passed=True，reason=exited，peak_threads=26，RSS_KiB=389824，PID/cgroup结束=True。

启动 v9-verify-b3-compute-c1，unit=step34-v9-verify-b3-compute-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-verify-b3-compute-c1：passed=True，reason=exited，peak_threads=23，RSS_KiB=347316，PID/cgroup结束=True。

启动 v9-verify-b3-fact-c0，unit=step34-v9-verify-b3-fact-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-verify-b3-fact-c0：passed=True，reason=exited，peak_threads=26，RSS_KiB=412224，PID/cgroup结束=True。

启动 v9-verify-b3-fact-c1，unit=step34-v9-verify-b3-fact-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-verify-b3-fact-c1：passed=True，reason=exited，peak_threads=23，RSS_KiB=368540，PID/cgroup结束=True。

启动 v9-verify-b3-erc721-c0，unit=step34-v9-verify-b3-erc721-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-verify-b3-erc721-c0：passed=True，reason=exited，peak_threads=22，RSS_KiB=413632，PID/cgroup结束=True。

启动 v9-verify-b3-erc721-c1，unit=step34-v9-verify-b3-erc721-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-verify-b3-erc721-c1：passed=True，reason=exited，peak_threads=23，RSS_KiB=395716，PID/cgroup结束=True。

启动 v9-verify-b3-exchange-c0，unit=step34-v9-verify-b3-exchange-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-verify-b3-exchange-c0：passed=True，reason=exited，peak_threads=28，RSS_KiB=538216，PID/cgroup结束=True。

启动 v9-verify-b3-exchange-c1，unit=step34-v9-verify-b3-exchange-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-verify-b3-exchange-c1：passed=True，reason=exited，peak_threads=45，RSS_KiB=520200，PID/cgroup结束=True。

启动 v9-verify-b3-exchange-c2，unit=step34-v9-verify-b3-exchange-c2，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-verify-b3-exchange-c2：passed=True，reason=exited，peak_threads=44，RSS_KiB=497788，PID/cgroup结束=True。

启动 v9-verify-b3-exchange-c3，unit=step34-v9-verify-b3-exchange-c3，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-verify-b3-exchange-c3：passed=True，reason=exited，peak_threads=44，RSS_KiB=472612，PID/cgroup结束=True。

启动 v9-cost-b3-compute-control，unit=step34-v9-cost-b3-compute-control，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-cost-b3-compute-control：passed=True，reason=exited，peak_threads=40，RSS_KiB=275436，PID/cgroup结束=True。

启动 v9-cost-b3-compute-new，unit=step34-v9-cost-b3-compute-new，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-cost-b3-compute-new：passed=True，reason=exited，peak_threads=24，RSS_KiB=277716，PID/cgroup结束=True。

启动 v9-cost-b3-fact-control，unit=step34-v9-cost-b3-fact-control，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-cost-b3-fact-control：passed=True，reason=exited，peak_threads=40，RSS_KiB=293756，PID/cgroup结束=True。

启动 v9-cost-b3-fact-new，unit=step34-v9-cost-b3-fact-new，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-cost-b3-fact-new：passed=True，reason=exited，peak_threads=23，RSS_KiB=291720，PID/cgroup结束=True。

启动 v9-cost-b3-erc721-control，unit=step34-v9-cost-b3-erc721-control，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-cost-b3-erc721-control：passed=True，reason=exited，peak_threads=40，RSS_KiB=304804，PID/cgroup结束=True。

启动 v9-cost-b3-erc721-new，unit=step34-v9-cost-b3-erc721-new，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-cost-b3-erc721-new：passed=True，reason=exited，peak_threads=22，RSS_KiB=297148，PID/cgroup结束=True。

启动 v9-cost-b3-exchange-control，unit=step34-v9-cost-b3-exchange-control，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-cost-b3-exchange-control：passed=True，reason=exited，peak_threads=176，RSS_KiB=557088，PID/cgroup结束=True。

启动 v9-cost-b3-exchange-new，unit=step34-v9-cost-b3-exchange-new，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-cost-b3-exchange-new：passed=True，reason=exited，peak_threads=45，RSS_KiB=524220，PID/cgroup结束=True。

最终build6验证批3完成：四合约四组正确性与同代码Store架构成本，所有区块/配对已落盘。

启动 v9-s1-compute-c0，unit=step34-v9-s1-compute-c0，pairs=one split block chunk, max2 targets；命令已保存。

启动 v9-race-owner，unit=step34-v9-race-owner，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-s1-compute-c0：passed=True，reason=exited，peak_threads=26，RSS_KiB=384256，PID/cgroup结束=True。

启动 v9-s1-compute-c1，unit=step34-v9-s1-compute-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-race-owner：passed=True，reason=exited，peak_threads=19，RSS_KiB=88544，PID/cgroup结束=True。

启动 v9-race-poison，unit=step34-v9-race-poison，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-s1-compute-c1：passed=True，reason=exited，peak_threads=25，RSS_KiB=361580，PID/cgroup结束=True。

启动 v9-s1-fact-c0，unit=step34-v9-s1-fact-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-race-poison：passed=True，reason=exited，peak_threads=6，RSS_KiB=81392，PID/cgroup结束=True。

结束 v9-s1-fact-c0：passed=True，reason=exited，peak_threads=22，RSS_KiB=405708，PID/cgroup结束=True。

启动 v9-s1-fact-c1，unit=step34-v9-s1-fact-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-s1-fact-c1：passed=True，reason=exited，peak_threads=24，RSS_KiB=375336，PID/cgroup结束=True。

启动 v9-s1-erc721-c0，unit=step34-v9-s1-erc721-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-s1-erc721-c0：passed=True，reason=exited，peak_threads=23，RSS_KiB=413020，PID/cgroup结束=True。

启动 v9-s1-erc721-c1，unit=step34-v9-s1-erc721-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-s1-erc721-c1：passed=True，reason=exited，peak_threads=24，RSS_KiB=395128，PID/cgroup结束=True。

启动 v9-s1-exchange-c0，unit=step34-v9-s1-exchange-c0，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-s1-exchange-c0：passed=True，reason=exited，peak_threads=45，RSS_KiB=529308，PID/cgroup结束=True。

启动 v9-s1-exchange-c1，unit=step34-v9-s1-exchange-c1，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-s1-exchange-c1：passed=True，reason=exited，peak_threads=46，RSS_KiB=535772，PID/cgroup结束=True。

启动 v9-s1-exchange-c2，unit=step34-v9-s1-exchange-c2，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-s1-exchange-c2：passed=True，reason=exited，peak_threads=47，RSS_KiB=511944，PID/cgroup结束=True。

启动 v9-s1-exchange-c3，unit=step34-v9-s1-exchange-c3，pairs=one split block chunk, max2 targets；命令已保存。

结束 v9-s1-exchange-c3：passed=True，reason=exited，peak_threads=48，RSS_KiB=508004，PID/cgroup结束=True。

离线检查发现执行wrapper已加版本前缀，但派生block/pair元数据labels忘加前缀，可能误读早期记录。原元数据备份audit/block-metadata-prefix-correction，按真实prefix+label修正并断言对应outcome存在；原始日志/收据未动，不重跑样本；统计重新计算并严格校验前缀及binary SHA。

完成：build9三轮四组12区块48根、72 buyNow子调用，另12个同代码架构直接配对；故障/恢复、真实业务错误、缺失方法、native trap、S1 hash、Race owner/poison与非test go build均通过。普通构建依赖问题和错误传播已修复，原始中间失败保留。生产main状态未变，无step34活动unit。SAFETY_GATE只放行原型，节点E2E未准入；下一项为节点owner/cache/Reset/Stop接线及smoke。
