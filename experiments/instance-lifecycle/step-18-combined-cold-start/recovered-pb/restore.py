"""Restore the recorded SDK-only patch in a private directory, never module cache."""
from pathlib import Path
import shutil,subprocess,hashlib,json
HERE=Path(__file__).resolve().parent
SOURCE=Path('/home/frankie/go/pkg/mod/github.com/!t!k!o!t!k!ch/contract-sdk-go-wasm@v0.1.3')
DEST=HERE/'sdk'
if DEST.exists():
 assert 'GetBatchState(batchKeys' not in (DEST/'sdk/chainmaker.go').read_text()
 print('private historical SDK patch already restored')
else:
 shutil.copytree(SOURCE,DEST)
 for p in DEST.rglob('*'):
  if p.is_file():p.chmod(p.stat().st_mode|0o200)
 subprocess.run(['patch','-p1','--input',str(HERE/'sdk.diff')],cwd=DEST,check=True)
 print('restored exact recorded SDK API deletion patch')
expected=json.loads((HERE/'sdk-source-sha256.json').read_text())
assert all(hashlib.sha256((DEST/name).read_bytes()).hexdigest()==digest for name,digest in expected.items()), 'private SDK differs from recovered patch'
assert 'GetBatchState(batchKeys' in (SOURCE/'sdk/chainmaker.go').read_text()
