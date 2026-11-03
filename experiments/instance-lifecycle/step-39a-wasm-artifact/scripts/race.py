from pathlib import Path
import subprocess,json
P=Path(__file__).resolve().parents[1];lib='/home/frankie/mygitprojects/.worktrees/cvw-step35b/experiments/instance-lifecycle/step-35b-native-wasi-thread/libraries/patched'
cmd=['systemd-run','--user','--wait','--pipe','--collect','--unit=step39a-race-identity','-p','MemoryMax=2G','-p','TasksMax=256','-p','RuntimeMaxSec=30s','--setenv=LD_LIBRARY_PATH='+lib,'--setenv=CM_STEP21A_POOL=capacity','--setenv=CM_STEP21A_STORE_GUARD=1','--setenv=CM_REUSE_EXPERIMENT=R1','--setenv=D_POLICY=R1','--setenv=E39_MODE=D',str(P/'binaries/vm-race'),'-test.run=^TestStep39Artifact$','-test.v','-test.timeout=20s']
f=P/'raw_logs/race-identity.log';assert not f.exists();(P/'audit/race-command.json').write_text(json.dumps(cmd,indent=2));r=subprocess.run(cmd,capture_output=True,text=True);f.write_text(r.stdout+r.stderr);print(f.read_text());assert r.returncode==0
