from run import *
CASES=list(json.loads((P/'inputs/cases.json').read_text()));STRATEGIES=['F0','C0','C1','C2','C3','C4']
def targets(label):
 rows=[json.loads(l[7:])for l in(P/'raw_logs'/f'{label}.log').read_text().splitlines()if l.startswith('STEP38 ')];return [r for r in rows if r.get('event')=='target'and r['phase']=='formal']
def signature(row):
 # Only persisted exact result/events/RWSet/state, no performance field normalization.
 return {k:row[k]for k in ['tx_id','result','rwset','before_hash','after_hash']}
def parity(labels,tag):
 a=targets(labels[0]);assert len(a)==2;checks=[]
 for label in labels[1:]:
  b=targets(label);same=all(signature(x)==signature(y)for x,y in zip(a,b))and len(b)==2;checks.append(dict(label=label,matched=same));assert same,('correctness mismatch',tag,label)
 (P/'raw_logs'/f'{tag}-parity.json').write_text(json.dumps({'passed':True,'labels':labels,'checks':checks},indent=2))
def state(x):(P/'STATE.json').write_text(json.dumps(x,indent=2))
# Phase1: every case/candidate full pre-start Memory check. No performance claims here.
for case in CASES:
 labels=[]
 for strategy in STRATEGIES:
  label=f'pre-{case}-{strategy}';state(dict(stage='precheck',case=case,strategy=strategy,label=label));execute(label,'A',case,strategy,verify=True);labels.append(label)
 parity(labels,'pre-'+case)
# Phase2: 3 independent batch process sets, balanced positions; each process2target+2warmup.
for batch in [1,2,3]:
 for j,case in enumerate(CASES):
  shift=(j+2*(batch-1))%len(STRATEGIES);order=STRATEGIES[shift:]+STRATEGIES[:shift]
  if batch==2:order=list(reversed(order))
  labels=[]
  for strategy in order:
   label=f'A-{case}-b{batch}-{strategy}';state(dict(stage='A-formal',case=case,batch=batch,order=order,label=label));execute(label,'A',case,strategy,batch=batch);labels.append(label)
  parity(labels,f'A-{case}-b{batch}')
# PartB isolated C0 instrumented-only. Compare each batch to existing A C0, explicitly noncontemporaneous diagnostic.
for batch in [1,2,3]:
 for case in CASES:
  label=f'B-{case}-b{batch}';state(dict(stage='B-timing',case=case,batch=batch,label=label));execute(label,'B',case,'C0',batch=batch)
  parity([f'A-{case}-b{batch}-C0',label],f'B-{case}-b{batch}')
# Allocation envelopes are intrusive and never merged with timing-only main data.
for case in CASES:
 label=f'B-alloc-{case}';state(dict(stage='B-allocation-diagnostic',case=case,label=label));execute(label,'B',case,'C0',batch=1,alloc=True)
 parity([f'A-{case}-b1-C0',label],f'B-alloc-{case}')
state(dict(stage='completed',formal_A_batches=3,formal_A_blocks_per_case=6,formal_B_batches=3,cases=len(CASES),new_nodes=0));(P/'COMPLETE.json').write_text(json.dumps({'cases':len(CASES),'A_batches':3,'paired_blocks_per_case':6,'B_batches':3,'alloc_runs':len(CASES)}));print('COMPLETE',flush=True)
