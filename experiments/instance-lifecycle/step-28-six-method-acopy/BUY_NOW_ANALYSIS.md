# buyNow根与子窗口（同区块直接差）

正值=左−右，右侧快。每项30个区块，root index0为包含所有子调用的完整Invoke；禁止把root与children再次相加。子窗口是解释性统计，没有单独确认CI。

| 对照 | 调用 | 方法 | Invoke配对节省Median ms | _start配对节省Median ms |
|---|---:|---|---:|---:|
| G0→G1 | 0 | exchange.buyNow | -2.870 | -0.035 |
| G0→G1 | 1 | identity.addWriteList | 0.686 | 0.005 |
| G0→G1 | 2 | identity.isApprovedUser | 0.304 | -0.100 |
| G0→G1 | 3 | identity.isApprovedUser | 0.300 | -0.081 |
| G0→G1 | 4 | erc721.mint | 0.949 | -0.014 |
| G0→G1 | 5 | erc721.setApprovalForAll2 | 0.180 | 0.080 |
| G0→G1 | 6 | erc721.transferFrom | 0.705 | 0.004 |
| G1→G2 | 0 | exchange.buyNow | 5.077 | 1.006 |
| G1→G2 | 1 | identity.addWriteList | 0.959 | 0.786 |
| G1→G2 | 2 | identity.isApprovedUser | 0.894 | 0.920 |
| G1→G2 | 3 | identity.isApprovedUser | 1.110 | 1.009 |
| G1→G2 | 4 | erc721.mint | -4.113 | 0.843 |
| G1→G2 | 5 | erc721.setApprovalForAll2 | 1.136 | 0.848 |
| G1→G2 | 6 | erc721.transferFrom | 1.248 | 0.924 |
| G0→G2 | 0 | exchange.buyNow | -0.058 | 0.926 |
| G0→G2 | 1 | identity.addWriteList | 1.413 | 0.793 |
| G0→G2 | 2 | identity.isApprovedUser | 1.310 | 0.842 |
| G0→G2 | 3 | identity.isApprovedUser | 1.469 | 0.850 |
| G0→G2 | 4 | erc721.mint | 0.128 | 0.757 |
| G0→G2 | 5 | erc721.setApprovalForAll2 | 1.300 | 0.983 |
| G0→G2 | 6 | erc721.transferFrom | 1.882 | 0.983 |

不能把多列/多行的Median相加解释root差值。原始子窗口、Gas、Instance/Store ID均在TIMING.csv，原始root/child业务回执在raw_logs。子调用均真实执行；差异属于包含初始化、WASI、业务和同步关闭的串行夹具，尚未识别波动的CPU/调度/native机制。

## 根export窗口扣除六个不重叠子Invoke的残余

每笔在同一root export区间内，先减六个串行、不重叠的child Invoke，随后对同区块两组残余作直接差。没有把root与children相加；残余包含根Guest工作、VM管理器/host跨调用、子调用退出后trace输出等未细分成本，不能直接命名为Guest计算或GC。

| 对照 | 窗口 | 配对节省Median [95%CI] ms |
|---|---|---:|
| G0→G1 | children_invoke_sum | 4.989 [-3.375, 10.019] |
| G0→G1 | root_export_minus_child_invokes | -7.025 [-9.145, -5.275] |
| G1→G2 | children_invoke_sum | 4.803 [-0.180, 9.620] |
| G1→G2 | root_export_minus_child_invokes | 0.215 [-1.336, 1.790] |
| G0→G2 | children_invoke_sum | 6.556 [-0.592, 15.859] |
| G0→G2 | root_export_minus_child_invokes | -7.566 [-9.261, -4.891] |

Copy相对Fresh的子Invoke合计节省点估计为正、CI跨零；root残余出现额外耗时；这是本轮buyNow整体收益未确认的直接窗口证据。尚未定位额外时间在根Guest、host编解码、诊断输出、GC/调度中的比例，不能认定为Copy memcpy本身变慢。要定位机制需要独立的低开销host syscall/guest函数追踪或减少诊断输出的对照，不在本轮偷偷改变计时协议。
