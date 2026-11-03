from pathlib import Path
import shutil
P=Path(__file__).resolve().parents[1];V=P/'source/vm';D=P/'source/diag/vm';assert not D.exists();shutil.copytree(V,D);f=D/'step39b_flags.go';f.write_text(f.read_text().replace('false','true'));(P/'diag.work').write_text((P/'A.work').read_text().replace(str(V),str(D)))
