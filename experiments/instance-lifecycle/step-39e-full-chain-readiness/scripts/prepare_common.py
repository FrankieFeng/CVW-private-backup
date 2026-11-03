"""Isolate the pinned common module; never write GOMODCACHE or production sources."""
from pathlib import Path
import shutil,hashlib,json
P=Path(__file__).resolve().parents[1];base=Path('/home/frankie/go/pkg/mod/chainmaker.org/chainmaker/common/v2@v2.4.0');dest=Path('/home/frankie/mygitprojects/.worktrees/cvw-step39e-deps/common');patch=P/'source/msgbus/message_bus.go'
if not dest.exists():
 shutil.copytree(base,dest)
 for f in dest.rglob('*'):
  if f.is_file():f.chmod(f.stat().st_mode|0o200)
assert (dest/'msgbus/message_bus.go').read_bytes()in [(base/'msgbus/message_bus.go').read_bytes(),patch.read_bytes()], 'preserve unexpected isolated dependency modifications'
(dest/'msgbus/message_bus.go').write_bytes(patch.read_bytes())
checks=[]
for f in base.rglob('*'):
 if not f.is_file():continue
 rel=f.relative_to(base);h=hashlib.sha256((dest/rel).read_bytes()).hexdigest();expected=hashlib.sha256((patch if str(rel)=='msgbus/message_bus.go'else f).read_bytes()).hexdigest();assert h==expected,rel;checks.append({'path':str(rel),'sha256':h,'modified':str(rel)=='msgbus/message_bus.go'})
(P/'evidence/common-copy-identity.json').write_text(json.dumps({'base':str(base),'isolated_copy':str(dest),'files':checks},indent=2));print('Pinned common isolated:',len(checks),'files; only1 diagnostic file differs')
