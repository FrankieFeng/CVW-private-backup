# Step-21A 容量补丁审计

原Step21运行源码077a8cb，报告commit dc4d63b；容量修复commit c6addbf3ddbc9bb56524b62557a6c52029bb8266，experiment/step21-capacity-fix。dc4d63b→c6addbf准确差异见audit/capacity-fix.patch：vm_pool.go的grow内仅增加10行。

| 检查项 | 结论 |
|---|---|
| 仅退出/关闭？ | 否。正常worker的apply、add、refresh、reset均调用grow，不是退出专用分支 |
| 容量配置 | min5/max10/grow5不变，channel容量10不变 |
| 初始库存 | 仍空池0。验证Instance在入worker前单独创建关闭，不算可用库存 |
| grow策略 | 改变：每轮按max10-currentSize裁剪size，room≤0立即返回；原版不在grow内检查这一上界 |
| 创建并发度 | grow仍单worker顺序创建；没有并行创建优化，但异步Close仍可多goroutine |
| GetInstance | 函数未改；select/空池发apply后阻塞接收不变。供给变化可间接改变等待 |
| RevertInstance | 该补丁未改；R1仍goroutine Close→remove→add，R0正常归还 |
| InvokeTime边界 | runtime.go diff为空；UnixNano起止和defer顺序原样 |
| 稳态供给 | 可能变化：apply增量与每笔drop/add叠加时，容量裁剪会在正常业务期间生效；不能声称倍率完全不受影响 |

原正常路径：GetInstance空池→applySignalC→worker shouldGrow→grow(5)；业务结束R1异步Close→remove→add→grow(1)。补丁统一限制这两条grow请求，避免队列满时仍创建/发送。退出阻塞是观察到的结果之一，并不代表修复只在退出生效。

先验结论：Step21四短方法仍有真实池等待证据，但10～15倍的精确倍率来自修复版，原版无法通过完整退出验证。需要安全的同环境新对照才能量化补丁影响，不能根据一对历史诊断与另一批中位数相减。

## 历史原始事件补充（不作跨批次性能相减）

读取原Step21、原路径重跑、修复版首批bigNumCal R1：各100次调用返回前均有101次创建完成（含验证用1次），返回后分别再完成11/11/10次创建。两个原版记录中的满队列enqueue尝试都发生在最后一次返回之后；修复版无该尝试。见audit/history_pool_event_counts.csv。

这支持“已观察到的满队列挂起发生在窗口后”，但不能据此证明补丁只影响退出：worker currentSize包含借出/等待remove的实例，不等于日志queue_len；该上界也可能在运行中裁剪请求。本轮未完成安全的主对照，精确倍率影响未量化。
