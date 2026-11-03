from pathlib import Path
import subprocess,sys,json,hashlib
P=Path(__file__).resolve().parents[1];part=sys.argv[1];label=sys.argv[2]if len(sys.argv)>2 else part;v=P/'source'/'vm'if label!='lean'else P/'source/lean/vm';log=P/'audit'/f'build-{label}.log';out=P/'binaries'/f'vm-{label}';assert not out.exists()and not log.exists()
# Reuse only the already-identified Selector-fixed native artifact; never download/replace another ABI.
import shutil
lib=Path('/home/frankie/mygitprojects/.worktrees/cvw-step35b/experiments/instance-lifecycle/step-35b-native-wasi-thread/libraries/patched/libwasmer.so')
assert hashlib.sha256(lib.read_bytes()).hexdigest()=='56b236ce1772b805819aec7c10eb417cd62bf0c6ee2c9b581e651f746bec17dc'
dest=v/'wasmer-go/packaged/lib/linux-amd64/libwasmer.so'
if not dest.exists():shutil.copy2(lib,dest)
assert hashlib.sha256(dest.read_bytes()).hexdigest()==hashlib.sha256(lib.read_bytes()).hexdigest()
out.parent.mkdir(exist_ok=True)
files=list(v.rglob('*.go'));cmd=['systemd-run','--user','--wait','--pipe','--collect','--unit=step39a-build-'+label,'-p','MemoryMax=2G','-p','TasksMax=192','-p','RuntimeMaxSec=180s','--working-directory='+str(v),'--setenv=GOWORK='+str(P/('lean.work'if label=='lean'else part+'.work')),'--setenv=GOPROXY=off','--setenv=GOTOOLCHAIN=local','--setenv=GOMAXPROCS=2','/usr/local/go/bin/go','test',*(['-race']if label=='race'else[]),'-p=2','-c','-o',str(out)];(P/'audit'/f'build-{label}-command.json').write_text(json.dumps(cmd,indent=2))
with log.open('w')as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
x={'exit':r.returncode,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()if out.exists()else None,'source_hashes':{str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest()for f in files}};(P/'audit'/f'build-{label}-outcome.json').write_text(json.dumps(x,indent=2));print(log.read_text()[-2800:]);raise SystemExit(r.returncode)
