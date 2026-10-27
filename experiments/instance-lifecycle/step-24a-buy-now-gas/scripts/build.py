from pathlib import Path
import hashlib,json,subprocess,sys
P=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
label=sys.argv[1]if len(sys.argv)>1 else'build01'
log=P/'audit'/f'{label}.log';assert not log.exists()
settings=dict(native_sha='dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9',max_pages=512,observer_version='step24a_readonly_hashtrie',copy_enabled=False,module_variants=1,model='Step22 owner cached Store+Module per contract/variant; R0 retains instance, R1/C1 fresh',gas_source_sha=sha((P/'source/vm/step21d_compile.go').read_bytes()),managed_sha=sha((P/'source/vm/wasmer-go/managed.go').read_bytes()),Go='1.25.0',GOMAXPROCS=2,GOGC=100,root_budget_per_process=1)
cfg=sha(json.dumps(settings,sort_keys=True).encode())
assert sha((P/'source/vm/wasmer-go/packaged/lib/linux-amd64/libwasmer.so').read_bytes())==settings['native_sha']
binary=P/'binaries'/f'{label}.test';assert not binary.exists()
cmd=['systemd-run','--user','--wait','--pipe','--collect','--unit=step24a-'+label,'-p','MemoryMax=2G','-p','TasksMax=192','-p','CPUQuota=400%','-p','RuntimeMaxSec=180s','-p','KillMode=control-group','--working-directory='+str(P/'source/vm'),'--setenv=GOROOT=/usr/local/go','--setenv=GOTOOLCHAIN=local','--setenv=GOPROXY=off','--setenv=GOWORK='+str(P/'go.work'),'--setenv=GOMAXPROCS=2','/usr/local/go/bin/go','test','-p=2','-c','-o',str(binary)]
(P/'audit'/f'{label}-command.json').write_text(json.dumps(cmd,indent=2)+'\n')
with log.open('w')as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
out=dict(exit=r.returncode,binary=str(binary),settings=settings,config_sha=cfg)
if not r.returncode:
 out['binary_sha']=sha(binary.read_bytes());out['source_hashes']={str(x.relative_to(P)):sha(x.read_bytes())for x in(P/'source/vm').rglob('*.go')}
 (P/'environment.json').write_text(json.dumps(out,indent=2)+'\n')
(P/'audit'/f'{label}-outcome.json').write_text(json.dumps(out,indent=2)+'\n')
print(log.read_text()[-2000:]);raise SystemExit(r.returncode)
