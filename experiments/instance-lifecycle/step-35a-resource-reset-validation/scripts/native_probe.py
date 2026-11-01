from pathlib import Path
import subprocess,hashlib,json,sys
P=Path(__file__).resolve().parents[1];label=sys.argv[1];mode=sys.argv[2];quiet='--quiet10'in sys.argv;assert mode in ['store','wasi'];source=P/'source'/('wasi_threads_quiet.c'if quiet else'wasi_threads.c');binary=P/'binaries'/label;log=P/'raw_logs'/f'{label}.log';assert not binary.exists()and not log.exists();lib=P/'source/vm/wasmer-go/packaged/lib/linux-amd64';sha=hashlib.sha256((lib/'libwasmer.so').read_bytes()).hexdigest();assert sha=='dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9'
compile=['cc','-O0','-g',str(source),'-I'+str(P/'source/vm/wasmer-go/packaged/include'),'-L'+str(lib),'-lwasmer','-Wl,-rpath,'+str(lib),'-o',str(binary)];subprocess.run(compile,check=True,capture_output=True)
argv=['systemd-run','--user','--wait','--pipe','--collect','--unit=step35a-'+label,'-p','MemoryMax=512M','-p','TasksMax=220','-p','RuntimeMaxSec=20s',str(binary),mode]+(['1']if quiet else[]);(P/'audit'/f'{label}-commands.json').write_text(json.dumps({'compile':compile,'run':argv,'native_sha':sha,'binary_sha':hashlib.sha256(binary.read_bytes()).hexdigest()},indent=2))
with log.open('w')as f:r=subprocess.run(argv,stdout=f,stderr=subprocess.STDOUT)
print(log.read_text());raise SystemExit(r.returncode)
