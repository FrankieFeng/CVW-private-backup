from pathlib import Path
import json,csv,hashlib,shutil,subprocess,platform
P=Path(__file__).resolve().parents[1];S=Path('/home/frankie/mygitprojects/CVW/experiments/instance-lifecycle/step-18-combined-cold-start')
sha=lambda b:hashlib.sha256(b).hexdigest()
manifest=json.loads((S/'manifest-full.json').read_text());vr=list(csv.DictReader((S/'variants.csv').open()));matrix=[];mapping={}
for contract in ['compute','fact','erc721']:
 for group,a,p,c in [('G0',0,0,0),('G1',0,0,1),('G2',1,0,1),('G3',0,1,1),('G4',1,1,1)]:
  label=f'{contract}-a{a}p{p}-plain';m=next(m for m in manifest if m['label']==label);v=next(v for v in vr if v['contract']==contract and v['A']==str(a)and v['P']==str(p)and v['C']==str(c)and v['flavor']=='plain')
  blob=Path(m['paths']['original']).read_bytes();assert sha(blob)==v['logical_wasm_sha256'];subprocess.run(['wasm-validate','--enable-all',m['paths']['original']],check=True,capture_output=True)
  out=P/'inputs'/f'{contract}-{group}.wasm';assert not out.exists();out.write_bytes(blob)
  mapping[f'{contract}-{group}']={'path':str(out),'sha':sha(blob),'copy':bool(c),'group':group,'A':a,'B1':p,'original_label':label}
  matrix.append(dict(contract=contract,group=group,A=a,B1=p,Copy=c,status='artifact_verified_pending_preflight',source_commit='95903a3',host_base='570b06a',wasm_sha256=sha(blob),sdk='0.1.3+GetBatchState-removal'if p else'0.1.3',API_compatibility='GetBatchState_removed'if p else'original',flavor='plain',wasm_bytes=len(blob),initial_pages=v['initial_pages'],padding_bytes=v['padding_bytes'],recorded_template_sha256=v['template_sha256'],original_label=label))
(P/'inputs/variants.json').write_text(json.dumps(mapping,indent=2)+'\n')
with(P/'MATRIX.csv').open('w')as f:w=csv.DictWriter(f,fieldnames=matrix[0]);w.writeheader();w.writerows(matrix)
# Historical claimed effects recomputed from paired ORIGINAL raw samples (not Markdown).
q=P/'audit/step24b';rows=list(csv.DictReader((q/'PAIRED_SAMPLES.csv').open()));print('historical paired fields',list(rows[0]))
(P/'audit/host.json').write_text(json.dumps({'kernel':platform.uname()._asdict(),'go':subprocess.check_output(['/usr/local/go/bin/go','version'],text=True),'cpu':subprocess.check_output(['lscpu'],text=True),'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip()},indent=2)+'\n')
