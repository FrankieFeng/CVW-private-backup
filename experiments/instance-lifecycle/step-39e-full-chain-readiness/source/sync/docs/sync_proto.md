1. 同步协议

   消息格式：

   ​		Type: uint8  协议类型

   ​		Flag: uint8	消息标志

   ​		Data: []byte  数据

   协议类型：

   - syncPing  同步节点发起，用于测试对端节点是否满足同步请求

     - flag: 

       - 请求: none | syncPingEstablish
       - 响应: syncPingAck 

     - data:

       - 请求：uint64块高

       - 响应：uint8，1表示可推送，0表示不可推送

         |     Name     |  Type  |             Desc             |
         | :----------: | :----: | :--------------------------: |
         |   support    | uint8  |         是否支持推送         |
         | syncWorkload | uint64 | 同步工作负载，正在推送工作量 |

     - state

       - 请求：statePingSend --- stateEstablish
       - 响应：statePingReceive  --- stateEstablish

     - behavior：

       - 请求:  附带块高数据发送syncPing消息，如果收到syncPing类型且flag包含SyncPingAck，解析data数据，data数据为false，则放弃后续流程，超时未收到响应也放弃后续流程；~~如果满足同步则发送syncPing，flag:syncPingReserve, 预定此推送~~。收到确定答复，则发送flag:syncPingEstablish完成连接
       - 回应:  回应方收到syncPing消息且flag为none，解析data数据为块高，拉取请求方相关的同步配置信息并根据自身持有的区块信息进行比对，并对是否满足同步请求结果回应，发送syncPing消息，flag为SyncPingAck，data: ok，如若收到flag:syncPingEstablish的syncPing消息，则完成连接，超时未收到则放弃连接

   - syncPushSettings 进行配置设置

     - flag:

       - 请求: syncSettingInit | syncSettingUpdate
       - 响应: syncSettingAck

     - data:

       - 请求：[]setting{ID:uint16, Value: uint32},  

         |            ID            |        Value        |        Desc        |
         | :----------------------: | :-----------------: | :----------------: |
         |   1 syncSettingVersion   |        pre+1        |     配置的版本     |
         |    2 syncSettingNodes    |        Nodes        |   推送的总节点数   |
         |  3 syncSettingNodeIndex  |      nodeIndex      | 推送节点所处的位置 |
         | 4 syncSettingRedundancy  | Redundancy strategy |      冗余策略      |
         | 5 syncSettingBlockHeight |     blockheight     |     生效的块高     |

       - 响应：setting{ID:uint16, Value: uint32},  返回请求中syncSettingVersion信息

     - behavior:

       - 请求：设置请求发送后，等待响应，超时后进行重传，重传再次未响应则判断此连接掉线
       - 响应：收到syncSettingInit消息，则初始化设置；收到syncSettingUpdate则进行消息更新，并返回syncSettingAck应答消息；如果在设置未初始化收到syncSettingUpdate消息/收到的版本号与自身不符，则发送syncReset响应以重置连接

   - syncPushWindowUpdate 同步速率配置，无响应

     - data

       - 请求：{~~height:uint64,~~ windowsize: uint64}

         |    Name    |    Type    |        Desc        |
         | :--------: | :--------: | :----------------: |
         | ~~height~~ | ~~uint64~~ | ~~当前收到的块高~~ |
         |  vacancy   |   uint64   |  还可容纳块的空间  |

     - behavior：

       - 请求：发送后即结束，后续如果速率还是快，则再次发送
       - 响应：~~接收方收到此消息后，跟自己当前发送到的块高跟height相比较，如果低于块高则快速发送直到height，然后降低速度发送height后面的数据~  收到此消息后，根据请求着的窗口大小进行发送速率的调整

   - syncFinish 同步结束

     - flag
       - 请求：none
       - 响应：syncFinishAck
     - data:
       - 请求：{id:uint64, blockheight: uint64}
       - 响应：{id: uint64}
     - state
       - 请求：stateFinishWait --- stateClose
       - 响应：stateCloseWait  --- stateClose
     - behavior：
       - 请求：发送请求，停止发送数据请求，并等待响应，超时重传
       - 响应：停止接收数据

   - syncDataPull 同步数据

     - flag

       - 请求：none
       - 响应：pullAck

     - data:

       - 请求：{height: uint64, fragment: string} 0/1/3

       - 响应：data: {height: uint64, merkle []byte, blockFragment: []byte}

         |     Name      |  Type  |   Desc   |
         | :-----------: | :----: | :------: |
         |    height     | uint64 |   块高   |
         |      Idx      |  int   | 分片索引 |
         |    merkle     | []byte | 默克尔根 |
         | blockFragment | []byte | 分片数据 |

     - ​	behavior：

       - 请求方: 发送获取请求，等待响应，超时返回错误

       - ### 响应方：根据请求获取对应的区块，并根据分片返回

   - syncDataPush 同步数据

     - flag：none

     - data: {height: uint64, settingVersion: uint64, merkle []byte, blockFragment: []byte}

       |      Name      |  Type  |           Desc           |
       | :------------: | :----: | :----------------------: |
       |     height     | uint64 |           块高           |
       | settingVersion | uint64 | 此分片数据生效的配置版本 |
       |     merkle     | []byte |         默克尔根         |
       | blockFragment  | []byte |         分片数据         |
       |                |        |                          |

   - syncReset 重置，表示非意外状态下中断通讯，接收到此消息后，需要重新发起连接

     - flag: none
     - data: nil
     - behavior:
       - 发送方：缺少同步必要的配置或者未建立同步通道，收到发来的其他请求则返回此消息
       - 接收方：接收到此消息后，中断此连接

   

   

   协议流程

   

   ![newsync-第 12 页.drawio](/Users/leon/work/sync/新设计/newsync-第 12 页.drawio.png)

   

   

   1. 同步节点：发送syncPing类型消息，询问请求的对端推送节点
   2. 推送节点：收到syncPing请求后，解析节点id,块高等信息，并拉取同步节点同步数据类型配置，同自身持有的数据范围进行比对，是否涵盖同步节点需要的数据，并将结果发回，消息类型为syncPing，flag: pingAck，然后等待初始化设置消息，超时则关闭连接
   3. 同步节点：
      1. 超时未收到syncPing消息的响应或收到的响应为不支持同步请求，则终止协商，清理协商数据 
      2. 根据推送节点的响应信息，是否使用此节点发送同步数据，如果使用则发送syncSettings类型消息，flag:settingInit, 初始化同步相关的配置，建立同步通道完成
   4. 推送节点：收到syncSettings消息且flag:settingInit则初始化配置，建立同步通道完成
   5. 推送节点：根据配置信息持续发送syncData消息
   6. ......
   7. 同步节点：根据自身的缓存的块及处理速度，随需向推送节点发送syncRate消息
   8. 推送节点：推送节点收到syncRate消息后，根据自身发送状态和同步节点状态，修正自身的发送速度，然后持续发送syncData消息
   9. 同步节点：发送syncSettings消息，flag:settingUpdate, 通知节点更新配置，每次更新配置配置版本要递增
   10. 推送节点：更新自己的配置信息，并发送syncSettings消息，flag：settingAck, 并附带配置版本
   11. 同步节点：超时未收到配置信息的回应或配置信息回应跟配置版本不一致，则将此节点剔除？然后重新发起更新配置
   12. 推送节点：如果节点推送的块高已经高于配置生效的块高，则从配置生效块高重新推送；如果块高低于配置生效块高，则按之前配置发送到此块高后，按照新配置继续推送
   13. 同步节点：收到的数据与配置版本不匹配则丢弃此数据
   14. ......
   15. 同步节点：发送syncFinish消息，flag:none，附带一个序列号，通知对端结束同步，如果超时未收到响应重发
   16. 推送节点：发送syncFinish消息，flag:finishAck，附带请求的序列号, 设置状态为stateCloseWait, 如果还有未完成的数据发送，则继续发送，直到结束
   17. 同步节点：收到syncFinish，flag:finishAck后，设置状态为stateFinishWait
   18. 推送节点：发送syncFinish，flag:none，附带之前的序列号+1，通知对端结束同步，如果超时未收到响应重发
   19. 同步节点：发送syncFinish消息，flag:finishAck，附带请求的序列号
   20. 推送节点：收到syncFinish消息，flag:finishAck后，close通路
   21. 