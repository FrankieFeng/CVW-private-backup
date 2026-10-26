from pathlib import Path
import shutil,json,hashlib,re,subprocess
P=Path(__file__).resolve().parents[1]
ROOT=Path('/home/frankie/mygitprojects')
BASE=ROOT/'.worktrees/cvw-step21c'
V=BASE/'chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0'
D=P/'source/vm';D.mkdir(parents=True,exist_ok=True)
assert not (D/'go.mod').exists(),'Already prepared; do not overwrite implementation'
manifest=[]
for folder in [Path('.'),Path('wasmer-go')]:
 for f in (V/folder).glob('*.go'):
  if f.name.endswith('_test.go'):continue
  dst=D/folder/f.name;dst.parent.mkdir(parents=True,exist_ok=True)
  text=f.read_text();original=text
  if folder==Path('wasmer-go'):text=text.replace('runtime.SetFinalizer(', 'managedSetFinalizer(')
  # A file using runtime exclusively for SetFinalizer needs no runtime import after interception.
  if folder==Path('wasmer-go') and 'runtime.'not in text:text=text.replace('import "runtime"\n','').replace('\n\t"runtime"','')
  dst.write_text(text)
  manifest.append({'source':str(f),'source_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'target':str(dst.relative_to(P)),'normalized':True})
for f in ['go.mod','go.sum']:shutil.copyfile(V/f,D/f)
pack=D/'wasmer-go/packaged';shutil.copytree(V/'wasmer-go/packaged',pack)
# All workspaces use original cached dependencies, replacing only VM module with the private copy.
work=(BASE/'go.work').read_text()
work=re.sub(r'(?m)^(\s*)(\.\S*|\.)(\s*)$',lambda m:m[1]+str((BASE/m[2]).resolve())+m[3],work)
work=work.replace(str(V),str(D))
(P/'go.work').write_text(work)
# Use the real Step21C fixture for accounts, state, VmManager, receipts and assertions.
s=(BASE/'experiments/instance-lifecycle/step-21c-exchange-cross-contract/source/step21c_fixture_test.go').read_text()
a=s.index('// This adapter observes');b=s.index('func s21cEmit',a)
s=s[:a]+s[b:]
s=s.replace('instances *InstancesManager','instances *dManager')
s=s.replace('base := NewInstancesManager(ChainId)','base := newDManager(os.Getenv("D_POLICY"))')
s=s.replace('observed := &s21cObservedManager{VmInstancesManager: base, actual: base, fixture: f}', 'base.fixture = f\n\tobserved := base')
s=s.replace('a.Contract != "exchange" && a.Contract != "identity" && a.Contract != "erc721"', 'a.Contract != "compute" && a.Contract != "exchange" && a.Contract != "identity" && a.Contract != "erc721"')
s=s.replace('if len(store.contracts) != 3 {','if len(store.contracts) < 1 {')
a=s.index('func (f *s21cFixture) close()');b=s.index('// Compiled assertions',a)
s=s[:a]+'''func (f *s21cFixture) close() {
 if err := f.instances.Close(); err != nil { f.t.Error(err) }
}

'''+s[b:]
# Do not enable old prepared test. New bounded tests invoke real fixture explicitly.
(D/'step21d_fixture_test.go').write_text(s)
# Snapshot interface is embedded with explicit nil failure for unimplemented APIs.
(D/'step21d_context_test.go').write_text('''package wasmer
import "chainmaker.org/chainmaker/protocol/v2"
const ChainId="chain02"
const BlockVersion=uint32(1)
type SnapshotMock struct { protocol.Snapshot }
var compileTime float64
''')
# Identical opcode/function maps/config copied textually; instantiate no verification instance/pool worker.
pool=(V/'vm_pool.go').read_text();a=pool.index('\topmap :=',pool.index('func newVmPool'));b=pool.index('\tvmPool :=',a)
body=pool[a:b]
body=body.replace('contractId.Name, contractId.Version','contractId.Name, contractId.Version')
(D/'step21d_compile.go').write_text('''package wasmer
import (
 "fmt"
 "time"
 "chainmaker.org/chainmaker/logger/v2"
 commonPb "chainmaker.org/chainmaker/pb-go/v2/common"
 wasmergo "chainmaker.org/chainmaker/vm-wasmer/v2/wasmer-go"
)
func dCompile(contractId *commonPb.Contract, byteCode []byte, log *logger.CMLogger)(*wasmergo.Store,*wasmergo.Module,error){
'''+body.replace('return nil, fmt.Errorf','return nil, nil, fmt.Errorf')+'\n return store,module,nil\n}\n')
(P/'audit/source-inputs.json').write_text(json.dumps(manifest,indent=2))
(P/'.gitignore').write_text('/binaries/\n/source/vm/wasmer-go/packaged/lib/**/*.so\n/source/vm/wasmer-go/packaged/lib/**/*.a\n/source/vm/wasmer-go/packaged/lib/**/*.dylib\n/source/vm/wasmer-go/packaged/lib/**/*.dll\n/source/vm/wasmer-go/packaged/lib/**/*.lib\n/source/vm/default.log*\n**/__pycache__/\n')
print(D)
