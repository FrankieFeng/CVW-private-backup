from pathlib import Path
import yaml,shutil,json
O=Path(__file__).resolve().parent; R=Path('/home/frankie/mygitprojects'); src=R/'chainmaker-go/build/release/chainmaker-v2.4.0_alpha-wx-org1.chainmaker.org/config'
# One-node TBFT network, fresh ledger; copies test certificates, never old ledger.
if (O/'network').exists():raise SystemExit('network already exists; preserve its ledger/config and use a new experiment output directory')
for mode,port in [('baseline',27301),('optimized',27302)]:
 home=O/'network'/mode; conf=home/'config'; conf.mkdir(parents=True,exist_ok=True)
 shutil.copytree(src,conf,dirs_exist_ok=True)
 org=conf/'wx-org1.chainmaker.org'; node=yaml.safe_load((org/'chainmaker.yml').read_text()); bc=yaml.safe_load((org/'chainconfig/bc1.yml').read_text()); log=yaml.safe_load((org/'log.yml').read_text())
 def absolute(x):
  if isinstance(x,dict): return {k:absolute(v) for k,v in x.items()}
  if isinstance(x,list): return [absolute(v) for v in x]
  if isinstance(x,str) and x.startswith('../config/'):return str(conf/x[len('../config/'):])
  if isinstance(x,str) and x.startswith('../data/'):return str(home/'data'/x[len('../data/'):])
  if isinstance(x,str) and x.startswith('../log/'):return str(home/'log'/x[len('../log/'):])
  return x
 node=absolute(node); bc=absolute(bc); log=absolute(log)
 bc['chain_id']='step17'; node['blockchain'][0]['chainId']='step17'; bc['consensus']['type']=1;bc['consensus']['nodes']=bc['consensus']['nodes'][:1];bc['vm']['support_list']=['wasmer'];bc['block']['block_interval']=20
 node['txpool']['pool_type']='SINGLE';node['rpc']['tls']['mode']='disable'
 node['net']['listen_addr']=f'/ip4/127.0.0.1/tcp/{port+1000}';node['net']['seeds']=[];node['rpc']['port']=port;node['rpc']['host']='127.0.0.1'
 for k in ['monitor','pprof']:
  if k in node:node[k]['enabled']=False
 for k in log['log']: log['log'][k]['log_level_default']='ERROR';log['log'][k]['log_levels']={}
 for f,v in [(org/'chainmaker.yml',node),(org/'chainconfig/bc1.yml',bc),(org/'log.yml',log)]: f.write_text(yaml.safe_dump(v,sort_keys=False))
 # SDK credentials from copied test release.
 client=R/'chainmaker-go/build/crypto-config/wx-org1.chainmaker.org/user/client1'
 sdk={'chain_client':{'chain_id':'step17','org_id':'wx-org1.chainmaker.org','retry_limit':100,'retry_interval':5,'nodes':[{'node_addr':f'127.0.0.1:{port}','conn_cnt':4,'enable_tls':False,'trust_root_paths':[],'tls_host_name':'chainmaker.org'}],'rpc_client':{'max_receive_message_size':100,'max_send_message_size':100,'send_tx_timeout':60,'get_tx_timeout':60}}}
 for field,ext in [('user_key_file_path','tls.key'),('user_crt_file_path','tls.crt'),('user_sign_key_file_path','sign.key'),('user_sign_crt_file_path','sign.crt')]: sdk['chain_client'][field]=str(client/('client1.'+ext))
 (home/'sdk.yml').write_text(yaml.safe_dump(sdk,sort_keys=False))
print('Created separate TBFT ledgers, ports 27301/27302 and P2P 28301/28302')
