from pathlib import Path
import csv,statistics as st
P=Path(__file__).resolve().parents[1]
rows=[r for r in csv.DictReader((P/'TIMING.csv').open())if r['phase']=='formal'and r['case']=='buyNow'and r['method']!='init_contract'and r['valid_block']=='True']
lookup={}
for r in rows:lookup.setdefault((int(r['batch']),int(r['slot']),r['group']),[]).append(r)
for k,v in lookup.items():
 v.sort(key=lambda r:int(r['instance_id']));assert len(v)==7 and v[0]['depth']=='0'
result=[]
for left,right in [('G0','G1'),('G1','G2'),('G0','G2')]:
 for index in range(7):
  for metric in ['invoke_ns','newinstance_ns','copy_ns','start_ns','export_call_ns','to_s1_ns']:
   values=[]
   for batch in range(1,4):
    for slot in range(1,11):
     a,b=lookup[(batch,slot,left)][index],lookup[(batch,slot,right)][index];assert(a['contract'],a['method'])==(b['contract'],b['method']);values.append((int(a[metric])-int(b[metric]))/1e6)
   result.append(dict(left=left,right=right,call_index=index,contract=a['contract'],method=a['method'],metric=metric,n=len(values),paired_save_median_ms=st.median(values),paired_save_mean_ms=st.mean(values)))
with(P/'CHILD_EFFECTS.csv').open('w',newline='')as f:
 w=csv.DictWriter(f,list(result[0]));w.writeheader();w.writerows(result)
lines=['# buyNow根与子窗口（同区块直接差）','','正值=左−右，右侧快。每项30个区块，root index0为包含所有子调用的完整Invoke；禁止把root与children再次相加。子窗口是解释性统计，没有单独确认CI。','','| 对照 | 调用 | 方法 | Invoke配对节省Median ms | _start配对节省Median ms |','|---|---:|---|---:|---:|']
for left,right in [('G0','G1'),('G1','G2'),('G0','G2')]:
 for i in range(7):
  rr=[r for r in result if r['left']==left and r['right']==right and r['call_index']==i];a=next(r for r in rr if r['metric']=='invoke_ns');b=next(r for r in rr if r['metric']=='start_ns');lines.append(f"| {left}→{right} | {i} | {a['contract']}.{a['method']} | {a['paired_save_median_ms']:.3f} | {b['paired_save_median_ms']:.3f} |")
lines+=['','不能把多列/多行的Median相加解释root差值。原始子窗口、Gas、Instance/Store ID均在TIMING.csv，原始root/child业务回执在raw_logs。子调用均真实执行；差异属于包含初始化、WASI、业务和同步关闭的串行夹具，尚未识别波动的CPU/调度/native机制。']
(P/'BUY_NOW_ANALYSIS.md').write_text('\n'.join(lines)+'\n')
print('child analysis saved')
import random
residuals=[];extra=[]
def root(v):return int(v[0]['export_call_ns'])
def child(v):return sum(int(r['invoke_ns'])for r in v[1:])
def pct(v,p):
 v=sorted(v);pos=(len(v)-1)*p;i=int(pos);return v[i]+(v[min(i+1,len(v)-1)]-v[i])*(pos-i)
for edge,(left,right)in enumerate([('G0','G1'),('G1','G2'),('G0','G2')]):
 vals={metric:{}for metric in ['children_invoke_sum','root_export_minus_child_invokes']}
 for batch in range(1,4):
  for slot in range(1,11):
   a,b=lookup[batch,slot,left],lookup[batch,slot,right]
   vals['children_invoke_sum'][batch,slot]=(child(a)-child(b))/1e6
   vals['root_export_minus_child_invokes'][batch,slot]=((root(a)-child(a))-(root(b)-child(b)))/1e6
 for metric,ds in vals.items():
  rng=random.Random(280028+edge);boots=[]
  for _ in range(10000):
   vv=[]
   for batch in rng.choices([1,2,3],k=3):vv.extend(ds[batch,slot]for slot in rng.choices(list(range(1,11)),k=10))
   boots.append(st.median(vv))
  residuals.append(dict(left=left,right=right,metric=metric,n=30,paired_save_median_ms=st.median(ds.values()),paired_save_mean_ms=st.mean(ds.values()),ci95_low_ms=pct(boots,.025),ci95_high_ms=pct(boots,.975)))
with(P/'BUY_NOW_RESIDUAL.csv').open('w',newline='')as f:
 w=csv.DictWriter(f,list(residuals[0]));w.writeheader();w.writerows(residuals)
extra=['','## 根export窗口扣除六个不重叠子Invoke的残余','','每笔在同一root export区间内，先减六个串行、不重叠的child Invoke，随后对同区块两组残余作直接差。没有把root与children相加；残余包含根Guest工作、VM管理器/host跨调用、子调用退出后trace输出等未细分成本，不能直接命名为Guest计算或GC。','','| 对照 | 窗口 | 配对节省Median [95%CI] ms |','|---|---|---:|']
for r in residuals:extra.append(f"| {r['left']}→{r['right']} | {r['metric']} | {r['paired_save_median_ms']:.3f} [{r['ci95_low_ms']:.3f}, {r['ci95_high_ms']:.3f}] |")
extra+=['','Copy相对Fresh的子Invoke合计节省点估计为正、CI跨零；root残余出现额外耗时；这是本轮buyNow整体收益未确认的直接窗口证据。尚未定位额外时间在根Guest、host编解码、诊断输出、GC/调度中的比例，不能认定为Copy memcpy本身变慢。要定位机制需要独立的低开销host syscall/guest函数追踪或减少诊断输出的对照，不在本轮偷偷改变计时协议。']
with(P/'BUY_NOW_ANALYSIS.md').open('a')as f:f.write('\n'.join(extra)+'\n')
