"""Reproduction build only; preserves existing measurement binary and logs."""
from pathlib import Path
import hashlib,json,subprocess,sys
P=Path(__file__).resolve().parents[1]
label=sys.argv[1]if len(sys.argv)>1 else'replay-build'
out=P/'audit'/f'{label}.log';binary=P/'binaries'/f'{label}.test'
assert not out.exists()and not binary.exists()
native=P/'source/vm/wasmer-go/packaged/lib/linux-amd64/libwasmer.so'
assert hashlib.sha256(native.read_bytes()).hexdigest()==json.loads((P/'environment.json').read_text())['config']['settings']['native_sha']
cmd=['systemd-run','--user','--wait','--pipe','--collect','--unit=step24b-'+label,'-p','MemoryMax=2G','-p','TasksMax=192','-p','CPUQuota=400%','-p','RuntimeMaxSec=180s','-p','KillMode=control-group','--working-directory='+str(P/'source/vm'),'--setenv=GOROOT=/usr/local/go','--setenv=GOTOOLCHAIN=local','--setenv=GOPROXY=off','--setenv=GOWORK='+str(P/'go.work'),'--setenv=GOMAXPROCS=2','/usr/local/go/bin/go','test','-p=2','-c','-o',str(binary)]
(P/'audit'/f'{label}-command.json').write_text(json.dumps(cmd,indent=2)+'\n')
with out.open('w')as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
result=dict(exit=r.returncode,binary=str(binary))
if r.returncode==0:result['sha256']=hashlib.sha256(binary.read_bytes()).hexdigest()
(P/'audit'/f'{label}-outcome.json').write_text(json.dumps(result,indent=2)+'\n')
print(result);raise SystemExit(r.returncode)
