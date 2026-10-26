"""Write audit/results from retained static evidence. Never executes a test or guest."""
from pathlib import Path
import csv,json,hashlib,subprocess,shutil
ROOT=Path(__file__).resolve().parent.parent
WORK=Path('/home/frankie/mygitprojects/.worktrees/cvw-step21c')
VM=WORK/'chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0'

def write(name,rows):
 with (ROOT/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rows for k in r)));w.writeheader();w.writerows(rows)

e=json.loads((ROOT/'environment.json').read_text());e['source_commit']=subprocess.check_output(['git','-C',str(WORK),'rev-parse','HEAD'],text=True).strip();e['test_binary_sha256']=hashlib.sha256((ROOT/'binaries/step21c.test').read_bytes()).hexdigest();e['execution_scope']='static_and_compile_only_per_user';e['boot_id_after']=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
assert e['boot_id']==e['boot_id_after']
(ROOT/'environment.json').write_text(json.dumps(e,indent=2)+'\n')
shutil.copyfile(VM/'step21c_fixture_test.go',ROOT/'source/step21c_fixture_test.go')
(ROOT/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(WORK),'diff','fc3e90d','HEAD','--','chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0/step21c_fixture_test.go']))
checks=[('three_artifact_hashes','static','pass'),('WASM_export_and_section_framing','static','pass'),('six_static_CallContract_sites','static','pass'),('frozen_100_inputs_unique_token','static','pass'),('test_entry_unconditional_skip','static','pass'),('fixture_typechecks_and_links','compile_only','pass'),('real_root_and_callee_execution','dynamic','not_tested'),('actual_child_depth_and_returns','dynamic','not_tested'),('initialized_business_state','dynamic','not_tested'),('write_set_and_events','dynamic','not_tested'),('negative_rollback_behavior','dynamic','not_tested'),('R0_R1_gas_equivalence','dynamic','not_tested'),('fresh_instance_nonreuse','dynamic','not_tested'),('native_Store_safety','dynamic','not_tested_pending_step21b'),('Table_elements','dynamic','not_tested')]
write('correctness.csv',[dict(check=n,phase=p,status=s,evidence='audit/static-validation.json or audit/compile.log' if p!='dynamic' else 'guest execution forbidden pending Step21B') for n,p,s in checks])
write('summary.csv',[dict(method='exchange.buyNow',policy=p,samples=0,successful_roots=0,root_invoke_mean_ms='',root_p50_ms='',root_p95_ms='',vm_log_tps='',historical_tps=881.2 if p=='R0' else 57.7,status='prepared_compile_only_pending_step21b',guest_executed=False) for p in ['R0','R1']])
old=ROOT.parent/'step-21-instance-reuse-loss/capacity-fix-20261024-01';comparison=list(csv.DictReader((old/'baseline_comparison.csv').open()));agg={r['method']:r for r in csv.DictReader((old/'aggregate_summary.csv').open())}
rows=[]
for c in comparison:
 a=agg.get(c['method'])
 rows.append(dict(method=c['method'],historical_r0_tps=c['historical_r0_tps'],historical_r1_tps=c['historical_r1_tps'],historical_ratio=c['historical_ratio'],current_r0_mean_ms=a['r0_mean_ms'] if a else '',current_r1_mean_ms=a['r1_mean_ms'] if a else '',current_r0_tps=c['r0_tps'] if a else '',current_r1_tps=c['r1_tps'] if a else '',current_ratio=c['ratio'] if a else '',n_each=300 if a else 0,valid_pairs=3 if a else 0,gas_equal_prior=a['gas_equal'] if a else 'not_tested',scope='Step21 existing capacity-fixed TestInvoke; not remeasured in Step21C' if a else 'Step21C compile/static only; full buyNow not executed',source=str(old/'aggregate_summary.csv') if a else str(ROOT/'summary.csv')))
write('six_method_comparison.csv',rows)
state_plan=[('identity','identity/adminAddress','actual init_contract derives sender address; no business-state seed'),('identity','identity/userCount','actual init_contract writes 0'),('identity','identity/from and identity/to','buyNow invokes real addWriteList; then both real isApprovedUser calls read it'),('erc721','erc721/name,symbol,tokenURI,admin','actual init_contract with recovered toolkit params'),('erc721','tokenIds/tokenId','actual mint creates owner=from; transferFrom must update to'),('erc721','balanceInfo/from,to; accountInfo/account_tokenId','actual mint/transfer accounting; captured in real RWSet'),('erc721','operatorApprove/from_senderUID','actual setApprovalForAll2 writes 1'),('erc721','tokenInfo/metadata,latestTxInfo; tokenApprove/tokenId','actual business writes/deletes; captured, no fabricated results')]
write('state_plan.csv',[dict(contract=c,state=k,prepared_assertion=p,dynamic_status='not_tested') for c,k,p in state_plan])
(ROOT/'AUDIT.md').write_text('''# Step-21C 历史、调用链、状态和Gas审计

## 范围与版本

用户已确认Step21B仅规划、未执行；不再查找不存在的报告。当前安全边界继承Step21A的Store创建/执行/关闭粗粒度区间重叠记录。Step21C只准备源码、编译和静态检查，无guest运行。所有源码路径以.worktrees/cvw-step21c为根；依赖生产源码相对fc3e90d不变，仅新增step21c_fixture_test.go。

## 三份实际产物与历史参照

当前测试件为vm-wasmer/v2@v2.4.0/testdata中的exchange、identity、erc721，完整SHA/Bytes见audit/artifact-inventory.json，冻结输入见fixture-manifest.json及inputs/exchange-buyNow.json。没有重编/变换合约。根SHA9387cb4e…、identity213d4d2b…、ERC7219b6eb47d…；toolkit候选根72ef5f1c…/identitya6590321…/ERCa692e438…不同，不能标为9月PPT精确用件。881.2/57.7和15.27只作用户历史参考。

实际恢复的toolkit入口parallel/Init.go:105–132的InitBeforeTest在exchange前先Install identity、erc721，再安装exchange；:506–523中identity/exchange无初始化参数，ERC721初始化name=huanletoken、symbol=hlt、tokenURI=https://chainmaker.org.cn。:214–217保存buyNow参数，RandParams将tokenId递增。不能证明该现存文件逐字等于9月PPT实际配置，未找到完整历史部署状态/逐笔Gas/工作负载记录。

## 调用链：三合约，六个下游调用

chainmaker/testdata/exchange/exchange.go:48、57、65、77、88、101：

```text
exchange.buyNow（根，depth0）
  1 identity.addWriteList(from,to)                 depth1
  2 identity.isApprovedUser(from)                depth1
  3 identity.isApprovedUser(to)                  depth1
  4 erc721.mint(to=from, tokenId, metadata)       depth1
  5 erc721.setApprovalForAll2(approvalFrom=from)  depth1
  6 erc721.transferFrom(from,to,tokenId)          depth1
  → buyNow事件 → buyNow success
```

当前根WASM反汇编有6个sdk.CallContract静态调用点，见audit/current-buynow-disassembly.txt与static-call-sites.json；分支可能提前返回，不能把6个静态点写成实测6个成功子调用。三份WASM必需导出已检查，见audit/artifact-exports.json。

选定identity addWriteList/isApprovedUser及ERC721路径没有额外用户合约调用，源码预期最大depth1；identity的另一个callerAddress方法:205会自调用identity.address，但不在本buyNow路径。完整动态深度仍not_tested，协议最大depth5未改。正常成功预期7个Runtime Invoke记录，只有1个根交易，不能计7笔TPS。R1若严格不复用，源码上预期每成功根交易消耗7个Fresh业务Instance（根1+子6）；验证实例、预建库存和额外grow另计，不能将7写成实测创建数或TPS倍数。

## 原TestInvoke夹具缺失

runtime_test.go:369–402通过prepareFile/prepareContract/newVmPool直接建根池；prepareFunc/getMethodParams只有业务参数，不安装callee、不初始化合约、不维护跨交易账本。prepareContract使用包级ContractName，存在空Name；prepareTxSimContext每笔新VmManager/InstancesManager，SnapshotMock.GetBlockchainStore/GetLastChainConfig未实现，GetKey只读未初始化cache。先前失败还没有进入真实callee，不能拿其耗时比较完整buyNow。

ParametersValueMaxLength在protocol/vm_interface.go:159–161为未赋值全局uint32，初值0。标准赋值存在vm/v2/wasi_test.go:33–35的测试init；构建vm-wasmer测试时依赖包_test.go不参与，因而不会执行这段赋值。wasi.go:573拒绝首次81字节address参数。本轮夹具在未来构造时显式设默认10MiB并用t.Cleanup恢复；不是改Gas或guest逻辑。此次constructor未执行，当前全局运行状态未修改。

## 恢复的真实夹具与验证边界

step21c_fixture_test.go实现：

- 三合约元数据/字节码注册；一个InstancesManager在进程内共享，避免每根交易重建子池。
- 内存Snapshot与账本只提供真实状态读写；使用原vm.NewTxSimContext、CallContract的深度/RWSet合并/回滚逻辑；根成功才提交真实TxWrites，失败不提交。
- 原vm.NewVmManager/RunContract负责实际成员参数及调用分发；observedRuntime只调用实际RuntimeInstance.InvokeTime并返回原Result，绝无callee答案表、空业务函数或Mock成功。
- 仅测试身份上下文：公开固定P256公钥、真实解析与SKI UID；成员提供器只识别该身份，签名/节点ACL未覆盖且不返回伪造认证成功。沿用Step21 BlockVersion1，不能宣称现代节点授权/交易签名验证通过。
- 真正调用三合约init_contract后再验证白名单、NFT owner、授权、事件、错误路径；三次成功/重复token/非法地址等断言已编译，但全部未执行。
- identity现存源码对非空adminAddress参数的处理有疑点，夹具沿原toolkit无参初始化，让真实guest走配置公钥的GetSenderAddress，且准备非空admin状态断言；不直接写入假管理员。

root/callee的Gas、返回值、读写集、事件和before/after状态hash会由真实调用收集。当前只有代码，没有任何业务receipt，不得将“断言已准备”标为通过。原源码中ERC721 mint/transferFrom若干权限拒绝分支被注释；本轮不更改，也不把业务成功当作标准ERC721授权安全认证。

## Instance生命周期与Store边界

原InstancesManager.getVmPool会newVmPool并同步grow(defaultMinSize=5)后缓存，三个合约各有Module/Store/池；原TestInvoke手工根池初始空，二者冷态边界不同，未来正式统计需重新明确，不能直接混用。GetInstance非阻塞借出，空则发apply并阻塞；runtime.go的根/子路径都GetInstance并defer RevertInstance。R0归还；R1 vm_pool.go:696–705异步Close→remove→add，worker触发grow，Close包含guest CallDeallocate及native删除。

连续identity3次、ERC7213次可使前次异步回收/新建与下次同Store执行重叠，即使只顺序发根交易也不能规避。Step21A容量补丁和CAS粗粒度守卫均不构成完整Store线程安全证明。本轮不添加全局执行锁、不逐callee排空伪装原负载，也不绕过守卫；guest入口无条件Skip。三个池的WASI线程/RSS总预算还需Step21B验证，不能抬高原220线程/1536MiB软限。

## Gas及计时路径（均未修改）

1. Runtime.InvokeTime按runtimeGasLimit−传入gasUsed设置可用Gas；CallMethod后通过导出函数读剩余值，runtime.go:329–341报告GasUsed。
2. SDK CallContractLen→bridge.callContractCore读取根当前GasUsed→wacsi.CallContract；wasi.go:583加CallContractGasOnce，再传入实际TxSimContext.CallContract→VmManager→子Invoke。
3. wasi.go:596在返回时加result.GasUsed，bridge:406回写根Gas。旧BlockVersion1中callee.GasUsed是否包含传入累计量需要单独核对；不能手工求和或默认R0/R1必相等。
4. bridge:396取得wacsi err后，:406复用err变量可能覆盖原错误，原Step16已记录。本轮不修生产错误处理；准备同时核对每个真实callee Code/Message与根结果，避免仅根字符串误判成功。
5. 子调用失败时BlockVersion<2300的TxSimContext仍合并到上一层，根失败的GetTxRWSet(false)及fixture不提交提供整笔失败保护；准备负向状态hash/写集断言，现代块版本语义未覆盖。

时长记录只包实际InvokeTime的原begin/end；根为inclusive，包含子合约工作及嵌套VM管理开销；子inclusive单列，禁止再次累加到根，主N只计成功根交易。RunContractWallNS含外层管理器/首次编译和观测日志，单独命名，不与InvokeTime或节点客户端延迟混用。原vm_factory计时还包adapter外层日志，因此未来不能自动声称与Step19 factory INFO逐字同边界。当前未生成任何性能数字。
''')
(ROOT/'README.md').write_text(f'''# Step-21C：exchange.buyNow真实跨合约夹具准备

2026-10-26。按用户最新范围，**本轮只完成真实夹具源码准备、编译及静态验证；没有执行测试binary、WASM、功能交易或正式压测。** Step21B仅规划、尚未执行，以Step21A Store风险为边界，不再继续寻找分支。Step21C编号/目录保持独立。

## 已完成

- 审计三份实际WASM及源码；成功路径包含identity三个调用和ERC721三个调用，根+子预期7个Invoke、源码depth1。当前WASM确认6个静态CallContract点，动态成功/深度仍未验证。
- 准备真实VmManager/TxSimContext、三合约登记、内存账本、公开测试身份、实际初始化与成功/异常断言；所有callee业务由原WASM执行，未写固定响应或Mock成功。
- 记录真实读写集、事件、Gas、每层inclusive时间、逐交易状态hash的代码已准备；根失败不提交写集。恢复toolkit可查的初始化和buyNow输入规则，没有改合约或Gas。
- go test -p2 -c已成功，只编译/链接；必需WASM导出、冻结100行参数及唯一token检查通过。冻结100行只是保留产物，本轮没有运行100次。
- 新增guest测试入口第一条语句无条件t.Skip，避免未审计Store生命周期时误启。编译通过不等于功能、安全或Gas通过。

源码编译commit `{e['source_commit']}`，分支`experiment/step21c-exchange-real-fixture`，父fc3e90d；只新增_test.go，不改生产源码。完整差异source.patch；最终报告commit以分支HEAD为准。Go/OS/native和binary哈希见environment.json。未推送远程。

## 本轮状态

| 项目 | 状态 |
|---|---|
| 三WASM哈希、必需导出、六个静态跨调用点 | 已静态检查 |
| fixture编译/链接 | 通过 |
| 根/子真实业务执行、状态和事件 | not_tested |
| Gas一致性、Fresh不复用、Table | not_tested |
| Store安全与资源生命周期 | 待独立Step21B |
| 本轮业务样本/正式100次负载 | 0 / 未启动 |
| buyNow R0/R1 TPS与15.27倍率比较 | 缺失，不能生成 |

只检查源码中的expected输出，不会产生guest成功；实际运行必须同时检查根/全部子调用Code、读写集和状态，不能仅Go PASS或根字符串。身份提供器是VM层测试上下文，不认证节点签名、现代ACL、共识或真实数据库。SnapshotMock未实现项只对未用API保留显式失败，实际合约/状态查读已由新夹具实现；动态可用性仍需验证。

## 安全阻碍和下一步

Step21A已观察创建/执行粗粒度区间重叠；这不是已证实native race，但不足以允许原池负载。R1连续子调用之间，异步Close/grow仍可触碰同一个Store。多合约三个池还增加WASI线程/RSS预算压力。没有通过全局锁、修改Gas、伪造callee结果、禁用守卫或提高资源阈值绕过。

按用户安排，下一阶段应独立执行Step21B，核实同Store创建/执行/关闭与finalizer所有权、跨调用重入、资源回收及池退出。确认边界后，才可评审解除Skip并运行已准备的少量真实功能场景；再决定是否另行恢复正式3批100次。当前未提供任何自动压测命令，runtime-safety-plan.json只是原保护阈值记录，执行仍为false。

## 交付与只读恢复

- AUDIT.md：历史入口、源码调用链、原夹具缺失、参数上限0原因、状态/Gas/计时与生命周期。
- source/step21c_fixture_test.go、source.patch：已编译的真实业务夹具，入口禁用。
- fixture-manifest.json、inputs/、audit/artifact-exports.json：三WASM SHA及冻结参数。
- audit/compile.log、compile-command.json、static-validation.json、current-buynow-disassembly.txt：构建和静态证据。
- correctness.csv、summary.csv：动态项目not_tested，TPS留空。
- six_method_comparison.csv：复用Step21原五方法数据；exchange仍缺失，不以新静态检查冒充实测。原五方法为容量修复版VM层历史数据，ERC721/fact的复用Gas不一致，且Store安全尚未认证，不作生产收益。
- PROGRESS.md、state.json：每阶段进度与恢复入口。raw_logs/无新guest日志，仅有范围说明。

只读/静态命令：

```bash
cat PROGRESS.md
python3 -B scripts/static_readiness.py
python3 -B scripts/report.py
```

这些脚本不会执行测试binary或guest。scripts/compile_only.py只输出/执行构建命令并拒绝覆盖已有binary；原实际完整命令见audit/compile-command.json。不要运行整个测试包来代替构建检查，父分支其他TestInvoke入口不是本轮执行范围。

所有构建单元已退出。未修改代理、Clash或VSCode配置，未覆盖旧实验。回滚仅弃用Step21C独立分支/二进制；不要reset/clean生产脏工作区。
''')
(ROOT/'raw_logs/README.md').write_text('本轮仅编译和静态检查，没有执行guest或测试binary，因此没有新业务日志、计时样本或receipt。构建输出见../audit/compile.log；不能用该日志证明合约执行成功。\n')
print('reports saved; 0 new guest samples; 5 historical methods reused + exchange missing')
