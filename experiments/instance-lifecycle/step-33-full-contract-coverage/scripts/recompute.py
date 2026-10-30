from pathlib import Path
import subprocess,sys,json,hashlib
P=Path(__file__).resolve().parents[1]
before=hashlib.sha256((P/'PAIRED_EFFECTS.csv').read_bytes()).hexdigest()if(P/'PAIRED_EFFECTS.csv').exists()else None
for n in ['analyze.py','stage_report.py','finalize_docs.py','recommend.py']:
 r=subprocess.run([sys.executable,str(P/'scripts'/n)],capture_output=True,text=True);(P/'audit'/f'recompute-{n}.log').write_text(r.stdout+r.stderr);print(n,r.returncode,r.stdout[-250:],flush=True)
 if r.returncode:print(r.stderr);raise SystemExit(r.returncode)
after=hashlib.sha256((P/'PAIRED_EFFECTS.csv').read_bytes()).hexdigest();assert before is None or before==after,'paired analysis unexpectedly changed'
(P/'audit/RECOMPUTE_CHECK.json').write_text(json.dumps(dict(before_effects_sha=before,after_effects_sha=after,identical=before==after,raw_data_unchanged=True),indent=2));print('DETERMINISTIC',after)
