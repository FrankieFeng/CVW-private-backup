from pathlib import Path
import json,csv,hashlib,subprocess,re
P=Path(__file__).resolve().parents[1];ROOT=Path('/home/frankie/mygitprojects');W=ROOT/'.worktrees/cvw-step18';B=ROOT/'CVW';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
A='8acfaca5eeec9f6f7c23c4ffac969b86f27799b0';TO='818fac1ac51525aeedf619a9a339b95854930159';peoples=json.dumps({'peoples':[{'num':1,'name':'Alice'},{'num':2,'name':'Bob'},{'num':3,'name':'Carol'}]},separators=(',',':'))
itin=json.dumps({'ip':'127.0.0.1','country':'CN','city':'Shanghai','region':'Shanghai'},separators=(',',':'));fact={'file_hash':'005521f27d745a04999c6d09f559764f9c44376a','file_name':'aoteman.jpg','time':'1792827547'}
cases=[]
def add(c,m,params=None,setup=None,expect='',kind='',contains=''):
 k=c+'_'+m;d=dict(case=k,contract=c,method=m,params=params or{},setup=setup or[],expected=expect,kind=kind,contains=contains);f=P/'inputs'/f'{k}-case.json';f.write_text(json.dumps(d,indent=2));cases.append(dict(case=k,contract=c,method=m,file=str(f),max_groups_per_process=1 if len(d['setup'])>1 else 2,status='ready'))
def step(m,p):return dict(method=m,params=p)
add('bigInput','inputSize',{'data':'x'*(512*1024)},expect=str(512*1024),kind='big_size')
add('bigInput','inputSizeMulti',dict(part_count='4',**{'data'+str(i):'x'*(256*1024)for i in range(4)}),expect=str(1024*1024),kind='big_multi')
add('bigInput','ioHeavy',{},expect='100',kind='io') # original default100x256, not reduced
add('identity','addWriteList',{'address':A},expect='add write list success',kind='identity_add')
add('identity','alterAdminAddress',{'address':A},expect='OK',kind='identity_admin')
add('identity','removeWriteList',{'address':A},[step('addWriteList',{'address':A})],expect='remove write list success',kind='identity_remove')
add('identity','isApprovedUser',{'address':A},[step('addWriteList',{'address':A})],expect='true')
add('identity','address',{},kind='identity_address')
for m in ['save','queryHistory','saveAndQueryHistory']:
 add('itinerary',m,{'phone':'13800000000','itinerary':itin},[step('save',{'phone':'13800000000','itinerary':itin})]if m!='save'else[],kind='itinerary_history'if m!='save'else'itinerary_save')
add('raffle','registerAll',{'peoples':peoples},expect='ok',kind='raffle_register')
add('raffle','query',{},[step('registerAll',{'peoples':peoples})],expect=peoples)
h=0
for x in '1700000000':h=(h*131+ord(x))&((1<<64)-1)
i=(h&0x7fffffff)%3;winner=['Alice','Bob','Carol'][i];pr={'level':'1','timestamp':'1700000000'}
add('raffle','raffle',pr,[step('registerAll',{'peoples':peoples})],expect=f'num: {i+1}, name: {winner}, level: 1',kind='raffle_draw')
add('raffle','registRaffle',dict(peoples=peoples,**pr),expect=f'num: {i+1}, name: {winner}, level: 1',kind='raffle_draw')
add('fact','save',fact,expect=fact['file_name']+fact['file_hash'],kind='fact_save')
add('fact','findByFileHash',{'file_hash':fact['file_hash']},[step('save',fact)],kind='fact_find')
mint={'to':A,'tokenId':'1','metadata':'http://chainmaker.org.cn/'};ms=[step('mint',mint)]
for m,params,expected,kind in [('balanceOf',{'account':A},'1',''),('ownerOf',{'tokenId':'1'},A,''),('getApproved',{'tokenId':'1'},'','erc_unapproved'),('tokenURI',{'tokenId':'1'},'https://chainmaker.org.cn/1',''),('tokenMetadata',{'tokenId':'1'},'tokenMetadata is http://chainmaker.org.cn/',''),('accountTokens',{'account':A},'','erc_tokens'),('tokenLatestTxInfo',{'tokenId':'1'},'','erc_latest')]:add('erc721',m,params,ms,expect=expected,kind=kind)
for m,expected in [('name','[name] name=huanletoken'),('symbol','[symbol] symbol=hlt')]:add('erc721',m,expect=expected)
add('erc721','setApprovalForAll2',{'approvalFrom':A},expect='setApprovalForAll2 success',kind='erc_approval_all')
add('erc721','approve',{'to':TO,'tokenId':'1'},ms+[step('setApprovalForAll2',{'approvalFrom':A})],expect='approve success',kind='erc_approve')
add('erc721','transferFrom',{'from':A,'to':TO,'tokenId':'1'},ms+[step('setApprovalForAll2',{'approvalFrom':A})],expect='transfer success',kind='erc_transfer')
add('erc721','mint2',mint,expect='mint success',kind='erc_mint2_partial')
(P/'inputs/cases.json').write_text(json.dumps(cases,indent=2));print('NEW CANDIDATE METHODS',len(cases))
# Repository-wide source scan; parse annotations, retain historical copies rather than count them as new deployments.
files=subprocess.check_output(['rg','--files',str(B),'-g','*.go'],text=True).splitlines();source_scan=[]
for name in files:
 p=Path(name)
 try:s=p.read_text(errors='replace')
 except OSError:continue
 exports=re.findall(r'//go:wasmexport\s+(\w+)',s)
 if exports and ('sdk.NewSimContext'in s or 'contract-sdk-go-wasm'in s):source_scan.append(dict(path=name,sha256=sha(p),exports=';'.join(exports),role='canonical_contract'if '/chainmaker/testdata-instrument/'in name and '/temp/'not in name else'historical_or_duplicate_source'))
with(P/'audit/ALL_CONTRACT_SOURCE_SCAN.csv').open('w')as f:w=csv.DictWriter(f,fieldnames=list(source_scan[0]));w.writeheader();w.writerows(source_scan)
old_done={('compute','bigNumCal'),('compute','hashCal'),('compute','normalCal'),('fact','saveAndFindByFileHash'),('erc721','mint'),('exchange','buyNow')};aux={'SetGas','GetGas','init_contract','upgrade','testgasJSONUnmarshal','testgasJSONMarshal','getGasRemaining','sprintf','errorf','jsonMarshal','jsonUnmarshal','parseInt','formatInt','stringsJoin','nolib','testgasWarmUp'};rows=[];vs=json.loads((P/'inputs/variants.json').read_text())
for c in ['compute','fact','erc721','exchange','identity','bigInput','itinerary','raffle']:
 s=subprocess.check_output(['git','-C',str(W),'show','95903a3:chainmaker/testdata-instrument/'+c+'/'+c+'.go'],text=True)
 for m in re.findall(r'//go:wasmexport\s+(\w+)',s):
  new=next((x for x in cases if x['contract']==c and x['method']==m),None);old=(c,m)in old_done
  helper=m in aux or c=='raffle'and m in['normalCal','hashCal','bigNumCal']or c=='bigInput'and m=='sleep5';reason='';status='step32_completed'if old else'ready'if new else'auxiliary_not_performance'if helper else'blocked'
  if c=='identity'and m=='callerAddress':reason='real same-contract cross-call hits unchanged active-contract Store guard; cannot bypass or mock'
  elif helper:reason='lifecycle/Gas probe or library warm-up/empty/delay benchmark; not independent business performance path'
  rows.append(dict(contract=c,method=m,source_path=str(B/'chainmaker/testdata-instrument'/c/(c+'.go')),frozen_source_commit='95903a3',wasm_path=vs[c+'-G0']['path'],wasm_sha256=vs[c+'-G0']['sha'],independent_deployable=True,also_child=c in['identity','erc721'],fixture_status=status,A_build_status='built-probe-validation-pending'if c in['bigInput','itinerary','raffle']else'historical_frozen',Copy_build_status='same inherited parser; preflight pending'if new else'historical',step32_covered=old,step33_execute=bool(new),status=status,blocking_reason=reason,case=new['case']if new else'',source_is_duplicate=False))
with(P/'CONTRACT_INVENTORY.csv').open('w')as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
# All deployed wasm candidates with source identities; do not infer a deployment from mere file presence.
paths=subprocess.check_output(['rg','--files',str(B),'-g','*.wasm','-g','!**/toolchains/**'],text=True).splitlines();ws=[]
for n in paths:
 f=Path(n);ws.append(dict(path=n,sha256=sha(f),bytes=f.stat().st_size,classification='canonical_go'if re.search(r'/chainmaker/testdata(?:-instrument)?/[^/]+/[^/]+-go.wasm$',n)else'historical_variant_or_synthetic_or_other_language'))
with(P/'audit/ALL_WASM_SCAN.csv').open('w')as f:w=csv.DictWriter(f,fieldnames=list(ws[0]));w.writeheader();w.writerows(ws)
(P/'audit/inventory_counts.json').write_text(json.dumps({'independent_contract_families':8,'all_exported_entries':len(rows),'new_business_candidates':len(cases),'step32_completed_methods':6,'source_files_scanned':len(files),'contract_source_candidates':len(source_scan),'wasm_artifacts_scanned':len(ws),'blocked_business':[r for r in rows if r['status']=='blocked']},indent=2));print('INVENTORY',len(rows),'exports;',len(source_scan),'source occurrences;',len(ws),'wasm files')
