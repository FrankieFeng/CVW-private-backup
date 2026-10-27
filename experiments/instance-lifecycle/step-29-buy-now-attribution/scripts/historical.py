from pathlib import Path
import json,csv,statistics as st
P=Path(__file__).resolve().parents[1];S=Path(json.loads((P/'audit/step28-reference.json').read_text())['directory'])
rows=[]
for batch in range(1,4):
 for slot in range(1,11):
  for g in ['G0','G1','G2']:
   label=f'formal-buyNow-b{batch}-s{slot:02d}-{g}';text=(S/'raw_logs'/f'{label}.log').read_text();samples=[json.loads(l[7:])['data']for l in text.splitlines()if l.startswith('STEP22 ')and json.loads(l[7:])['event']=='sample'];target=[r for r in samples if r['tx_id']=='step28-buyNow-fixed'];assert len(target)==7
   root=next(r for r in target if r['depth']==0);children=[r for r in target if r['depth']==1];total=sum(r['invoke_ns']for r in children);assert total<=root['export_call_ns'];rows.append(dict(batch=batch,slot=slot,group=g,log=str(S/'raw_logs'/f'{label}.log'),invoke_ns=root['invoke_ns'],root_export_ns=root['export_call_ns'],children_invoke_sum_ns=total,root_export_residual_ns=root['export_call_ns']-total))
lookup={(r['batch'],r['slot'],r['group']):r for r in rows};effects=[]
for l,r in [('G0','G1'),('G1','G2'),('G0','G2')]:
 for metric in ['invoke_ns','root_export_residual_ns']:
  ds=[(lookup[b,s,l][metric]-lookup[b,s,r][metric])/1e6 for b in range(1,4)for s in range(1,11)];effects.append(dict(source='Step28 raw logs only; no new sample pooled',left=l,right=r,metric=metric,n=30,paired_save_median_ms=st.median(ds)))
for name,data in [('HISTORICAL_ROOT_TIMING.csv',rows),('HISTORICAL_PAIRED_RECALC.csv',effects)]:
 with(P/'audit'/name).open('w',newline='')as f:w=csv.DictWriter(f,list(data[0]));w.writeheader();w.writerows(data)
print('Step28 90 original root logs re-read; paired medians',effects)
