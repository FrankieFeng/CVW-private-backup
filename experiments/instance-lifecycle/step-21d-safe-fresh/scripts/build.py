from pathlib import Path
import subprocess,json,sys,hashlib
p=Path(__file__).resolve().parents[1];label=sys.argv[1];out=p/'audit'/f'{label}.log';assert not out.exists()
(p/'binaries').mkdir(exist_ok=True)
cmd=['systemd-run','--user','--wait','--pipe','--collect','--unit=step21d-'+label,'-p','MemoryMax=2G','-p','TasksMax=192','-p','CPUQuota=400%','-p','RuntimeMaxSec=180s','-p','KillMode=control-group','--working-directory='+str(p/'source/vm'),'--setenv=GOROOT=/usr/local/go','--setenv=GOTOOLCHAIN=local','--setenv=GOPROXY=off','--setenv=GOWORK='+str(p/'go.work'),'--setenv=GOMAXPROCS=2','/usr/local/go/bin/go','test','-p=2','-c','-o',str(p/'binaries/step21d.test')]
(p/'audit'/f'{label}-command.json').write_text(json.dumps(cmd,indent=2))
with out.open('w')as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
(p/'audit'/f'{label}-outcome.json').write_text(json.dumps({'exit':r.returncode}))
print(out.read_text()[-5000:]);raise SystemExit(r.returncode)
