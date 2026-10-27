from pathlib import Path
import csv,json,hashlib
P=Path(__file__).resolve().parents[1]
def read(n):return list(csv.DictReader((P/n).open()))
for r in read('audit/ORIGIN_FILES.csv'):assert hashlib.sha256((P/r['copied_path']).read_bytes()).hexdigest()==r['sha256'],r['copied_path']
mapold={'G1':'G1','G2':'G2','G3':'G4'}
for file,fields in [('ORDER_SENSITIVITY.csv',['paired_saving_median_ms','ci95_low_ms','ci95_high_ms']),('STAGE_EFFECTS.csv',['paired_saving_median_ms','left_median_ms','right_median_ms'])]:
 old=read('audit/original_step25/'+file)
 for r in read(file):
  x=next(x for x in old if(x['case'],x['left'],x['right'])==(r['case'],mapold[r['left']],mapold[r['right']])and all(x[k]==r[k]for k in(['factor','value']if file.startswith('ORDER')else['metric'])))
  for k in fields:
   oldkey='paired_median_ms'if file.startswith('ORDER')and k=='paired_saving_median_ms'else k
   assert abs(float(x[oldkey])-float(r[k]))<1e-10,(file,k)
mat={(r['contract'],r['step25_group']):r for r in read('MATRIX.csv')}
for r in read('TIMING.csv'):
 if r['phase']!='formal':continue
 m=mat[r['contract'],r['old_group']]
 assert r['source_wasm_sha']==m['wasm_sha256']and r['execution_wasm_sha']==m['execution_wasm_sha256']and r['cache_key']==m['actual_cache_key']and r['copy_enabled']=='True'
 assert r['binary_sha']==m['host_binary_sha']
for m in mat.values():assert hashlib.sha256((P/'inputs'/f"{m['contract']}-{m['group']}.wasm").read_bytes()).hexdigest()==m['wasm_sha256']
assert len(read('PAIRED_SAMPLES.csv'))==162 and len(read('PAIRED_EFFECTS.csv'))==9 and len(read('CORRECTNESS.csv'))==177
assert all(r['semantic_equal']=='True'for r in read('CORRECTNESS.csv'))
assert not(P/'PPT.md').exists(),'Step26 produces no presentation'
print('source hashes, direct pairs, semantic checks, order/stage recomputation verified; no new guest run')
