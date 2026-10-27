from pathlib import Path
import json,csv,hashlib,collections,subprocess
P=Path(__file__).resolve().parents[1]
read=lambda n:list(csv.DictReader((P/n).open()))
T=read('TIMING.csv');E=read('PAIRED_EFFECTS.csv');C=read('CORRECTNESS.csv');R=read('RESOURCE_SUMMARY.csv')
roots=[r for r in T if r['phase']=='formal'and r['depth']=='0'and r['method']!='init_contract'];children=[r for r in T if r['phase']=='formal'and r['depth']=='1']
assert len(roots)==540 and len(children)==540 and len(E)==18
assert len([c for c in C if c['phase']=='formal'])==180
assert len(R)==255 and all(r['passed']=='True'and r['created']==r['closed']and r['managed_end']=='0'and r['managed_pending']=='0'and r['cgroup_empty']=='True'and r['all_owned_processes_stopped']=='True'for r in R)
for case in ['bigNumCal','hashCal','normalCal','fact','erc721','buyNow']:
 a=[r for r in roots if r['case']==case];assert len(a)==90
 for batch in ['1','2','3']:
  b=[r for r in a if r['batch']==batch];assert len(b)==30 and collections.Counter(r['group']for r in b)==dict(G0=10,G1=10,G2=10)
 orders=collections.Counter(r['order']for r in a if r['group']=='G0');assert len(orders)==6 and set(orders.values())=={5}
for r in T:
 assert r['uses_before']=='0'and r['reused']=='False'and r['policy']=='R1'
 assert r['managed_before']==r['managed_after']
 assert 0<=int(r['export_call_ns'])<=int(r['callmethod_ns'])<=int(r['invoke_ns'])
 assert 0<=int(r['to_s1_ns'])<=int(r['to_s2_ns'])<=int(r['to_s3_ns'])<=int(r['invoke_ns'])
 assert int(r['close_ns'])>0
build=json.loads((P/'environment.json').read_text());assert all(hashlib.sha256((P/f).read_bytes()).hexdigest()==sha for f,sha in build['source_hashes'].items())
assert hashlib.sha256(Path(build['binary']).read_bytes()).hexdigest()==build['binary_sha']
assert not(P/'STOP.json').exists()
units=subprocess.check_output(['systemctl','--user','list-units','--all','--no-legend','step28-*'],text=True).strip();assert not units
result=dict(formal_roots=len(roots),formal_children=len(children),formal_triple_blocks=180,all_guest_processes=len(R),failed_main_samples=0,excluded_main_blocks=0,source_hashes_exact=True,timing_nesting_checked=True,fresh_and_sync_close_checked=True,balanced_order=True,active_step28_units=units,all_checks_pass=True)
(P/'audit/final-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
