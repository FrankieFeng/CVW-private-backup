from pathlib import Path
import csv,json,statistics,hashlib,re
P=Path(__file__).resolve().parents[1];H=P/'audit/history21e'
read=lambda p:list(csv.DictReader(p.open()))
old=read(H/'audit/history-normal-samples.csv');assert len(old)==600;out=[]
for mode in ['R0','R1']:
 rr=[r for r in old if r['policy']==mode];assert len(rr)==300
 out.append({'source':'capacity-fixed b/c/d historical','mode':mode,'n':len(rr),'invoke_mean_ms':statistics.mean(float(r['invoke_ms'])for r in rr),'callmethod_mean_ms':statistics.mean(float(r['callmethod_ms'])for r in rr),'export_mean_ms':statistics.mean(float(r['export_ms'])for r in rr)})
short=read(H/'normal_samples.csv');assert len(short)==14 and sum(r['label']in ['normal-ab','normal-ba']for r in short)==12
for label in ['normal-ab','normal-ba']:
 for mode in ['R0','R1']:
  rr=[r for r in short if r['label']==label and r['policy']==mode];assert len(rr)==3;out.append({'source':label,'mode':mode,'n':3,'invoke_mean_ms':statistics.mean(float(r['invoke_ms'])for r in rr),'callmethod_mean_ms':statistics.mean(float(r['callmethod_ms'])for r in rr),'export_mean_ms':statistics.mean(float(r['export_ms'])for r in rr)})
with(P/'HISTORICAL_RECOMPUTATION.csv').open('w')as f:w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
# Verify old B5 links by Instance ID and CallMethod, not trusting Markdown alone.
checks=[]
for r in old:
 file=H/'audit/history-source'/Path(r['source_file']).name;lines=file.read_text().splitlines();i=int(r['sample_line'])-1;prior=[l for l in lines[:i+1]if 'b5_profile 'in l];assert prior
 x=dict(re.findall(r'(\w+)=([^\s]*)',prior[-1].split('b5_profile ',1)[1]));assert x['instance_id']==r['instance_id']and x['sample_id']==r['sample_id']and x['method']=='normalCal';assert abs(int(x['total_ns'])/1e6-float(r['callmethod_ms']))<1.01e-6 and abs(int(x['export_call_ns'])/1e6-float(r['export_ms']))<1e-9;checks.append({'id':r['instance_id'],'b5':x})
(P/'audit/history-raw-links.json').write_text(json.dumps({'raw_B5_records_checked':len(checks),'first_record':checks[0],'note':'IDs/export exactly linked; converted CallMethod CSV allowed <=1ns float truncation difference'},indent=2)+'\n')
print(out)
