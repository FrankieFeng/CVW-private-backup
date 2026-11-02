"""Additional descriptive tables from existing paired transactions; no experiment."""
from pathlib import Path
import csv,json,statistics as st,collections,random,hashlib
P=Path(__file__).resolve().parents[1]
def read(n):return list(csv.DictReader((P/n).open()))
def q(v,p):
 a=sorted(v);k=(len(a)-1)*p;i=int(k);return a[i]+(a[min(i+1,len(a)-1)]-a[i])*(k-i)
def write(n,r):
 keys=list(dict.fromkeys(k for x in r for k in x))
 with(P/n).open('w',newline='')as f:w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows(r)
T=read('RECOMPUTED_TRANSACTIONS.csv');b=collections.defaultdict(list)
for t in T:b[t['case'],t['group'],t['batch']].append(t)
r=[]
for(c,g,batch),ts in sorted(b.items()):
 for m in ['e2e_ms','vm_factory_ms','vm_inner_ms','s0_s1_ms','start_ms','callmethod_ms','newinstance_ms','copy_ms','close_ms','s1_s2_ms']:
  v=[float(x[m])for x in ts];r.append(dict(case=c,group=g,batch=batch,metric=m,N=len(v),mean=st.mean(v),p50=st.median(v),p95=q(v,.95)))
write('GROUP_BATCH_STATISTICS.csv',r)
E=read('PAIRED_EFFECTS.csv');tp=[]
for e in E:
 if e['metric']!='e2e_ms':continue
 v=[float(e['batch'+str(i)+'_tps_gain'])for i in [1,2,3]];seed=int(hashlib.sha256((e['case']+e['left']+e['right']+'TPS').encode()).hexdigest()[:16],16);rng=random.Random(seed);boot=[st.median(rng.choices(v,k=3))for _ in range(10000)];tp.append(dict(case=e['case'],left=e['left'],right=e['right'],N_paired_windows=3,median_tps_gain=st.median(v),mean_tps_gain=st.mean(v),ci95_low=q(boot,.025),ci95_high=q(boot,.975),positive_fraction=sum(x>0 for x in v)/3,batch1=v[0],batch2=v[1],batch3=v[2],bootstrap_seed=seed,status='secondary descriptive; not included in Holm latency family; only3 windows'))
write('TPS_EFFECTS.csv',tp)
# Disjoint seven-instance initialization comparisons for buyNow only.
B=read('BUY_NOW_PHASES.csv');d={g:{(r['batch'],r['slot']):r for r in B if r['group']==g}for g in ['G0','G1','G2','G3']};out=[]
for l,r in [('G0','G1'),('G0','G3'),('G0','G2'),('G1','G2'),('G3','G2')]:
 for m in ['all7_newinstance_ms','all7_copy_ms','all7_start_ms','all7_close_ms']:
  v=[float(d[l][k][m])-float(d[r][k][m])for k in d[l]];out.append(dict(left=l,right=r,metric=m,N=len(v),paired_saving_median=st.median(v),paired_saving_mean=st.mean(v),positive_fraction=sum(x>0 for x in v)/len(v),status='non-overlapping initialization/close windows only; not sum of seven Invokes'))
write('BUY_NOW_INITIALIZATION_EFFECTS.csv',out)
print('extra tables',len(r)if False else len(tp),'TPS contrasts')
