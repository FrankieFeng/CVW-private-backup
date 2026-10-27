# Step-22 分阶段结果

以下为主实验，同一条样本的累计S1/S2/S3及Invoke是嵌套边界，不相加。NewInstance不含Copy；static_init是逐行NewInstance+Copy再统计。所有单位ms。

| 合约 | 指标 | A0 Median | A1 Median | 配对节省 [95% CI] |
|---|---|---:|---:|---:|
| compute | newinstance | 2.207 | 0.060 | 2.151 [1.596, 2.369] |
| compute | copy | 0.000 | 1.260 | -1.260 [-1.382, -0.780] |
| compute | static_init | 2.207 | 1.320 | 0.938 [0.635, 1.330] |
| compute | wasi_imports | 1.076 | 1.207 | -0.221 [-0.389, 0.124] |
| compute | to_s1 | 3.239 | 2.582 | 0.693 [0.305, 1.025] |
| compute | start | 1.684 | 1.662 | -0.011 [-0.402, 0.098] |
| compute | to_s2 | 4.917 | 4.478 | 0.676 [-0.090, 1.286] |
| compute | callmethod | 0.304 | 0.315 | 0.008 [-0.128, 0.052] |
| compute | to_s3 | 5.184 | 4.881 | 0.691 [-0.237, 1.292] |
| compute | close | 0.040 | 0.037 | 0.002 [-0.012, 0.004] |
| compute | invoke | 5.220 | 4.922 | 0.695 [-0.254, 1.280] |
| fact | newinstance | 2.114 | 0.063 | 2.052 [1.638, 2.242] |
| fact | copy | 0.000 | 1.257 | -1.257 [-1.352, -0.854] |
| fact | static_init | 2.114 | 1.333 | 0.786 [0.487, 0.971] |
| fact | wasi_imports | 1.131 | 1.378 | -0.138 [-0.606, -0.011] |
| fact | to_s1 | 3.162 | 2.761 | 0.353 [0.089, 0.775] |
| fact | start | 1.558 | 1.593 | -0.050 [-0.172, 0.251] |
| fact | to_s2 | 4.737 | 4.373 | 0.416 [-0.089, 0.722] |
| fact | callmethod | 0.460 | 0.415 | 0.042 [-0.060, 0.225] |
| fact | to_s3 | 5.414 | 4.801 | 0.305 [-0.054, 0.942] |
| fact | close | 0.039 | 0.037 | 0.001 [-0.005, 0.005] |
| fact | invoke | 5.454 | 4.843 | 0.301 [-0.056, 0.947] |
| erc721 | newinstance | 2.290 | 0.071 | 2.190 [1.506, 2.423] |
| erc721 | copy | 0.000 | 1.293 | -1.293 [-1.462, -0.834] |
| erc721 | static_init | 2.290 | 1.369 | 0.829 [0.627, 0.983] |
| erc721 | wasi_imports | 1.197 | 1.288 | -0.112 [-0.283, 0.294] |
| erc721 | to_s1 | 3.520 | 2.835 | 0.743 [0.424, 0.911] |
| erc721 | start | 1.530 | 1.496 | 0.017 [-0.221, 0.229] |
| erc721 | to_s2 | 5.107 | 4.607 | 0.615 [0.059, 1.140] |
| erc721 | callmethod | 0.612 | 0.549 | 0.071 [0.001, 0.207] |
| erc721 | to_s3 | 5.702 | 5.187 | 0.821 [-0.169, 1.143] |
| erc721 | close | 0.041 | 0.040 | 0.002 [-0.001, 0.013] |
| erc721 | invoke | 5.741 | 5.225 | 0.829 [-0.170, 1.143] |
| exchange | newinstance | 1.859 | 0.154 | 1.711 [1.507, 2.096] |
| exchange | copy | 0.000 | 1.225 | -1.225 [-1.234, -1.140] |
| exchange | static_init | 1.859 | 1.388 | 0.486 [0.366, 0.862] |
| exchange | wasi_imports | 1.311 | 1.344 | 0.120 [-0.327, 0.148] |
| exchange | to_s1 | 3.172 | 2.819 | 0.429 [0.071, 0.896] |
| exchange | start | 1.942 | 1.676 | 0.202 [-0.346, 0.830] |
| exchange | to_s2 | 5.558 | 4.801 | 0.900 [0.084, 1.102] |
| exchange | callmethod | 63.696 | 58.910 | 10.506 [-16.876, 12.877] |
| exchange | to_s3 | 68.747 | 63.727 | 11.478 [-15.767, 12.963] |
| exchange | close | 0.034 | 0.032 | 0.002 [0.002, 0.047] |
| exchange | invoke | 68.782 | 63.760 | 11.528 [-15.765, 12.965] |

完整分位数/均值/N及Median CI在summary.csv，逐对记录在paired_samples.csv，配对Mean及Median CI在paired_effects.csv。平衡补充的同一组字段在balanced_summary/paired_effects，不能混合批次相减。

## Copy减少什么

主实验三个单合约static_init配对中位数节省0.938/0.786/0.829ms，全部9/9正向；累计to_s1分别节省0.693/0.353/0.743ms。额外的WASI/import准备及其他前导开销，使到S1的实际收益小于只看标准Data初始化移除的数字。启动和业务开销的变化没有被证明是Copy的因果效果。

平衡补充static_init分别节省0.774/0.589/0.792ms；to_s1分别0.759/0.857/0.699ms。新实例化API由约2ms降到约0.1ms，但必须支付约1ms的restore，不能把API差值直接当作完整路径收益。

## exchange真实调用链

`buyNow → identity.addWriteList → identity.isApprovedUser → identity.isApprovedUser → erc721.mint → erc721.setApprovalForAll2 → erc721.transferFrom`，六个callee均深度1、真实WASM/真实TxSimContext，未伪造成功响应。根CallMethod已包含子Invoke，不再次相加。exchange_transaction_stages.csv只对不相互嵌套的七次static/start/close求和。

第三批：A0根Invoke66.385277ms，A1为82.150221ms，反向15.764944ms；根CallMethod增加16.876238ms，六个子Invoke总和增加16.832774ms。七个Instance的NewInstance+Copy总和反而节省5.195181ms。

明确的大波动在其中erc721.mint的wasi_imports窗口：A0 15.836721ms，A1 34.912890ms（精确值以outlier_stages.csv为准）；它包含Finalize/GenerateImportObject/host GetImports。**已定位到计时窗口，尚未定位到GC、调度或native线程创建的具体原因**。没有数据支持把负收益归于memcpy慢、业务变更或节点共识。本实验没有节点/客户端阶段。

## 统计与局限

三独立进程批不等于每对均独立环境。主实验随机顺序有7:2失衡，补充逐批平衡但属于后续审计触发的小样本补充，均分表。P95=max，置信区间不能保证未来长周期稳定。不预设内存预热或segment数量是原因。

进程内正式性能没有S1 hash；预检hash会拉长S2/Invoke，严禁混入。父Invoke包含子调用日志开销；批末Store清理和部分native资源终结不在单Invoke中。原池/真实节点/长期吞吐仍未测定。
