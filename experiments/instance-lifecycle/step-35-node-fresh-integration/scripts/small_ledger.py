from pathlib import Path
import shutil,json,yaml,math
P=Path(__file__).resolve().parents[1];old=Path('/tmp/cvw-step35-isolated');new=Path('/tmp/cvw-step35-small-ledger');assert not new.exists();new.mkdir();shutil.copytree(old/'config',new/'config');shutil.copytree(old/'network',new/'network')
for f in [*new.rglob('*.yml')]:
 text=f.read_text().replace(str(old),str(new));f.write_text(text)
f=new/'config/wx-org1.chainmaker.org/chainmaker.yml';x=yaml.safe_load(f.read_text());assert x['storage']['statedb_config']['bloom_config']['keys_capacity']==1000000000;x['storage']['statedb_config']['bloom_config']['keys_capacity']=100000;f.write_text(yaml.safe_dump(x,sort_keys=False))
(P/'audit/small-ledger-config.json').write_text(json.dumps({'previous_home':str(old),'new_home':str(new),'only_semantic_change':{'storage.statedb_config.bloom_config.keys_capacity':[1000000000,100000]},'bloom_enabled':True,'false_positive_rate':.01,'original_estimated_bit_array_bytes':math.ceil(-1000000000*math.log(.01)/math.log(2)**2/8),'new_estimated_bit_array_bytes':math.ceil(-100000*math.log(.01)/math.log(2)**2/8),'soft_rss_limit_mib':1536,'thread_limit':220,'new_empty_ledger':True,'not_a_native_leak_fix':True},indent=2))
