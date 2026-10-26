from pathlib import Path
import json,csv
P=Path(__file__).resolve().parents[1]
rows=[];preps=[];conditions=[]
for file in sorted((P/'raw_logs').glob('*-outcome.json')):
 o=json.loads(file.read_text());label=o['label'];conditions.append(o)
 for s in (P/'raw_logs'/f'{label}.log').read_text(errors='replace').splitlines():
  if s.startswith('STEP22 '):
   x=json.loads(s[7:]);r=x['data']
   if x['event']=='sample':rows.append(dict(label=label,phase=o['phase'],condition_contract=o['contract'],passed_process=o['passed'],**r))
   elif x['event']in['module','template','cache_closed','preparation_total']:preps.append(dict(label=label,event=x['event'],**r))
def write(name,rs):
 fields=list(dict.fromkeys(k for r in rs for k in r))
 with(P/name).open('w',newline='')as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rs)
write('samples.csv',rows);write('preparation.csv',preps);write('per_run_summary.csv',conditions)
print('saved',len(rows),'invoke records,',len(conditions),'processes')
