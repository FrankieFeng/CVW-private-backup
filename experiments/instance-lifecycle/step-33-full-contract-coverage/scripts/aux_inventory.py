from pathlib import Path
import csv,json,re,hashlib,subprocess
P=Path(__file__).resolve().parents[1];root=Path('/home/frankie/mygitprojects/CVW');rows=list(csv.DictReader((P/'CONTRACT_INVENTORY.csv').open()));extra=[]
for sub in ['test/output/formatTest.go','test/example/test.go','registry/registry.go']:
 p=root/sub
 if not p.exists():continue
 wasm=root/'test/output/formatTest-go.wasm'if sub.startswith('test/output')else None
 methods=re.findall(r'//go:wasmexport\s+(\w+)',p.read_text())or['(library/source-only)']
 for m in methods:
  if any(x['contract']==p.stem and x['method']==m for x in rows):continue
  extra.append(dict(contract=p.stem,method=m,source_path=str(p),frozen_source_commit='current read-only artifact; not benchmarked',wasm_path=str(wasm)if wasm else'',wasm_sha256=hashlib.sha256(wasm.read_bytes()).hexdigest()if wasm and wasm.exists()else'',independent_deployable=False,also_child=False,fixture_status='not_applicable_tool',A_build_status='not_built',Copy_build_status='not_built',step32_covered=False,step33_execute=False,status='auxiliary_not_performance',blocking_reason='Go syntax/instrumentation sample or helper; no ChainMaker init_contract/SDK business ABI',case='',source_is_duplicate=False))
rows+=extra;keys=list(dict.fromkeys(k for r in rows for k in r));f=(P/'CONTRACT_INVENTORY.csv').open('w',newline='');w=csv.DictWriter(f,keys);w.writeheader();w.writerows(rows);f.close();print('extra auxiliary rows',len(extra),'inventory',len(rows))
