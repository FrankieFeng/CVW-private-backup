/*
Copyright (C) 2023 Beijing Advanced Innovation Center for Future Blockchain and Privacy Computing (未来区块链与隐私计算高精尖创新中心). All rights reserved.
SPDX-License-Identifier: Apache-2.0
*/
package parallel

import (
	"bufio"
	"chain-performance-test/chainclient"
	"chain-performance-test/datahandler"
	logger "chain-performance-test/log"
	sub "chain-performance-test/subservice"
	"context"
	"fmt"
	"io"
	"math"
	"os"
	"path/filepath"
	"reflect"
	"regexp"
	"sort"
	"strconv"
	"strings"
	"time"

	"chainmaker.org/chainmaker/pb-go/v2/common"
	"chainmaker.org/chainmaker/pb-go/v2/txpool"
	sdk "chainmaker.org/chainmaker/sdk-go/v2"
)

// ContinuousClaimPressureTester 创建持续压测的接口
type ContinuousClaimPressureTester interface {
	ClaimPressureTest(*sdk.ChainClient, bool) (error, []string)
}

func addMaps(m1, m2 map[int64]int64) map[int64]int64 {
	for key, value := range m2 {
		m1[key] += value // 如果键存在，累加值；如果键不存在，初始化为 value
	}
	return m1
}

type ClaimPressureTester struct{}

// PoolDrainTimeoutSeconds 压测结束后等待交易池清空的超时时间（秒）
var PoolDrainTimeoutSeconds = 90

const poolDrainStableRounds = 2

func SetPoolDrainTimeoutSeconds(seconds int) {
	if seconds < 0 {
		seconds = 0
	}
	PoolDrainTimeoutSeconds = seconds
}

func poolRemain(st *txpool.TxPoolStatus) int32 {
	if st == nil {
		return -1
	}
	return st.CommonTxNumInQueue + st.CommonTxNumInPending +
		st.ConfigTxNumInQueue + st.ConfigTxNumInPending
}

// waitTxPoolDrained 轮询各节点交易池，连续两次为空后返回；超时则打日志并继续。
func waitTxPoolDrained(clients []*sdk.ChainClient) {
	timeout := time.Duration(PoolDrainTimeoutSeconds) * time.Second
	fmt.Printf("压测结束，等待交易池清空(timeout=%ds)...\n", PoolDrainTimeoutSeconds)
	logger.Logger.Printf("压测结束，等待交易池清空(timeout=%ds)...\n", PoolDrainTimeoutSeconds)
	if len(clients) == 0 {
		fmt.Println("无可用 client，跳过交易池等待")
		return
	}
	if timeout == 0 {
		fmt.Println("pool drain timeout=0，跳过交易池等待")
		return
	}

	deadline := time.Now().Add(timeout)
	stable := 0
	for {
		totalRemain := int32(0)
		allOk := true
		for i, c := range clients {
			if c == nil {
				continue
			}
			st, err := c.GetPoolStatus()
			if err != nil || st == nil {
				allOk = false
				fmt.Printf("GetPoolStatus client[%d] err=%v\n", i, err)
				logger.Logger.Printf("GetPoolStatus client[%d] err=%v\n", i, err)
				break
			}
			n := poolRemain(st)
			totalRemain += n
			fmt.Printf("client[%d] queue=%d pending=%d configQueue=%d configPending=%d remain=%d\n",
				i, st.CommonTxNumInQueue, st.CommonTxNumInPending,
				st.ConfigTxNumInQueue, st.ConfigTxNumInPending, n)
		}
		if allOk && totalRemain == 0 {
			stable++
			if stable >= poolDrainStableRounds {
				fmt.Println("交易池已清空，继续读日志统计")
				logger.Logger.Println("交易池已清空，继续读日志统计")
				return
			}
		} else {
			stable = 0
		}
		if time.Now().After(deadline) {
			fmt.Printf("等待交易池清空超时(%ds)，继续读日志统计\n", PoolDrainTimeoutSeconds)
			logger.Logger.Printf("等待交易池清空超时(%ds)，继续读日志统计\n", PoolDrainTimeoutSeconds)
			return
		}
		time.Sleep(time.Second)
	}
}

// 定义交易数据结构
type TransactionRunningInfo struct {
	txId                  string
	contractName          string
	contractMethod        string
	RuntimeType           string
	RuntimeContractResult int
	StartTime             int64
	EndTime               int64
	ExecutionTime         float64
}

// 处理日志文件
func getLastTimestamp(logFilePath string) ([]TransactionRunningInfo, int64, int64, int64) {
	// 正则表达式匹配交易信息
	logPattern := regexp.MustCompile(`tx id:(?P<txid>[a-f0-9]+),\s*` +
		`contractName:(?P<contractName>[^,]+),\s*` +
		`contractMethod:(?P<contractMethod>[^,]+),\s*` +
		`runtime type:(?P<runtime_type>\w+),\s*` +
		`runtimeContractResult:(?P<runtimeContractResult>\d+)\s*,\s*` +
		`startTime:(?P<startTime>\d+),\s*` +
		`endTime:(?P<endTime>\d+),\s*` +
		`executionTime:(?P<executionTime>[\d.]+) s`)

	var txData []TransactionRunningInfo
	var minStartTime int64 = 1<<63 - 1 // 设为 int64 最大值
	var maxEndTime int64 = 0
	var totalExecutionTime int64 = 0
	// 打开日志文件
	file, err := os.Open(logFilePath)
	if err != nil {
		fmt.Println("无法打开文件:", logFilePath, "错误:", err)
		return nil, 0, 0, 0
	}
	defer file.Close()
	cnt := 0
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := scanner.Text()
		//vm2.3.1"vm_factory.go:417" vm2.3.7"vm_factory.go:380" vm2.4.0"vm_factory.go:438"
		if strings.Contains(line, "vm_factory.go:438") { // 仅匹配包含特定标识的行

			matches := logPattern.FindStringSubmatch(line)
			if matches != nil {
				//第一个匹配的是安装合约执行的结果，跳过
				if cnt == 0 {
					cnt++
					continue
				}
				// 提取匹配组
				txId := matches[1]
				thisContractName := matches[2]
				thisContractMethod := matches[3]
				runtimeType := matches[4]
				runtimeContractResult, _ := strconv.Atoi(matches[5])
				startTime, _ := strconv.ParseInt(matches[6], 10, 64)
				endTime, _ := strconv.ParseInt(matches[7], 10, 64)
				//这个executionTime是在虚拟机执行的时候直接计算了，保留了6位小数，为了提高计算精度最好还是自己弄
				executionTime, _ := strconv.ParseFloat(matches[8], 64)
				totalExecutionTime += endTime - startTime
				//如果合约执行结果失败跳过
				//if runtimeContractResult != 0 || thisContractName != ContractName || thisContractMethod != contractMethod {
				//	continue
				//}
				if thisContractName != ContractName || thisContractMethod != contractMethod {
					continue
				}
				transaction := TransactionRunningInfo{
					txId:                  txId,
					contractName:          ContractName,
					contractMethod:        contractMethod,
					RuntimeType:           runtimeType,
					RuntimeContractResult: runtimeContractResult,
					StartTime:             startTime,
					EndTime:               endTime,
					ExecutionTime:         executionTime,
				}
				txData = append(txData, transaction)
				// 更新最小开始时间 & 最大结束时间
				if startTime < minStartTime {
					minStartTime = startTime
				}
				if endTime > maxEndTime {
					maxEndTime = endTime
				}
			}
		}
	}

	if len(txData) > 0 && maxEndTime > minStartTime {

	} else {
		fmt.Printf("文件: %s, 没有有效交易数据\n", logFilePath)
	}

	return txData, minStartTime, maxEndTime, totalExecutionTime
}

type GasUsedAnalysis struct {
	AllGasUsed      []int       // 所有gasUsed值的汇总列表
	GasUsedCount    map[int]int // 每个gasUsed值出现的次数
	MaxGasUsed      int         // 最大gasUsed值
	MinGasUsed      int         // 最小gasUsed值
	VariancePercent float64     // 最大值与最小值的误差百分比
}

// 获取gas数据
func analyzeGasUsedLogs(logFilePath string) (*GasUsedAnalysis, error) {
	// 正则表达式匹配tx GasUsed list行
	gasUsedPattern := regexp.MustCompile(`common/tx_helper\.go:\d+\s*` +
		`verifyTx:\s*` +
		`contractName=\s*(?P<contractName>[^,]+),\s*` +
		`contractMethod=\s*(?P<contractMethod>[^,]+),\s*` +
		`tx GasUsed list=\s*\[(?P<gasUsedList>[^\]]+)\]`)

	analysis := &GasUsedAnalysis{
		GasUsedCount: make(map[int]int),
	}

	// 打开日志文件
	file, err := os.Open(logFilePath)
	if err != nil {
		return nil, fmt.Errorf("无法打开文件: %s, 错误: %v", logFilePath, err)
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := scanner.Text()
		matches := gasUsedPattern.FindStringSubmatch(line)
		if matches != nil {
			// 提取gasUsed列表部分
			gasUsedStr := strings.TrimSpace(matches[3])
			gasUsedParts := strings.Split(gasUsedStr, " ")
			thisContractName := matches[1]
			thisContractMethod := matches[2]
			if thisContractName != ContractName || thisContractMethod != contractMethod {
				continue
			}
			// 解析每个gasUsed值
			for _, part := range gasUsedParts {
				if part == "" {
					continue
				}
				gasUsed, err := strconv.Atoi(part)
				if err != nil {
					continue // 跳过无效的数字
				}

				// 添加到汇总列表
				analysis.AllGasUsed = append(analysis.AllGasUsed, gasUsed)

				// 统计出现次数
				analysis.GasUsedCount[gasUsed]++

				// 更新最大值和最小值
				if gasUsed > analysis.MaxGasUsed {
					analysis.MaxGasUsed = gasUsed
				}
				if gasUsed < analysis.MinGasUsed || analysis.MinGasUsed == 0 {
					analysis.MinGasUsed = gasUsed
				}
			}
		}
	}

	// 计算误差百分比
	if analysis.MaxGasUsed != 0 && analysis.MinGasUsed != 0 {
		diff := analysis.MaxGasUsed - analysis.MinGasUsed
		analysis.VariancePercent = (float64(diff) / float64(analysis.MinGasUsed)) * 100
	}

	return analysis, nil
}

func analyzeGasUsedLogs_new(logFilePath string) (*GasUsedAnalysis, error) {
	// 正则表达式匹配日志格式，提取 contractName、contractMethod 和 gas used
	// 注意：使用 `[^\s,]+` 匹配非空格和非逗号的字符，避免 ANSI 颜色代码干扰
	//gasUsedPattern := regexp.MustCompile(
	//	`contract invoke finished.*?contractName:\s*([^\s,]+).*?contractMethod:\s*([^\s,]+).*?` +
	//		`runtimeContractResult:\s*(\d+).*?gas used:\s*(\d+)`,
	//)
	gasUsedPattern := regexp.MustCompile(`tx:([a-f0-9]+),\s*` +
		`contractName:([^,]+),\s*` +
		`contractMethod:([^,]+),\s*` +
		`runtimeContractResult:(\d+)\s*,\s*` +
		`gasUsed:(\d+)`)
	analysis := &GasUsedAnalysis{
		GasUsedCount: make(map[int]int),
	}

	file, err := os.Open(logFilePath)
	if err != nil {
		return nil, fmt.Errorf("无法打开文件: %s, 错误: %v", logFilePath, err)
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	lineCount := 0
	matchCount := 0
	for scanner.Scan() {
		lineCount++
		line := scanner.Text()
		// 匹配日志行
		matches := gasUsedPattern.FindStringSubmatch(line)
		if matches != nil {

			thisContractName := matches[2]
			thisContractMethod := matches[3]
			runtimeContractResult, _ := strconv.Atoi(matches[4])
			gasUsedStr := matches[5]
			if thisContractName != ContractName || thisContractMethod != contractMethod || runtimeContractResult != 0 {
				continue
			}

			// 提取 gasUsed 值
			gasUsed, err := strconv.Atoi(gasUsedStr)
			if err != nil {
				fmt.Printf("警告: 第%d行解析gasUsed失败: %v (原始文本: %s)\n",
					lineCount, err, gasUsedStr)
				continue
			}

			// 更新统计数据
			matchCount++
			analysis.AllGasUsed = append(analysis.AllGasUsed, gasUsed)
			analysis.GasUsedCount[gasUsed]++

			if gasUsed > analysis.MaxGasUsed {
				analysis.MaxGasUsed = gasUsed
			}
			if gasUsed < analysis.MinGasUsed || analysis.MinGasUsed == 0 {
				analysis.MinGasUsed = gasUsed
			}
		}
	}

	fmt.Printf("处理完成: 共扫描%d行, 匹配到%d条gas used记录\n", lineCount, matchCount)

	//if err := scanner.Err(); err != nil {
	//	fmt.Printf("读取文件时出错: %v\n", err)
	//	return nil, fmt.Errorf("读取文件时出错: %v", err)
	//}

	// 计算误差百分比
	if analysis.MaxGasUsed != 0 && analysis.MinGasUsed != 0 {
		diff := analysis.MaxGasUsed - analysis.MinGasUsed
		analysis.VariancePercent = (float64(diff) / float64(analysis.MinGasUsed)) * 100
	}

	return analysis, nil
}

// 处理日志文件
func getLastTimestampMap(logFilePath string) (map[string]TransactionRunningInfo, int64, int64, int64) {
	// 正则表达式匹配交易信息
	logPattern := regexp.MustCompile(`tx id:(?P<txid>[a-f0-9]+),\s*` +
		`contractName:(?P<contractName>[^,]+),\s*` +
		`contractMethod:(?P<contractMethod>[^,]+),\s*` +
		`runtime type:(?P<runtime_type>\w+),\s*` +
		`runtimeContractResult:(?P<runtimeContractResult>\d+)\s*,\s*` +
		`startTime:(?P<startTime>\d+),\s*` +
		`endTime:(?P<endTime>\d+),\s*` +
		`executionTime:(?P<executionTime>[\d.]+) s`)
	txData := make(map[string]TransactionRunningInfo)

	var minStartTime int64 = 1<<63 - 1 // 设为 int64 最大值
	var maxEndTime int64 = 0
	var totalExecutionTime int64 = 0
	// 打开日志文件
	file, err := os.Open(logFilePath)
	if err != nil {
		fmt.Println("无法打开文件:", logFilePath, "错误:", err)
		return nil, 0, 0, 0
	}
	defer file.Close()
	cnt := 0
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := scanner.Text()
		if strings.Contains(line, "vm_factory.go:417") { // 仅匹配包含特定标识的行
			matches := logPattern.FindStringSubmatch(line)
			if matches != nil {
				//第一个匹配的是安装合约执行的结果，跳过
				if cnt == 0 {
					cnt++
					continue
				}
				// 提取匹配组
				txId := matches[1]
				thisContractName := matches[2]
				thisContractMethod := matches[3]
				runtimeType := matches[4]
				runtimeContractResult, _ := strconv.Atoi(matches[5])
				startTime, _ := strconv.ParseInt(matches[6], 10, 64)
				endTime, _ := strconv.ParseInt(matches[7], 10, 64)
				//这个executionTime是在虚拟机执行的时候直接计算了，保留了6位小数，为了提高计算精度最好还是自己弄
				executionTime, _ := strconv.ParseFloat(matches[8], 64)
				totalExecutionTime += endTime - startTime
				//如果合约执行结果失败跳过
				if runtimeContractResult != 0 || thisContractName != ContractName || thisContractMethod != contractMethod {
					continue
				}

				transaction := TransactionRunningInfo{
					txId:                  txId,
					contractName:          ContractName,
					contractMethod:        contractMethod,
					RuntimeType:           runtimeType,
					RuntimeContractResult: runtimeContractResult,
					StartTime:             startTime,
					EndTime:               endTime,
					ExecutionTime:         executionTime,
				}
				txData[txId] = transaction
				// 更新最小开始时间 & 最大结束时间
				if startTime < minStartTime {
					minStartTime = startTime
				}
				if endTime > maxEndTime {
					maxEndTime = endTime
				}
			}
		}
	}

	if len(txData) > 0 && maxEndTime > minStartTime {

	} else {
		fmt.Printf("文件: %s, 没有有效交易数据\n", logFilePath)
	}

	return txData, minStartTime, maxEndTime, totalExecutionTime
}

func copyFile(srcPath, distDir string) error {
	// 获取当前时间，并格式化为 "20060102150405" (YYYYMMDDHHmmss)
	timeStr := time.Now().Format("20060102150405")
	filename := "system.log." + timeStr
	distPath := filepath.Join(distDir, filename)

	// 打开源文件
	srcFile, err := os.Open(srcPath)
	if err != nil {
		return fmt.Errorf("无法打开源文件 %s: %v", srcPath, err)
	}
	defer srcFile.Close()

	// 创建目标文件
	distFile, err := os.Create(distPath)
	if err != nil {
		return fmt.Errorf("无法创建目标文件 %s: %v", distPath, err)
	}
	defer distFile.Close()

	// 复制文件内容
	_, err = io.Copy(distFile, srcFile)
	if err != nil {
		return fmt.Errorf("复制文件失败: %v", err)
	}

	// 确保数据写入磁盘
	err = distFile.Sync()
	if err != nil {
		return fmt.Errorf("写入磁盘失败: %v", err)
	}

	fmt.Printf("文件%s 成功复制到 %s\n", srcPath, distPath)
	logger.Logger.Printf("文件%s 成功复制到 %s\n", srcPath, distPath)
	return nil
}

type NodeGasStat struct {
	Node       string
	MatchCount int
	AvgGas     float64
	MinGasUsed int
	MaxGasUsed int
	GasUsedMap map[int]int
}

func calcAvgGas(analysis *GasUsedAnalysis) float64 {
	if analysis == nil || len(analysis.AllGasUsed) == 0 {
		return 0
	}
	total := 0
	for _, v := range analysis.AllGasUsed {
		total += v
	}
	return float64(total) / float64(len(analysis.AllGasUsed))
}

// evaluateGasConsistency returns whether all nodes are consistent and average gas error percentage.
func evaluateGasConsistency(stats []NodeGasStat) (bool, float64) {
	if len(stats) == 0 {
		return false, 0
	}
	base := stats[0]
	isConsistent := true

	minAvg := math.MaxFloat64
	maxAvg := 0.0
	hasAvg := false
	for _, s := range stats {
		if s.AvgGas > 0 {
			hasAvg = true
			if s.AvgGas < minAvg {
				minAvg = s.AvgGas
			}
			if s.AvgGas > maxAvg {
				maxAvg = s.AvgGas
			}
		}
		if s.MatchCount != base.MatchCount || s.MinGasUsed != base.MinGasUsed || s.MaxGasUsed != base.MaxGasUsed || !reflect.DeepEqual(s.GasUsedMap, base.GasUsedMap) {
			isConsistent = false
		}
	}
	if !hasAvg || minAvg == 0 {
		return isConsistent, 0
	}
	return isConsistent, (maxAvg - minAvg) / minAvg * 100
}

func printGasConsistency(stats []NodeGasStat) {
	isConsistent, errPercent := evaluateGasConsistency(stats)
	fmt.Printf("gas一致性: %t, 本轮节点间误差: %.6f%%\n", isConsistent, errPercent)
	logger.Logger.Printf("gas一致性: %t, 本轮节点间误差: %.6f%%\n", isConsistent, errPercent)
	for _, s := range stats {
		fmt.Printf("节点%s: matched=%d, avgGas=%.2f, min=%d, max=%d\n", s.Node, s.MatchCount, s.AvgGas, s.MinGasUsed, s.MaxGasUsed)
		logger.Logger.Printf("节点%s: matched=%d, avgGas=%.2f, min=%d, max=%d\n", s.Node, s.MatchCount, s.AvgGas, s.MinGasUsed, s.MaxGasUsed)
	}
}

func ClaimTPSCTPSWithSub(pressureTester ContinuousClaimPressureTester,
	clientCreator chainclient.ClientCreator, blockSubscriber sub.BlockSubscriber) error {

	logger.Logger.Println("============ 开始压测 ============")

	countClimb := ThreadNum / 10
	if countClimb == 0 {
		countClimb = 1
	}
	// 设置线程启动时间
	interval := time.Duration(ClimbTime/countClimb) * time.Second

	// 开始压测计时
	//pTimeStart := time.Now()
	//pDateStart := pTimeStart.Format("2006-01-02 15:04:05")

	ctxForTest, cancelForTest := context.WithCancel(context.Background())

	//txIdMap := make(map[int][]string)
	//var totalTxIds []string
	for index := 0; index < ThreadNum; {
		for j := 0; j < 10; j++ {
			// 多节点加压
			for i := 0; i < Clientslen; i++ {
				// 持续的执行压测方法
				// 设置需要等待的协程数量
				k := i
				Wg.Add(1)
				go func(ctx context.Context) {
					defer Wg.Done()
					select {
					case <-ctx.Done():
						// 如果收到取消信号，直接返回不执行任务
						return
					default:
						defer func() {
							if err := recover(); err != nil {
								cancelForTest()
								logger.Logger.Println("Error:", err)
							}
						}()
						//这个Clients1[k]，只是发送client身份而已，跟节点没关系，每个节点都会执行一遍
						//同时需注意在并发时计算的ThreadNum跟设置时设置thread_num的不一样，他是ThreadNum = ConfigurableParameter.PressureParameters.ThreadNum / Clientslen // 单次并发进程数,总并发进程/节点数
						//所以并发顺序执行次数时LoopNum*Clients*Clients*thread_num/Clients=LoopNum*Clients*thread_num
						err, _ := pressureTester.ClaimPressureTest(Clients1[k], false)

						//err, txIds := pressureTester.ClaimPressureTest(Clients1[k], false)
						//totalTxIds = append(totalTxIds, txIds...)
						//if existingTxIds, exists := txIdMap[k]; exists {
						//	txIdMap[k] = append(existingTxIds, txIds...) // 追加新的 txIds
						//} else {
						//	// 如果 k 不存在，则直接存入 txIds
						//	txIdMap[k] = txIds
						//}

						if err != nil {
							cancelForTest()
							fmt.Println("cancel by err:", err)
							logger.Logger.Panicln(err)
						}
					}
				}(ctxForTest)
			}
			index++
			if index >= ThreadNum {
				break
			}
		}
		time.Sleep(interval)
	}
	Wg.Wait()
	cancelForTest()
	waitTxPoolDrained(Clients1)

	// 构建文件名
	originSrcDir := "/home/frankie/mygitprojects/chainmaker-go/build/release/chainmaker-v2.4.0_alpha-wx-org1.chainmaker.org/log/"
	now := time.Now()
	// 格式化时间为文件名中的格式（例如 YYYYMMDDHH）
	timeStr := now.Format("2006010215")
	filename := "system.log." + timeStr

	minStartTime := int64(math.MaxInt64)
	maxEndTime := int64(0)
	lastSrcPath := ""
	txNum := 0
	orgNum := Clientslen
	var totalExecutionTime int64 = 0
	nodeGasStats := make([]NodeGasStat, 0, orgNum)
	for i := 1; i <= orgNum; i++ {
		orgNum := "org" + strconv.Itoa(i)                          // 生成 orgX
		srcDir := strings.Replace(originSrcDir, "org1", orgNum, 1) // 替换 org1 为 orgX
		srcPath := filepath.Join(srcDir, filename)

		currentTxData, currentMinStartTime, currentMaxEndTime, currentTotalExecutionTime := getLastTimestamp(srcPath)
		gasUsedAnalysis, _ := analyzeGasUsedLogs_new(srcPath)
		currentTxNum := len(currentTxData)
		errorNum := 0
		for _, tx := range currentTxData {
			if tx.RuntimeContractResult != 0 {
				errorNum++
			}
		}
		fmt.Printf("errorNum: %d\n", errorNum)
		fmt.Println(currentMinStartTime, currentMaxEndTime, currentTxNum, float64(currentTxNum)/(float64(currentMaxEndTime-currentMinStartTime)/1e9))

		fmt.Printf("minGasUsed: %d, maxGasUsed: %d, gasUsedVariant: %+v,gasUsedCount: %+v\n", gasUsedAnalysis.MinGasUsed, gasUsedAnalysis.MaxGasUsed, gasUsedAnalysis.VariancePercent, gasUsedAnalysis.GasUsedCount)
		nodeGasStats = append(nodeGasStats, NodeGasStat{
			Node:       orgNum,
			MatchCount: len(gasUsedAnalysis.AllGasUsed),
			AvgGas:     calcAvgGas(gasUsedAnalysis),
			MinGasUsed: gasUsedAnalysis.MinGasUsed,
			MaxGasUsed: gasUsedAnalysis.MaxGasUsed,
			GasUsedMap: gasUsedAnalysis.GasUsedCount,
		})
		//fmt.Printf("gasUsedCount: %+v\n", gasUsedAnalysis)

		//fmt.Println(currentMinStartTime, currentMaxEndTime, currentTxNum, currentTotalExecutionTime, float64(currentTxNum)/float64(currentTotalExecutionTime)/1e9)
		// 找到最大的 maxEndTime
		if currentMaxEndTime > maxEndTime {
			maxEndTime = currentMaxEndTime
			lastSrcPath = srcPath
		}
		if currentMinStartTime < minStartTime {
			minStartTime = currentMinStartTime
		}
		txNum = txNum + currentTxNum
		totalExecutionTime = totalExecutionTime + currentTotalExecutionTime
	}
	printGasConsistency(nodeGasStats)
	distDir := "/home/frankie/mygitprojects/chainmaker-test-toolkit-master/chainmaker-performance-test/log/experimentlog"
	copyFile(lastSrcPath, distDir)
	//timeStart := pTimeStart
	timeStart := time.Unix(0, minStartTime)
	dateStart := timeStart.Format("2006-01-02 15:04:05")
	timeEnd := time.Unix(0, maxEndTime)
	dateEnd := timeEnd.Format("2006-01-02 15:04:05")
	//fmt.Println(timeStart.UnixNano(), timeEnd.UnixNano())
	// txNum交易数
	//txNum := LoopNum * ThreadNum * Clientslen*Clientslen
	// txNum为实际虚拟机执行成功的交易数,如果全都正常完成的话等于loop_num*thread_num* Clientslen*Clientslen
	count := float64(txNum)
	timeResult := float64(maxEndTime-minStartTime) / 1e9

	datahandler.TestResult.TxNum = txNum
	datahandler.TestResult.TPS = count / timeResult

	logger.Logger.Printf("并发数: %d\n", ThreadNum)
	logger.Logger.Println("timeStart:", dateStart, timeStart.UnixNano(), "timeEnd:", dateEnd, timeEnd.UnixNano())
	logger.Logger.Println("txNum:", txNum, "totalExecutionTime:", strconv.FormatFloat(timeResult, 'g', 30, 32)+" s",
		"TPS:", count/timeResult)
	//totalTimeMap := make(map[int64]int64)
	//for key, _ := range txIdMap {
	//	addMaps(totalTimeMap, checkTime(Clients1[key], totalTxIds))
	//}
	//var minKey, maxKey int64
	//first := true
	//
	//// 遍历 map
	//for k := range totalTimeMap {
	//	if first {
	//		minKey, maxKey = k, k
	//		first = false
	//	} else {
	//		if k < minKey {
	//			minKey = k
	//		}
	//		if k > maxKey {
	//			maxKey = k
	//		}
	//	}
	//}
	//fmt.Println(minKey, maxKey, float64(txNum)/(float64(maxKey-minKey)), "timeStart:", dateStart, timeStart.UnixNano(), "timeEnd:", dateEnd, timeEnd.UnixNano())
	fmt.Println("timeStart:", dateStart, timeStart.UnixNano(), "timeEnd:", dateEnd, timeEnd.UnixNano(), "totalExecutionTime:", strconv.FormatFloat(timeResult, 'g', 30, 32)+" s",
		"TPS:", count/timeResult)
	return nil
}

func normalTPSTest(pressureTester ContinuousClaimPressureTester) error {
	logger.Logger.Println("============ 开始非并发、顺序执行压测 ============")

	for i := 0; i < Clientslen; i++ {
		k := i
		//这个Clients1[k]，只是发送client身份而已，跟节点没关系，每个节点都会执行一遍
		//所以非并发顺序执行次数是LoopNum*Clients*Clients
		err, _ := pressureTester.ClaimPressureTest(Clients1[k], true)
		if err != nil {
			fmt.Println("cancel by err:", err)
			logger.Logger.Panicln(err)
			break
		}
	}
	waitTxPoolDrained(Clients1)
	// 构建文件名
	originSrcDir := "/home/frankie/mygitprojects/chainmaker-go/build/release/chainmaker-v2.4.0_alpha-wx-org1.chainmaker.org/log/"
	now := time.Now()
	// 格式化时间为文件名中的格式（例如 YYYYMMDDHH）
	timeStr := now.Format("2006010215")
	filename := "system.log." + timeStr

	minStartTime := int64(math.MaxInt64)
	maxEndTime := int64(0)
	lastSrcPath := ""
	txNum := 0
	orgNum := Clientslen
	var totalExecutionTime int64 = 0
	nodeGasStats := make([]NodeGasStat, 0, orgNum)
	for i := 1; i <= orgNum; i++ {
		orgNum := "org" + strconv.Itoa(i)                          // 生成 orgX
		srcDir := strings.Replace(originSrcDir, "org1", orgNum, 1) // 替换 org1 为 orgX
		srcPath := filepath.Join(srcDir, filename)

		currentTxData, currentMinStartTime, currentMaxEndTime, currentTotalExecutionTime := getLastTimestamp(srcPath)
		gasUsedAnalysis, _ := analyzeGasUsedLogs_new(srcPath)
		currentTxNum := len(currentTxData)
		errorNum := 0
		for _, tx := range currentTxData {
			if tx.RuntimeContractResult != 0 {
				errorNum++
			}
		}
		fmt.Printf("errorNum: %d\n", errorNum)
		fmt.Println(currentMinStartTime, currentMaxEndTime, currentTxNum, float64(currentTxNum)/(float64(currentMaxEndTime-currentMinStartTime)/1e9))
		fmt.Printf("minGasUsed: %d, maxGasUsed: %d, gasUsedVariant: %+v,gasUsedCount: %+v\n", gasUsedAnalysis.MinGasUsed, gasUsedAnalysis.MaxGasUsed, gasUsedAnalysis.VariancePercent, gasUsedAnalysis.GasUsedCount)
		nodeGasStats = append(nodeGasStats, NodeGasStat{
			Node:       orgNum,
			MatchCount: len(gasUsedAnalysis.AllGasUsed),
			AvgGas:     calcAvgGas(gasUsedAnalysis),
			MinGasUsed: gasUsedAnalysis.MinGasUsed,
			MaxGasUsed: gasUsedAnalysis.MaxGasUsed,
			GasUsedMap: gasUsedAnalysis.GasUsedCount,
		})

		//fmt.Println(currentMinStartTime, currentMaxEndTime, currentTxNum, currentTotalExecutionTime, float64(currentTxNum)/float64(currentTotalExecutionTime)/1e9)
		// 找到最大的 maxEndTime
		if currentMaxEndTime > maxEndTime {
			maxEndTime = currentMaxEndTime
			lastSrcPath = srcPath
		}
		if currentMinStartTime < minStartTime {
			minStartTime = currentMinStartTime
		}
		txNum = txNum + currentTxNum
		totalExecutionTime = totalExecutionTime + currentTotalExecutionTime
	}
	printGasConsistency(nodeGasStats)
	distDir := "/home/frankie/mygitprojects/chainmaker-test-toolkit-master/chainmaker-performance-test/log/experimentlog"
	copyFile(lastSrcPath, distDir)

	timeStart := time.Unix(0, minStartTime)
	dateStart := timeStart.Format("2006-01-02 15:04:05")
	timeEnd := time.Unix(0, maxEndTime)
	dateEnd := timeEnd.Format("2006-01-02 15:04:05")
	count := float64(txNum)
	timeResult := float64(totalExecutionTime) / 1e9

	datahandler.TestResult.TxNum = txNum
	datahandler.TestResult.TPS = count / timeResult

	logger.Logger.Printf("并发数: %d\n", ThreadNum)
	logger.Logger.Println("timeStart:", dateStart, timeStart.UnixNano(), "timeEnd:", dateEnd, timeEnd.UnixNano())
	logger.Logger.Println("txNum:", txNum, "totalExecutionTime:", strconv.FormatFloat(timeResult, 'g', 30, 32)+" s",
		"TPS:", count/timeResult)
	fmt.Println("timeStart:", dateStart, timeStart.UnixNano(), "timeEnd:", dateEnd, timeEnd.UnixNano(), "totalExecutionTime:", strconv.FormatFloat(timeResult, 'g', 30, 32)+" s",
		"TPS:", count/timeResult)
	return nil
}

func (p ClaimPressureTester) ClaimPressureTest(client *sdk.ChainClient, withSyncResult bool) (error, []string) {
	txIds := []string{}
	for i := 0; i < LoopNum; i++ {
		err, resp := UserContractClaimInvoke(client, contractMethod, withSyncResult, datahandler.ParametersList.ContractParametersList.ContractFunctionParametersMap)
		if err != nil {
			return err, txIds
		}
		txIds = append(txIds, resp.TxId)
		time.Sleep(time.Duration(SleepTime) * time.Millisecond)
	}
	return nil, txIds
}

// UserContractClaimInvoke 调用合约
func UserContractClaimInvoke(client *sdk.ChainClient, method string, withSyncResult bool, FunctionParametersMap map[string]string) (error, *common.TxResponse) {

	params := RandParams(FunctionParametersMap)
	resp, err := chainclient.InvokeUserContract(client, ContractName, method, "", params, withSyncResult)
	if err != nil {
		return err, resp
	}
	return nil, resp
}

func checkTime(client *sdk.ChainClient, txIds []string) map[int64]int64 {
	timeMap := map[int64]int64{}
	resultMap := map[string]int64{}
	wrongMap := map[string]int64{}
	for _, value := range txIds {
		transactionInfo, err := client.GetTxByTxId(value)

		if err != nil {
			wrongMap["err"] += 1
		} else {

			resultMap[string(transactionInfo.Transaction.Result.ContractResult.Result)] += 1
			tempTime := transactionInfo.BlockTimestamp
			if tempvalue, exist := timeMap[tempTime]; exist {
				timeMap[tempTime] = tempvalue + 1
			} else {
				timeMap[tempTime] = 1
			}

		}
	}
	fmt.Println(resultMap)
	return timeMap
}

// VmPoolGrowEvent 实例池扩容/缩容日志事件（来自 vm_pool.go）。
type VmPoolGrowEvent struct {
	Timestamp   string
	EventType   string // grow_size | pool_grows | pool_shrinks
	ContractKey string
	GrowSize    int
	CurrentSize int // 未知时为 -1
	RawLine     string
}

var (
	vmPoolGrowSizePattern = regexp.MustCompile(`vm pool grow size = (\d+)`)
	vmPoolGrowsPattern    = regexp.MustCompile(`\[([^\]]+)\] vm pool grows by (\d+), the current size is (\d+)`)
	vmPoolShrinkPattern   = regexp.MustCompile(`\[([^\]]+)\] vm pool shrinks by (\d+), the current size is (\d+)`)
	vmPoolLogTimePattern  = regexp.MustCompile(`^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)`)
)

func parseVmPoolGrowEvent(line string) (VmPoolGrowEvent, bool) {
	ts := ""
	if m := vmPoolLogTimePattern.FindStringSubmatch(line); m != nil {
		ts = m[1]
	}

	if m := vmPoolGrowsPattern.FindStringSubmatch(line); m != nil {
		grow, _ := strconv.Atoi(m[2])
		cur, _ := strconv.Atoi(m[3])
		return VmPoolGrowEvent{
			Timestamp:   ts,
			EventType:   "pool_grows",
			ContractKey: m[1],
			GrowSize:    grow,
			CurrentSize: cur,
			RawLine:     strings.TrimSpace(line),
		}, true
	}
	if m := vmPoolShrinkPattern.FindStringSubmatch(line); m != nil {
		shrink, _ := strconv.Atoi(m[2])
		cur, _ := strconv.Atoi(m[3])
		return VmPoolGrowEvent{
			Timestamp:   ts,
			EventType:   "pool_shrinks",
			ContractKey: m[1],
			GrowSize:    shrink,
			CurrentSize: cur,
			RawLine:     strings.TrimSpace(line),
		}, true
	}
	if m := vmPoolGrowSizePattern.FindStringSubmatch(line); m != nil {
		grow, _ := strconv.Atoi(m[1])
		return VmPoolGrowEvent{
			Timestamp:   ts,
			EventType:   "grow_size",
			GrowSize:    grow,
			CurrentSize: -1,
			RawLine:     strings.TrimSpace(line),
		}, true
	}
	return VmPoolGrowEvent{}, false
}

// AnalyzeVmPoolGrowLogs 按日志顺序解析各节点 system.log 中的实例池增长/缩容过程。
func AnalyzeVmPoolGrowLogs(logFilePath string) ([]VmPoolGrowEvent, error) {
	file, err := os.Open(logFilePath)
	if err != nil {
		return nil, fmt.Errorf("无法打开日志文件 %s: %v", logFilePath, err)
	}
	defer file.Close()

	var events []VmPoolGrowEvent
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := scanner.Text()
		if !strings.Contains(line, "vm pool grow") &&
			!strings.Contains(line, "vm pool grows") &&
			!strings.Contains(line, "vm pool shrinks") {
			continue
		}
		if ev, ok := parseVmPoolGrowEvent(line); ok {
			events = append(events, ev)
		}
	}
	if err := scanner.Err(); err != nil {
		return nil, fmt.Errorf("读取日志文件出错: %v", err)
	}
	return events, nil
}

const chainmakerSystemLogOriginDir = "/home/frankie/mygitprojects/chainmaker-go/build/release/chainmaker-v2.4.0_alpha-wx-org1.chainmaker.org/log/"

// InstanceExportMemoryPeak 单个 wasmer 实例在压测期间观测到的 exportMemory 峰值。
type InstanceExportMemoryPeak struct {
	InstanceID       string
	MaxDataSizeBytes uint64
	MaxPages         uint64
	Observations     int
}

// NodeExportMemoryMaxSummary 单个节点 system.log 中各实例 exportMemory 峰值汇总。
type NodeExportMemoryMaxSummary struct {
	Node           string
	LogPath        string
	Instances      []InstanceExportMemoryPeak
	TotalSamples   int
	GlobalMaxBytes uint64
	GlobalMaxPages uint64
	ReadError      string // 非空表示读取/解析该节点日志失败
}

// parseExportMemoryLine 解析 runtime.go Debugf 行：
// instance id: %s, ... exportMemory datasize %d字节 %d页
func parseExportMemoryLine(line string) (instanceID string, dataSizeBytes, pages uint64, ok bool) {
	if !strings.Contains(line, "exportMemory datasize") {
		return "", 0, 0, false
	}
	idIdx := strings.Index(line, "instance id: ")
	if idIdx < 0 {
		return "", 0, 0, false
	}
	rest := line[idIdx+len("instance id: "):]
	commaIdx := strings.Index(rest, ",")
	if commaIdx < 0 {
		return "", 0, 0, false
	}
	instanceID = strings.TrimSpace(rest[:commaIdx])

	dsIdx := strings.Index(line, "exportMemory datasize ")
	if dsIdx < 0 {
		return "", 0, 0, false
	}
	tail := strings.TrimSpace(line[dsIdx+len("exportMemory datasize "):])
	n, err := fmt.Sscanf(tail, "%d字节 %d页", &dataSizeBytes, &pages)
	if err != nil || n != 2 {
		return "", 0, 0, false
	}
	return instanceID, dataSizeBytes, pages, true
}

// AnalyzeExportMemoryMaxPerInstance 扫描日志，按 instance id 统计 exportMemory 最大字节数/页数。
func AnalyzeExportMemoryMaxPerInstance(logFilePath string) (map[string]*InstanceExportMemoryPeak, int, error) {
	file, err := os.Open(logFilePath)
	if err != nil {
		return nil, 0, fmt.Errorf("无法打开日志文件 %s: %v", logFilePath, err)
	}
	defer file.Close()

	peaks := make(map[string]*InstanceExportMemoryPeak)
	totalSamples := 0
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		instanceID, dataSizeBytes, pages, ok := parseExportMemoryLine(scanner.Text())
		if !ok {
			continue
		}
		totalSamples++
		peak, exists := peaks[instanceID]
		if !exists {
			peaks[instanceID] = &InstanceExportMemoryPeak{
				InstanceID:       instanceID,
				MaxDataSizeBytes: dataSizeBytes,
				MaxPages:         pages,
				Observations:     1,
			}
			continue
		}
		peak.Observations++
		if dataSizeBytes > peak.MaxDataSizeBytes {
			peak.MaxDataSizeBytes = dataSizeBytes
			peak.MaxPages = pages
		}
	}
	if err := scanner.Err(); err != nil {
		return nil, totalSamples, fmt.Errorf("读取日志文件出错: %v", err)
	}
	return peaks, totalSamples, nil
}

func buildNodeExportMemorySummary(node, logPath string, peaks map[string]*InstanceExportMemoryPeak, totalSamples int) NodeExportMemoryMaxSummary {
	summary := NodeExportMemoryMaxSummary{
		Node:         node,
		LogPath:      logPath,
		TotalSamples: totalSamples,
	}
	for _, peak := range peaks {
		summary.Instances = append(summary.Instances, *peak)
		if peak.MaxDataSizeBytes > summary.GlobalMaxBytes {
			summary.GlobalMaxBytes = peak.MaxDataSizeBytes
			summary.GlobalMaxPages = peak.MaxPages
		}
	}
	sort.Slice(summary.Instances, func(i, j int) bool {
		return summary.Instances[i].InstanceID < summary.Instances[j].InstanceID
	})
	return summary
}

// CollectExportMemoryMaxStatsFromChainLogs 读取各 org 节点当前小时的 system.log，统计每个实例的最大 exportMemory。
func CollectExportMemoryMaxStatsFromChainLogs() []NodeExportMemoryMaxSummary {
	timeStr := time.Now().Format("2006010215")
	filename := "system.log." + timeStr
	orgNum := Clientslen
	if orgNum <= 0 {
		orgNum = 1
	}

	summaries := make([]NodeExportMemoryMaxSummary, 0, orgNum)
	for i := 1; i <= orgNum; i++ {
		node := "org" + strconv.Itoa(i)
		srcDir := strings.Replace(chainmakerSystemLogOriginDir, "org1", node, 1)
		srcPath := filepath.Join(srcDir, filename)

		peaks, totalSamples, err := AnalyzeExportMemoryMaxPerInstance(srcPath)
		if err != nil {
			summaries = append(summaries, NodeExportMemoryMaxSummary{
				Node:      node,
				LogPath:   srcPath,
				ReadError: err.Error(),
			})
			continue
		}
		summaries = append(summaries, buildNodeExportMemorySummary(node, srcPath, peaks, totalSamples))
	}
	return summaries
}

func writeExportMemoryLine(w io.Writer, line string) {
	_, _ = fmt.Fprintln(w, line)
}

// WriteExportMemoryMaxStatsReport 将各节点不同实例数及 exportMemory 峰值写入 w（不输出到终端）。
func WriteExportMemoryMaxStatsReport(w io.Writer, round int, summaries []NodeExportMemoryMaxSummary) {
	writeExportMemoryLine(w, fmt.Sprintf("[exportMemory] round=%d begin", round))

	if len(summaries) == 0 {
		writeExportMemoryLine(w, fmt.Sprintf("[exportMemory] round=%d no node logs analyzed", round))
		writeExportMemoryLine(w, fmt.Sprintf("[exportMemory] round=%d end", round))
		return
	}

	var roundDistinctTotal int
	for _, summary := range summaries {
		if summary.ReadError != "" {
			writeExportMemoryLine(w, fmt.Sprintf("[exportMemory] round=%d node=%s log=%s read_failed=%s",
				round, summary.Node, summary.LogPath, summary.ReadError))
			continue
		}
		distinct := len(summary.Instances)
		roundDistinctTotal += distinct
		writeExportMemoryLine(w, fmt.Sprintf("[exportMemory] round=%d node=%s distinct_instance_count=%d samples=%d log=%s",
			round, summary.Node, distinct, summary.TotalSamples, summary.LogPath))

		if summary.TotalSamples == 0 {
			writeExportMemoryLine(w, fmt.Sprintf("[exportMemory] round=%d node=%s note=no matching exportMemory lines (ensure vm-wasmer runtime.go logs exportMemory datasize at INFO)",
				round, summary.Node))
			continue
		}

		writeExportMemoryLine(w, fmt.Sprintf("[exportMemory] round=%d node=%s global_max_bytes=%d global_max_pages=%d",
			round, summary.Node, summary.GlobalMaxBytes, summary.GlobalMaxPages))

		for _, inst := range summary.Instances {
			writeExportMemoryLine(w, fmt.Sprintf("[exportMemory] round=%d node=%s instance_id=%s max_datasize_bytes=%d max_pages=%d observations=%d",
				round, summary.Node, inst.InstanceID, inst.MaxDataSizeBytes, inst.MaxPages, inst.Observations))
		}
	}

	writeExportMemoryLine(w, fmt.Sprintf("[exportMemory] round=%d summary distinct_instance_total_across_nodes=%d",
		round, roundDistinctTotal))
	writeExportMemoryLine(w, fmt.Sprintf("[exportMemory] round=%d end", round))
}

// LogExportMemoryMaxStats 兼容旧调用：写入压测 logger（不写终端逐条明细）。
func LogExportMemoryMaxStats(round int, summaries []NodeExportMemoryMaxSummary) {
	if logger.Logger == nil {
		return
	}
	var b strings.Builder
	WriteExportMemoryMaxStatsReport(&b, round, summaries)
	for _, line := range strings.Split(strings.TrimSuffix(b.String(), "\n"), "\n") {
		if line != "" {
			logger.Logger.Println(line)
		}
	}
}
