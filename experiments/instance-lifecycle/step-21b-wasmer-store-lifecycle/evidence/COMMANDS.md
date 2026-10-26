# 本轮命令索引

实际构建/运行argv、stdout/stderr和退出状态见build.json、commands.jsonl、raw_logs/*command.json与*launch.json；没有通过文档重跑旧实验。

源码/版本只读命令包括：

- git -C CVW status --short / branch --show-current / worktree list / rev-parse HEAD
- git -C CVW switch -c step-21b-wasmer-store-lifecycle（唯一分支切换）
- rg --files、rg -n、nl -ba及sed/cat读取历史报告和VM/绑定源码
- git -C wasmer_chainmaker branch -av / remote -v / log -5 --oneline / rev-parse HEAD
- git -C wasmer_chainmaker show origin/chainmaker/v6.0.1:<文件>（快照文件路径见snapshot-manifest.json）
- git -C CVW diff dc4d63b c6addbf -- <vm_pool.go>
- sha256sum / readelf -n <packaged/lib/linux-amd64/libwasmer.so>
- ldd <Step21A binary>及本轮serial-native
- objdump -d -C --disassemble=<wasm_store_new/wasm_instance_new/wasm_instance_delete/wasm_func_call/wasi_env_delete> <so>
- 官方web查询、固定v6.0.1源码及C API README下载，URL/hash/status见official/sources.json
- python3 -B scripts/run_serial.py（已执行一次；恢复禁止重复）

报告和快照通过Python及here-doc写入本Step21B目录；没有修改其他实验或生产源码，没有git push，没有变更代理/WSL/VSCode。
