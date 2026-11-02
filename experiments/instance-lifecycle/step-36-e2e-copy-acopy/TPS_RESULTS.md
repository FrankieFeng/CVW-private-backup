# 同步单客户端提交 TPS

表中为三批成功提交数之和/三批正式窗口秒数之和；不是三批TPS的简单平均，不是节点最大TPS。每笔同步返回后才发下一笔。

| 方法 | Fresh | Copy | A+Copy | A-only |
|---|---:|---:|---:|---:|
| bigInput.inputSize | 17.360 | 17.402 | 17.755 | 16.967 |
| bigInput.inputSizeMulti | 16.010 | 16.149 | 16.181 | 15.585 |
| bigInput.ioHeavy | 16.038 | 15.550 | 16.377 | 16.274 |
| identity.addWriteList | 16.574 | 18.379 | 18.397 | 18.734 |
| identity.alterAdminAddress | 18.686 | 19.834 | 21.523 | 18.765 |
| identity.removeWriteList | 3.056 | 3.001 | 2.940 | 2.992 |
| identity.isApprovedUser | 2.996 | 3.017 | 3.005 | 3.009 |
| identity.address | 19.248 | 19.249 | 18.938 | 18.691 |
| itinerary.save | 19.427 | 18.831 | 20.881 | 18.908 |
| itinerary.queryHistory | 3.000 | 2.963 | 2.955 | 2.953 |
| itinerary.saveAndQueryHistory | 2.981 | 2.919 | 2.911 | 2.920 |
| raffle.registerAll | 18.029 | 19.479 | 18.970 | 18.651 |
| raffle.query | 3.072 | 3.051 | 3.084 | 3.129 |
| raffle.raffle | 21.127 | 20.711 | 20.576 | 20.056 |
| raffle.registRaffle | 19.070 | 17.831 | 19.405 | 16.939 |
| fact.save | 18.438 | 17.714 | 18.719 | 20.077 |
| fact.findByFileHash | 3.043 | 2.971 | 2.916 | 3.012 |
| erc721.balanceOf | 3.192 | 3.030 | 3.039 | 2.976 |
| erc721.ownerOf | 3.109 | 3.095 | 3.129 | 3.082 |
| erc721.getApproved | 3.072 | 3.016 | 3.036 | 3.056 |
| erc721.tokenURI | 3.058 | 3.072 | 3.017 | 3.147 |
| erc721.tokenMetadata | 3.042 | 2.960 | 3.031 | 2.983 |
| erc721.accountTokens | 3.071 | 2.940 | 3.003 | 3.031 |
| erc721.tokenLatestTxInfo | 3.095 | 3.002 | 3.054 | 3.050 |
| erc721.name | 18.601 | 18.803 | 19.080 | 18.894 |
| erc721.symbol | 19.349 | 20.762 | 18.672 | 19.167 |
| erc721.setApprovalForAll2 | 17.473 | 17.993 | 18.563 | 18.019 |
| erc721.approve | 21.135 | 21.017 | 19.577 | 20.873 |
| erc721.transferFrom | 18.174 | 18.884 | 18.752 | 20.078 |
| erc721.mint2 | 17.748 | 18.326 | 19.818 | 17.813 |
| compute.bigNumCal | 14.875 | 15.100 | 14.943 | 15.625 |
| compute.hashCal | 16.338 | 17.233 | 17.275 | 16.944 |
| compute.normalCal | 7.840 | 7.757 | 7.824 | 8.157 |
| fact.saveAndFindByFileHash | 18.871 | 20.196 | 19.297 | 19.053 |
| erc721.mint | 18.094 | 16.742 | 18.851 | 17.585 |
| exchange.buyNow | 8.033 | 8.036 | 8.790 | 8.515 |
| identity.callerAddress | 15.405 | 15.003 | 15.369 | 14.798 |

THROUGHPUT.csv保留每个窗口起止、分子、成功/失败/超时及客户端响应率；TPS_STATISTICS.csv给出逐批结果；TPS_EFFECTS.csv仅有3个配对窗口的探索性增量CI。主矩阵1728/1728成功提交，0超时、0拒绝；原无效raffle窗口单列，不混入此成功率。

只有3个独立批次；一般每组12次，alterAdminAddress每组3次，raffle每组9次。95%CI采用批次/槽位两层成对bootstrap 10,000次；3个批次不足以稳定估计总体尾部或消除环境/顺序混杂。37方法、多对照未作多重比较校正，因此局部CI为探索性信号，不是普遍收益证明。四组顺序平衡但三个批次无法覆盖四个位置的全部排列。
