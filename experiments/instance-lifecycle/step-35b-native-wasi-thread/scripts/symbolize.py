from pathlib import Path
import subprocess,re,json,sys,bisect
P=Path(__file__).resolve().parents[1];label=sys.argv[1];lib=Path(sys.argv[2]);s=subprocess.check_output(['nm','-n','-C','--defined-only',str(lib)],text=True);entries=[]
for l in s.splitlines():
 m=re.match(r'([0-9a-f]+)\s+[tT]\s+(.*)',l)
 if m:entries.append((int(m[1],16),m[2]))
addrs=[x[0]for x in entries];text=(P/'raw_logs'/f'{label}-pthread.log').read_text();rows=[]
for l in text.splitlines():
 m=re.match(r' FRAME id=(\d+) module=(.*?) offset=(0x[0-9a-f]+) symbol=(.*)',l)
 if m and 'libwasmer'in m[2]:
  off=int(m[3],16);i=bisect.bisect_right(addrs,off)-1;rows.append({'id':int(m[1]),'module':m[2],'offset':m[3],'nearest_function':entries[i][1]if i>=0 else'unknown','function_offset':off-entries[i][0]if i>=0 else None})
(P/'audit'/f'{label}-frames.json').write_text(json.dumps(rows,indent=2));print('\n'.join(str(x)for x in rows if 'Selector'in x['nearest_function']))
