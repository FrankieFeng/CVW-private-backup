from run import *
lib=LIB
for mode in ['A','B','C','D']:
 label='reject-'+mode;cmd=['systemd-run','--user','--wait','--pipe','--collect','--unit=step39a-'+label,'-p','MemoryMax=2G','-p','TasksMax=256','-p','RuntimeMaxSec=30s','--setenv=LD_LIBRARY_PATH='+str(lib),'--setenv=CM_STEP21A_POOL=capacity','--setenv=CM_STEP21A_STORE_GUARD=1','--setenv=CM_REUSE_EXPERIMENT=R1','--setenv=D_POLICY=R1','--setenv=E39_MODE='+mode,str(P/'binaries/vm-correctness'),'-test.run=^TestStep39Reject$','-test.v','-test.timeout=20s'];f=P/'raw_logs'/f'{label}.log';assert not f.exists();(P/'audit'/f'{label}-command.json').write_text(json.dumps(cmd,indent=2));r=subprocess.run(cmd,capture_output=True,text=True);f.write_text(r.stdout+r.stderr);print(label,r.returncode);assert r.returncode==0,f.read_text()
# Module identity uses same guarded Owner as business; monitor it through inherited runner.
execute('module-identity','A','compute_hashCal','D',test='TestStep39ModuleIdentity',binary_label='vm-correctness')
