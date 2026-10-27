"""Read-only file/config provenance checks; no build, RPC or node startup."""
from pathlib import Path
import json,hashlib,subprocess,re
P=Path(__file__).resolve().parents[1];ROOT=Path('/home/frankie/mygitprojects');CVW=ROOT/'CVW';S=CVW/'experiments/instance-lifecycle/step-20-e2e-performance-attribution'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
old=json.loads((S/'environment.json').read_text());checks=[]
for key in ['chainmaker-original','client-original','chainmaker-trace','client-trace']:
 p=S/key;expected=old['binaries'][key]['sha256'];checks.append(dict(kind=key,path=str(p),exists=p.exists(),expected_sha=expected,sha256=sha(p)if p.exists()else'',matches=p.exists()and sha(p)==expected))
p=ROOT/'.worktrees/cvw-step17/chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0/wasmer-go/packaged/lib/linux-amd64/libwasmer.so';checks.append(dict(kind='native',path=str(p),exists=p.exists(),sha256=sha(p)if p.exists()else'',matches=p.exists()and sha(p)==old['native_sha256']))
p=ROOT/'.worktrees/cvw-step27/experiments/instance-lifecycle/step-27-normalcal-diagnostic/inputs/original.wasm';checks.append(dict(kind='same original-family saved WASM',path=str(p),exists=p.exists(),sha256=sha(p)if p.exists()else'',matches=p.exists()and sha(p)==old['wasm_sha256']))
config=[]
for ep in ['baseline','optimized']:
 home=S/'network'/ep
 for rel in ['sdk.yml','config/wx-org1.chainmaker.org/chainmaker.yml','config/wx-org1.chainmaker.org/chainconfig/bc1.yml']:
  p=home/rel;lines=p.read_text().splitlines();allowed=['chain_id','retry_limit','retry_interval','node_only_async','node_addr','listen_addr','seeds','host','port','block_interval','sync_tx_result_timeout']
  selected=[dict(line=i,text=s.strip())for i,s in enumerate(lines,1)if any(re.match(r'(?:-\s*)?'+k+r'\s*:',s.strip())for k in allowed)]
  config.append(dict(endpoint=ep,path=str(p),sha256=sha(p),selected_non_secret_fields=selected))
evidence=[]
files=[ROOT/'.worktrees/cvw-step17/chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0'/n for n in ['runtime.go','vm_pool.go','wasmer-go/store.go','wasmer-go/exports.go','wasmer-go/function.go','wasmer-go/memory.go','wasmer-go/wasi.go','wasmer-go/error.go']]
files += [ROOT/'.worktrees/node-step17/module/rpcserver/api_service.go',ROOT/'chainmaker-test-toolkit-master/chainmaker-performance-test/parallel/parallel_claim.go',Path('/home/frankie/go/pkg/mod/chainmaker.org/chainmaker/sdk-go/v2@v2.4.0/sdk_client.go'),Path('/home/frankie/go/pkg/mod/chainmaker.org/chainmaker/sdk-go/v2@v2.4.0/conn_pool.go'),CVW/'experiments/instance-lifecycle/step-21b-wasmer-store-lifecycle/CONCURRENCY_CONTRACT.md']
for i,p in enumerate(files):
 b=p.read_bytes();dst=P/'audit/evidence'/f'{i:02d}-{p.name}';dst.parent.mkdir(exist_ok=True);dst.write_bytes(b);evidence.append(dict(source=str(p),copy=str(dst.relative_to(P)),sha256=sha(p),has_managed_owner='ManagedBeginOwner'in b.decode(errors='replace')))
node_deps=[]
for name in ['node-step17','node-step19','node-step19-reuse']:
 p=ROOT/'.worktrees'/name/'go.mod';text=p.read_text();targets=re.findall(r'chainmaker.org/chainmaker/vm-wasmer/v2\s*=>\s*(\S+)',text)
 for target in targets:
  vm=Path(target);g=vm/'wasmer-go';has_owner=any('ManagedBeginOwner'in f.read_text(errors='replace')for f in g.glob('*.go'))
  node_deps.append(dict(node_worktree=name,vm_module=target,has_lifetime_owner_api=has_owner,managed_go_exists=(g/'managed.go').exists(),note='OS pinning in per-call error helper is not lifetime ownership'))
(P/'audit/environment-check.json').write_text(json.dumps(dict(binaries=checks,configuration=config,node_dependencies=node_deps,evidence=evidence,uname=subprocess.check_output(['uname','-a'],text=True).strip(),host_go=subprocess.check_output(['/usr/local/go/bin/go','version'],text=True).strip(),new_nodes_started=0,new_requests_sent=0,old_legacy_e20_path_exists=(CVW/'experiments/instance-lifecycle/e20-e2e-copy-attribution').exists(),actual_step20_path=str(S)),indent=2)+'\n')
assert all(c['matches']for c in checks)
assert all(not r['has_lifetime_owner_api']for r in node_deps)
for m in json.loads((P/'audit/HISTORICAL_MANIFEST.json').read_text()):assert sha(Path(m['source']))==m['sha256']==sha(P/m['copy'])
print('saved binary/native/WASM SHA verified; historical files unchanged; node owner integration not found')
