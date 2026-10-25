"""Stream disassembly of fixed WASM, retaining only main.normalCal. No guest execution."""
from pathlib import Path
import json,subprocess,hashlib
ROOT=Path(__file__).resolve().parent.parent
c=next(c for c in json.loads((ROOT/'cases.json').read_text()) if c['method']=='normalCal')
p=Path(c['wasm_path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==c['wasm_sha256']
r=subprocess.Popen(['wasm-objdump','-d',str(p)],stdout=subprocess.PIPE,text=True)
lines=[];keep=False
for line in r.stdout:
    if ' func[' in line:
        keep='<main.normalCal>:' in line
    if keep:lines.append(line)
assert r.wait()==0 and any('i64.const 10000000' in s for s in lines)
(ROOT/'audit/current-normalcal-disassembly.txt').write_text(''.join(lines))
print('verified current WASM normalCal loop 10000000; retained',len(lines),'lines')
