from pathlib import Path
import hashlib,json,re,subprocess,shutil
P=Path(__file__).resolve().parents[1];B=P.parent/'step-23-buy-now-gas-attribution'
manifest=json.loads((B/'inputs/manifest.json').read_text());a=next(a for a in manifest['Artifacts']if a['Contract']=='erc721');w=Path(a['Path']);assert hashlib.sha256(w.read_bytes()).hexdigest()==a['SHA256']
text=subprocess.check_output(['wasm-objdump','-x',str(w)],text=True);(P/'audit/erc721-symbols.txt').write_text(text)
heads=subprocess.check_output(['wasm-objdump','-h',str(w)],text=True);(P/'audit/erc721-sections.txt').write_text(heads)
targets=['main.transferFrom','main.transfer','main.setTokenLatestTxInfo','main.setAccountToken','main.testgasJSONMarshal','main.testgasJSONUnmarshal','main.testgasJsonMarshal_stub','encoding_json.Marshal','encoding_json.typeEncoder','encoding_json.newTypeEncoder','encoding_json.cachedTypeFields','internal_sync.__HashTrieMap_go.shape.interface____go.shape.interface_____.Load','internal_sync.__HashTrieMap_go.shape.interface____go.shape.interface_____.LoadOrStore','internal_sync.__HashTrieMap_go.shape.interface____go.shape.interface_____.Swap','internal_sync.__entry_go.shape.interface____go.shape.interface_____.lookup']
proc=subprocess.Popen(['wasm-objdump','-d',str(w)],stdout=subprocess.PIPE,text=True);out=[];all_headers=[];keep=False
for line in proc.stdout:
 if re.match(r'[0-9a-f]+ func\[',line):
  all_headers.append(line);name=line.split('<',1)[-1].rsplit('>',1)[0];keep=any(name==t or name.startswith(t)for t in targets)
 if keep:out.append(line)
assert proc.wait()==0
(P/'audit/selected-disassembly.txt').write_text(''.join(out));(P/'audit/function-headers.txt').write_text(''.join(all_headers))
# Producers identifies the actual compiler version, independent of nearby source paths.
b=w.read_bytes();i=8;custom={}
def u(data,p):
 n=s=0
 while True:
  q=data[p];p+=1;n|=(q&127)<<s;s+=7
  if q<128:return n,p
while i<len(b):
 kind=b[i];i+=1;n,i=u(b,i);payload=b[i:i+n];i+=n
 if kind==0:
  length,start=u(payload,0);name=payload[start:start+length].decode(errors='replace')
  if name=='producers':custom[name]=payload[start+length:].hex();(P/'audit/producers-readable.txt').write_text(repr(payload[start+length:])+'\n')
(P/'audit/static_identity.json').write_text(json.dumps(dict(wasm_path=str(w),sha256=a['SHA256'],custom=custom,dwarf_present='debug_info'in heads),indent=2)+'\n')
for n in ['README.md','GAS_ATTRIBUTION.md','COPY_PARITY.csv','BLOCK_SUMMARY.csv','verification.json','inputs/business.json','inputs/gas-slots.json','inputs/manifest.json','audit/first_divergences.json','raw_logs/v2-lifecycle-b1-R0.log','raw_logs/v2-lifecycle-b1-R1.log']:
 src=B/n;dst=P/'audit/history'/n;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
for n in ['erc721.go','exchange.go']:
 src=B/'audit/history/step21e/guest-reference'/n
 if src.exists():shutil.copyfile(src,P/'audit'/('reference-'+n))
print('static functions',len(all_headers),'selected lines',len(out),'original WASM unchanged')
