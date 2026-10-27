"""Offline verification only; never starts checks or E2E."""
from pathlib import Path
import json,csv,hashlib,subprocess
P=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
for r in json.loads((P/'audit/HISTORICAL_MANIFEST.json').read_text()):assert sha(Path(r['path']))==r['sha256']
outs=[json.loads(f.read_text())for f in sorted((P/'raw_logs').glob('*-outcome.json'))];assert len(outs)==3 and sum(x['passed']for x in outs)==2
assert all(x['pid_stopped']and x['cgroup_empty']for x in outs)
for x in [x for x in outs if x['passed']]:assert x['owner_closed']['managed_pending']==x['owner_closed']['managed_objects']==0 and x['peak_rss_kib']<=768*1024 and x['peak_threads']<=125
raw=(P/'raw_logs/cached-module-fresh-configured.log').read_text();probe=[json.loads(l[7:])for l in raw.splitlines()if l.startswith('STEP22 ')and json.loads(l[7:])['event']=='lifecycle_probe'];assert len(probe)==1 and probe[0]['data']==dict(fresh_count=3,managed_after=0,result=42,zero_new_memory=True)
raw=(P/'raw_logs/owner-errors-configured.log').read_text();assert 'creation_failure_handled'in raw and'close_failure_handled'in raw and'"created":1'in raw and'"closed":1'in raw
assert (P/'STOP.json').exists()and not(P/'STOP_CONFIGURED.json').exists();correction=json.loads((P/'audit/configuration-correction.json').read_text());assert sha(P/'STOP.json')==correction['original_stop_sha256']
assert (P/'raw_logs/cached-module-fresh.log').read_text().startswith('panic: CM_REUSE_EXPERIMENT must explicitly be R0 or R1')
assert list(csv.DictReader((P/'E2E_SAMPLES.csv').open()))==[]
for r in csv.DictReader((P/'PAIRED_EFFECTS.csv').open()):assert r['valid_pairs']=='0'and r['ci95_low_ms']==r['ci95_high_ms']==r['paired_save_median_ms']==r['positive_fraction']==''
for r in csv.DictReader((P/'THROUGHPUT.csv').open()):assert r['numerator']==r['denominator_seconds']==r['value_per_second']==''
assert json.loads((P/'raw_logs/E2E_NOT_RUN.json').read_text())['verdict']=='C'
units=subprocess.check_output(['systemctl','--user','list-units','--all','--no-legend','--plain','step31-*','step32-*'],text=True).strip()
unit_records=[]
for line in units.splitlines():
 name=line.split()[0];text=subprocess.check_output(['systemctl','--user','show',name,'-p','MainPID','-p','ActiveState','-p','SubState','-p','ExecMainStatus','-p','ControlGroup'],text=True);d=dict(l.split('=',1)for l in text.splitlines()if'='in l);assert d['MainPID']=='0'and d['ActiveState']in['failed','inactive'];unit_records.append(dict(unit=name,**d))
(P/'audit/unit-status.json').write_text(json.dumps(dict(records=unit_records,note='initial failed configuration unit retained; MainPID0, no active probe; failure state is not a running process'),indent=2)+'\n')
result=dict(verdict='C',safety_gate='NOT_PASSED',new_protocol_checks_passed=2,configuration_rejected_processes=1,e2e_nodes_started=0,e2e_clients_started=0,e2e_requests=0,e2e_valid_pairs=0,e2e_rounds_completed=0,historical_evidence_unchanged=True,all_probe_processes_stopped=True,all_offline_checks_pass=True)
(P/'audit/final-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
