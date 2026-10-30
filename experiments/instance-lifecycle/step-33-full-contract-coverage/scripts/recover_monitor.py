# Recover one completed process after a /proc read raced with normal process exit.
from run import *
label=json.loads((P/'state.json').read_text())['label'];unit='step33-'+label
c=json.loads((P/'raw_logs'/f'{label}-command.json').read_text());log=(P/'raw_logs'/f'{label}.log').read_text(errors='replace');stats=dict(x.split('=',1)for x in cmd(['systemctl','--user','show',unit,'-p','MainPID','-p','ExecMainStatus','-p','SubState','-p','ControlGroup']).stdout.splitlines()if'='in x)
assert stats['MainPID']=='0'and stats['ExecMainStatus']=='0'and stats['SubState']=='exited'and'--- PASS: TestStep33Serial'in log and'--- FAIL:'not in log
es=[json.loads(x[8:])for x in log.splitlines()if x.startswith('STEP21C ')];bs=[e for e in es if e.get('event')=='boundary'];owner=[e for e in es if e.get('event')=='owner_closed'][-1];manager=[e for e in es if e.get('event')=='manager_closed'][-1];assert owner['managed_pending']==0 and manager['created']==manager['closed']and manager['in_flight']==0
rs=[json.loads(x)for x in(P/'raw_logs'/f'{label}-resources.jsonl').read_text().splitlines()];rss=max([x['rss_kib']for x in rs]+[e.get('VmRSS',0)for e in bs]);threads=max([x['threads']for x in rs]+[e.get('Threads',0)for e in bs]);assert rss<768*1024 and threads<=125
cgn=stats['ControlGroup']or next(x['systemd']['ControlGroup']for x in rs if x['systemd'].get('ControlGroup'));assert cgn;cg=Path('/sys/fs/cgroup')/cgn.lstrip('/');assert not cg.exists()or not(cg/'cgroup.procs').read_text().strip();assert cmd(['systemctl','--user','stop',unit]).returncode==0
save(P/'raw_logs'/f'{label}-outcome.json',dict(label=label,case=c['case'],contract=c['env']['E22_CONTRACT'],phase=c['env']['E22_PHASE'],batch=c['batch'],slot=c['slot'],order=c['order'],single=c['single'],exception='',alignment=False,passed=True,reason='completed_before_proc_status_read; recovered without rerun',peak_rss_kib=rss,peak_threads=threads,wall_s=rs[-1]['elapsed_s'],systemd=stats,all_owned_processes_stopped=True,cgroup_empty=True,boundaries=bs,owner=owner,monitor_recovery=True))
save(P/'audit'/f'{label}-monitor-recovery.json',dict(command=c,stats=stats,recovered_completed_samples=True,new_guest_execution=False))
with(P/'PROGRESS.md').open('a')as f:f.write('\n监控/proc退出竞态 '+label+'：Guest正常PASS，无资源异常；检查原unit退出、receipt、owner和cgroup后恢复outcome，未重跑。Python捕获ProcessLookupError与FileNotFoundError。\n')
print(label,'RECOVERED_NO_RERUN')
