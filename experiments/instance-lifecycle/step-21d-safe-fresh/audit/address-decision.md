# Step21C夹具的地址模式修正

首次真实init在BlockVersion1 + CHAINMAKER地址模式失败：vm/v2@v2.4.0/wasi.go:402–436对小于2201只接受ETHEREUM（或单独的ZXL分支），不接受CHAINMAKER。不能绕过GetSenderAddr或直接写管理员状态。

第二次使用ZXL，identity及ERC721实际init都成功，但ERC721管理员是原公钥PEM，击中原夹具UID断言。vm_factory.go:470–489明确ZXL在旧块版本注入MemberInfo，而非UID。此处没有native失败，正常计数关闭。

最终选ETHEREUM：这是旧块版本明确支持的非ZXL地址模式，同时保留原夹具期望的SDK GetSenderPk=UID语义；不改BlockVersion、Gas算法、合约、冻结输入或callee响应。重新真实初始化，仍不直接seed管理员/白名单/NFT状态。两个失败进程及receipt保留。当前VM fixture不是节点ACL/签名认证。
