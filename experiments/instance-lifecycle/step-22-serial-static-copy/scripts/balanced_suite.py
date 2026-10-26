"""Registered order sensitivity supplement, does not replace the original 3x3 pairs."""
from pathlib import Path
import subprocess,sys
P=Path(__file__).resolve().parents[1]
# Go rand(seed+i).Intn(2) already recorded by the primary run: 22003=>A1,A0;
# 22004=>A0,A1. Selection uses order only, never a measured duration.
for c in ['compute','fact','erc721']:
    for b,seed in enumerate([22003,22004,22003],1):
        subprocess.run([sys.executable,'-B',str(P/'scripts/run.py'),f'{c}-balanced-batch-{b}',c,
                        '--pairs','2','--phase','formal','--seed',str(seed)],check=True)
