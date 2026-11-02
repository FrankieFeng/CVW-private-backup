from pathlib import Path
import json,csv,collections,re
P=Path(__file__).resolve().parents[1];S=P.parent/'step-36-e2e-copy-acopy'
expected={1:['G0','G1','G2','G3'],2:['G2','G3','G0','G1'],3:['G1','G0','G3','G2']}
r=list(csv.DictReader((P/'RECOMPUTED_TRANSACTIONS.csv').open()));runs={x['run']:(x['case'],int(x['batch']),x['group'])for x in r};d=collections.defaultdict(list)
for run,(c,b,g)in runs.items():
 stamps=[]
 for l in(S/'raw_logs'/f'{run}-node.log').open():
  if l.startswith('STEP35C '):
   x=json.loads(l[8:])
   if x['event']=='proposer_ready':stamps.append(x['mono_ns'])
 assert stamps,run
 d[c,b].append((min(stamps),g,run))
rows=[]
for(c,b),v in d.items():
 a=sorted(v);assert [g for _,g,_ in a]==expected[b],(c,b,a)
 rows.extend(dict(case=c,batch=b,position=i+1,group=g,run=run,ready_node_mono_ns=t)for i,(t,g,run)in enumerate(a))
with(P/'ACTUAL_RUN_ORDER.csv').open('w',newline='')as f:w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
classif=list(csv.DictReader((P/'METHOD_CLASSIFICATION.csv').open()));ef=list(csv.DictReader((P/'PAIRED_EFFECTS.csv').open()));inter=list(csv.DictReader((P/'INTERACTION_ANALYSIS.csv').open()));ph=list(csv.DictReader((P/'STAGE_BREAKDOWN.csv').open()))
assert len(classif)==37 and len(ef)==925 and len(inter)==37 and len(ph)==37*4*15
assert all(float(x['p_holm_222'])==1 for x in ef if x['metric']=='e2e_ms')
assert all(abs(float(x['cost_interaction_median'])+float(x['saving_synergy_median']))<1e-10 for x in inter)
required=['README.md','METHOD_CLASSIFICATION.csv','PAIRED_EFFECTS.csv','BATCH_ANALYSIS.csv','INTERACTION_ANALYSIS.csv','SOURCE_TRACE.md','COPY_MECHANISM.md','A_MECHANISM.md','GO_RUNTIME_ANALYSIS.md','E2E_ATTRIBUTION.md','CASE_STUDIES.md','OPTIMIZATION_CANDIDATES.md','RENEW_RESEARCH.md','LIMITATIONS.md','NEXT_STEP.md','PROGRESS.md']
assert all((P/n).is_file()for n in required)
(P/'audit/validation.json').write_text(json.dumps(dict(required_deliverables=len(required),actual_order_verified_blocks=len(d),paired_effects=len(ef),interaction_rows=len(inter),stage_rows=len(ph),new_benchmarks=0),indent=2));print((P/'audit/validation.json').read_text())
