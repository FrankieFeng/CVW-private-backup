from harness import *
label,contract,flavor=sys.argv[1:];group='G0'if flavor=='plain'else'G2';vs=json.loads((P/'inputs/variants.json').read_text());node=None;client=None;out={'contract':contract,'flavor':flavor,'seed':str(H),'passed':False}
try:
 clone(SOURCE,H,True);node=Node(label,'E0');client=Client(label);deps=['identity','erc721','exchange']if contract=='exchange'else[contract]
 for c in deps:
  params={'name':'huanletoken','symbol':'hlt','tokenURI':'https://chainmaker.org.cn'}if c=='erc721'else{}
  res=client.batch([{'Op':'deploy','Contract':c,'Path':vs[c+'-'+group]['path'],'Params':params,'Tag':'deploy-'+c,'Phase':'deployment'}]);assert len(res['rows'])==1;good(res['rows'][0]);print('DEPLOYED',contract,flavor,c,flush=True)
 out['passed']=True
finally:
 if client:client.close()
 if node:
  n=node.close();out['node']=n;out['passed']=out['passed']and not n['reason']and n['systemd'].get('ExecMainStatus')=='0'and n['owner']and n['owner']['managed_pending']==0
 (P/'raw_logs'/f'{label}-seed.json').write_text(json.dumps(out,indent=2));assert out['passed'],out
 with(P/'PROGRESS.md').open('a')as f:f.write('\nSeed '+label+' PASS, deployment only, no performance samples.\n')
