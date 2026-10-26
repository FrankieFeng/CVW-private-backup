"""Freeze committed history; construct a private Step22-based diagnostic source tree."""
from pathlib import Path
import csv,hashlib,json,shutil,subprocess
P=Path(__file__).resolve().parents[1];R=P.parents[2]
E='experiments/instance-lifecycle/step-21e-fresh-diagnostics';B='experiments/instance-lifecycle/step-22-serial-static-copy'
def blob(commit,path):return subprocess.check_output(['git','show',commit+':'+path],cwd=R)
def save(path,b):path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b)
def sha(b):return hashlib.sha256(b).hexdigest()
history=[]
for commit,base,tag,names in [
 ('507310c',E,'step21e',['GAS_ANALYSIS.md','PLAN.md','call_records.csv','gas_timeline.csv','audit/gas-inputs.json','audit/gas-slots.json','audit/first-gas-divergence.json','source/vm/step21e_probe.go','source/vm/step21e_checks_test.go','source/vm/sim_context.go','source/vm/vm_bridge.go','source/vm/step21d_runtime_test.go','source/vm/step21d_fixture_test.go','raw_logs/buyNow-r0.log','raw_logs/buyNow-r1.log','raw_logs/buyNow-r0-command.json','raw_logs/buyNow-r1-command.json','raw_logs/buyNow-r0-receipts/success-1.json','raw_logs/buyNow-r1-receipts/success-1.json']),
 ('394d291',B,'step22',['README.md','CORRECTNESS.md','environment.json','variants.csv','raw_logs/exchange-batch-1-A0-receipts/pair-000-A0.json','raw_logs/exchange-batch-1-A1-receipts/pair-000-A1.json','audit/step16_copy_identity.json'])]:
    for name in names:
        data=blob(commit,base+'/'+name);dest=P/'audit/history'/tag/name;save(dest,data)
        history.append(dict(commit=commit,source=base+'/'+name,frozen=str(dest.relative_to(P)),sha256=sha(data)))
(P/'audit/history_hashes.json').write_text(json.dumps(history,indent=2)+'\n')
e0=json.loads((P/'audit/history/step21e/raw_logs/buyNow-r0-receipts/success-1.json').read_text());e1=json.loads((P/'audit/history/step21e/raw_logs/buyNow-r1-receipts/success-1.json').read_text())
b0=json.loads((P/'audit/history/step22/raw_logs/exchange-batch-1-A0-receipts/pair-000-A0.json').read_text());b1=json.loads((P/'audit/history/step22/raw_logs/exchange-batch-1-A1-receipts/pair-000-A1.json').read_text())
for key in ['business_input','before_hash','after_hash','actual_rwset']:assert e0[key]==e1[key]
assert e0['business_input']==b0['business_input']==b1['business_input']
assert e0['before_hash']==b0['before_hash']==b1['before_hash']
inputs=dict(root_tx_id=e0['tx_id'],root_input=e0['business_input'],expected_initial_hash=e0['before_hash'],expected_final_hash=e0['after_hash'],initialization_order=['identity','erc721','exchange'],initialization_tx_ids={n:'step21c-init-'+n for n in ['identity','erc721','exchange']})
(P/'inputs/business.json').write_text(json.dumps(inputs,indent=2)+'\n')
save(P/'inputs/gas-slots.json',blob('507310c',E+'/audit/gas-slots.json'))
save(P/'inputs/manifest.json',blob('394d291',B+'/inputs/exchange-manifest.json'))
hist=dict(step21e_R0_gas=e0['actual_result']['gas_used'],step21e_R1_gas=e1['actual_result']['gas_used'],step22_A0_gas=b0['actual_result']['gas_used'],step22_A1_gas=b1['actual_result']['gas_used'],step21e_tx=e0['tx_id'],step22_tx=b0['tx_id'],same_business_inputs=True,same_initial_hash=True,different_txids=True)
(P/'audit/historical_summary.json').write_text(json.dumps(hist,indent=2)+'\n')
assert not(P/'source').exists(),'source already prepared; never overwrite local diagnostic edits'
for name in subprocess.check_output(['git','ls-tree','-r','--name-only','394d291',B+'/source/vm'],cwd=R,text=True).splitlines():
    save(P/'source/vm'/Path(name).relative_to(B+'/source/vm'),blob('394d291',name))
hashes=json.loads(blob('394d291',B+'/audit/source_hashes.json'))
for name,h in hashes.items():
    if '/packaged/lib/'in name and name.endswith('.go'):
        b=(R.parent/'cvw-step22'/B/name).read_bytes();assert sha(b)==h
        save(P/name,b)
native=R.parent/'cvw-step22'/B/'source/vm/wasmer-go/packaged/lib/linux-amd64/libwasmer.so'
expected='dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9';assert sha(native.read_bytes())==expected
save(P/'source/vm/wasmer-go/packaged/lib/linux-amd64/libwasmer.so',native.read_bytes())
save(P/'go.work',blob('394d291',B+'/go.work').replace(str(R.parent/'cvw-step22'/B/'source/vm').encode(),str(P/'source/vm').encode()))
save(P/'go.work.sum',blob('394d291',B+'/go.work.sum'))
(P/'HISTORICAL_AUDIT.md').write_text('''# Step-23 历史条件审计

只读冻结Git提交507310c与394d291中的原CSV、trace、命令和receipt，hash见audit/history_hashes.json。下面条件根据实际源代码和原始记录，不直接采用报告推测。

| 条件 | Step21E R0 | Step21E R1 | Step22 A0 | Step22 A1 | 本轮计划 |
|---|---|---|---|---|---|
| Instance | 每合约从init开始保留；下游同合约继续用 | 每次包括子调用均Fresh | 每调用Fresh | 每调用Fresh | R0/R1同缓存模型仅Instance历史不同；再独立测R1/C1 |
| Store/Module | 首次每合约创建，随后复用 | 每次调用重建/编译 | 每合约/变体预先缓存 | 同左，noData Module | 同Step22缓存，不每Invoke编译；与21E R1有明确区别 |
| Copy | 无 | 无 | 无 | S1前静态区间Copy | 只在C1启用已有方案 |
| 根调用次数/进程 | 1 | 1 | 1（exchange分进程） | 1 | 每进程最多1根、六真实callee |
| 初始化 | identity→ERC721→exchange | 同左 | ERC721→exchange→identity | 同左 | 固定使用21E初始化顺序和TxID |
| 目标TxID | step21c-buy-001 | 同左 | step22-exchange-000 | 同左 | 两阶段全固定step21c-buy-001 |
| 业务参数 | 固定from/to/tokenId1/metadata | 相同 | 与21E相同 | 相同 | 完全固定；原JSON已冻结 |
| 初始账本 | a27f2d1e… | 相同 | 相同 | 相同 | 真实init后hash必须与21E匹配 |
| 根Gas | 12761395 | 12765774 | 12767294 | 12767294 | 待实测，不预设 |
| 并发/池 | 固定owner、无原后台池 | 同左 | 同左 | 同左 | 保留全部所有权与资源边界 |

三个实际依赖WASM的SHA完全相同，见inputs/manifest.json及21E gas-slots：identity213d4d2b…、ERC7219b6eb47d…、exchange9387cb4e…。都使用真实VmManager/TxSimContext/合约业务，非子合约成功Mock。Gas映射/runtime limit沿用既有代码。完整构建版本和native hash在各提交源码及Step22 environment中。

**历史比较对象**：21E只有一次根buyNow，不是先后两根冷/热。R0根Instance此前只init，但ERC721同一Instance在transferFrom前已init、mint、setApprovalForAll2；R1的每个子Instance都新建。因此复用历史与局部guest冷热相关，但不能把概念等同。21E的fact/ERC独立重复业务另属于等账本的首次/后续调用比较，不替换buyNow条件。

**第六次**：按真实子调用进入顺序（排除3次init），1 identity.addWriteList；2、3 identity.isApprovedUser；4 ERC721.mint；5 ERC721.setApprovalForAll2；6 ERC721.transferFrom。历史Instance ID：R0第六次仍为ERC721 ID2，R1为新ID10；根R0 ID3、R1 ID4。深度均1，不是递归第六层。完整调用原始记录保留在audit/history/step21e/call_records.csv。

原Gas是GetGas返回的registry累计计数。R0/R1前五个子Gas入/出相等，第6入参6374268相等、返回6386947/6391326；本地增量12679/17058；根差4379。原trace最后相同DeleteState.after=6378616，首个不同log_message.before=6386180/6390559。仅能把差异缩在transferFrom的两host边界间，不能认定JSON缓存为已证实根因。

Step22与21E不同TxID也进入guest日志、写集、事件；因此绝对Gas/最终账本不同不直接说明Copy或计量错误。本轮固定TxID消除此差异，若新Store模型无法复现，也会明确报告。

采样边界审计发现GetTxRWSet会releaseAllUsedIters，**禁止在中途为采样调用它**。本轮改用已有只读GetTxRWMapByContractName，立即序列化可见累计映射，明确非callee独占读写集；最终真实RWSet仍由原f.run结束时取得。不会改变Gas逻辑。
''')
print('frozen committed evidence, condition table and private source prepared')
