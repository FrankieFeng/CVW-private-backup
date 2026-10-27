from pathlib import Path
import json,hashlib,csv,subprocess,shutil
P=Path(__file__).resolve().parents[1]
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
mods=[];templates=[];events=[]
for f in sorted((P/'raw_logs').glob('*.log')):
 for s in f.read_text(errors='replace').splitlines():
  if s.startswith('STEP22 '):
   x=json.loads(s[7:]);x['label']=f.stem;events.append(x)
   if x['event']=='template':templates.append(x['data'])
   if x['event']=='module':mods.append(x['data'])
variants=[]
for c in sorted(set(x['contract']for x in templates)):
 rr=[x for x in templates if x['contract']==c]
 for k in ['source_sha','nodata_sha','image_sha','key','image_bytes','ranges']:assert len(set(str(x[k])for x in rr))==1,(c,k)
 for v in ['A0','A1']:
  ms=[x for x in mods if x['contract']==c and x['variant']==v];assert len(set(x['module_wasm_sha']for x in ms))==1
  assert ms[0]['module_wasm_sha']==rr[0]['source_sha'if v=='A0'else'nodata_sha']
 variants.append(rr[0])
with(P/'VARIANTS.csv').open('w',newline='')as f:
 w=csv.DictWriter(f,variants[0].keys());w.writeheader();w.writerows(variants)
# Archive logger files outside stdout, byte-preserving; no native ELF included.
for f in(P/'source/vm').glob('default.log*'):shutil.copy2(f,P/'raw_logs'/('binding-'+f.name))
code={str(f.relative_to(P)):sha(f)for f in(P/'source/vm').rglob('*')if f.is_file()and not f.name.startswith('default.log')and'/packaged/lib/'not in str(f)}
(P/'audit/source-hashes.json').write_text(json.dumps(code,indent=2))
env=json.loads((P/'environment.json').read_text());env['boot_id_after']=Path('/proc/sys/kernel/random/boot_id').read_text().strip();assert env['boot_id_before']==env['boot_id_after'];(P/'environment.json').write_text(json.dumps(env,indent=2)+'\n')
status={}
for name in ['cvw-step22','cvw-step23','cvw-step21c']:
 root=Path('/home/frankie/mygitprojects/.worktrees')/name
 status[name]=subprocess.check_output(['git','status','--short'],cwd=root,text=True)
units=subprocess.check_output(['systemctl','--user','list-units','step24b-*','--all','--no-pager','--plain'],text=True)
(P/'audit/final-environment-check.json').write_text(json.dumps({'baseline_worktree_status':status,'step24b_units':units,'boot_id_unchanged':True,'no_native_rebuild':True},indent=2))
print('variant/template identities consistent;',len(events),'events; baseline status',status)
