from pathlib import Path
import subprocess,sys,json,hashlib
P=Path(__file__).resolve().parents[1];part=sys.argv[1];label=sys.argv[2]if len(sys.argv)>2 else part;v=P/'source'/part/'vm';log=P/'audit'/f'build-{label}.log';out=P/'binaries'/f'vm-{label}';assert not out.exists()and not log.exists()
files=list(v.rglob('*.go'));cmd=['systemd-run','--user','--wait','--pipe','--collect','--unit=step38-build-'+label,'-p','MemoryMax=2G','-p','TasksMax=192','-p','RuntimeMaxSec=180s','--working-directory='+str(v),'--setenv=GOWORK='+str(P/(part+'.work')),'--setenv=GOPROXY=off','--setenv=GOTOOLCHAIN=local','--setenv=GOMAXPROCS=2','/usr/local/go/bin/go','test','-p=2','-c','-o',str(out)];(P/'audit'/f'build-{label}-command.json').write_text(json.dumps(cmd,indent=2))
with log.open('w')as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
x={'exit':r.returncode,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()if out.exists()else None,'source_hashes':{str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest()for f in files}};(P/'audit'/f'build-{label}-outcome.json').write_text(json.dumps(x,indent=2));print(log.read_text()[-2800:]);raise SystemExit(r.returncode)
