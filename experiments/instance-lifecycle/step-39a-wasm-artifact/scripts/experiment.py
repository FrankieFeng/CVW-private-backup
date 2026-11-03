from run import *
CASES=['compute_hashCal','exchange_buyNow','bigInput_inputSize'];MODES=['A','B','C','D']
def targets(label):return [json.loads(l[7:])for l in(P/'raw_logs'/f'{label}.log').read_text().splitlines()if l.startswith('STEP38 ')and'"target"'in l]
def parity(labels,tag):
 d=[targets(l)for l in labels];assert all(len(x)==4 for x in d);keys=['tx_id','result','rwset','before_hash','after_hash']
 ref=[{k:r[k]for k in keys}for r in d[0]]
 for label,rows in zip(labels,d):assert ref==[{k:r[k]for k in keys}for r in rows],label+' business mismatch'
 (P/'audit'/f'parity-{tag}.json').write_text(json.dumps({'labels':labels,'warm_and_formal':4,'passed':True,'keys':keys},indent=2))
for case in CASES:
 labels=[]
 for mode in MODES:
  label='pre-'+case+'-'+mode
  if case=='compute_hashCal'and mode=='A':label='pre-compute-A'
  execute(label,'A',case,mode,batch='pre',verify=True);labels.append(label)
 parity(labels,'pre-'+case)
for batch in [1,2,3]:
 for j,case in enumerate(CASES):
  shift=(j+batch-1)%4;order=MODES[shift:]+MODES[:shift]
  if batch==2:order=order[::-1]
  (P/'audit'/f'order-{case}-b{batch}.json').write_text(json.dumps(order));labels=[]
  for mode in order:
   label=f'formal-{case}-b{batch}-{mode}';execute(label,'A',case,mode,batch=batch);labels.append(label)
  parity(labels,f'{case}-b{batch}')
(P/'COMPLETE.json').write_text(json.dumps({'cases':3,'batches':3,'blocks_per_case':6,'formal_calls':72,'precheck_calls':48}))
