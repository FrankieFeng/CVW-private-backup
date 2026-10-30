from pathlib import Path
import json,argparse
from run import run,P,save
from check_pair import check
ORDERS=['G0,G1,G3,G2','G1,G2,G0,G3','G2,G3,G1,G0','G3,G0,G2,G1']
def block(c,phase,batch,slot):
 case=c['case'];label=f'{phase}-{case}-b{batch}-s{slot}'
 if phase=='preflight' and case=='erc721_accountTokens':label+='-backend-v2'
 f=P/'raw_logs'/f'{label}-block.json'
 if f.exists():
  assert json.loads(f.read_text())['valid'];return
 order=ORDERS[((batch-1)*10+slot-1)%4];groups=order.split(',');labels=[];receipts={};n=c['max_groups_per_process']
 for i in range(0,4,n):
  chunk=groups[i:i+n];lab=label+'-c'+str(i//n);o=run(lab,case,phase,order,batch,slot,','.join(chunk));assert o['passed'];labels.append(lab)
  folder=P/'raw_logs'/f'{lab}-receipts'
  for g in chunk:receipts[g]=json.loads((folder/f'target-{g}.json').read_text())
 for g in ['G1','G2','G3']:check(receipts['G0'],receipts[g])
 save(f,dict(case=case,phase=phase,batch=batch,slot=slot,order=order,labels=labels,valid=True,gas=receipts['G0']['actual_result'].get('gas_used'),real_business=True,table_identity='not_tested',exception_rollback='not_tested'))
 print('BLOCK_VALID',label,flush=True)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('phase',choices=['alignment','preflight','formal']);a.add_argument('--case');args=a.parse_args();cases=json.loads((P/'inputs/cases.json').read_text())
 if args.case:cases=[c for c in cases if c['case']==args.case]
 if args.phase=='alignment':
  for c in ['bigInput_inputSize','itinerary_save','raffle_registerAll']:run('alignment-'+c,c,alignment=True)
 else:
  for b in ([0]if args.phase=='preflight'else[1,2,3]):
   for c in cases:
    if args.phase=='formal':assert list((P/'raw_logs').glob(f'preflight-{c["case"]}-b0-s1*-block.json')),'preflight missing'
    for sl in ([1]if args.phase=='preflight'else range(1,11)):block(c,args.phase,b,sl)
   with(P/'PROGRESS.md').open('a')as f:f.write(f'\n{args.phase} batch {b} finished; every completed block saved separately.\n')
