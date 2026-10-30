from pathlib import Path
import json,csv,hashlib,subprocess
P=Path(__file__).resolve().parents[1];ROOT=Path('/home/frankie/mygitprojects');B=ROOT/'CVW/experiments/instance-lifecycle';S=B/'step-28-six-method-acopy';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();v=json.loads((P/'inputs/variants.json').read_text())
methods={'compute':['bigNumCal','hashCal','normalCal'],'fact':['saveAndFindByFileHash'],'erc721':['mint'],'exchange':['buyNow'],'identity':['isApprovedUser'],'bigInput':['inputSize'],'itinerary':['save'],'raffle':['registerAll']};rows=[]
for c,ms in methods.items():
 for m in ms:
  if c in ['compute','fact','erc721','exchange']:
   for g in ['G0','G1','G2','G3']:
    x=v[c+'-'+g];rows.append(dict(contract=c,method=m,variant=g,wasm_sha256=x['sha'],wasm_path=x['path'],build_source='Step18 P0 family / Step28 frozen; guest source95903a3',real_fixture=True,historical_fresh_copy_acopy='Step28 all3',included=True,reason='',fresh_A=g in['G1','G3'],Copy=x['copy']))
  else:
   for d in ['testdata','testdata-instrument']:
    f=ROOT/'CVW/chainmaker'/d/c/(c+'-go.wasm')
    if f.exists():rows.append(dict(contract=c,method=m,variant=d,wasm_sha256=sha(f),wasm_path=str(f),build_source='historical candidate; not merged with frozen Step18',real_fixture='legacy Step16 fixture; current factorial root fixture not audited',historical_fresh_copy_acopy='Fresh/Copy Step16; identity also real buyNow callee',included=False,reason='blocked for extension: standalone safe root fixture/four-group same-family build not fully validated; prioritize six required methods',fresh_A='',Copy=''))
# Inventory fact.save as an additional historical method, not silently counted as the target fact method.
f=ROOT/'CVW/chainmaker/testdata/fact/fact-go.wasm';rows.append(dict(contract='fact',method='save',variant='legacy',wasm_sha256=sha(f),wasm_path=str(f),build_source='legacy family; not Step28 target',real_fixture='Step16',historical_fresh_copy_acopy='Fresh/Copy only',included=False,reason='additional method not in six-method frozen fixture',fresh_A='',Copy=''))
with(P/'CONTRACT_INVENTORY.csv').open('w')as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
# All candidate wasm locations, including the two TinyGo fact binaries; hashes are not family equivalence claims.
ws=[]
for d in ['testdata','testdata-instrument']:
 for f in sorted((ROOT/'CVW/chainmaker'/d).rglob('*.wasm')):ws.append(dict(path=str(f),contract=f.parent.name,sha256=sha(f),bytes=f.stat().st_size,flavor='tinygo-not-target'if 'tinygo'in f.name else'go-candidate'))
with(P/'audit/ALL_WASM_CANDIDATES.csv').open('w')as f:w=csv.DictWriter(f,fieldnames=list(ws[0]));w.writeheader();w.writerows(ws)
(P/'EXPERIMENT_DESIGN.md').write_text('''# Step32 四组有界串行方案

G0 Fresh；G1 Fresh+A；G2 Fresh+Copy；G3 Fresh+A+Copy。不得沿用Step28 G1/G2编号含义。每方法3批，每批10个四组配对区块；6方法合计180新区块、720正式根调用。所有WASM冻结来自同源Step18 P0/plain家族，非Step24B旧原件；compute bigNum/hash为10000轮、normal10000000轮。

每组每合约独立Store+cached Module，固定OS owner；每次新WASI/Instance，同步执行与scope清理，无池后台、异步关闭、B1或新Gas策略。最多每进程2个组/2正式根调用；buyNow每进程1组，全部六真实子调用。一个block跨两个/四个连续独立进程完成，所有组等价账本，相同输入与TxID，三批独立进程无残留。该进程拆分用于保持旧资源限，不能称原池或E2E。

顺序采用随机重命名、随机行序的Williams四组平衡设计；每批各组每位置出现2或3次，种子320027/320127加batch/case，实际顺序保存在command/outcome/block。无业务100ms Sleep；资源监控25ms轮询不属于请求间隔。

## 计时

Module编译、模板准备、init_contract、账本克隆和根回执输出在目标Invoke外。S0→S1包含WASI/imports和新Instance/Copy，不包含缓存Module编译；S1→S2包含WASI.Initialize和_start；S2→S3包含SetGas/CallMethod/GetGas及结果处理，不能标成CallMethod前剩余准备。CallMethod包含export，根buyNow export包含子调用。Close随后执行并包含在Invoke总窗。以上均用time.Now/time.Since单调时钟，不重复加嵌套阶段。

## 统计预登记

主效应直接按同(batch,slot)四组计算：G0−G1，G0−G2，G0−G3，G2−G3，G1−G3。Mean/Median/P50/P95单列；CI为10000次batch→whole-block层次bootstrap，固定seed320027+case/edge，线性分位；3批只是3个时间层，不是30独立环境。另报告位置、前后执行与批次分层。

原需求Interaction=G0−G1−G2+G3保留为interaction_cost_ms。若把耗时降低称收益，额外协同应为synergy_saving_ms=−Interaction。例如单项各省1ms、组合省3ms，原式为−1ms；因此原式负代表协同，正代表抵消。两种符号都报告，不反转实测数据、不把独立Median相减当交互。

## 门槛及局限

逐block比较Gas/返回/业务操作及实际root RWSet/事件/完整初始最终账本。buyNow比较7条真实根/子调用；空参数和重复token失败回滚四组独立预检，不称全部异常路径覆盖。真实Table函数身份、一般OOG/异常、长期Store回收、节点并发均not_tested。全局MemAvailable≥8GiB、swap used≤1GiB；非exchange软RSS768MiB/125线程，exchange1536MiB/220线程；原hard2GiB/256tasks、Go45s/process60s保持不变。任何STOP保留并禁止继续。
''')
(P/'BUILD_LINEAGE.md').write_text('''# 同源构建与实现

分支experiment/step32-all-contracts-acopy-matrix，父29950ab1（Step28）。Host Go1.25.0、Guest Go1.24.1、SDK0.1.3完整API、ChainMaker2.4.0、native6.0.1 SHA dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9，max512页、原Gas配置保持。四组均Fresh，不复用业务Instance；Module缓存/Store架构不随组改变。

audit/variants.csv及inputs/variants.json列出最终二进制hash与历史来源。G0/G2原WASM逐字节相同；G1/G3同A布局WASM逐字节相同。A-only直接使用既有A原WASM并关闭Copy，不重写A；Copy使用同一prepareStaticMemory/noData/restore路径，恢复在WASI.Initialize/_start前。A是链接期可达静态padding，非initial memory128页；历史首次arena对齐诊断在Step18/28，不将旧计时并入本轮。

新source/vm仅改实验driver为四组、允许有界分进程，以及在cache_closed输出已成功关闭的Store/Module scope数量（在Invoke外）。不改生产VM/Gas/managed守卫。scope计数不是native StoreRef泄漏检测；owner pending0和进程退出作为本轮有界终点。编译argv/build1-outcome/environment逐文件SHA保留。初次准备发现IDE镜像省略native.so，尚未运行Guest；改从当前CVW已冻结同hash库复制到新实验目录，无版本替换，记录audit/initial-preparation.txt。

只读历史审计：Step18恢复A/P0家族；Step22建立cached Module安全串行Copy；24B提供原件参照但不混入；25包含B1不用于本轮；26仅复算旧样本；27证实Guest波动和同Store协议边界；28提供六方法真实夹具；29说明buyNow子窗口/字节码克隆处于root export；30没有新E2E。对应报告hash见audit/history-manifest.json。
''')
(P/'audit/initial-preparation.txt').write_text('First prepare attempt copied IDE source mirror without ignored native.so and stopped on assertion before build/Guest. Resumed by copying only the existing pinned dcdfa... library from CVW default linux-amd64 into new experiment source; no different native version used.\n')
# Freeze new scripts/design before formal starts.
(P/'audit/pre-formal-scripts.json').write_text(json.dumps({str(f.relative_to(P)):sha(f)for f in(P/'scripts').glob('*.py')},indent=2))
print('Inventory rows',len(rows),'canonical candidate WASMs',len(ws))
