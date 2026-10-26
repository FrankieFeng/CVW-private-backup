from pathlib import Path
import hashlib,shutil
P=Path(__file__).resolve().parents[1]
src=Path('/home/frankie/mygitprojects/.worktrees/cvw-step21c/chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0/wasmer-go/packaged/lib/linux-amd64/libwasmer.so')
expected='dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9'
assert hashlib.sha256(src.read_bytes()).hexdigest()==expected
dst=P/'source/vm/wasmer-go/packaged/lib/linux-amd64/libwasmer.so';dst.parent.mkdir(parents=True,exist_ok=True)
if dst.exists():assert hashlib.sha256(dst.read_bytes()).hexdigest()==expected
else:shutil.copyfile(src,dst)
print('verified pinned native library; no runtime build or guest execution')
