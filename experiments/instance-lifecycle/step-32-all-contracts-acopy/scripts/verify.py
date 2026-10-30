from pathlib import Path
import json,csv,hashlib,statistics as st,collections,subprocess
P=Path(__file__).resolve().parents[1];R=lambda f:list(csv.DictReader((P/f).open()));H=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
a=json.loads((P/'analysis.json').read_text());expected=180
assert a['valid_formal_blocks']==expected and a['formal_root_calls']==720 and a['formal_real_child_calls']==720,a
assert a['failed']==0 and all(n==30 for n in a['valid_by_case'].values())
timing=R('TIMING.csv');main=[r for r in timing if r['phase']=='formal' and r['valid_block']=='True' and r['depth']=='0' and r['tx_id']=='step32-'+r['case']+'-fixed'];lookup={(r['case'],r['batch'],r['slot'],r['group']):r for r in main};assert len(main)==len(lookup)==720
logs={}
for r in timing:
 f=P/'raw_logs'/(r['label']+'.log')
 if f not in logs:logs[f]=f.read_text().splitlines()
 s=logs[f][int(r['source_log_line'])-1];assert s.startswith('STEP22 ');x=json.loads(s[7:])['data']
 for k in ['invoke_ns','gas','depth','instance_id','newinstance_ns','copy_ns']:assert str(x[k])==r[k],(r['label'],k)
for r in main:assert r['code']=='0' and r['uses_before']=='0' and r['reused']=='False'
for (c,b,sl),rs in __import__('itertools').groupby(sorted(main,key=lambda r:(r['case'],r['batch'],r['slot'])),key=lambda r:(r['case'],r['batch'],r['slot'])):
 rs=list(rs);assert {r['group']for r in rs}=={'G0','G1','G2','G3'};assert len({r['gas']for r in rs})==1
 rs={r['group']:r for r in rs};assert rs['G0']['source_sha']==rs['G2']['source_sha'] and rs['G1']['source_sha']==rs['G3']['source_sha'];assert all(int(rs[g]['copy_bytes'])==0 for g in ['G0','G1']);assert all(int(rs[g]['copy_bytes'])>0 for g in ['G2','G3'])
for row in R('PAIRED_EFFECTS.csv'):
 ids=[k for k in lookup if k[0]==row['case']and k[-1]==row['left']];ds=[(int(lookup[k]['invoke_ns'])-int(lookup[(*k[:-1],row['right'])]['invoke_ns']))/1e6 for k in ids];assert len(ds)==30 and abs(st.median(ds)-float(row['paired_saving_median_ms']))<1e-9
for row in R('INTERACTION_ANALYSIS.csv'):
 ids=[k for k in lookup if k[0]==row['case']and k[-1]=='G0'];d=[sum(s*int(lookup[(*k[:-1],g)]['invoke_ns'])for s,g in [(1,'G0'),(-1,'G1'),(-1,'G2'),(1,'G3')])/1e6 for k in ids];assert abs(st.median(d)-float(row['interaction_cost_median_ms']))<1e-9
res=R('RESOURCE_SUMMARY.csv');assert len(res)==442 # 420 formal +14 six-method preflight chunks +8 rollback processes
for r in res:
 assert r['passed']=='True' and r['instances_created']==r['instances_closed'] and r['managed_pending']=='0' and r['managed_remaining']=='0' and r['in_flight_end']=='0' and r['pids_stopped']=='True' and r['cgroup_empty']=='True'
 modules=[x for x in R('MODULE_PREPARATION.csv')if x['label']==r['label']and x['event']=='module'];assert len(modules)==int(r['store_scopes_closed'])==int(r['modules_closed'])
for f,sha in json.loads((P/'audit/history-manifest.json').read_text()).items():assert H(Path(f))==sha,f
for name,sha in json.loads((P/'environment.json').read_text())['source_hashes'].items():assert H(P/name)==sha,name
assert not(P/'STOP.json').exists()
# Executed ordering has each group at each position2 or3 times per batch/method.
for c in a['valid_by_case']:
 for b in ['1','2','3']:
  rr=[r for r in main if r['case']==c and r['batch']==b and r['group']=='G0'];counts=collections.Counter((i,g)for r in rr for i,g in enumerate(r['order'].split(',')));assert set(counts.values())<={2,3},counts
# No owned unit is still executing; none are retained because runner stopped them.
z=subprocess.run(['systemctl','--user','list-units','--all','--no-legend','step32-*'],capture_output=True,text=True);assert not any('running' in l or 'activating'in l for l in z.stdout.splitlines())
result=dict(formal_blocks=180,formal_roots=720,real_children=720,valid_by_case=a['valid_by_case'],processes=len(res),raw_sample_rows_verified=len(timing),raw_logs_verified=len(logs),all_scope_resources_closed=True,all_processes_stopped=True,historical_sources_unchanged=True,compiled_go_sources_unchanged=True,gas_result_state_parity=True,interaction_sign_checked=True,new_node_e2e_runs=0)
(P/'VERIFICATION.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
