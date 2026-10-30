from pathlib import Path
import json,hashlib,subprocess,csv,sys
P=Path(__file__).resolve().parents[1];base=Path('/home/frankie/mygitprojects/CVW/experiments/instance-lifecycle/step-33-full-contract-coverage/source/vm');diff=[];index=[]
for p in sorted((P/'source/vm').rglob('*.go')):
 old=base/p.relative_to(P/'source/vm')
 if not old.exists()or old.read_bytes()!=p.read_bytes():diff.append(subprocess.run(['git','diff','--no-index','--ignore-all-space','--',str(old)if old.exists()else'/dev/null',str(p)],capture_output=True,text=True).stdout)
 if p.name.startswith('step34')or p.name in ['instance.go','store.go','module.go','managed.go','wasi.go','memory.go','step22_runtime_test.go','step21d_runtime_test.go','step27_diagnostic.go']:
  for i,l in enumerate(p.read_text().splitlines(),1):
   if l.startswith('func '):index.append(dict(path=str(p.relative_to(P)),line=i,declaration=l[:200]))
(P/'audit/source-semantic.diff').write_text('\n'.join(diff));f=(P/'CODE_INDEX.csv').open('w',newline='');w=csv.DictWriter(f,['path','line','declaration']);w.writeheader();w.writerows(index);f.close()
meta=json.loads((P/'audit/build9-outcome.json').read_text());assert all(hashlib.sha256((P/n).read_bytes()).hexdigest()==h for n,h in meta['source_hashes'].items())
for f,h in json.loads((P/'audit/history-readonly-hashes.json').read_text()).items():assert hashlib.sha256(Path(f).read_bytes()).hexdigest()==h
# Recompute current version only. Prior versions remain explicit raw/audit records.
for script in ['analyze.py','report.py']:
 r=subprocess.run([sys.executable,str(P/'scripts'/script)],capture_output=True,text=True);(P/'audit'/f'final-{script}.log').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr
required=['README.md','ARCHITECTURE.md','OWNERSHIP_MATRIX.md','IMPLEMENTATION.md','MODULE_STORE_COMPATIBILITY.md','LIFECYCLE_TESTS.md','CORRECTNESS.md','RESOURCE_SUMMARY.csv','SAFETY_GATE.md','NEXT_STEP.md','PROGRESS.md'];assert all((P/n).exists()for n in required)
with(P/'audit/RAW_MANIFEST.csv').open('w',newline='')as f:
 w=csv.DictWriter(f,['path','bytes','sha256']);w.writeheader()
 for d in ['raw_logs','inputs']:
  for p in sorted((P/d).rglob('*')):
   if p.is_file():w.writerow(dict(path=str(p.relative_to(P)),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
print('final source hashes, old files, derived statistics and deliverables PASS')
