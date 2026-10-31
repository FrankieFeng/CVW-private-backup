from pathlib import Path
import shutil,json,yaml,hashlib
P=Path(__file__).resolve().parents[1];R=Path('/home/frankie/mygitprojects');H=Path('/tmp/cvw-step35-isolated');assert not H.exists(),'preserve existing ledger';H.mkdir();source=R/'CVW/experiments/instance-lifecycle/step-17-real-node/network/baseline'
shutil.copytree(source/'config',H/'config')
def adjust(x):
 if isinstance(x,dict):return {k:adjust(v)for k,v in x.items()}
 if isinstance(x,list):return [adjust(v)for v in x]
 if isinstance(x,str):return x.replace(str(source),str(H))
 return x
org=H/'config/wx-org1.chainmaker.org'
for f in [org/'chainmaker.yml',org/'log.yml',org/'chainconfig/bc1.yml']:
 x=adjust(yaml.safe_load(f.read_text()))
 if f.name=='chainmaker.yml':x['blockchain'][0]['chainId']='step35';x['rpc']['port']=27535;x['net']['listen_addr']='/ip4/127.0.0.1/tcp/28535';x['blockchain'][0]['genesis']=str(org/'chainconfig/bc1.yml')
 if f.name=='bc1.yml':x['chain_id']='step35';x['block']['block_interval']=20
 f.write_text(yaml.safe_dump(x,sort_keys=False))
sdk=adjust(yaml.safe_load((source/'sdk.yml').read_text()));sdk['chain_client']['chain_id']='step35';sdk['chain_client']['nodes'][0]['node_addr']='127.0.0.1:27535'
for m in ['baseline','optimized']:
 d=H/'network'/m;d.mkdir(parents=True);(d/'sdk.yml').write_text(yaml.safe_dump(sdk))
(P/'audit/runtime-path.json').write_text(json.dumps({'home':str(H),'node_config':str(org/'chainmaker.yml'),'rpc':'127.0.0.1:27535','p2p':'127.0.0.1:28535','chain':'step35','source_config':str(source),'credentials':'existing development test-network credentials copied only to /tmp, excluded from deliverables'}))
B=R/'.worktrees/cvw-step34/experiments/instance-lifecycle/step-34-safe-fresh-runtime/inputs';(P/'inputs').mkdir();rows={}
for c in ['compute','fact','erc721','identity','exchange']:
 f=B/(c+'-G0.wasm');shutil.copy2(f,P/'inputs'/f.name);rows[c]={'path':str(P/'inputs'/f.name),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
(P/'inputs/manifest.json').write_text(json.dumps(rows,indent=2));print('isolated config ready; no node started')
