"""Freeze source/environment hashes and verify final WASM sections without executing guest code."""
from pathlib import Path
from collections import defaultdict
import csv,difflib,hashlib,json,platform,shutil,subprocess
P=Path(__file__).resolve().parents[1]
D=P.parent/'step-21d-safe-fresh'
ROOT=P.parents[2]
def sha(b):return hashlib.sha256(b).hexdigest()
def capture(argv):return subprocess.run(argv,capture_output=True,text=True,check=True).stdout
def sections(b):
    assert b[:8]==b'\0asm\1\0\0\0';i=8;ss=[]
    while i<len(b):
        begin=i;kind=b[i];i+=1;n=shift=0
        while True:
            q=b[i];i+=1;n|=(q&127)<<shift;shift+=7
            if q<128:break
        assert i+n<=len(b);ss.append((kind,b[begin:i+n]));i+=n
    return ss
manifest={}
for p in (P/'source/vm').rglob('*'):
    if p.is_file()and(p.suffix in ['.go','.h']or p.name in ['go.mod','go.sum']):manifest[str(p.relative_to(P))]=sha(p.read_bytes())
(P/'audit/source_hashes.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
diff=[];changed=[]
for relative in sorted(Path(k).relative_to('source/vm') for k in manifest):
    a=D/'source/vm'/relative;b=P/'source/vm'/relative
    old=a.read_text()if a.exists()else'';new=b.read_text()
    if old!=new:
        changed.append(str(relative))
        diff.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+str(relative),tofile='b/'+str(relative)))
(P/'source.diff').write_text(''.join(diff))
(P/'audit/source_changes.json').write_text(json.dumps(dict(base='87eb925:experiments/instance-lifecycle/step-21d-safe-fresh/source/vm',changed=changed),indent=2)+'\n')
assert changed==['step21d_fixture_test.go','step21d_runtime_test.go','step22_runtime_test.go','step22_static_test.go'],changed
original=Path('/home/frankie/mygitprojects/CVW/experiments/instance-lifecycle/step-16-chainmaker-copy/prototype/static_init_copy.go').read_text()
copied=(P/'source/vm/step22_static_test.go').read_text()
def function(s,name):
    start=s.index(name);rest=s[start:];end=rest.find('\nfunc ',1)
    return (rest if end<0 else rest[:end]).strip()
verified={}
for name in ['func prepareStaticMemory(', 'func (p *staticMemoryPlan) restore(']:
    a=function(original,name);b=function(copied,name)
    def formatted(x):
        return subprocess.run(['/usr/local/go/bin/gofmt'],input='package audit\n'+x,text=True,capture_output=True,check=True).stdout
    assert formatted(a)==formatted(b),name
    verified[name]=dict(gofmt_normalized_sha256=sha(formatted(a).encode()),only_formatting_diff_allowed=True)
(P/'audit/step16_copy_identity.json').write_text(json.dumps(verified,indent=2)+'\n')
pool=Path('/home/frankie/mygitprojects/CVW/experiments/instance-lifecycle/step-16-chainmaker-copy/prototype/vm_pool.go').read_text()
compiler=(P/'source/vm/step21d_compile.go').read_text()
def gas_config(s):
    start=s.index('opmap :=');end=s.index('config.MaxPagesLimit(512)',start)+len('config.MaxPagesLimit(512)')
    return formatted('func gasAudit(){\n'+s[start:end]+'\n}')
assert gas_config(pool)==gas_config(compiler),'Gas configuration changed'
(P/'audit/step16_gas_config_identity.json').write_text(json.dumps(dict(gofmt_normalized_sha256=sha(gas_config(pool).encode()),identical=True),indent=2)+'\n')

rows=list(csv.DictReader((P/'preparation.csv').open()))
templates={r['contract']:r for r in rows if r['event']=='template'}
artifacts={}
for f in (P/'inputs').glob('*-manifest.json'):
    for a in json.loads(f.read_text())['Artifacts']:
        artifacts[a['Contract']]=a
variants=[]
for c,a in sorted(artifacts.items()):
    raw=Path(a['Path']).read_bytes();assert sha(raw)==a['SHA256']
    ss=sections(raw);nodata=raw[:8]+b''.join(s for k,s in ss if k!=11)
    assert sha(nodata)==templates[c]['nodata_sha']
    # Exact section preservation, including Globals/Table/Element/Memory/Code.
    assert [(k,s)for k,s in ss if k!=11]==sections(nodata)
    (P/'audit'/f'{c}-nodata.wasm.sha256').write_text(sha(nodata)+'\n')
    for v,code in [('A0',raw),('A1',nodata)]:
        variants.append(dict(contract=c,variant=v,logical_source_sha256=sha(raw),module_sha256=sha(code),wasm_bytes=len(code),source_path=a['Path'],template_sha256=templates[c]['image_sha']if v=='A1'else'',template_image_bytes=int(templates[c]['image_bytes'])if v=='A1'else 0,copy_ranges=int(templates[c]['ranges'])if v=='A1'else 0,non_data_sections_byte_identical=True,config_sha=json.loads((P/'environment.json').read_text())['config_sha']))
with(P/'variants.csv').open('w',newline='')as f:
    w=csv.DictWriter(f,fieldnames=list(variants[0]));w.writeheader();w.writerows(variants)
env=json.loads((P/'environment.json').read_text())
env.update(go_version=capture(['/usr/local/go/bin/go','version']).strip(),os=capture(['uname','-srvmo']).strip(),cpu=capture(['lscpu']),meminfo=Path('/proc/meminfo').read_text(),go_env=json.loads(capture(['/usr/local/go/bin/go','env','-json','GOOS','GOARCH','CGO_ENABLED','GOFLAGS','GOTOOLCHAIN','GOROOT'])),source_hashes='audit/source_hashes.json',source_changes=changed,native_source_mapping='not proven exact; binary pinned by SHA; no runtime rebuild',business_sdk='existing candidate WASM; nearby source requires github.com/TKOTKCh/contract-sdk-go-wasm v0.1.3; exact original WASM build provenance not independently established',resource_limits=dict(MemoryMax='2GiB',rss_soft='1536MiB',TasksMax=256,threads_soft=220,RuntimeMaxSec=60,GoTimeoutSec=45,MemAvailable_min='8GiB',SwapUsed_max='1GiB'),boot_id_after=Path('/proc/sys/kernel/random/boot_id').read_text().strip())
assert env['boot_id_after']==env['boot_id_before'],'WSL reboot detected'
(P/'environment.json').write_text(json.dumps(env,indent=2)+'\n')
print('verified 5 original WASM, all non-Data sections, exact Step16 parser/restore, unchanged D compiler/managed sources; changed:',changed)
