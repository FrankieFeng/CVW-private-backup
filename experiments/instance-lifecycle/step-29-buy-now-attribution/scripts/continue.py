from experiment import block,P,check
import json
# Final instrumentation build3 error/rollback gate, each group in a fresh process.
for kind in ['empty','duplicate']:block(1,1,'exception2',True,kind)
assert(P/'audit/preflight-span-check2.json').exists()
for batch in range(1,4):
 for slot in range(1,11):
  receipts={}
  for trace in ([False,True]if ((batch-1)*10+slot)%2 else[True,False]):receipts[trace]=block(batch,slot,'formal',trace)
  for a,b in zip(receipts[False],receipts[True]):check(a,b,True)
