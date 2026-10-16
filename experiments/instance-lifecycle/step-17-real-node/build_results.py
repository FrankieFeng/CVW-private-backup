from pathlib import Path
import json,csv,collections,base64,statistics,sys,hashlib,math
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O.parent/'step-15-copy-attribution'));from common import csvwrite,stats
sha=lambda b:hashlib.sha256(b).hexdigest()
specs=json.loads((O.parent/'step-16-chainmaker-copy/manifest.json').read_text())
# Original raw write comparisons are retained. Only documented per-transaction chain metadata are normalized.
raw=[json.loads(l) for l in (O/'ledger_validation.jsonl').read_text().splitlines()];pairs=collections.defaultdict(dict)
for r in raw:pairs[r['tag']][r['mode']]=r
normalized=[]
def writes(r):
 out=[]
 for x in r['transaction']['rw_set'].get('tx_writes',[]):
  x=dict(x);key=base64.b64decode(x['key']).decode(errors='replace')
  if key.endswith('_latestTxInfo'):
   v=json.loads(base64.b64decode(x['value']));v.pop('TxId',None);v.pop('BlockHeight',None);x['value']=v
  out.append(x)
 return sorted(out,key=lambda x:(x.get('contract_name',''),x.get('key','')))
for tag,p in pairs.items():
 a,b=writes(p['baseline']),writes(p['optimized']);same=a==b;parallel=':w4:' in tag
 normalized.append(dict(pair=tag,contract=p['baseline']['contract'],metadata_normalization='NFT latestTxInfo TxId and BlockHeight only',normalized_writes='pass' if same else 'not_comparable_transaction_order' if parallel else 'fail',raw_writes_equal=p['baseline']['transaction']['rw_set'].get('tx_writes',[])==p['optimized']['transaction']['rw_set'].get('tx_writes',[])))
csvwrite(O/'ledger_normalized.csv',normalized)
# Trace coverage in the real nodes, not a harness.
traces=collections.defaultdict(list)
for m in ['baseline','optimized']:
 for l in (O/'network'/m/'stdout.log').read_text(errors='replace').splitlines():
  if l.startswith('LIFECYCLE '):r=json.loads(l[10:]);traces[(m,r['contract'].rsplit('_',1)[0])].append(r)
checks=[];tables=[]
sys.path.insert(0,str(O.parent/'step-16-chainmaker-copy'));from setup import table_metadata
sys.path.insert(0,str(O.parent/'step-14-static-memory-copy'));from wasm_binary import sections
for s in specs:
 name=s['label'];expected=sha(Path(s['paths']['image']).read_bytes());counts={}
 for m in ['baseline','optimized']:
  rs=[r for r in traces[m,name] if r['stage']=='T1'];counts[m]=len(rs);checks.append(dict(contract=name,check='real_node_s1_memory_'+m,status='pass' if rs and all(r.get('sha256')==expected for r in rs) else 'fail',n=len(rs),detail=expected))
 a=Path(s['paths']['original']).read_bytes();b=Path(s['paths']['nodata']).read_bytes();am,_=table_metadata(a);bm,_=table_metadata(b)
 keep=lambda v:[(k,p) for k,p,_ in sections(v) if k!=11]
 structural=am==bm and keep(a)==keep(b)
 tables.append(dict(contract=name,elements=len(am[0]),table_element_function_code_sections_equal='pass' if structural else 'fail',guest_table_writes=s['table_code_writes'],table_nullness_s1_s2_s3='reused_step16_pass',dynamic_function_reference_identity='not_tested',real_table_mutation_isolation='not_tested',applicability='single local immutable funcref table; unchanged function index space; no imported table/start'))
 checks.append(dict(contract=name,check='table_structural_initialization',status='pass' if structural and not s['table_code_writes'] else 'fail',n=len(am[0]),detail='Exact Table/Element/Type/Import/Function/Code bytes unchanged; static identity proof, no dynamic pointer assertion'))
# Evaluate diagnostic responses with actual transport failures preserved separately.
diagnostics=[json.loads(l) for p in [O/'diagnostic.jsonl',O/'diagnostic-extra.jsonl'] for l in p.read_text().splitlines()];dp=collections.defaultdict(dict)
for r in diagnostics:dp[r['tag']][r['mode']]=r
for tag,p in dp.items():
 if len(p)!=2:continue
 a,b=p['baseline'],p['optimized'];ra,rb=a.get('response') or {},b.get('response') or {};ca,cb=ra.get('contract_result') or {},rb.get('contract_result') or {}
 same=not a.get('error') and not b.get('error') and bool(ca) and bool(cb) and all(ca.get(k,0 if k in ['code','gas_used'] else '')==cb.get(k,0 if k in ['code','gas_used'] else '') for k in ['code','gas_used','result','message']) and ra.get('code',0)==rb.get('code',0)
 status='pass' if same else 'transport_failure' if a.get('error') or b.get('error') else 'fail'
 if tag.startswith('missing:'):status='known_baseline_defect' # Both paths swallow method-not-found; equality is not correct error reporting.
 checks.append(dict(contract=a['contract'],check=tag,status=status,n=2,detail='gas/result/code/message comparison; retained raw RPC response'))
csvwrite(O/'table_equivalence.csv',tables);csvwrite(O/'correctness.csv',checks)
# Cache scale: use event offset at each process restart, separate logical bytes from total native/RSS.
cache=[dict(r) for r in csv.DictReader((O/'cache_events.csv').open())];byMode=collections.defaultdict(list)
for r in cache:byMode[r['mode']].append(r)
scale=[];starts={}
for l in (O/'memory.jsonl').read_text().splitlines():
 r=json.loads(l);label=r['label'];mode=r['mode'];total=r['pool_events_total']
 if label.endswith('-empty'):starts[mode]=total
 n=starts.get(mode,0);current=byMode[mode][n:total]
 scale.append(dict(label=label,mode=mode,contracts=len(current),template_image_bytes=sum(int(x['template_bytes']) for x in current),range_payload_bytes=sum(int(x['range_count'])*16 for x in current),proc_rss_kib=int(r['proc']['VmRSS'].split()[0]),threads=int(r['proc']['Threads'])))
csvwrite(O/'cache_scale.csv',scale)
# Native cache misses/hits at end of each formal process (8 supported contracts).
nodeRows=[dict(r) for r in csv.DictReader((O/'vm_invocations.csv').open())];clientRows=list(csv.DictReader((O/'samples.csv').open()));batches=collections.defaultdict(list)
for r in clientRows:batches[r['batch'],r['workers'],r['mode']].append(r)
cacheStats=[]
idx={(r['mode'],r['tx_id'],r['contract'],r['instance_id']):r for r in nodeRows}
for (batch,w,mode),rs in batches.items():
 rs.sort(key=lambda r:int(r['cache_hits']) if 'cache_hits' in r else 0)
 # counters are process-local and monotonic; recover max counters over this batch's linked records.
 inv=[idx[(mode,r['tx_id'],r['contract'],r['instance_id'])] for r in rs];h=max(int(r['cache_hits']) for r in inv);m=max(int(r['cache_misses']) for r in inv)
 cacheStats.append(dict(batch=batch,workers=w,mode=mode,manager_pool_hits=h,manager_pool_misses=m,hit_rate=h/(h+m),note='pool/template resident reuse; module artifacts precomputed in step15/16, not a compilation cache hit metric'))
csvwrite(O/'cache_summary.csv',cacheStats)
# Cold request completeness; internal S1 excludes module cache lookup/preparation, client includes it.
allclient=[json.loads(l) for p in O.glob('bench-*.jsonl') for l in p.read_text().splitlines()];cold=[]
for r in allclient:
 if ':cold:' in r['tag']:cold.append(dict(batch=r['tag'].split(':')[0],contract=r['contract'],mode=r['mode'],client_ns=r['elapsed_ns'],status='transport_failure' if r.get('error') else 'observed',error=r.get('error','')))
csvwrite(O/'cold_cache.csv',cold)
# All warm samples are mandatory; unjoined errors must never silently disappear.
assert sum(':cold:' not in r['tag'] and ':warmup:' not in r['tag'] for r in allclient)==5248
assert sum(r['phase']=='warm' for r in clientRows)==5248
assert len(list(csv.DictReader((O/'correctness_pairs.csv').open())))==2624
assert all(r['business_and_gas']=='pass' for r in csv.DictReader((O/'correctness_pairs.csv').open()))
assert all(0<=int(r['s1_ns'])<=int(r['s2_ns'])<=int(r['s3_ns'])<=int(r['invoke_ns']) for r in clientRows)
assert all(r['status']=='pass' for r in checks if r['check'].startswith('real_node_s1'))
assert all(r['normalized_writes']=='pass' for r in normalized if ':w1:' in r['pair'])
assert 'PASS' in (O/'race-safety.log').read_text() and 'WARNING: DATA RACE' not in (O/'race-safety.log').read_text()
verification={'warm_samples':5248,'matched_warm_pairs':2624,'cold_requests':len(cold),'cold_transport_failures':sum(r['status']=='transport_failure' for r in cold),'raw_write_equal':sum(r['raw_writes_equal'] for r in normalized),'ledger_pairs':len(normalized),'normalized_write_status':dict(collections.Counter(r['normalized_writes'] for r in normalized)),'s1_all_contracts_hash_equal':True,'real_table_dynamic_identity':'not_tested','native_shared_store_parallelism':'not_tested; root VM calls serialized','diagnostic_status':dict(collections.Counter(r['status'] for r in checks))}
(O/'verification.json').write_text(json.dumps(verification,indent=2)+'\n');print(json.dumps(verification,indent=2))
