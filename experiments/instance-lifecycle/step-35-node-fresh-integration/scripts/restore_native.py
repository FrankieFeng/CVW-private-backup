# Restore only the unchanged, already present CVW native artifact; never fetch/upgrade or replace a mismatch.
from pathlib import Path
import hashlib,shutil
P=Path(__file__).resolve().parents[1];target=P/'source/vm/wasmer-go/packaged/lib/linux-amd64/libwasmer.so';source=Path('/home/frankie/mygitprojects/CVW/chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0/wasmer-go/packaged/lib/linux-amd64/libwasmer.so');sha='dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9';assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
if target.exists():assert hashlib.sha256(target.read_bytes()).hexdigest()==sha
else:target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
print(sha,target)
