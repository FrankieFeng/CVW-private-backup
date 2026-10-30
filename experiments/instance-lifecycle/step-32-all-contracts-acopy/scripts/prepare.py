from pathlib import Path
import shutil,json,hashlib,csv,subprocess
ROOT=Path('/home/frankie/mygitprojects');S=ROOT/'CVW/experiments/instance-lifecycle/step-28-six-method-acopy';P=ROOT/'.worktrees/cvw-step32/experiments/instance-lifecycle/step-32-all-contracts-acopy'
shutil.copytree(S/'source',P/'source',dirs_exist_ok=True)
shutil.copyfile(ROOT/'CVW/chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0/wasmer-go/packaged/lib/linux-amd64/libwasmer.so', P/'source/vm/wasmer-go/packaged/lib/linux-amd64/libwasmer.so')
# Native is ignored by Git but stays local and pinned.
N=P/'source/vm/wasmer-go/packaged/lib/linux-amd64/libwasmer.so';assert N.exists();assert hashlib.sha256(N.read_bytes()).hexdigest()=='dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9'
for n in ['go.work','go.work.sum']:(P/n).write_text((S/n).read_text().replace('/.worktrees/cvw-step28/experiments/instance-lifecycle/step-28-six-method-acopy','/.worktrees/cvw-step32/experiments/instance-lifecycle/step-32-all-contracts-acopy'))
old=json.loads((S/'inputs/variants.json').read_text());variants={};lineage=[]
for c in ['compute','fact','erc721','identity','exchange']:
 for g,og,copy in [('G0','G0',False),('G1','G2',False),('G2','G1',True),('G3','G2',True)]:
  a=old[c+'-'+og];src=Path(a['path']);assert src.exists();data=src.read_bytes();assert hashlib.sha256(data).hexdigest()==a['sha'];dst=P/'inputs'/f'{c}-{g}.wasm';dst.write_bytes(data);variants[c+'-'+g]=dict(path=str(dst),sha=a['sha'],copy=copy,group=g);lineage.append(dict(contract=c,group=g,A=g in ['G1','G3'],Copy=copy,source_commit='95903a3',guest_go='1.24.1',B1=False,logical_wasm_sha=a['sha'],path=str(dst),historical_source=str(src)))
(P/'inputs/variants.json').write_text(json.dumps(variants,indent=2))
with(P/'audit/variants.csv').open('w')as f:w=csv.DictWriter(f,fieldnames=list(lineage[0]));w.writeheader();w.writerows(lineage)
# New factorial driver; lifecycle/restore/Gas implementation remains inherited.
s=(S/'source/vm/step28_test.go').read_text().replace('TestStep28Serial','TestStep32Serial').replace('E28_','E32_').replace('step28-','step32-').replace('len(groups) != 3','len(groups) != 4').replace('triple order required','quadruple order required')
s=s.replace('if name != "exchange" {\n\t\t\tt.Fatal("single only buyNow")\n\t\t}\n\t\tgroups = []string{g}', 'groups = strings.Split(g, ",")\n        if len(groups)>2 || (name=="exchange" && len(groups)>1) { t.Fatal("process target-call budget") }')
s=s.replace('if len(groups) == 3 {\n\t\te22Assert(t, receipts["G0"], receipts["G1"])\n\t\te22Assert(t, receipts["G1"], receipts["G2"])\n\t}', 'for i:=1; i<len(groups); i++ { e22Assert(t, receipts[groups[0]], receipts[groups[i]]) }')
(P/'source/vm/step28_test.go').unlink();(P/'source/vm/step32_test.go').write_text(s)
# Count complete per-Store module scope destruction outside the Invoke timing.
f=P/'source/vm/step22_runtime_test.go';s=f.read_text();s=s.replace('"managed_remaining": w.ManagedCount()', '"managed_remaining": w.ManagedCount(), "store_scopes_closed": len(s.order), "module_scopes_closed": len(s.order)');f.write_text(s)
for n in ['run.py','build.py','check_pair.py']:
 s=(S/'scripts'/n).read_text().replace('step28','step32').replace('Step28','Step32').replace('E28_','E32_')
 if n=='build.py':s=s.replace("'host_base':'c8c46ee'","'host_base':'29950ab1'").replace("one triple/process or one real buyNow/group/process", "at most2 groups/process; buyNow1 group/process")
 if n=='run.py':
  s=s.replace("order='G0,G1,G2'","order='G0,G1,G2,G3'").replace("P/'binaries/build3.test'","P/'binaries/build1.test'").replace("P/'audit/build3-outcome.json'","P/'audit/build1-outcome.json'")
  s=s.replace("group=single or 'G0'","group=(single or 'G0').split(',')[0]")
  s=s.replace("default='G0,G1,G2'","default='G0,G1,G2,G3'")
  s=s.replace("1 triple or 1 split group","one split block chunk, max2 targets")
 (P/'scripts'/n).write_text(s)
# Historical audit source hashes, not mixed into new measurements.
h={}
for step in ['step-18-combined-cold-start','step-22-serial-static-copy','step-24b-copy-invoke','step-25-ab-copy-screening','step-26-ab-copy-incremental','step-27-normalcal-diagnostic','step-28-six-method-acopy','step-29-buy-now-attribution','step-30-e2e-copy-validation']:
 d=S.parent/step
 for name in ['README.md','BUILD_LINEAGE.md','CORRECTNESS.md','RESULTS.md','PAIRED_EFFECTS.csv']:
  f=d/name
  if f.exists():h[str(f)]=hashlib.sha256(f.read_bytes()).hexdigest()
(P/'audit/history-manifest.json').write_text(json.dumps(h,indent=2));print('ready',P)
