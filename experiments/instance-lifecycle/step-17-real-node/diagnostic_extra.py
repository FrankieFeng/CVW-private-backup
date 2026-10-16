from run import Client,record,O,specs,modes,job
c=Client();f=open(O/'diagnostic-extra.jsonl','a')
# Retry failed diagnostic request; retain the original transport error.
for m in modes:record(c,[job(specs[0],m,'retry-diagnostic:compute',900000000100)],f)
for m in modes:
 for address in [specs[1]['params']['to'],specs[4]['params']['to']]:record(c,[dict(Mode=m,Op='query',Contract='erc721',Method='balanceOf',Params={'account':address},Tag='balance:'+address)],f)
c.close();f.close()
