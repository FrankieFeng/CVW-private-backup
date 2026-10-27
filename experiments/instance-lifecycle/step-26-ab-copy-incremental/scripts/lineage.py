"""Read existing binaries, source manifests, git objects and zip candidates. No builds."""
from pathlib import Path
import hashlib,json,csv,subprocess,zipfile,re,shutil
P=Path(__file__).resolve().parents[1];B=P.parent/'step-25-ab-copy-screening';HOME=Path('/home/frankie/mygitprojects');CVW=HOME/'CVW'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def initial_pages(blob):
 def u(b,i):
  n=s=0
  while True:
   c=b[i];i+=1;n|=(c&127)<<s;s+=7
   if c<128:return n,i
 i=8
 while i<len(blob):
  k=blob[i];i+=1;ln,i=u(blob,i);part=blob[i:i+ln];i+=ln
  if k==5:
   count,j=u(part,0);assert count==1;flags,j=u(part,j);pages,j=u(part,j);return pages
 raise ValueError('no declared memory section')
# SDK/padding provenance captured in Step25 is immutable, not a new mechanism.
for src in [B/'audit/step18/recovered-pb/sdk.diff',B/'audit/step18/recovered-pb/RECOVERY.md',B/'audit/step18/pipeline.py']:
 assert src.exists()
zip_path=CVW/'chainmaker/testdata-instrument/testdata-instrument.zip';ziprows=[]
with zipfile.ZipFile(zip_path)as z:
 for n in z.namelist():
  s=n.replace('\\','/');parts=s.split('/')
  if len(parts)>1 and parts[-2]in ['compute','fact','erc721']and parts[-1]in [parts[-2]+'.go',parts[-2]+'-go.wasm']:
   b=z.read(n);r={'entry':s,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
   if s.endswith('compute.go'):r['source_loop_limits']=re.findall(r'i < (\d+)',b.decode(errors='replace'))
   ziprows.append(r)
mat=list(csv.DictReader((B/'MATRIX.csv').open()));binaryrows=[]
for c in ['compute','fact','erc721']:
 for fam,group in [('step24b','G0'),('step18','G1'),('step18','G2'),('step18','G4')]:
  r=next(r for r in mat if r['family']==fam and r['case']==c and r['group']==group);f=B/'inputs'/(f'{c}-step24b-original.wasm'if fam=='step24b'else f'{c}-{group}.wasm');assert sha(f)==r['wasm_sha256'];subprocess.run(['wasm-validate','--enable-all',str(f)],check=True,capture_output=True)
  binaryrows.append({'case':c,'family':fam,'step25_group':group,'sha256':sha(f),'bytes':f.stat().st_size,'memory_initial_pages':initial_pages(f.read_bytes()),'SDK_API':r['API_compatibility'],'source_commit':r['source_commit'],'saved_wasm_valid':True})
# Actual bigNumCal code, retaining full function rather than guessing from today's source.
for fam,file in [('step24b',B/'inputs/compute-step24b-original.wasm'),('step18',B/'inputs/compute-G1.wasm')]:
 p=subprocess.Popen(['wasm-objdump','-d',str(file)],stdout=subprocess.PIPE,text=True);keep=False;out=[]
 for line in p.stdout:
  if re.match(r'[0-9a-f]+ func\[',line):keep='<main.bigNumCal>'in line
  if keep:out.append(line)
 assert p.wait()==0 and out;(P/'audit'/f'{fam}-bigNumCal.txt').write_text(''.join(out))
 assert f'i64.const {100 if fam=="step24b"else 10000}\n'in ''.join(out)
# Cross-family Step25 runs used the same target input and ledger, but binaries/Gas differ.
cross=[]
for c in ['compute','fact','erc721']:
 a=json.loads((B/'raw_logs'/f'{c}-b1-G1-G2-p0-receipts/pair-000-A0.json').read_text());b=json.loads((B/'raw_logs'/f'ref-{c}-b1-p0-receipts/pair-000-A0.json').read_text());ra=dict(a['actual_result']);rb=dict(b['actual_result']);ga=ra.pop('gas_used',0);gb=rb.pop('gas_used',0)
 cross.append({'case':c,'same_business_params':a['business_input']==b['business_input'],'same_fixed_txid':a['tx_id']==b['tx_id'],'same_initial_ledger':a['before_hash']==b['before_hash'],'same_final_ledger':a['after_hash']==b['after_hash'],'same_result_excluding_gas':ra==rb,'same_root_rwset':a['actual_rwset']==b['actual_rwset'],'step18_gas':ga,'step24b_reference_gas':gb,'inputs':a['business_input'],'tx_id':a['tx_id']})
 assert all(cross[-1][k]for k in ['same_business_params','same_fixed_txid','same_initial_ledger','same_final_ledger','same_result_excluding_gas'])
for name,data in [('BINARY_LINEAGE.csv',binaryrows)]:
 with(P/name).open('w')as f:w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
(P/'audit/lineage-findings.json').write_text(json.dumps({'zip_path':str(zip_path),'zip_sha256':sha(zip_path),'zip_candidates':ziprows,'zip_matches_step24b_original':any(z['sha256']==r['sha256']for z in ziprows for r in binaryrows if r['family']=='step24b'),'cross_family_input_checks':cross,'recoverable_step18_saved_artifacts':True,'step24b_A_B1_matching_build':'blocked_not_recovered','new_builds':0,'instrumenter_candidates':'source exists; no evidence tying exact SDK/stdlib/blacklist/flags to original binary; not executed'},indent=2)+'\n')
print('lineage verified: Step18 saved variants; original Step24B match not recovered; zip mismatch; no new build')
