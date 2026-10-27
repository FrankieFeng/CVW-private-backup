from pathlib import Path
import csv,json,hashlib,subprocess
P=Path(__file__).resolve().parents[1]
def read(n):return list(csv.DictReader((P/n).open()))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
for m in json.loads((P/'audit/HISTORICAL_MANIFEST.json').read_text()):assert sha(Path(m['source']))==m['sha256']==sha(P/m['copy'])
for r in json.loads((P/'audit/prerequisite-files.json').read_text()):assert sha(Path(r['path']))==r['sha256']
a=read('E2E_SAMPLES.csv');completed=[r for r in a if r['row_kind']=='completed_response'];pending=[r for r in a if r['row_kind']=='resource_censored_request']
assert len(completed)==207 and len(pending)==1 and all(r['origin_step']=='20'and r['is_step30_new']=='False'for r in a)
assert len(set(r['tx_id']for r in completed))==207 and pending[0]['tx_id']==''
assert all(r['sdk_begin_mono_ns']==r['sdk_end_mono_ns']==r['commit_complete_mono_ns']==''for r in completed)
assert all(r['gas']=='106028'and r['client_success']=='True'and r['root_attempts']=='1'for r in completed)
status=read('EXECUTION_STATUS.csv');assert all(r['new_requests_sent']=='0'and r['new_completed_blocks']=='0'and r['status']=='blocked'for r in status)
for r in read('THROUGHPUT.csv'):
 if r['origin_step']=='30'or r['metric']in['independently_confirmed_commit_tps','vm_factory_equivalent_tps']:assert r['value_per_second']==''
for r in read('PAIRED_EFFECTS.csv'):
 assert r['ci95_low_ms']==r['ci95_high_ms']==''
 if r['origin_step']=='30':assert r['n']=='0'and r['paired_save_median_ms']==r['paired_save_mean_ms']==''
assert all(r['go_heap_bytes']==''for r in read('RESOURCE_SUMMARY.csv'))
assert not list((P/'raw_logs').glob('step30*-requests.jsonl'))
units=subprocess.check_output(['systemctl','--user','list-units','--all','--no-legend','step30-*'],text=True).strip();assert not units
result=dict(scope='audit and historical reanalysis only',new_node_launches=0,new_rpc_requests=0,new_valid_blocks=0,new_independent_batches=0,historical_saved_success_responses=207,historical_unknown_pending=1,historical_files_unchanged=True,missing_new_measurements_not_zero_filled=True,current_step30_units=units,production_vm_modified=False,all_offline_checks_pass=True)
(P/'audit/final-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
