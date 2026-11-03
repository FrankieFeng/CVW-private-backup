from pathlib import Path
import subprocess,json,hashlib,sys
P=Path(__file__).resolve().parents[1];label=sys.argv[1];test=label=='observer-test';cwd=P/'source/readiness'if test else Path('/home/frankie/mygitprojects/.worktrees/node-step39e')
args=['test','-v','.']if test else ['build','-p=2','-o',str(P/'binaries/node-ready'),'./main']
cmd=['systemd-run','--user','--wait','--pipe','--collect','--unit=step39e-build-'+label,'-p','MemoryMax=2G','-p','TasksMax=192','-p','RuntimeMaxSec=180s','--working-directory='+str(cwd),'--setenv=GOWORK=off','--setenv=GOPROXY=off','--setenv=GOTOOLCHAIN=local','--setenv=GOMAXPROCS=2','/usr/local/go/bin/go']+args
out=P/'raw_logs'/('build-'+label+'.log');assert not out.exists();
if not test:assert not(P/'binaries/node-ready').exists(),'preserve existing measured binary; rebuild only in a new experiment copy'
(P/'evidence'/('build-'+label+'-command.json')).write_text(json.dumps(cmd,indent=2))
with out.open('w')as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
x={'returncode':r.returncode};b=P/'binaries/node-ready'
if not test and b.exists():x['binary_sha']=hashlib.sha256(b.read_bytes()).hexdigest()
(P/'evidence'/('build-'+label+'-result.json')).write_text(json.dumps(x,indent=2));print(label,r.returncode,flush=True);print(out.read_text()[-1600:]);raise SystemExit(r.returncode)
