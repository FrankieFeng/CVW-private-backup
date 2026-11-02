"""Read frozen WASM sections, mirror plan range logic; never emit modified WASM."""
from pathlib import Path
import json,hashlib,csv,struct
P=Path(__file__).resolve().parents[1];S=P.parent/'step-36-e2e-copy-acopy';V=json.loads((S/'inputs/variants.json').read_text())
class R:
 def __init__(self,b):self.b=b;self.p=0
 def byte(self):x=self.b[self.p];self.p+=1;return x
 def u(self):
  v=s=0
  while True:
   x=self.byte();v|=(x&127)<<s;s+=7
   if x<128:return v
 def si(self):
  v=s=0
  while True:
   x=self.byte();v|=(x&127)<<s;s+=7
   if x<128:return v-(1<<s)if x&64 else v
 def take(self,n):x=self.b[self.p:self.p+n];assert len(x)==n;self.p+=n;return x
rows=[]
for key,v in V.items():
 if not key.endswith(('-G0','-G2')):continue
 f=S/'inputs'/Path(v['path']).name;b=f.read_bytes();assert hashlib.sha256(b).hexdigest()==v['sha'];r=R(b);assert r.take(8)==b'\0asm\1\0\0\0';parts=[];nodata=b[:8];ranges=[];payload=0;segments=0;pages=None
 while r.p<len(b):
  begin=r.p;k=r.byte();d=r.take(r.u());parts.append((k,d))
  if k!=11:nodata+=b[begin:r.p]
  if k==5:
   q=R(d);assert q.u()==1;flags=q.u();pages=q.u()
 assert pages is not None;image=bytearray(pages*65536)
 for k,d in parts:
  if k!=11:continue
  q=R(d);segments=q.u()
  for _ in range(segments):
   flags=q.u();assert flags in[0,2]
   if flags==2:assert q.u()==0
   assert q.byte()==0x41;a=q.si();assert q.byte()==0x0b;p=q.take(q.u());end=a+len(p);assert end<=len(image);image[a:end]=p;payload+=len(p);ranges.append((a,end))
 merged=[]
 for a,e in sorted(ranges):
  if merged and a<=merged[-1][1]:merged[-1]=(merged[-1][0],max(e,merged[-1][1]))
  else:merged.append((a,e))
 copyranges=[(a,e)for a,e in merged if image[a:e].count(0)<e-a];copied=sum(e-a for a,e in copyranges);zeros=sum(image[a:e].count(0)for a,e in copyranges)
 # Same pinned Go moduledata layout validator as historical pipeline, no probe execution.
 candidate=[];start=0
 while True:
  h=image.find(bytes.fromhex('f1ffffff00000108'),start)
  if h<0:break
  start=h+1;pos=0;needle=struct.pack('<Q',h)
  while True:
   pos=image.find(needle,pos+1)
   if pos<0:break
   if pos%8 or pos+35*8>len(image):continue
   fs=struct.unpack_from('<35Q',image,pos);end=fs[34]
   if 0<fs[24]<=fs[25]<=fs[26]<=fs[27]<=fs[28]<=fs[29]<=fs[30]<=fs[31]<=end<len(image)and(end+(1<<20))//65536==pages:candidate.append(end)
 rows.append(dict(contract=key.rsplit('-',1)[0],A=v['A'],wasm_sha256=v['sha'],wasm_bytes=len(b),initial_pages=pages,initial_bytes=len(image),active_segments=segments,payload_bytes=payload,covered_union_bytes=sum(e-a for a,e in merged),copy_ranges=len(copyranges),copy_bytes=copied,zero_bytes_within_copy_ranges=zeros,nonzero_bytes_within_copy_ranges=copied-zeros,template_sha256=hashlib.sha256(image).hexdigest(),nodata_sha256=hashlib.sha256(nodata).hexdigest(),module_end=candidate[0]if len(candidate)==1 else'not_recovered',init_bloc=((candidate[0]+65535)//65536)*65536 if len(candidate)==1 else'not_recovered',range_semantics='merge overlap/adjacency, drop wholly zero merged ranges, retain interior zeros',ranges=json.dumps(copyranges)))
public=[dict({k:v for k,v in r.items()if k!='ranges'},ranges_sha256=hashlib.sha256(r['ranges'].encode()).hexdigest())for r in rows]
with(P/'STATIC_LAYOUT.csv').open('w',newline='')as f:w=csv.DictWriter(f,list(public[0]));w.writeheader();w.writerows(public)
print('frozen layouts',len(rows),'A differences',[(r['contract'],r['A'],r['copy_bytes'],r['zero_bytes_within_copy_ranges'])for r in rows])
# Hypothetical range coalescing operation counts only; no Copy code/output WASM changes.
scenarios=[]
for r in rows:
 rr=json.loads(r['ranges']);base=int(r['copy_bytes'])
 for gap in [0,8,16,64,256,4096,2**32]:
  merged=[]
  for a,e in rr:
   if merged and a-merged[-1][1]<=gap:merged[-1]=(merged[-1][0],e)
   else:merged.append((a,e))
  size=sum(e-a for a,e in merged);scenarios.append(dict(contract=r['contract'],A=r['A'],gap_threshold_bytes=gap,ranges=len(merged),copy_bytes=size,extra_zero_gap_bytes=size-base,original_ranges=r['copy_ranges'],original_copy_bytes=base,evidence='static operation/byte count only; no measured speedup'))
with(P/'COPY_RANGE_SCENARIOS.csv').open('w',newline='')as f:w=csv.DictWriter(f,list(scenarios[0]));w.writeheader();w.writerows(scenarios)
