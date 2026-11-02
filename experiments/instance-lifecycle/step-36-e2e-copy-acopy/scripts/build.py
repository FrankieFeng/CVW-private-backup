from pathlib import Path
import subprocess,json,hashlib,sys
P=Path(__file__).resolve().parents[1];R=Path('/home/frankie/mygitprojects');label=sys.argv[1];target=sys.argv[2];cwd=R/'.worktrees/node-step36'if target in ['node','client']else P/'source/vm';binary=P/'binaries'/label;log=P/'audit'/f'{label}.log';assert not binary.exists()and not log.exists()
args=['build','-p=2','-o',str(binary),('./main'if target=='node'else str(P/'source/client.go')if target=='client'else'.')]
if target=='test':args=['test','-p=2','-c','-o',str(binary)]
argv=['systemd-run','--user','--wait','--pipe','--collect','--unit=step36-'+label,'-p','MemoryMax=2G','-p','TasksMax=192','-p','RuntimeMaxSec=180s','--working-directory='+str(cwd),'--setenv=GOWORK='+('off'if target in ['node','client']else str(P/'go.work')),'--setenv=GOPROXY=off','--setenv=GOTOOLCHAIN=local','--setenv=GOMAXPROCS=2','/usr/local/go/bin/go']+args
(P/'audit'/f'{label}-command.json').write_text(json.dumps(argv,indent=2));
with log.open('w')as f:r=subprocess.run(argv,stdout=f,stderr=subprocess.STDOUT)
x={'exit':r.returncode,'sha256':hashlib.sha256(binary.read_bytes()).hexdigest()if binary.exists()else None,'source_hashes':{str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest()for f in(P/'source').rglob('*.go')}};(P/'audit'/f'{label}-outcome.json').write_text(json.dumps(x,indent=2));print(log.read_text()[-1000:]);raise SystemExit(r.returncode)
