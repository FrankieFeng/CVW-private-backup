from pathlib import Path
import json,csv,hashlib,subprocess
P=Path(__file__).resolve().parents[1];root=P.parents[2];prefix=str(P.relative_to(root));build=json.loads((P/'environment.json').read_text());source_commit=subprocess.check_output(['git','-C',str(root),'rev-parse','ebbe636'],text=True).strip()
for rel,sha in build['source_hashes'].items():
 assert hashlib.sha256((P/rel).read_bytes()).hexdigest()==sha
 archived=subprocess.check_output(['git','-C',str(root),'show',source_commit+':'+prefix+'/'+rel]);assert hashlib.sha256(archived).hexdigest()==sha
outcomes=[json.loads(f.read_text())for f in sorted((P/'raw_logs').glob('*-outcome.json'))]
for o in outcomes:
 assert o['passed']and o['all_owned_processes_stopped']and o['cgroup_empty']
 cmd=json.loads((P/'raw_logs'/f"{o['label']}-command.json").read_text());assert cmd['binary_sha256']==build['binary_sha']
 provenance={'source_commit':source_commit,'baseline_commit':'81e1c0a','binary_sha':build['binary_sha'],'source_manifest_sha':hashlib.sha256(json.dumps(build['source_hashes'],sort_keys=True).encode()).hexdigest(),'metadata_added_after_sampling':True,'source_commit_exact_bytes_match_build_manifest':True,'native_sha':build['settings']['native_sha'],'family':o['family'],'left':o['left'],'right':o['right']}
 (P/'raw_logs'/f"{o['label']}-provenance.json").write_text(json.dumps(provenance,indent=2)+'\n')
v=json.loads((P/'verification.json').read_text());assert v['processes']==102 and v['formal_pairs']==180 and v['preflight_pairs']==12 and v['diagnostic_pairs']==6 and v['semantic_pairs']==198
rr=list(csv.DictReader((P/'PAIRED_EFFECTS.csv').open()));assert all(r['n_pairs']=='30'and r['batches']=='3'and r['processes']=='15'for r in rr)
c=list(csv.DictReader((P/'CORRECTNESS.csv').open()));assert all(r['semantic_equal']=='True'for r in c)
assert not(P/'PPT.md').exists()
print('verified 102 exits, shared Store/Module pairing, 198 semantic pairs, 3x10 main pairs, frozen code/source identity; no PPT')
