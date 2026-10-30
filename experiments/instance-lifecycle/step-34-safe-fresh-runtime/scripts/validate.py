import os,json
from run import run as original_run,P,save
prefix=os.environ.get("E34_RUN_PREFIX","v9-")
def run(label,*args,**kwargs):return original_run(prefix+label,*args,**kwargs)
os.environ['E34_BINARY_LABEL']=os.environ.get('E34_BINARY_LABEL','build9')
run('owner-freeze','owner')
run('poison-freeze','poison')
for fault in ['store','wasi','instance','initialize','execute','close','cancel-wasi','cancel-close']:
 run('freeze-fault-'+fault,'fact',single='G0',fault=fault)
for c,ex in [('erc721','empty'),('exchange','duplicate'),('fact','missing')]:run('business-error-'+c,c,single='G0',exception=ex)
for b in [1,2,3]:
 order=['G0,G1,G3,G2','G2,G3,G1,G0','G1,G0,G2,G3'][b-1]
 for c in ['compute','fact','erc721','exchange']:
  gs=order.split(',');n=1 if c=='exchange'else 2;labels=[]
  for i in range(0,4,n):
   lab=f'verify-b{b}-{c}-c{i//n}';run(lab,c,phase='correctness',order=order,batch=b,slot=1,single=','.join(gs[i:i+n]));labels.append(prefix+lab)
  save(P/'raw_logs'/f'{prefix}verify-b{b}-{c}-block.json',dict(case=c,batch=b,labels=labels,groups=gs))
 # Direct architecture cost, both options use the same patched bindings, same WASM/input and Invoke boundary.
 for c in ['compute','fact','erc721','exchange']:
  labels=[]
  for independent in ([False,True]if b%2 else[True,False]):
   lab=f'cost-b{b}-{c}-'+('new'if independent else'control');run(lab,c,phase='architecture_cost',batch=b,slot=1,single='G0',independent=independent);labels.append(prefix+lab)
  save(P/'raw_logs'/f'{prefix}cost-b{b}-{c}-pair.json',dict(case=c,batch=b,labels=labels,positive_definition='new minus control is extra lifecycle cost, not Copy saving'))
 with(P/'PROGRESS.md').open('a')as f:f.write(f'\n最终build6验证批{b}完成：四合约四组正确性与同代码Store架构成本，所有区块/配对已落盘。\n')
