from pathlib import Path
import subprocess,json,hashlib,csv
P=Path(__file__).resolve().parents[1];R=P.parents[2];V=P/'source/vm'
def run(cmd):return subprocess.run(cmd,capture_output=True,text=True).stdout
lib=Path('/home/frankie/mygitprojects/.worktrees/cvw-step35b/experiments/instance-lifecycle/step-35b-native-wasi-thread/libraries/patched/libwasmer.so')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(lib)=='56b236ce1772b805819aec7c10eb417cd62bf0c6ee2c9b581e651f746bec17dc'
info={'parent':run(['git','-C',str(R),'rev-parse','HEAD']).strip(),'branch':run(['git','-C',str(R),'branch','--show-current']).strip(),'node_head':run(['git','-C','/home/frankie/mygitprojects/.worktrees/node-step36','rev-parse','HEAD']).strip(),'node_status':run(['git','-C','/home/frankie/mygitprojects/.worktrees/node-step36','status','--porcelain']),'go':run(['/usr/local/go/bin/go','version']).strip(),'os':run(['uname','-a']).strip(),'native_path':str(lib),'native_sha':sha(lib),'source38_original':str(R/'experiments/instance-lifecycle/step-38-copy-range-cost/source/A/vm'),'compile_failures_preserved':['build-main.log','build-main-r1.log'],'initialization_failure_preserved':'identity.log'}
(P/'audit/environment.json').write_text(json.dumps(info,indent=2));(P/'audit/cpu.txt').write_text(run(['lscpu']));env=['env','GOWORK='+str(P/'A.work'),'GOPROXY=off','/usr/local/go/bin/go'];(P/'audit/modules.json').write_text(run(env+['list','-m','-json','chainmaker.org/chainmaker/vm/v2','chainmaker.org/chainmaker/vm-wasmer/v2','chainmaker.org/chainmaker/store/v2']));(P/'audit/buildinfo-main.txt').write_text(run(['/usr/local/go/bin/go','version','-m',str(P/'binaries/vm-main-r2')]))
# Recorded performance source must still agree with its build hash (except tests added subsequently).
build=json.loads((P/'audit/build-main-r2-outcome.json').read_text());changes=[]
for f,h in build['source_hashes'].items():
 p=P/f
 if sha(p)!=h:changes.append(f)
assert changes==['source/vm/step39_artifact_test.go'],changes
(P/'audit/source-frozen.json').write_text(json.dumps({'performance_binary_sha':sha(P/'binaries/vm-main-r2'),'build_sha':build['sha256'],'runtime_sources_still_identical_to_build':True,'only_changed_test_file':changes},indent=2))
rs=list(csv.DictReader((P/'RESOURCE_SUMMARY.csv').open()));assert len(rs)==67
assert all(r['passed']=='True'and r['pid_exited']=='True'and r['stores_created']==r['stores_closed']and r['instances_created']==r['instances_closed']and r['pending']=='0'for r in rs)
for f in (P/'raw_logs').glob('*-command.json'):
 x=json.loads(f.read_text())
 if isinstance(x,dict):assert x['native_sha']==sha(lib)
assert not(P/'STOP_SHARED.json').exists()
# Keep a completed progress record, no hidden live job.
units=run(['systemctl','--user','list-units','--state=running','--no-legend']);assert not any('step39a-'in l for l in units.splitlines())
(P/'PROGRESS.md').write_text('''# Step-39A 已完成\n\n父提交93c3bea0；分支experiment/step39a-wasm-artifact。\n\n1. 源码审计完成：三次全WASM SHA用途、Clone拥有权、实际Factory依赖及边界已核实。\n2. 四组独立原型完成：A原路径/B摘要缓存/C快照引用/D组合；Copy C0、Owner、Guest、Gas、native不变。\n3. 缓存身份、并发只读Race、错误输入拒绝、Module同版换内容/旧内容命中/Reset重编译通过。\n4. 真实预检12进程、48目标调用通过；四组正式3方法×3批×2样本=72调用完成。\n5. 关闭Step-39新增插桩的A/B独立补充18进程、36正式调用完成。未与主样本混合。\n6. 所有原始观测和失败均保留，统计/报告/校验完成。资源监控67进程均正常退出；另保存身份/Race/4模式错误拒绝命令。\n\n构建错误：首次生成GOWORK绝对路径重复；第二次链接缺忽略的libwasmer产物。已保留两次日志，核对known patched library SHA后main-r2成功。identity首轮漏显式R1，原包init守卫拒绝，补齐后通过，无native泄漏。\n\n下一条如需复算：python3 scripts/analyze.py；python3 scripts/report.py；python3 scripts/finalize.py。运行脚本不会覆盖既有有效log；不重复性能实验。\n\n结论：仅SHA方向值得进入下一轮有限验证，Clone仅内存分配改善、未证实性能增量。hashCal无新增插桩补充的Factory CI跨零，未隐藏。缓存容量/Reset纯Go快照回收政策及真实节点升级还需独立验证。没有启动节点、没有自动下一阶段、没有推送。\n''')
# No source/history mutations outside new experiment; hash all portable deliverables, exclude ignored binaries/native/pycache.
files=[p for p in P.rglob('*')if p.is_file()and 'binaries'not in p.relative_to(P).parts and '__pycache__'not in p.parts and p.name not in ['libwasmer.so','SHA256SUMS']]
(P/'audit/SHA256SUMS').write_text(''.join(sha(p)+'  '+str(p.relative_to(P))+'\n'for p in sorted(files)))
print('VALIDATED',len(rs),'resource-balanced processes;',len(files),'files; no live step39a unit')
