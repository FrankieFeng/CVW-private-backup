"""Read-only fixture/source/WASM validation. Does not run a Go test binary or guest."""
from pathlib import Path
import csv,json,hashlib,re,subprocess
ROOT=Path(__file__).resolve().parent.parent
WORK=Path('/home/frankie/mygitprojects/.worktrees/cvw-step21c')
VM=WORK/'chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0'
manifest=json.loads((ROOT/'fixture-manifest.json').read_text())
source=VM/'step21c_fixture_test.go';text=source.read_text()
entry=re.search(r'func TestStep21CRealCrossContractPrepared\(t \*testing.T\)\s*\{\s*t.Skip\(',text)
assert entry,'guest test entry must remain unconditionally skipped'
assert not re.search(r'^func init\(',text,re.M),'no package initializer may launch the fixture'
assert 'r.actual.InvokeTime(' in text and 'return result, order' in text
assert 'vm.NewVmManager(' in text and 'vm.NewTxSimContext(' in text
assert 'answers :=' not in text and 'ctx.SuccessResult(' not in text,'fixture must not generate a guest business response'
assert 'sync.Mutex' not in text and 'sync.RWMutex' not in text,'no new global Store execution lock'
assert {'exchange','identity','erc721'}=={a['Contract'] for a in manifest['Artifacts']}

def leb(b,i):
 n=s=0
 while True:
  x=b[i];i+=1;n|=(x&127)<<s
  if not x&128:return n,i
  s+=7;assert s<64

def exports(b):
 assert b[:8]==b'\0asm\1\0\0\0';p=8;out=[]
 while p<len(b):
  kind=b[p];size,start=leb(b,p+1);end=start+size;assert end<=len(b)
  if kind==7:
   n,k=leb(b,start)
   for _ in range(n):
    length,k=leb(b,k);name=b[k:k+length].decode();k+=length;export_kind=b[k];index,k=leb(b,k+1)
    out.append(dict(name=name,kind=export_kind,index=index))
   assert k==end
  p=end
 assert p==len(b)
 return out
required={'exchange':['init_contract','buyNow'],'identity':['init_contract','addWriteList','isApprovedUser'],'erc721':['init_contract','mint','setApprovalForAll2','transferFrom']}
artifacts=[]
for a in manifest['Artifacts']:
 b=Path(a['Path']).read_bytes();assert hashlib.sha256(b).hexdigest()==a['SHA256']
 es=exports(b);missing=set(required[a['Contract']])-{x['name'] for x in es};assert not missing,missing
 artifacts.append(dict(contract=a['Contract'],path=a['Path'],sha256=a['SHA256'],bytes=len(b),required_exports=required[a['Contract']],exports=es,framing_valid=True,wasmer_validation_executed=False))
inputs=Path(manifest['InputsFile']).read_bytes();assert hashlib.sha256(inputs).hexdigest()==manifest['InputsSHA256'];rows=json.loads(inputs)
assert len(rows)==100 and len({x['tokenId'] for x in rows})==100
assert all(len(x['from'])==40 and len(x['to'])==40 and re.fullmatch('[0-9a-f]+',x['from']) and re.fullmatch('[0-9a-f]+',x['to']) for x in rows)
exchange_source=(WORK/'chainmaker/testdata/exchange/exchange.go').read_text()
call_seq=re.findall(r'ctx.CallContract\("([^\"]+)",\s*"([^\"]+)"',exchange_source)
expected=[('identity','addWriteList'),('identity','isApprovedUser'),('identity','isApprovedUser'),('erc721','mint'),('erc721','setApprovalForAll2'),('erc721','transferFrom')]
assert call_seq==expected
identity_text=(WORK/'chainmaker/testdata/identity/identity.go').read_text()
for method in ['addWriteList','isApprovedUser']:
 start=re.search(r'^func '+method+r'\(',identity_text,re.M).start()
 following=re.search(r'^func ',identity_text[start+1:],re.M)
 body=identity_text[start:start+1+following.start()] if following else identity_text[start:]
 assert not re.search(r'ctx.CallContract\(',body)
assert not re.search(r'ctx.CallContract\(', (WORK/'chainmaker/testdata/erc721/erc721.go').read_text())
# identity.callerAddress has a self-call to identity.address, outside the buyNow path.

with (ROOT/'call_graph.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['sequence','caller','contract','method','expected_depth','basis','executed']);w.writeheader()
 for i,(contract,method) in enumerate(call_seq,1):w.writerow(dict(sequence=i,caller='exchange.buyNow',contract=contract,method=method,expected_depth=1,basis='source + required WASM export, not dynamic confirmation',executed=False))
# Disassemble only for static call-site evidence. wasm-objdump is a parser, not a WASM runtime.
root_artifact=next(a for a in manifest['Artifacts'] if a['Contract']=='exchange')
p=subprocess.Popen(['wasm-objdump','-d',root_artifact['Path']],stdout=subprocess.PIPE,text=True)
lines=[];keep=False
for line in p.stdout:
 if ' func[' in line:keep='<main.buyNow>:' in line
 if keep:lines.append(line)
assert p.wait()==0 and lines
(ROOT/'audit/current-buynow-disassembly.txt').write_text(''.join(lines))
call_sites=[s.strip() for s in lines if re.search(r'\bcall \d+ <.*\.CallContract>',s)]
assert len(call_sites)==6,call_sites
(ROOT/'audit/static-call-sites.json').write_text(json.dumps(dict(count=len(call_sites),sites=call_sites,meaning='six static call sites; branches may return early, no dynamic success claimed'),indent=2)+'\n')
result=dict(artifact_count=3,artifact_hashes_verified=True,required_exports_present=True,input_count=100,unique_tokens=100,source_call_sequence=call_seq,downstream_source_nested_user_contract_calls=0,source_expected_max_depth=1,root_plus_child_Invoke_count_if_success=7,wasm_static_CallContract_sites=6,entry_skip_first=True,compile_only=True,test_binary_executions=0,guest_invocations=0,formal_invocations=0,source_semantic_equivalence_to_all_WASM_unverified=True,guest_correctness='not_tested',native_Store_safety='not_tested_pending_Step21B')
(ROOT/'audit/static-validation.json').write_text(json.dumps(result,indent=2)+'\n')
(ROOT/'audit/artifact-exports.json').write_text(json.dumps(artifacts,indent=2)+'\n')
print(json.dumps(result,indent=2))
