from run import *
for name in ['Registry','Collectible','Upgrade','Failure','ResetStop']:
 execute('lifecycle-'+name,'A','compute_hashCal','G1',test='TestStep39B'+name,binary_label='vm-diag-r1',expect_owner=name not in ['Registry','Collectible'])
(P/'LIFECYCLE_COMPLETE.json').write_text(json.dumps({'passed':True,'tests':5}))
