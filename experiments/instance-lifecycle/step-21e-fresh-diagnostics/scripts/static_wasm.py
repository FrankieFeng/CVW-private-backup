from pathlib import Path
import subprocess,re,json,hashlib
P=Path(__file__).resolve().parents[1]
base=Path('/home/frankie/mygitprojects/.worktrees/cvw-step21c/chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0/testdata')
rows=[]
for name in ['compute','fact','erc721','identity','exchange']:
 file=base/(name+'-go.wasm');x=subprocess.run(['wasm-objdump','-x',str(file)],capture_output=True,text=True,check=True).stdout
 (P/f'audit/{name}-symbols.txt').write_text('\n'.join(s for s in x.splitlines()if any(t in s for t in ['GetGas','SetGas','gcStart','ReadMemStats','memstats','json.','registry.']))+'\n')
 targets=['<GetGas>','<SetGas>','<main.GetGas>','<main.SetGas>','<main.normalCal>','<main.saveAndFindByFileHash>','<main.setTokenLatestTxInfo>','<encoding_json.typeEncoder>','<encoding_json.newTypeEncoder>']
 proc=subprocess.Popen(['wasm-objdump','-d',str(file)],stdout=subprocess.PIPE,text=True);out=[];keep=False
 for line in proc.stdout:
  if re.match(r'[0-9a-f]+ func\[',line):keep=any(t in line for t in targets)
  if keep:out.append(line)
 assert proc.wait()==0
 (P/f'audit/{name}-selected-disassembly.txt').write_text(''.join(out))
 rows.append({'contract':name,'path':str(file),'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
(P/'audit/wasm-manifest.json').write_text(json.dumps(rows,indent=2))
