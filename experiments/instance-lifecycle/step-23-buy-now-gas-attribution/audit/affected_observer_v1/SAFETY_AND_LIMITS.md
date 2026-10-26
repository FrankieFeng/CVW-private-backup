# 安全与证据边界

本轮只放行已验证的**有界串行诊断**，没有放行默认共享Store后台池、同Store跨线程创建/执行/关闭，未运行100次或TPS压测。

沿用Step22：固定OS owner、每合约/变体独立Store+Module缓存，imports/exports持久元数据提前物化。每次Fresh独立WASI/Instance，同步完成并清理后再调用。跨合约父子使用不同Store，同Store回调重入仍只限已有GetGas/SetGas；原ManagedAssert、in-flight/owner/native函数调用深度守卫未删除。

R0有意保留每个合约的Instance和真实运行时历史，不清理guest缓存、不重跑_start、不重置除原本SetGas之外的运行时状态。它只是性能/语义差异参考，不是可生产正确性基线。

Step22的“每次close后global ManagedCount回到创建前”只适用于Fresh临时scope。R0的其他持久Instance在期间可增长，因此本轮增加了只读 `ManagedScope.ManagedLiveCount`：每次清理必须严格满足 **after = beforeClose − ownedLiveEntries**；Fresh同时继续检查原创建前基线。没有以忽略清理错误或删守卫放行R0。最终manager.created=closed、全部scope登记0、owner退场和进程终止分别核查；已有guard实现原字节保留证据在final-health.json/source.diff。

Gas观测从固定WASM SHA绑定的GetGas槽读取registry指针及Remain，只读且检查地址边界。每个callee在原Getter处核对1次，根原12次bridge Getter+最终Getter共13次；无新增guest Getter调用。桥接观察放在原WACSI调用及原SetGas周围；没有改写Gas规则/结果/guest内存。三模式probe on/off的所有实际Gas和状态均相等，不能据此声称观察对CPU时间无影响。

GetTxRWSet会释放迭代器，本轮没有在调用中途执行它。采用已有只读GetTxRWMapByContractName并立即序列化，记录**当前深度可见的累计映射**，不是callee独占写集或每条内存写入日志。真实最终RWSet按原f.run只在事务结束取得。

S1全Memory SHA在每次创建后、_start前检查。Copy parser/restore与Step22完全一致；没有S2快照、没有Copy已执行Instance。所有Fresh已使用次数必须为0。R0样本中的继承Step22时间profile和S1 hash属于其**原创建时**，不会伪称每次复用重新创建/哈希，也不纳入任何性能结论。

尚未验证：真实Table元素函数身份、所有内部Globals动态等价、异常/OOG/回滚路径、节点ACL/共识/数据库行为、长期native资源有界和原共享Store池安全。原Table/Element/Global section保留及成功间接调用不等于全表身份验证。

Store长期保留时WASI线程增长的Step22问题仍未解决；本轮每进程最多10次创建，单独退出作为明确资源终点，不放宽上限。native二进制SHA已固定，但精确native构建源码映射仍缺。scope登记0、有限运行无崩溃不能证明不存在所有native泄漏/race。

构建build01因Step22 Git快照遗漏packaged/lib的6个占位Go文件失败，未执行guest。已按Step22实际执行source_hashes恢复原字节，未更新依赖；本轮会提交这些Go文件，只忽略.so。build02才执行全部诊断。比较脚本首轮有括号语法错误，修正后才启动正式块；没有掩盖guest失败或筛除不利Gas样本。
