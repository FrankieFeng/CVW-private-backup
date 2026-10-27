from pathlib import Path
from spans import P,extract,within,duration
import json,csv,hashlib,collections,subprocess
read=lambda n:list(csv.DictReader((P/n).open()))
T=read('TIMING.csv');ROOT=read('ROOT_TIMING.csv');R=read('RESOURCE_SUMMARY.csv');C=read('CORRECTNESS.csv');CP=read('CHILD_PREPARATION.csv')
main=[r for r in ROOT if r['phase']=='formal'];assert len(main)==180 and len(R)==204
assert len([r for r in C if r['phase']=='formal'])==60
assert len([r for r in CP if r['phase']=='formal'])==540
for mode in ['plain','trace']:
 rr=[r for r in main if r['mode']==mode];assert len(rr)==90
 for g in ['G0','G1','G2']:
  gr=[r for r in rr if r['group']==g];assert len(gr)==30 and collections.Counter(r['batch']for r in gr)==dict.fromkeys(['1','2','3'],10)
 assert set(collections.Counter(r['order']for r in rr if r['group']=='G0').values())=={5}
assert all(r['passed']=='True'and r['created']==r['closed']and r['managed_end']=='0'and r['managed_pending']=='0'and r['cgroup_empty']=='True'and r['all_owned_processes_stopped']=='True'for r in R)
for r in T:
 assert r['policy']=='R1'and r['uses_before']=='0'and r['reused']=='False'and r['managed_before']==r['managed_after']
 assert 0<=int(r['export_call_ns'])<=int(r['callmethod_ns'])<=int(r['invoke_ns'])
 assert 0<=int(r['to_s1_ns'])<=int(r['to_s2_ns'])<=int(r['to_s3_ns'])<=int(r['invoke_ns'])and int(r['close_ns'])>0
for r in main:
 assert r['gas']=='12612158'and r['code']=='0'
 if r['mode']=='trace':
  m,d,sp=extract(r['label']);assert len(d)==6 and sum(x['kind']=='fixture_bytecode_clone'and within(x,next(y for y in sp if y['kind']=='export'and y['method']=='buyNow'))for x in sp)==6
build=json.loads((P/'environment.json').read_text());assert all(hashlib.sha256((P/f).read_bytes()).hexdigest()==s for f,s in build['source_hashes'].items());assert hashlib.sha256(Path(build['binary']).read_bytes()).hexdigest()==build['binary_sha']
for p,h in json.loads((P/'audit/HISTORICAL_REFERENCE.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
assert not(P/'STOP.json').exists()
units=subprocess.check_output(['systemctl','--user','list-units','--all','--no-legend','step29-*'],text=True).strip();assert not units
result=dict(formal_roots=180,formal_children=1080,formal_triple_blocks_per_mode=30,independent_batches_per_mode=3,all_test_processes=204,failed_main_samples=0,excluded_main_blocks=0,fresh_serial_guard_passed=True,source_binary_and_historical_hashes_exact=True,span_partition_checked=True,gas_and_semantics_parity=True,active_step29_units=units,all_checks_pass=True)
(P/'audit/final-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
