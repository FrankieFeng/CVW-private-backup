"""Recover static type identity and verify offsets from the actual pinned binary, not host ABI."""
from pathlib import Path
import json,struct,re,shutil,hashlib
P=Path(__file__).resolve().parents[1];identity=json.loads((P/'audit/static_identity.json').read_text());b=Path(identity['wasm_path']).read_bytes()
def u(data,p):
 v=s=0
 while True:
  q=data[p];p+=1;v|=(q&127)<<s;s+=7
  if q<128:return v,p
def signed(data,p):
 v=s=0
 while True:
  q=data[p];p+=1;v|=(q&127)<<s;s+=7
  if q<128:return v-(1<<s)if q&64 else v,p
i=8;payloads={}
while i<len(b):k=b[i];i+=1;n,i=u(b,i);payloads[k]=b[i:i+n];i+=n
m=payloads[5];n,p=u(m,0);assert n==1;flags,p=u(m,p);pages,p=u(m,p);image=bytearray(pages*65536)
d=payloads[11];n,p=u(d,0)
for _ in range(n):
 flag,p=u(d,p);assert flag in [0,2]
 if flag==2:index,p=u(d,p);assert index==0
 assert d[p]==0x41;p+=1;offset,p=signed(d,p);assert d[p]==0xb;p+=1;length,p=u(d,p);image[offset:offset+length]=d[p:p+length];p+=length
assert p==len(d)
q=lambda off:struct.unpack_from('<Q',image,off)[0]
ptr_type=89248;struct_type=214464
assert q(ptr_type)==8 and image[ptr_type+23]&31==22 and q(ptr_type+48)==struct_type
assert q(struct_type)==56 and image[struct_type+23]&31==25
fields=q(struct_type+56);num=q(struct_type+64);assert num==4
names=[]
for j in range(num):
 namep=q(fields+24*j);length,start=u(image,namep+1);name=bytes(image[start:start+length]).decode();names.append(dict(name=name,type=q(fields+24*j+8),offset=q(fields+24*j+16)))
assert [r['name']for r in names]==['TxId','BlockHeight','From','To']
asm=(P/'audit/selected-disassembly.txt').read_text()
def function(name):
 chunks=re.split(r'(?=^[0-9a-f]+ func\[)',asm,flags=re.M)
 return next(c for c in chunks if '<'+name+'>:'in c.split('\n',1)[0])
encoder=function('encoding_json.typeEncoder');field=function('encoding_json.cachedTypeFields');load=function('internal_sync.__HashTrieMap_go.shape.interface____go.shape.interface_____.Load');lookup=function('internal_sync.__entry_go.shape.interface____go.shape.interface_____.lookup')
assert 'i64.const 2267392'in encoder and 'i64.const 2267456'in field
for name in ['main.setTokenLatestTxInfo','main.testgasJsonMarshal_stub','main.testgasJsonMarshal_stub2']:
 x=function(name);assert 'i64.const 89248'in x and '<encoding_json.Marshal>'in x
assert 'i64.const 16'in load and 'i64.const 24'in load and 'i64.const 15'in load and 'i64.load8_u 0 0'in load
assert 'i64.load 3 16'in lookup and 'i64.load 3 24'in lookup and 'i64.load 3 32'in lookup and 'i64.load 3 40'in lookup and 'i64.const 8'in lookup
root=Path('/home/frankie/mygitprojects/CVW/experiments/instance-lifecycle/step-18-combined-cold-start/toolchains/go1.24.1-diagnostic/src')
for rel in ['internal/sync/hashtriemap.go','internal/abi/type.go','encoding/json/encode.go']:
 dst=P/'audit/go1.24.1-reference'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/rel,dst)
elems={int(a):dict(function_index=int(f),name=n)for a,f,n in re.findall(r'elem\[(\d+)\] = ref.func:(\d+) <([^>]+)>',(P/'audit/erc721-symbols.txt').read_text())}
out=dict(wasm_sha=identity['sha256'],compiler='go1.24.1 from producers; local sources are layout reference, not exact rebuilt toolchain proof',dwarf_available=False,encoder_cache=2267392,field_cache=2267456,target_pointer_type=ptr_type,target_struct_type=struct_type,fields=names,reflect_type_interface_itab=519328,encoder_func_value_type=138816,layout=dict(map_root_offset=16,node_tag=0,indirect_children=24,child_count=16,entry_overflow=8,entry_key_type=16,entry_key_data=24,entry_value_type=32,entry_value_data=40),static_image_sha256=hashlib.sha256(image).hexdigest(),table_element_map=elems)
(P/'inputs/cache-layout.json').write_text(json.dumps(out,indent=2)+'\n')
print('verified target type fields',names,'cache globals',out['encoder_cache'],out['field_cache'])
