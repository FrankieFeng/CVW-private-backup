from run import *
CASES=['compute_hashCal','exchange_buyNow','bigInput_inputSize'];GROUPS=['G0','G1','G2','G3']
def targets(label):return [json.loads(l[7:])for l in(P/'raw_logs'/f'{label}.log').read_text().splitlines()if l.startswith('STEP38 ')and'"target"'in l]
def parity(labels,tag):
 sets=[]
 for label in labels:
  rows=targets(label);assert len(rows)==4
  sets.append([{k:r[k]for k in ['tx_id','result','rwset','before_hash','after_hash']}for r in rows])
 assert all(rows==sets[0]for rows in sets),tag+' Gas/state mismatch'
 (P/'audit'/f'parity-{tag}.json').write_text(json.dumps({'labels':labels,'passed':True,'warmup_plus_formal':4}))
if __name__=='__main__':
 assert json.loads((P/'LIFECYCLE_COMPLETE.json').read_text())['passed']
 phase=sys.argv[1]
 if phase=='pre':
  for case in CASES:
   labels=[]
   for group in GROUPS:
    label=f'pre-{case}-{group}';execute(label,'A',case,group,batch='pre',verify=True);labels.append(label)
   parity(labels,'pre-'+case)
  (P/'PRECHECK_COMPLETE.json').write_text(json.dumps({'passed':True,'methods':3,'groups':4}))
 elif phase=='formal':
  assert json.loads((P/'PRECHECK_COMPLETE.json').read_text())['passed'];assert json.loads((P/'audit/race-passed.json').read_text())['passed']
  orders=[['G0','G1','G2','G3'],['G3','G2','G1','G0'],['G1','G0','G3','G2']]
  for batch in [1,2,3]:
   for j,case in enumerate(CASES):
    seq=orders[batch-1];shift=2*(j%2);order=seq[shift:]+seq[:shift];labels=[]
    (P/'audit'/f'order-{case}-b{batch}.json').write_text(json.dumps(order))
    for group in order:
     label=f'formal-{case}-b{batch}-{group}';execute(label,'A',case,group,batch=batch);labels.append(label)
    parity(labels,f'formal-{case}-b{batch}')
   with(P/'PROGRESS.md').open('a')as f:f.write(f'\nBatch{batch} completed across all3methods; raw/parity retained.\n')
  (P/'COMPLETE.json').write_text(json.dumps({'passed':True,'cases':3,'groups':4,'independent_batches':3,'pairs_per_contrast':6,'formal_calls':72}))
 elif phase=='diag':
  for case in CASES:
   for group in ['G1','G3']:execute(f'diag-{case}-{group}','A',case,group,batch='diag',binary_label='vm-diag-r3')
