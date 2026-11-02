# 版本与构建来源

CVW独立工作树`.worktrees/cvw-step36`、节点`.worktrees/node-step36`，均独立分支`experiment/step36-e2e-copy-acopy`。

- CVW父提交885db6465a0aeee59ce2c06ffb8c4833049e5aaf。
- 节点父提交0ce8fba61761f0ced5fb598ab28727080706577a。
- native Wasmer6.0.1 Selector修复库SHA-256：56b236ce1772b805819aec7c10eb417cd62bf0c6ee2c9b581e651f746bec17dc。
- 实际库路径：`.worktrees/cvw-step35b/experiments/instance-lifecycle/step-35b-native-wasi-thread/libraries/patched/libwasmer.so`。
- 正式node3 SHA：c93bef9a1b38285363afd386a0d77b81b39ccd1b821fe85dd822b30efe15083d。
- 正式client2 SHA：33b16cc3f5e15d9547d2d20fa5fba1a13146329d7a75b345a35d8938dfa6bd07。
- **实际二进制均Go1.25.0**，以audit/*-buildinfo.txt为准，不沿用历史报告Go版本。SDKv2.4.0、pb/commonv2.4.0及local replaces完整在buildinfo/go.mod。

所有762份加载maps均指向上述修复库，验证见audit/loaded-native-check.json。命令启动前重复校验库SHA，未替换生产库。

Guest来自Step18/33同源95903a3家族，无B1。inputs/variants.json完整列32个组引用、16个唯一plain/A产物的SHA、路径和历史组映射。G0 Fresh=A0/Copy0；G1 Copy=A0/Copy1；G2 A+Copy=A1/Copy1；G3 A-only=A1/Copy0。A0与A1二进制不同但来自同一业务源码/输入；实际Gas由逐槽核对确定，不预设跨二进制必然相同。Step24B原始WASM未用于本轮。

节点最小增量：go.mod local replace到本实验VM/Store；启动只读proposer_ready观测。Store增量为既有drain lease下只读状态验证端点；业务/关闭/Gas/Guest语义未改。客户端为同步serial批执行与单调计时。audit/node-working-diff.patch保存节点diff，Store/VM相对35C的diff另存source-diff.patch。

node3构建清单对source/client.go的旧hash是构建脚本遍历整个source目录的附带记录；node构建不导入该main文件。正式客户端使用client2清单与当前source/client.go，哈希吻合；所有node实际VM/Store输入文件与node3清单吻合。客户端和节点没有交错混用版本。原node构建GetState未定义失败保留audit/node.log；node2仅基础设施预检，主统计仅node3/client2。

构建命令audit/node3-command.json、client2-command.json；源码hash在outcome，配置audit/node.yml、chain.yml、sdk.yml，环境audit/environment.txt。配置仅引用测试证书/密钥路径，未打包私钥。二进制和so不入Git，可由固定来源重建；运行需已有隔离测试证书、历史local dependency目录及原测试网络模板，不是脱离CVW的零依赖安装包。

节点本轮最终提交：c28bfa89c61531b2e61acb41bf69c4c06d142ba8。CVW报告提交见本独立分支Git HEAD；构建在提交前完成，准确输入以binary SHA和source_hashes为准。
