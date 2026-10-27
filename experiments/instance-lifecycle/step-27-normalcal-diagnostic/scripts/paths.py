from pathlib import Path
import subprocess,re,json,hashlib
P=Path(__file__).resolve().parents[1];result=[]
for name in ['original','step18','step18-A']:
 file=P/'inputs'/f'{name}.wasm';proc=subprocess.Popen(['wasm-objdump','-d',str(file)],stdout=subprocess.PIPE,text=True);keep=False;out=[]
 for l in proc.stdout:
  if re.match(r'[0-9a-f]+ func\[',l):keep='<main.normalCal>'in l
  if keep:out.append(l)
 assert proc.wait()==0 and out and 'i64.const 10000000\n'in ''.join(out)
 (P/'audit'/f'{name}-normalCal-disassembly.txt').write_text(''.join(out));result.append({'variant':name,'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'normal_loop_limit':10000000,'body_disassembly_lines':len(out)})
(P/'audit/workload-check.json').write_text(json.dumps(result,indent=2)+'\n')
