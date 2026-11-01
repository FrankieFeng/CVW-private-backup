from pathlib import Path
import shutil,yaml,json,hashlib
P=Path(__file__).resolve().parents[1];old=Path('/tmp/cvw-step35-small-ledger');new=Path('/tmp/cvw-step35a-diag');assert not new.exists(),'preserve old diagnostic ledger';assert old.exists();shutil.copytree(old,new)
for f in new.rglob('*.yml'):f.write_text(f.read_text().replace(str(old),str(new)))
(P/'audit/ledger-source.json').write_text(json.dumps({'copy_from_stopped_step35_ledger':str(old),'new_home':str(new),'storage_config_changes':[],'bloom_capacity':100000,'rpc':'127.0.0.1:27535','port_unchanged_isolated_node':True},indent=2))
