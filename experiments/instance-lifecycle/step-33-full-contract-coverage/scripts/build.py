from pathlib import Path
import subprocess,json,hashlib,sys
P=Path(__file__).resolve().parents[1];label=sys.argv[1];out=P/'audit'/f'{label}.log';binary=P/'binaries'/f'{label}.test';assert not out.exists()and not binary.exists()
settings={'native_sha':'dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9','host_go':'1.25.0','guest_go':'1.24.1','host_base':'7eccc36e','max_pages':512,'GOMAXPROCS':2,'GOGC':100,'gas_rule':'unchanged original Step24B/21D','model':'independent Store/module per group and contract; fixed owner; at most2 groups/process; buyNow1 group/process; sync close'}
sha=lambda x:hashlib.sha256(x).hexdigest();assert sha((P/'source/vm/wasmer-go/packaged/lib/linux-amd64/libwasmer.so').read_bytes())==settings['native_sha'];cfg=sha(json.dumps(settings,sort_keys=True).encode())
argv=['systemd-run','--user','--wait','--pipe','--collect','--unit=step33-'+label,'-p','MemoryMax=2G','-p','TasksMax=192','-p','CPUQuota=400%','-p','RuntimeMaxSec=180s','-p','KillMode=control-group','--working-directory='+str(P/'source/vm'),'--setenv=GOROOT=/usr/local/go','--setenv=GOTOOLCHAIN=local','--setenv=GOPROXY=off','--setenv=GOWORK='+str(P/'go.work'),'--setenv=GOMAXPROCS=2','/usr/local/go/bin/go','test','-p=2','-c','-o',str(binary)]
(P/'audit'/f'{label}-command.json').write_text(json.dumps(argv,indent=2)+'\n')
with out.open('w')as f:r=subprocess.run(argv,stdout=f,stderr=subprocess.STDOUT)
data=dict(exit=r.returncode,binary=str(binary),settings=settings,config_sha=cfg)
if r.returncode==0:data['binary_sha']=sha(binary.read_bytes());data['source_hashes']={str(f.relative_to(P)):sha(f.read_bytes())for f in(P/'source/vm').rglob('*.go')};(P/'environment.json').write_text(json.dumps(data,indent=2)+'\n')
(P/'audit'/f'{label}-outcome.json').write_text(json.dumps(data,indent=2)+'\n');print(json.dumps({k:v for k,v in data.items()if k!='source_hashes'}));print(out.read_text()[-1400:]);raise SystemExit(r.returncode)
