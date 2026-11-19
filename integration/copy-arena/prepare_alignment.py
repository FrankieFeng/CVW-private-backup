from pathlib import Path
import struct
def u(b,p):
 v=s=0
 while True:
  a=b[p];p+=1;v|=(a&127)<<s
  if a<128:return v,p
  s+=7
def sections(b):
 p=8;out=[]
 while p<len(b):
  k=b[p];n,q=u(b,p+1);out.append((k,b[q:q+n]));p=q+n
 return out
def name(b,p):
 n,p=u(b,p);return b[p:p+n].decode(),p+n
def layout(path):
 sec=sections(path.read_bytes());mem=next(b for k,b in sec if k==5);n,p=u(mem,0);flags,p=u(mem,p);pages,p=u(mem,p);assert n==1
 image=bytearray(pages*65536)
 for k,b in sec:
  if k!=11:continue
  n,p=u(b,0)
  for _ in range(n):
   flag,p=u(b,p)
   if flag==2:idx,p=u(b,p);assert idx==0
   else:assert flag==0
   assert b[p]==0x41;p+=1;offset,p=u(b,p);assert b[p]==0x0b;p+=1;size,p=u(b,p);image[offset:offset+size]=b[p:p+size];p+=size
 candidates=[];hpos=0
 while True:
  h=image.find(bytes.fromhex('f1ffffff00000108'),hpos)
  if h<0:break
  hpos=h+1;pos=0
  while True:
   pos=image.find(struct.pack('<Q',h),pos+1)
   if pos<0:break
   if pos%8 or pos+35*8>len(image):continue
   f=struct.unpack_from('<35Q',image,pos);end=f[34]
   if 0<f[24]<=f[25]<=f[26]<=f[27]<=f[28]<=f[29]<=f[30]<=f[31]<=end<len(image) and (end+(1<<20))//65536==pages:candidates.append({'module_end':end,'bloc':(end+65535)&~65535,'initial_pages':pages})
 assert len(candidates)==1,candidates
 return candidates[0]

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser(description="Existing Step18 Go1.24.1 Arena-padding extraction; output must be new")
 p.add_argument('plain',type=Path);p.add_argument('padding',type=Path);p.add_argument('--arena',type=Path)
 a=p.parse_args();base=layout(a.plain);amount=(4<<20)-base['bloc']-5*65536
 if amount<=0:raise SystemExit('unsupported layout; no padding written')
 text='package main\nimport "unsafe"\nvar experimentHeapLayoutPad = [%d]byte{%d-1:1}\nvar experimentHeapLayoutPadPtr = unsafe.Pointer(&experimentHeapLayoutPad)\nfunc init() { if experimentHeapLayoutPadPtr == nil { panic("experiment heap layout padding unavailable") } }\n'%(amount,amount)
 with a.padding.open('x') as f:f.write(text)
 if a.arena is not None:assert layout(a.arena)['bloc']==(4<<20)-5*65536
 print('padding_bytes',amount,'expected arena bloc', (4<<20)-5*65536)
