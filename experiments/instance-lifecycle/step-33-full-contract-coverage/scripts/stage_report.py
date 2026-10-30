from report import *
stages=read(P/'STAGE_EFFECTS.csv');se={(r['case'],r['effect'],r['metric']):r for r in stages};out=[];lines=['# 阶段归因','', '以下为同区块直接差的Mean，单位ms；阶段互不重叠，采用Mean才可代数分解，不能相加Median。S2→S3包含CallMethod及Gas结算。剩余项是完整Invoke减去已列阶段，保持未归因。','', '|方法|效应|完整Invoke|S0→S1|S1→S2|S2→S3|Close|剩余|','|---|---|---:|---:|---:|---:|---:|---:|']
for r in new:
 if r['effect']not in ['A','Copy','A+Copy']:continue
 cs=r['case'];e=r['effect'];vals=[float(se[(cs,e,m)]['paired_saving_mean_ms'])for m in ['to_s1_ns','s1_to_s2_ns','s2_to_s3_ns','close_ns']];iv=float(r['paired_saving_mean_ms']);res=iv-sum(vals);out.append(dict(case=cs,effect=e,N=r['N'],invoke_mean_saving_ms=iv,s0_s1_mean_saving_ms=vals[0],s1_s2_mean_saving_ms=vals[1],s2_s3_mean_saving_ms=vals[2],close_mean_saving_ms=vals[3],unattributed_mean_saving_ms=res));lines.append('|'+cs+'|'+e+'|'+'|'.join(f'{x:.4f}'for x in [iv,*vals,res])+'|')
write(P/'STAGE_ATTRIBUTION.csv',out);lines+=['','NewInstance和Copy是S0→S1的子窗，_start是S1→S2子窗，export是CallMethod子窗；原始子窗直接效应见STAGE_EFFECTS.csv。模板解析与Module编译在目标Invoke之外，不能拿其缩短解释此完整Invoke收益。','', 'A按源码构造reachable padding以改变bloc，新增三个合约probe确认first arena skip=0；Copy剔除active Data初始化后restore，位置在WASI Initialize/_start前。阶段计时可支持收益集中在哪个窗口；对GC、cache、native allocator或未观测机制的具体归因仍需独立证据。','', '同一合约多方法共享相同WASM/初始化布局，业务执行长短会改变初始化节省占比；不能将方法之间比例差自动归因于Data Segment数量。不同方法/批次绝对时间不合并估计因果。Step32旧六方法阶段统计保留其原来源，本轮不重算成新样本。']
(P/'STAGE_ATTRIBUTION.md').write_text('\n'.join(lines)+'\n')
art=[]
for key,v in vs.items():
 c,g=key.rsplit('-',1);f=Path(v['path']);assert hashlib.sha256(f.read_bytes()).hexdigest()==v['sha'];art.append(dict(contract=c,group=g,A=g in ['G1','G3'],Copy=v['copy'],path=str(f),wasm_sha256=v['sha'],bytes=f.stat().st_size,source_family='Step18-P0-plain',source_snapshot=snap if 'snap'in globals()else json.loads((P/'audit/SOURCE_SNAPSHOT.json').read_text())['source_snapshot_commit']))
for c in {r['contract']for r in art}:assert vs[c+'-G0']['sha']==vs[c+'-G2']['sha']and vs[c+'-G1']['sha']==vs[c+'-G3']['sha']
write(P/'WASM_MANIFEST.csv',art)
mods=read(P/'MODULE_PREPARATION.csv');temps={}
for r in mods:
 if r['event']=='template' and r['source_sha']in {v['sha']for v in vs.values()}:
  k=(r['contract'],r['source_sha']);d=dict(contract=k[0],wasm_sha256=k[1],image_bytes=r['image_bytes'],image_mib=int(r['image_bytes'])/1048576,ranges=r['ranges'],nodata_sha=r['nodata_sha'],image_sha=r['image_sha'],cache_key=r['key']);assert k not in temps or temps[k]==d;temps[k]=d
write(P/'TEMPLATE_CAPACITY.csv',list(temps.values()));print('stage and artifact manifests complete')
