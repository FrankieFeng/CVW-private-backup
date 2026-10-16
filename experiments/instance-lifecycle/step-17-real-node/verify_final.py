from pathlib import Path
import csv,json,base64,collections,subprocess,hashlib
O=Path(__file__).resolve().parent
rows=list(csv.DictReader((O/'samples.csv').open()));warm=[r for r in rows if r['phase']=='warm'];assert len(warm)==5248
expected={'compute':'success bigNumCal: 607723520','erc721':'mint success','bigInput':'1024','exchange':'buyNow success','identity':'true','raffle':'ok'}
for r in warm:
 value=base64.b64decode(r['result']).decode();name=r['contract']
 if name in expected:assert value==expected[name],(name,value)
 elif name=='fact':assert value.startswith('s15files17'),value
 elif name=='itinerary':
  v=json.loads(value);assert v['code']==200 and v['data']['ip']=='127.0.0.1' and v['data']['city']=='Shanghai'
 assert int(r['gas'])>0 and r['code']==r['rpc_code']=='0'
inv=list(csv.DictReader((O/'vm_invocations.csv').open()));ids=[(r['mode'],r['instance_id']) for r in inv];assert len(ids)==len(set(ids))
for key in ['a','b','a4','b4']:
 rs=[r for r in warm if r['batch']==key];assert len(rs)==(1600 if key in ['a','b'] else 1024)
assert all(float(r['ci95_high_ns'])<0 for r in csv.DictReader((O/'paired_effects.csv').open()) if r['metric']=='s1_ns')
v=json.loads((O/'verification.json').read_text());v['all_warm_expected_business_outputs']=True;v['fresh_instance_ids_unique']=len(ids);v['no_race_free_node_claim']=True;(O/'verification.json').write_text(json.dumps(v,indent=2)+'\n')
for name in ['CVW','chainmaker-go']:
 assert subprocess.check_output(['git','diff','--binary'],cwd='/home/frankie/mygitprojects/'+name)==(O/(name+'-before.patch')).read_bytes()
print(f'PASS: {len(warm)} expected business outputs, all paired Gas, {len(ids)} unique logged Instance IDs; exclusions retained')
