# 执行与回退

本目录是**真实节点**实验，不是mock TxSimContext的VM微基准。限制与所有负结果见README.md、AUDIT.md。当前原型不支持在线reset/升级/缓存逐出，不可部署到正式节点。

## 已完成的执行

```bash
python3 run.py bench --batch a --n 100 --workers 1
python3 run.py bench --batch b --n 100 --workers 1
python3 run.py bench --batch a4 --n 64 --workers 4
python3 run.py bench --batch b4 --n 64 --workers 4
python3 analyze.py
python3 verify_node.py ledger
python3 verify_node.py diagnostic
python3 diagnostic_extra.py
python3 build_results.py
python3 write_report.py
```

以上batch命令会重启**本目录pid文件所指、cmdline匹配本目录二进制**的两个实验进程；不会运行pkill或正式网络stop脚本。批次名不得复用，脚本的JSONL使用append保存，重用会混入重复样本。为保持原始产物，请在新的输出目录中开展新批次，勿覆盖本轮CSV。

真实ledger校验使用新增rwset操作的client-verify；正式性能客户端client-benchmark保持不变。两者均常驻进程接收JSON请求，一行数组可并发执行，请勿把该CLI接口开放给外部网络。

## 源码与构建

- CVW独立分支：`/home/frankie/mygitprojects/.worktrees/cvw-step17`。
- 节点独立分支：`/home/frankie/mygitprojects/.worktrees/node-step17`。
- prototype/是源码副本；prototype.patch、node-workspace.patch可审查；environment.json和source_hashes.json记录基线、依赖、构建和文件SHA。两个branch最终commit见branches.json。
- 编译原型不运行go mod tidy、不升级依赖：

```bash
cd /home/frankie/mygitprojects/.worktrees/node-step17
GOFLAGS=-mod=readonly /usr/local/go/bin/go build -o /ABS/OUTPUT/chainmaker ./main
GOFLAGS=-mod=readonly /usr/local/go/bin/go build -o /ABS/OUTPUT/client ./experiment/step17client
```

正式计时二进制保留为chainmaker和client-benchmark，node文件后续commit会改变Go内嵌VCS信息；源码相同不保证新二进制SHA与已测构建相同。已测构建的go version -m和完整SHA保留。

新建隔离网络：在空的输出目录保留脚本和step-16 manifest/artifact相对关系后运行setup_network.py。它复制现有test release的配置及测试证书，使用TBFT单验证节点、空seeds、回环端口、独立账本。**不会复制原release账本**。端口冲突时先选新的专用端口；不要停止其他节点。setup脚本禁止覆盖已存在的network目录。

compiled/按Wasmer实际编译输入Wasm的SHA命名，内容复用step-16首编译隔离产物，每个.module必须带.json并匹配WasmSHA/ConfigID/ArtifactSHA。prepare_artifacts.py重新建立该只读索引。不能从不可信来源导入serialized Module。首次异常未解决，因此正式比较不可去掉artifact隔离后仍复用本轮结论。

```bash
python3 prepare_artifacts.py
python3 setup_network.py
python3 nodes.py start
# 等待RPC就绪；首次SDK连接失败必须保留并单独标注，不得当成功样本。
python3 run.py deploy
```

重复运行deploy不会覆盖已有合约，但会返回已存在错误；不要将其计入业务成功率。合约Wasm仍来自step-16 manifest，生产部署不会使用nodata文件；转换由新建pool时完成。

## 开关与回退

Copy开关是pool创建时的`CM_STATIC_MEMORY_COPY`，运行中的pool不热切换。节点管理脚本通过模式设置该变量；关闭两个实验节点的Copy：

```bash
python3 nodes.py stop
CM_STATIC_MEMORY_COPY_OVERRIDE=0 python3 nodes.py start
```

恢复实验对照：

```bash
python3 nodes.py stop
python3 nodes.py start
```

`CM_FRESH_INVOKE=1`和`CM_STEP17_SERIALIZE_VM=1`在两模式相同；关闭Copy不代表恢复生产排队或生产并行策略。彻底回退本轮实验只需`python3 nodes.py stop`，保留原正式二进制/源码，或在实验分支切回记录的父commit。不要revert主分支用户修改、不要删除既有测试release。新源码不会自动启动任何节点。

## 验证命令与限制

```bash
cd /home/frankie/mygitprojects/.worktrees/cvw-step17/chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0
GOFLAGS=-mod=readonly /usr/local/go/bin/go test -race -tags step16 \
  -run 'TestStep17SharedTemplateConcurrent|TestStep16SafetyAndTableSynthetic|TestStep16UnsupportedAndFallback' -count=1 -v .
GOFLAGS=-mod=readonly /usr/local/go/bin/go test -race -tags step16 \
  -run 'TestStep17RejectStaleWasm|TestStep17FreshResetAudit' -count=1 -v .
```

FreshResetAudit通过意味着**确定复现reset阻塞**，不是reset功能通过。旧step16Integration测试依赖lastCreated写入，本轮节点已移除该共享写入，因此不能直接运行它作为step17验证。

整节点`-race`已实际构建并尝试恢复已有账本、启动全新账本。原始构建在bloom unsafe pointer处checkptr失败；只屏蔽该包checkptr的补充诊断构建及全新账本原始race构建均在存储RollingWindowCacher报告race。详细stack原样保留。没有声称128条race业务完成；这些脚本的失败记录就是未覆盖结果。正式非race并发调用和独立模板race测试数据分别保留，不合并成整节点无race结论。

原始节点stdout归档在raw/；network/含本机生成的私钥、账本、配置和pid，忽略版本控制。raw/只复制日志，提交前仍应按实际使用的测试证书策略审查。发布文件不含复制的私钥。实验结束节点已停止。
