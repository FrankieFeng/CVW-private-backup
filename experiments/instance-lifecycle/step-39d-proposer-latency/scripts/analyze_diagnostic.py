from pathlib import Path
import json,csv,re,statistics as st
P=Path(__file__).resolve().parents[1];D=P/'raw_logs'
def save(n,rs):
 keys=list(dict.fromkeys(k for r in rs for k in r))
 with(P/n).open('w',newline='')as f:w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(rs)
def q(v,p):
 a=sorted(v);k=(len(a)-1)*p;i=int(k);return a[i]+(a[min(i+1,len(a)-1)]-a[i])*(k-i)
allrows=[];windows=[];stacks=[];resources=[]
for label in ['window8','window12-prelude2']:
 x=json.loads((D/(label+'-case.json')).read_text());assert x['passed'];text=(D/(label+'-node.log')).read_text();ev=[json.loads(l[8:])for l in text.splitlines()if l.startswith('STEP35C ')];base=ev[0]['mono_ns'];ready=[e for e in ev if e['event']=='proposer_ready'];out=[]
 for ordinal,it in enumerate(x['records'],1):
  r=it['row'];tx=r['response']['tx_id'];same=[e for e in ev if e.get('tx_id')==tx];stamp=lambda n:next(e for e in same if e['event']==n);a=stamp('rpc_tx_begin');v=stamp('vm_invoke_begin');z=stamp('rpc_tx_end');restore=next((e for e in ready if a['mono_ns']<e['mono_ns']<v['mono_ns']and e['ready']),None);gas=r['response']['contract_result']['gas_used'];assert gas==120127
  out.append(dict(run=label,phase='prelude'if it['tag'].startswith('prelude')else'diagnostic_window',submitted_ordinal=ordinal,window_request_number=int(it['tag'].split('-')[-1])+1 if it['tag'].startswith('target')else'outside_window',tx_id=tx,block_height=it['committed']['block_height'],sdk_ms=r['elapsed_ns']/1e6,sdk_start_wall_ns=r['sdk_start_wall_ns'],sdk_end_wall_ns=r['sdk_end_wall_ns'],rpc_begin_node_mono_ns=a['mono_ns'],vm_begin_node_mono_ns=v['mono_ns'],rpc_end_node_mono_ns=z['mono_ns'],rpc_to_vm_ms=(v['mono_ns']-a['mono_ns'])/1e6,rpc_since_first_ready_ms=(a['mono_ns']-base)/1e6,vm_since_first_ready_ms=(v['mono_ns']-base)/1e6,ready_recovery_since_first_ready_ms=(restore['mono_ns']-base)/1e6 if restore else'no_true_between',gas=gas,committed=True))
 allrows+=out;target=[r for r in out if r['phase']=='diagnostic_window'];dur=x['window']['window_ns']/1e9;windows.append(dict(run=label,N=len(target),prelude_count=len(out)-len(target),p50_ms=st.median(r['sdk_ms']for r in target),p95_ms=q([r['sdk_ms']for r in target],.95),mean_ms=st.mean(r['sdk_ms']for r in target),window_seconds=dur,submitted=len(target),confirmed=len(target),submit_tps=len(target)/dur,slow_window_ordinals=','.join(str(r['window_request_number'])for r in target if r['sdk_ms']>1000),slow_block_heights=','.join(str(r['block_height'])for r in target if r['sdk_ms']>1000),classification='instrumented mechanism diagnostic; not replacement formal benchmark'))
 chunks=re.findall(r'STEP39D_STACK_BEGIN (\w+)\n(.*?)\nSTEP39D_STACK_END \1',text,re.S);assert len(chunks)==1,label;tx,stack=chunks[0];selected=[]
 for block in stack.split('\n\n'):
  if any(t in block for t in ['RuleManager).NotifyNewBlock','Registry).Start','ConsensusTBFTImpl).handle','ApiService).dealTransact']):selected.append(block)
 assert any('RuleManager).NotifyNewBlock'in s and '[chan send]'in s for s in selected)
 assert any('Registry).Start'in s and '[sleep]'in s for s in selected)
 assert any('ConsensusTBFTImpl).handle'in s and '[select]'in s for s in selected)
 (P/'evidence'/f'{label}-selected-stacks.txt').write_text('\n\n'.join(selected)+'\n');stacks.append(dict(run=label,tx_id=tx,full_stack_bytes=len(stack.encode()),rule_notify_blocked=True,registry_start_sleeping=True,tbft_select_idle=True))
for f in D.glob('*-outcome.json'):
 x=json.loads(f.read_text());o=x['owner'];assert x['systemd']['ExecMainStatus']=='0'and not x['reason']and x['pid_exited']and x['cgroup_empty']and o['stores_created']==o['stores_closed']and o['instances_created']==o['instances_closed']and o['managed_pending']==0
 resources.append(dict(run=x['label'],rss_peak_mib=x['peak_rss_kib']/1024,threads_peak=x['peak_threads'],stop_seconds=x['stop_s'],stores_created=o['stores_created'],stores_closed=o['stores_closed'],instances_created=o['instances_created'],instances_closed=o['instances_closed'],exit_code=0,managed_pending=0))
assert len(allrows)==22 and [r['window_request_number']for r in allrows if r['sdk_ms']>1000]==[5,3]
save('DIAGNOSTIC_TIMELINE.csv',allrows);save('DIAGNOSTIC_WINDOWS.csv',windows);save('DIAGNOSTIC_RESOURCES.csv',resources);(P/'evidence/diagnostic-stack-checks.json').write_text(json.dumps(stacks,indent=2));print('Two diagnostic windows reproduced:5→3, bothheight6;22 confirmed includes2prelude; allresources balanced')
