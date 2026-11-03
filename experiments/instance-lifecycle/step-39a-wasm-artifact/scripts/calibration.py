from run import *
def parity(labels,tag):
 d=[]
 for label in labels:
  rows=[json.loads(l[7:])for l in(P/'raw_logs'/f'{label}.log').read_text().splitlines()if l.startswith('STEP38 ')and '"target"'in l]
  d.append([{k:r[k]for k in ['tx_id','result','rwset','before_hash','after_hash']}for r in rows])
 assert len(d[0])==4 and all(x==d[0]for x in d)
 (P/'audit'/f'parity-{tag}.json').write_text(json.dumps({'labels':labels,'passed':True,'warm_and_formal':4}))
for batch in [1,2,3]:
 for j,case in enumerate(['compute_hashCal','exchange_buyNow','bigInput_inputSize']):
  order=['A','B']if(batch+j)%2 else['B','A'];labels=[]
  for mode in order:
   label=f'lean-{case}-b{batch}-{mode}';execute(label,'A',case,mode,batch=batch,binary_label='vm-lean');labels.append(label)
  parity(labels,f'lean-{case}-b{batch}')
