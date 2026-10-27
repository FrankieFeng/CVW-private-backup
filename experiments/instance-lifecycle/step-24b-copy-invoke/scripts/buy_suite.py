import json
from run import run,P
from check_pair import check,receipt
# This is an extension after complete core checks, never an unconditional launch.
verification=json.loads((P/'verification.json').read_text());assert verification['all_passed']and verification['all_stopped']and verification['all_managed_zero']and verification['all_semantic_pairs_equal']
assert verification['formal_pairs']=={'compute':90,'erc721':90,'fact':90}
(P/'audit/buyNow-extension-gate.json').write_text(json.dumps({'core_verification':verification,'gate':'complete core raw/semantic/resource validation; no threshold/scope relaxation','not_a_requirement_that_all_effects_are_positive':True},indent=2))
for phase,batch,order in [('preflight',0,['A0','A1']),('formal',1,['A1','A0']),('formal',2,['A0','A1']),('formal',3,['A1','A0'])]:
 labels={}
 for v in order:
  label=f'exchange-{phase}-b{batch}-{v}';run(label,'exchange',pairs=1,phase=phase,batch=batch,single=v,module_first='A0'if batch%2==0 else'A1');labels[v]=label
 checked=check(receipt(labels['A0'],0,'A0'),receipt(labels['A1'],0,'A1'),True)
 (P/'audit'/f'buyNow-{phase}-b{batch}-parity.json').write_text(json.dumps(checked,indent=2))
 with(P/'PROGRESS.md').open('a')as f:f.write(f'\nbuyNow {phase}批{batch}两独立变体各根1+六真实子调用已比较，通过Gas/返回/根读写集/事件/初始最终账本，保持split预算。\n')
print('REGISTERED BUY NOW EXTENSION COMPLETE',flush=True)
