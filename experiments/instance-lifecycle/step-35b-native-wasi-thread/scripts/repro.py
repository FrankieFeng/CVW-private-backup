from pathlib import Path
import subprocess,json,sys,hashlib
P=Path(__file__).resolve().parents[1];label=sys.argv[1];lib=Path(sys.argv[2]).resolve();n=int(sys.argv[3]);trace='--trace'in sys.argv;assert 1<=n<=8;out=P/'raw_logs'/f'{label}.log';assert not out.exists();headers=Path('/home/frankie/mygitprojects/.worktrees/cvw-step35a/experiments/instance-lifecycle/step-35a-resource-reset-validation/source/vm/wasmer-go/packaged/include');binary=P/'binaries'/label
subprocess.run(['cc','-O0','-g',str(P/'source'/('repro_fd.c'if '--fd'in sys.argv else'repro.c')),'-I'+str(headers),'-L'+str(lib.parent),'-lwasmer','-ldl','-Wl,-rpath,'+str(lib.parent),'-o',str(binary)],check=True,capture_output=True)
if trace:
 shim=P/'binaries'/('pthread_trace_wake.so'if '--fd'in sys.argv else'pthread_trace.so')
 if not shim.exists():subprocess.run(['cc','-shared','-fPIC','-O0','-g',str(P/'source'/('pthread_trace_wake.c'if '--fd'in sys.argv else'pthread_trace.c')),'-ldl','-pthread','-o',str(shim)],check=True,capture_output=True)
argv=['systemd-run','--user','--wait','--pipe','--collect','--unit=step35b-'+label,'-p','MemoryMax=512M','-p','TasksMax=220','-p','RuntimeMaxSec=20s','--setenv=LD_LIBRARY_PATH='+str(lib.parent)]+(['--setenv=LD_PRELOAD='+str(shim),'--setenv=STEP35B_TRACE='+str(P/'raw_logs'/f'{label}-pthread.log')]if trace else[])+[str(binary),str(n)]
(P/'audit'/f'{label}-command.json').write_text(json.dumps({'argv':argv,'lib':str(lib),'sha':hashlib.sha256(lib.read_bytes()).hexdigest(),'binary_sha':hashlib.sha256(binary.read_bytes()).hexdigest()},indent=2))
with out.open('w')as f:r=subprocess.run(argv,stdout=f,stderr=subprocess.STDOUT)
print(out.read_text()[-1500:]);raise SystemExit(r.returncode)
