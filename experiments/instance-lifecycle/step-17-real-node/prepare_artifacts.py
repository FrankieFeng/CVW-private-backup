from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent;manifest=json.loads((O.parent/'step-16-chainmaker-copy/manifest.json').read_text());out=O/'compiled';out.mkdir(exist_ok=True)
for s in manifest:
 for k in ['original','nodata']:
  p=Path(s['paths'][k]).with_suffix('.module');m=Path(str(p)+'.json');meta=json.loads(m.read_text())
  assert hashlib.sha256(p.read_bytes()).hexdigest()==meta['ArtifactSHA']
  assert hashlib.sha256(Path(s['paths'][k]).read_bytes()).hexdigest()==meta['WasmSHA']
  dst=out/(meta['WasmSHA']+'.module')
  for src,target in [(p,dst),(m,Path(str(dst)+'.json'))]:
   if target.exists():assert target.resolve()==src.resolve()
   else:target.symlink_to(src.resolve())
print('verified 16 existing artifacts and metadata; no compilation rerun')
