# 单一最小补丁与构建

```diff
- closer: mio::Waker::new(poll.registry(), Token(0)).unwrap(),
+ closer: mio::Waker::new(poll.registry(), Token(1)).unwrap(),
  token_close: Token(1),
```

native提交 `24b6afd79`；精确补丁 `source/selector-token.patch`。正常I/O Token从seed10开始分配，关闭Token1与其不冲突。已有LocalNetworking析构调用shutdown，故不增加另一套close或新的强制回收。线程仍靠wake/return自然退出，不使用kill、强行close FD或全局锁。

| 库 | SHA-256 |
|---|---|
| 原始6.0.1 | dcdfa7164c58856f6e0c01597fd52c9a4c5f7da772751e3a874f7333612c3db9 |
| 重建未修复 | 75dea41cd2d9b7d83a77b54c21fcda756b187305a1a967e5877a0ce370cab07b |
| 单行补丁 | 56b236ce1772b805819aec7c10eb417cd62bf0c6ee2c9b581e651f746bec17dc |

原始ELF记录rustc1.81.0，重建使用相同历史版本、fork6.0.1的Cargo.lock固定依赖、相同Cranelift及features：

```sh
cargo +1.81.0 build --release --manifest-path lib/c-api/Cargo.toml   --no-default-features --features wat,compiler,cranelift,wasi,middlewares,webc_runner --locked
```

构建通过单任务、MemoryMax1536MiB、TasksMax128、600秒上限。第一次仅因C-API build.rs要求输出路径目录名为target而失败；用target指向同一产物目录的symlink恢复，不改build.rs，失败日志保留。精确命令/环境见 `audit/*build-command.json`。安装rust1.81未改变默认toolchain；rustup管理器安装时自动更新1.29.1→1.29.2，已如实记录。

Go Smoke二进制相同，仅通过LD_LIBRARY_PATH选择库；`*-loaded-maps.txt`验证实际加载路径，每条命令记录so和二进制hash。旧库专用的私有Rc布局探针调用已从实验副本去掉，避免拿不适用的私有布局读新库；空的strong计数不作证据。标准计数/所有权守卫仍启用。复制的旧C helper未被调用。

补丁不改Store、Engine、Module缓存、Gas metering、Guest及Copy实现。新旧原始库不能当作位级同构建；Gas/状态另用原始库、未修复重建库、补丁库实测核对。未做性能对比或正式E2E。

回退：生产未替换，无需回滚生产。实验运行改回 `libraries/baseline` 或 `libraries/original` 并使用新进程；不要热替换运行进程so。native分支可在另一个干净worktree取基线0910740重建，或revert单行提交；不要reset/clean历史工作区。
