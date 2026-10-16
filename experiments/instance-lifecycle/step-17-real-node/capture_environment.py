from pathlib import Path
import json,subprocess,hashlib,platform,os
R=Path('/home/frankie/mygitprojects');O=R/'CVW/experiments/instance-lifecycle/step-17-real-node';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
env={'uname':platform.uname()._asdict(),'go':subprocess.check_output(['/usr/local/go/bin/go','version'],text=True).strip(),'cpu':subprocess.check_output(['lscpu'],text=True),'date':subprocess.check_output(['date','-Iseconds'],text=True).strip(),'repositories':{},'builds':{},'configuration':{},'artifacts':{}}
for name,d in [('CVW-main',R/'CVW'),('node-original',R/'chainmaker-go'),('CVW-step17',R/'.worktrees/cvw-step17'),('node-step17',R/'.worktrees/node-step17')]:
 env['repositories'][name]={k:subprocess.check_output(['git',*cmd],cwd=d,text=True).strip() for k,cmd in [('head',['rev-parse','HEAD']),('branch',['branch','--show-current']),('status',['status','--porcelain'])]}
for f in ['chainmaker','client-benchmark','client-verify']:
 p=O/f;env['builds'][f]={'sha256':sha(p),'go_version_m':subprocess.check_output(['/usr/local/go/bin/go','version','-m',str(p)],text=True)}
for p in (O/'network').glob('*/config/wx-org1.chainmaker.org/*.yml'):env['configuration'][str(p.relative_to(O))]=sha(p)
for p in (O/'network').glob('*/config/wx-org1.chainmaker.org/chainconfig/*.yml'):env['configuration'][str(p.relative_to(O))]=sha(p)
for p in (O/'compiled').glob('*.module'):
 env['artifacts'][p.name]={'sha256':sha(p),'meta':json.loads(Path(str(p)+'.json').read_text()),'target':str(p.resolve())}
vm=R/'.worktrees/cvw-step17/chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0';env['native_sha256']=sha(vm/'wasmer-go/packaged/lib/linux-amd64/libwasmer.so')
(O/'environment.json').write_text(json.dumps(env,indent=2)+'\n')
print('recorded versions/config/builds/artifact hashes')
