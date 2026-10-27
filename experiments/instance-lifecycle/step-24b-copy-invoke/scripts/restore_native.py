"""Restore only git-ignored packaged native libraries from the pinned local source; no guest."""
from pathlib import Path
import hashlib,shutil
P=Path(__file__).resolve().parents[1]
base=Path('/home/frankie/mygitprojects/.worktrees/cvw-step21c/chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0/wasmer-go/packaged/lib')
src=base/'linux-amd64/libwasmer.so';expected='dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9'
assert hashlib.sha256(src.read_bytes()).hexdigest()==expected
out=P/'source/vm/wasmer-go/packaged/lib/linux-amd64/libwasmer.so';out.parent.mkdir(parents=True,exist_ok=True)
if out.exists():assert hashlib.sha256(out.read_bytes()).hexdigest()==expected
else:shutil.copyfile(src,out)
print('verified native',expected)

# The packaged dummy packages are also Git-ignored inherited dependencies.
restored=[]
for f in base.rglob('*.go'):
 target=P/'source/vm/wasmer-go/packaged/lib'/f.relative_to(base)
 target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():assert target.read_bytes()==f.read_bytes(),str(target)
 else:shutil.copyfile(f,target)
 restored.append(str(f.relative_to(base)))
print('verified packaged Go dummy files',restored)
