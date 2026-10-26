"""Explicit compile-only helper. Never runs a test binary, fixture or guest."""
from pathlib import Path
import argparse,json,subprocess
ROOT=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'binaries/step21c.test');p.add_argument('--dry-run',action='store_true');a=p.parse_args()
cmd=json.loads((ROOT/'audit/compile-command.json').read_text());cmd[-1]=str(a.output.resolve())
assert '-c' in cmd and cmd[cmd.index('/usr/local/go/bin/go')+1]=='test'
if a.dry_run:print(json.dumps(cmd,indent=2));raise SystemExit(0)
assert not a.output.exists(),'preserve existing binary; use another output path'
mem={s.split(':',1)[0]:int(s.split()[1]) for s in Path('/proc/meminfo').read_text().splitlines() if s.startswith(('MemAvailable:','SwapTotal:','SwapFree:'))}
assert mem['MemAvailable']>=8*1024**2 and mem['SwapTotal']-mem['SwapFree']<=1024**2,'global resource guard'
a.output.parent.mkdir(parents=True,exist_ok=True)
subprocess.run(cmd,check=True,timeout=190)
