"""Read-only replay of saved experiments, then regenerate reports. Never starts nodes."""
from pathlib import Path
import json,csv,hashlib,subprocess,platform,statistics,os,re
P=Path(__file__).resolve().parents[1];D=P/'raw_logs';A=P/'audit';R=Path('/home/frankie/mygitprojects');W=R/'.worktrees';N=W/'node-step39c';ROOT=P.parents[2]
def sh(args,cwd=None):return subprocess.check_output(args,cwd=cwd,text=True).strip()
def digest(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def load(f):return json.loads(Path(f).read_text())
def rows(f):return list(csv.DictReader((P/f).open()))
def write(f,s):(P/f).write_text(s.strip()+'\n')
def table(h,rr):return '| '+' | '.join(h)+' |\n|'+ '|'.join(['---']*len(h))+'|\n'+'\n'.join('| '+' | '.join(map(str,r))+' |'for r in rr)+'\n'
def fmt(x):return f'{float(x):.3f}'
# Stronger check than historical parity.py: no field deletion, no history time normalization.
def exact(x):
 out=[]
 for it in x['records']:
  rw=it['committed'].get('rw_set')or{}
  out.append({'tag':it['tag'],'tx_id':it['row']['response']['tx_id'],'result':it['row']['response']['contract_result'],'reads':sorted(rw.get('tx_reads',[]),key=lambda v:json.dumps(v,sort_keys=True)),'writes':sorted(rw.get('tx_writes',[]),key=lambda v:json.dumps(v,sort_keys=True))})
 return {'records':out,'initial':x['initial_projection'],'final':sorted(x['projection'],key=lambda v:json.dumps(v,sort_keys=True))}
checks=[]
for c in ['compute_hashCal','bigInput_inputSize','exchange_buyNow']:
 for b in [1,2,3]:
  a=exact(load(D/f'formal-{c}-b{b}-E0-case.json'))
  for g in ['E1','E2','E3']:
   assert a==exact(load(D/f'formal-{c}-b{b}-{g}-case.json')),(c,b,g)
   checks.append(dict(case=c,batch=b,group=g,exact_business_equal=True))
  if c=='exchange_buyNow':
   signatures=[]
   for g in ['E0','E1','E2','E3']:
    x=load(D/f'formal-{c}-b{b}-{g}-case.json');ids={a['row']['response']['tx_id']for a in x['records']};ev=[json.loads(l[7:])for l in(D/(x['label']+'-node.log')).read_text().splitlines()if l.startswith('STEP35 ')]
    signatures.append([(e['tx_id'],e['contract'],e['method'],e['depth'],e['gas'],e['code'],e['error'])for e in ev if e['event']=='invoke_end'and e.get('depth',0)>0 and e.get('tx_id')in ids])
   assert len(signatures[0])==60 and all(v==signatures[0]for v in signatures[1:]),('child gas/order mismatch',b)

(A/'strict-business-parity.json').write_text(json.dumps(dict(passed=True,normalization='only sorting read/write collection order; no field deletion/time substitution',checks=checks),indent=2))
rr=rows('RESOURCE_SUMMARY.csv');tx=rows('E2E_RESULTS.csv');tp=rows('TPS_RESULTS.csv');ef=rows('PAIRED_EFFECTS.csv');summ=rows('SUMMARY.csv');te=rows('TPS_EFFECTS.csv')
assert len(rr)==107 and len(tx)==360 and len(tp)==36
assert all(r['exit_code']=='0' and r['pid_exited']=='True' and r['cgroup_empty']=='True' and r['managed_pending']=='0' and r['stores_created']==r['stores_closed'] and r['instances_created']==r['instances_closed'] and r['artifact_stop_entries']=='0' and r['artifact_stop_bytes']=='0' and r['artifact_stop_closed']=='True'for r in rr)
assert all(r['unique_confirmed_commits']=='10'and r['failures']=='0'and r['timeouts']=='0'and r['owner_limit']=='32'and r['owner_accepted']=='12'for r in tp)
assert all(r['put_end_not_after_rpc_end']=='True'for r in rows('NODE_STAGES.csv'))
assert all(load(f)['passed']for f in D.glob('restart-formal-*-postcheck.json'));assert len(list(D.glob('restart-formal-*-postcheck.json')))==36
assert not(P/'STOP_SHARED.json').exists()
build=load(A/'node4-outcome.json');mismatch=[]
for name,h in build['source_hashes'].items():
 # client.go is separately compiled and is not a node dependency.
 if name.startswith('source/vm/')and not name.endswith('_test.go'):assert digest(P/name)==h,name
client=load(A/'client3-outcome.json');assert client['source_hashes']['source/client.go']==digest(P/'source/client.go')
lib=W/'cvw-step35b/experiments/instance-lifecycle/step-35b-native-wasi-thread/libraries/patched/libwasmer.so';lh=digest(lib);assert lh=='56b236ce1772b805819aec7c10eb417cd62bf0c6ee2c9b581e651f746bec17dc'
for r in rr:
 cmd=load(D/(r['run']+'-command.json'));assert cmd['native_sha']==lh and cmd['binary_sha']==build['sha256']
 assert str(lib)in(D/(r['run']+'-loaded-maps.txt')).read_text()
 if r['phase']=='formal':
  args=cmd['argv'];assert '--setenv=CM39C_DIAGNOSTIC=0'in args and '--setenv=E38_STRATEGY=C0'in args
  assert ('--setenv=E39_MODE=B'if r['run'].endswith('-E3')else'--setenv=E39_MODE=A')in args
variants=load(P/'inputs/variants.json');wasms=[]
for name,v in variants.items():
 assert digest(v['path'])==v['sha'],name
 wasms.append(dict(name=name,path=v['path'],sha256=v['sha'],bytes=Path(v['path']).stat().st_size,family=v['family']))
(A/'wasm-identity.json').write_text(json.dumps(wasms,indent=2))
old=W/'cvw-step39b/experiments/instance-lifecycle/step-39b-artifact-lifecycle-acopy/source/vm'
if not old.exists():old=R/'CVW/experiments/instance-lifecycle/step-39b-artifact-lifecycle-acopy/source/vm'
assert old.exists()
diffs=[]
for f in sorted((P/'source/vm').rglob('*')):
 if not f.is_file()or f.suffix=='.so':continue
 rel=f.relative_to(P/'source/vm');before=old/rel
 if before.exists()and digest(f)!=digest(before):
  result=subprocess.run(['diff','-u','--label','step39b/'+str(rel),'--label','step39c/'+str(rel),str(before),str(f)],capture_output=True,text=True);diffs.append(result.stdout)
(A/'vm-relative39b.diff').write_text(''.join(diffs));(A/'node.diff').write_text(sh(['git','diff','c28bfa8','--','go.mod'],N)+'\n')
(A/'vm-diff-files.json').write_text(json.dumps([s.splitlines()[0]for s in diffs],indent=2))
configdir=A/'configuration';configdir.mkdir(exist_ok=True);cfg=[]
for f in Path('/tmp/cvw-step39c-template').rglob('*.yml'):
 rel=f.relative_to('/tmp/cvw-step39c-template');out=configdir/rel;out.parent.mkdir(parents=True,exist_ok=True);text=f.read_text();text=re.sub(r'(?m)^(\s*(?:password|redis_password|dsn):).*$', r'\1 <redacted-unused-default>', text);out.write_text(text);cfg.append(dict(path=str(f),sha256=digest(f),archived=str(out.relative_to(P)),archived_sha256=digest(out)))
(A/'configuration-identity.json').write_text(json.dumps(cfg,indent=2))
env=dict(recorded='post-run audit; process resource data remains original',host=platform.uname()._asdict(),host_go=sh(['/usr/local/go/bin/go','version']),go_env=json.loads(sh(['/usr/local/go/bin/go','env','-json','GOOS','GOARCH','CGO_ENABLED','GOTOOLCHAIN'])),node_base='c28bfa8',cvw_base='cda3c0f3',native_path=str(lib),native_sha256=lh,node_binary_sha256=build['sha256'],client_binary_sha256=client['sha256'],guest_go='go1.24.1; Step18/33 same-source 95903a3 plain/A padding; frozen hashes in wasm-identity.json',limits=dict(rss_mib=1536,threads=220,owner_root_budget=32,artifact_items=8,artifact_bytes=67108864),node_worktree_status=sh(['git','status','--short'],N))
(A/'environment.json').write_text(json.dumps(env,indent=2))
# Tables regenerated entirely from saved CSVs.
names={'compute_hashCal':'compute.hashCal','bigInput_inputSize':'bigInput.inputSize','exchange_buyNow':'exchange.buyNow'}
absolute=[];paired=[];batches=[];vm=[]
for c,name in names.items():
 for g in ['E0','E1','E2','E3']:
  r=next(r for r in summ if r['case']==c and r['group']==g and r['metric']=='e2e_ms');absolute.append([name,g,r['N'],fmt(r['mean']),fmt(r['p50']),fmt(r['p95']),fmt(r['pooled_tps'])])
 for r in [r for r in ef if r['case']==c and r['metric']=='e2e_ms']:
  paired.append([name,r['left']+'→'+r['right'],fmt(r['paired_saving_median']),f"[{float(r['ci95_low']):.6f}, {float(r['ci95_high']):.6f}]",f"{float(r['paired_reduction_percent_median']):.2f}%",f"{float(r['positive_fraction'])*100:.1f}%",'/'.join(fmt(r['batch'+str(b)])for b in [1,2,3])])
  v=next(z for z in ef if z['case']==c and z['left']==r['left']and z['right']==r['right']and z['metric']=='vm_factory_ms');vm.append([name,r['left']+'→'+r['right'],fmt(v['paired_saving_median']),f"[{fmt(v['ci95_low'])}, {fmt(v['ci95_high'])}]",fmt(r['paired_saving_median'])])
 for r in [r for r in te if r['case']==c]:batches.append([name,r['left']+'→'+r['right'],f"{float(r['pooled_increase_percent']):+.2f}%",f"[{float(r['ci95_low_percent']):+.2f}, {float(r['ci95_high_percent']):+.2f}]",'/'.join(f"{float(r['batch'+str(b)+'_percent']):+.2f}%"for b in [1,2,3])])
write('README.md', '''# Step-39C：SHA Artifact + A+Copy 真实节点端到端验证

已完成真实节点 Smoke 及 360 笔正式根交易，全部成功确认提交并在重启后查回。采用独立安全 Fresh Store、缓存 Module、原始 C0 Ranges；E0=Fresh、E1=Copy、E2=A+Copy、E3=A+Copy+SHA。所有组保留 Runtime Clone 和每次 Invoke 输入 SHA。未修改 Gas、Guest 业务、Selector 或 Core/PutBlock 排空协议。

## 完整客户端结果

单位 ms，TPS 为成功确认提交数/实际 SDK 串行窗口秒数。每行 3 批×10 笔，P95 由合并 30 笔重新计算；P99 样本不足，不报告。\n\n'''+table(['方法','组别','N','Mean','P50','P95','同步提交 TPS'],absolute)+'''
## 直接配对收益

相同方法、批次、正式位置构成配对，正数表示右组更快。比例为逐对 `(左−右)/左` 的中位数，不能用两组 Median 相减代替。每对不是独立实验批次；独立单位只有 3 个批次。CI 对完整批次有放回抽样，枚举 3³=27 个组合，取经验分位数，属于探索性 CI；未作多重比较校正。\n\n'''+table(['方法','对照','配对节省 Median(ms)','探索性95% CI','逐对降幅中位数','正向比例','三批节省 Median(ms)'],paired)+'''
## TPS 与三批结果

合并 TPS=30/三批窗口秒数之和，并非三个 TPS 的算术平均。\n\n'''+table(['方法','对照','合并TPS变化','探索性95% CI(%)','三批TPS变化'],batches)+'''
## VM 收益与客户端收益

Factory Invoke 是根 Runtime.Invoke 外围窗口，根 Clone 在其外、仍在 SDK 窗口内；子调用已经嵌套在根窗口内，不能再次累加。以下是同一批位置分别计算的直接配对节省，不能相除当作转化率。逐笔 E2E−Factory 残余另见 E2E_RESULTS.csv。\n\n'''+table(['方法','对照','Factory节省Median(ms)','Factory95% CI','SDK节省Median(ms)'],vm)+'''
## 结论与限制

1. Copy 对 buyNow 的 E2E 节省为 8.132ms，三批均正；hashCal 的配对中位数改善，但 Mean/TPS/P95 不支持普遍收益；bigInput 的 Copy CI 跨零。
2. A 在 Copy 之上的增量对 buyNow 为 7.195ms，三批均正。hashCal 为 −0.247ms、CI 跨零；bigInput 的 CI 下界仅 0.000393ms，配对平均节省为负，不足以认定稳定改善。
3. SHA 叠加 A+Copy：buyNow 节省 19.432ms、TPS +16.99%；bigInput 节省 3.175ms、TPS +2.26%；hashCal 节省 2.403ms 但 CI 跨零、TPS CI 跨零。不能声称三种方法效果一致。
4. E0→E3：buyNow 配对节省 34.819ms，TPS +33.19%，P95 从 161.693 降至 132.378ms；hashCal 和 bigInput P50 改善，但 TPS 分别 −0.27%、−0.25%，P95 分别增加 88.545、64.336ms。buyNow 的 SHA 单项 P95 差 CI 跨零，完整组合 P95 改善有本轮证据。
5. 24 笔超过 1 秒的交易全部保留，均是两个短方法的第五笔正式交易。NODE_STAGES.csv 显示主要延迟在节点 RPC 接收至 VM 进入之间；PROPOSER_OVERLAP.csv 显示与 proposer_ready=false 重叠约 1063～1228ms。没有证据将其归因于 Artifact、Store 损坏或 Copy；提案就绪恢复为何迟延尚未定位。
6. 实际配置 consensus.type=1、单验证节点，即单节点 TBFT，不能沿用旧文档“Solo”称呼。本轮未改配置以追求收益。两次 Query 预热确保 Module/Artifact 已命中，不证明 TBFT 已达到长期稳定态；这是有限缓存热态窗口的同步单客户端结果，不是节点最大 TPS。各组分进程连续运行，位置配对不能消除所有时间漂移；顺序与批次分层见 ORDER_EFFECTS.csv。
7. 正式样本 360/360 成功、失败/超时均 0；Gas、返回值、逐笔读写集、事件和业务 KV 最终投影跨组精确一致。buyNow 每笔确有六次下游调用，根无重复执行。完整系统账本包括不同部署 WASM，故不宣称全库字节相等；业务投影及已写键经节点校验和重启复查。
8. 107 个节点进程均正常退出、资源计数配平、Artifact 关闭后归零。正式 RSS 峰值 1161.727MiB，全部 Smoke 最大 1310.508MiB；OS 线程最大 46。未越过 1536MiB/220 保护线。这是有界证据，不是长期无泄漏证明；Artifact 有最多 3 项/约14MiB 的额外持有成本，E0/E1/E2 不登记。
9. 安全接入通过，支持对 buyNow 的阶段性 E2E 收益总结。暂不建议直接扩大 Step-40 全量：先人工审阅短方法 VM 前尾延迟和窗口稳定性，以及仅三批的统计限制。本轮到此停止，不启动下一阶段。

## 复算与来源

只读复算：`python3 scripts/analyze.py`，然后 `python3 scripts/finalize.py`。脚本不启动节点；生成表格会更新本实验派生文件，不改 raw_logs。原始命令、二进制哈希、实际加载 maps、源码 diff、Go/OS、WASM 哈希和配置快照在 audit/ 与 raw_logs/。构建及运行入口详见 SMOKE.md、SDK_TIMING_CODE.md；原实验账本在 /tmp 的独立目录中。私钥、证书及二进制未加入交付。
''')
print('FINALIZE reports/strict checks generated',len(rr),len(tx))
