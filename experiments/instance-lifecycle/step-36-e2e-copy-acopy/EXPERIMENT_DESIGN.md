# 冻结设计（任何正式样本开始前）

一个隔离节点，Common0，同步单客户端SendRequestSync，1536MiB/220线程软限，无A/B1以外隐藏优化（本轮B1禁用），同一Step35B Selector补丁so与Step35C关闭协议。

主组G0 Fresh，G1 Copy，G2 A+Copy；G3 A-only已有同源构建且不增加每进程资源，预检与正式均纳入；单方法任一组失败则该方法不进性能主统计。Guest来自Step18/33同源家族95903a3，组别映射已明确，模板依最终Guest重新生成。

每方法先三组功能预检，之后3个独立批次；每批四组顺序G0/G1/G2/G3、G2/G3/G0/G1、G1/G0/G3/G2；三批不可能完全覆盖四个位置，披露这一限制。每组独立进程+等价seed克隆，无历史样本混用。初步只作节点可启动/部署检查后，在任何正式性能数据产生前，样本数从原预案2调整为4次/组/批，以仍满足Owner32任务限制的条件增加独立新样本；alterAdminAddress保留1次，因为业务会撤销原发送者权限，不通过修改业务负载凑样本。N12或N3均为探索性，不宣称普遍结论。

Module编译、模板准备、部署、fixture前置、1次不提交的Query预热均在主窗口外。正式调用使用InvokeContract(...,true)，即使目标是读取方法也提交真实事务。每批TPS窗口为本组第1笔SDK Invoke开始到最后1笔SDK返回，所有目标调用在Go进程内串行，无Python往返间隔。失败后中止，保留全部已发记录。窗口结束后查询TxID/RWset和实际账本键，不把验证耗时纳入窗口；只有窗口内成功响应且随后查证提交的唯一交易才进分子。没有观察窗口外发出的交易。

读取setup可复用同一个静态token；mint/transfer/approve/buyNow等写入路径预置或使用不同tokenId，每组序列一致，所有setup在窗口之前。identity增删使用相同长度、确定的独立地址。Query预热不提交，不能复用执行业务Instance。

配对单位batch+slot：同输入及等价初态，差值G0-G1、G1-G2、G0-G2直接计算，不用独立Median相减。bootstrap seed固定，分层批次结果全部保留，低N、只有3个独立批次和多方法筛选限制须披露。P50=Median，P95明确线性分位数。节点源沿用诊断计时，因此结论仅限该实验构建，不能替代生产最大TPS。

新增唯一代码为测量客户端以及测量窗口外的只读账本校验端点；校验用真实ReadObject，持同一生命周期租约，未修改VM/Guest/Gas和关闭协议。首次构建误用不存在GetState接口失败，已改为现有ReadObject并另存node2成功构建。无版本升级。

在首个基础设施预检、正式采样开始前补充：每个节点等待真实proposer_ready事件（原Solo约3s延迟，不修改其逻辑），再预热/进入窗口；不是请求节奏Sleep。此前node2的compute预检只作基础设施Smoke，正式全部使用node3同一冻结二进制。

配对事务输入：独立等价账本中的同一case/batch/slot使用相同确定TxID，避免随机TxID改变history JSON排序/Gas；每个账本内不重复。全局请求ID=run namespace+TxID，跨组不能只按TxID去重；TPS每个窗口单独计算。SDK自己生成的时间戳仍真实保留，历史元数据规范化须显式标明，不能任意删除业务输入时间。

## 最终执行记录与补充验证

37方法均完成三批四组；35方法每组12次，identity.alterAdminAddress每组3次（首笔改管理员后当前签名者失权，不能伪造等价重复），raffle.raffle每组9次。raffle原计划4次超过三人名单，原失败窗口完整保留，改为相同三人名单3次，作为revision1重新独立三批。总有效正式提交1728、窗口444。

所有方法batch3各组账本另外重启查询（148次），每合约每组无效export错误回滚+raffle空名单真实错误，共36次。此补充在正式窗口外执行，不进入主TPS。并非逐方法全部业务异常路径测试。

统计脚本analyze.py输出直接成对分布；report.py和stages.py只复算，不启动节点。对应源码与窗口详见SDK_TIMING_CODE.md；源版本与构建详见BUILD_LINEAGE.md。
