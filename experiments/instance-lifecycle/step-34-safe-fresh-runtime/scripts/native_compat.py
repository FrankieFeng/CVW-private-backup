from pathlib import Path
import subprocess,sys,json,hashlib
P=Path(__file__).resolve().parents[1];label=sys.argv[1]if len(sys.argv)>1 else'compat-replay';lib=P/'source/vm/wasmer-go/packaged/lib/linux-amd64';inc=P/'source/vm/wasmer-go/packaged/include';assert hashlib.sha256((lib/'libwasmer.so').read_bytes()).hexdigest()=='dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9';assert not(P/'raw_logs'/f'{label}.log').exists();(P/'binaries').mkdir(exist_ok=True)
cmds=[['wat2wasm',str(P/'source/compat.wat'),'-o',str(P/'binaries'/f'{label}.wasm')],['gcc',str(P/'source/compat.c'),'-I'+str(inc),'-L'+str(lib),'-Wl,-rpath,'+str(lib),'-lwasmer','-ldl','-o',str(P/'binaries'/label)],['systemd-run','--user','--wait','--pipe','--collect','--unit=step34-'+label,'-p','MemoryMax=768M','-p','TasksMax=125','-p','RuntimeMaxSec=15s',str(P/'binaries'/label),str(P/'binaries'/f'{label}.wasm')]]
(P/'audit'/f'{label}-commands.json').write_text(json.dumps(cmds,indent=2));text=''
for cmd in cmds:
 r=subprocess.run(cmd,capture_output=True,text=True);text+=r.stdout+r.stderr;(P/'raw_logs'/f'{label}.log').write_text(text)
 if r.returncode:raise SystemExit(r.returncode)
print(text)
