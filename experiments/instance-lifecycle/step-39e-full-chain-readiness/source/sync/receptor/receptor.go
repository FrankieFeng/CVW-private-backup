/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package receptor

import (
	"context"
	"fmt"
	"math"
	"sync/atomic"
	"time"

	"chainmaker.org/chainmaker/localconf/v2"
	"chainmaker.org/chainmaker/sync/v2/setting"

	"chainmaker.org/chainmaker/pb-go/v2/store"
	"chainmaker.org/chainmaker/protocol/v2"
	"chainmaker.org/chainmaker/sync/v2/internal/controller"
	"chainmaker.org/chainmaker/sync/v2/internal/errors"
	"chainmaker.org/chainmaker/sync/v2/types"
	"github.com/gogo/protobuf/proto"
)

const (
	//receptorStateInit the default state
	receptorStateInit int32 = iota
	//receptorStateStarting indicates the receptor is starting up.
	receptorStateStarting
	//receptorStateStarted indicates the receptor has been activated
	receptorStateStarted
	//receptorStatePausing indicates the receptor is executing pause
	receptorStatePausing
	//receptorStatePaused indicates the receptor has been paused
	receptorStatePaused
	//receptorStateStopped indicates the receptor has been stopped
	receptorStateStopped
)

var (
	//作为一个唤醒信号
	wakeUpSg            = newStreamGroup(0, streamConf{})
	defaultTimeout      = 2 * time.Second
	errNoAvailableNodes = fmt.Errorf("no available nodes")
)

type receptor struct {
	//state the state of the receptor
	state int32
	//heightWait the height to be synchronized
	heightWait uint64
	//withRWSet whether the received data has a read-write set
	withRWSet   bool
	blockOut    chan *Block
	informer    types.NodeInformer
	ledgerCache protocol.LedgerCache
	transport   *transport
	//endPool caches the endpoints information.
	endPool *endpointPool
	timeout time.Duration //the timeout of the connection
	//streamList  caches the stream group
	streamList *streamLinkedListLocked
	//stopCh pass stop signal
	stopCh chan struct{}
	//wg used to manage sub go routines.
	wg *controller.GoRoutineGroup
	// conf user configuration items
	conf *localconf.SyncConfig
	//adjustCh transmit node information change signal.
	adjustCh chan types.Event
	//pauseCh pass a signal that triggers the program to pause
	pauseCh chan struct{}
	//pauseCompleteCh pass a signal that the program has been paused completely.
	pauseCompleteCh chan struct{}
	// mergeBuf        []byte
	logger protocol.Logger
	//fragmentMerger used to merge block data fragments
	fragmentMerger types.Merger
	// reuse cache when merge block fragments serially.
	buffer *types.Buffer
	config *Config
	// overLoop pass a signal causes the loop logic to jump out.
	overLoop <-chan struct{}
}

// NewBlockReceptor create receptor with the config.
func NewBlockReceptor(conf *Config) types.Receptor {
	conf.complete()
	timeout := defaultTimeout
	if conf.ExposeConf.ConnTimeoutScale > 0 {
		timeout = time.Millisecond * time.Duration(conf.ExposeConf.ConnTimeoutScale)
	}

	transport := newTransport(conf.Transport, conf.Logger)
	r := &receptor{
		withRWSet:       conf.WithRWSet,
		blockOut:        make(chan *Block, conf.blockChannelSize),
		informer:        newNodeInformer(conf.Informer),
		ledgerCache:     conf.LedgerCache,
		endPool:         newEndpointPool(transport, conf.Logger),
		streamList:      newStreamLinkedListLocked(),
		stopCh:          make(chan struct{}),
		pauseCh:         make(chan struct{}, 1),
		pauseCompleteCh: make(chan struct{}, 1),
		wg:              controller.NewGoRoutineGroup(),
		conf:            conf.ExposeConf,
		adjustCh:        make(chan types.Event, 4),
		logger:          conf.Logger,
		fragmentMerger:  conf.FragmentMerger,
		buffer:          types.NewBuffer(1024),
		config:          conf,
		transport:       transport,
		timeout:         timeout,
	}
	r.logger.Infof("receptor config: %s", conf.String())
	return r
}

// Start the receptor.
// Only receptor in the initial state can be successfully started.
// otherwise, an error will be returned.
// The receptor is marked as starting during startup, and get the block height of the local ledger.
// Then initialize a stream group with the required endpoint information.
// Start a goroutine to monitor endpoint information changes
// and a goroutine to fetch block from the stream group.
// Finally change the status to started.
func (r *receptor) Start() error {
	if !atomic.CompareAndSwapInt32(&r.state, receptorStateInit, receptorStateStarting) {
		return fmt.Errorf("receptor already started")
	}
	r.logger.Info("receptor is starting")
	curH, err := r.ledgerCache.CurrentHeight()
	if err != nil {
		atomic.StoreInt32(&r.state, receptorStateInit)
		return err
	}
	r.overLoop = r.triggerJumpOut()
	r.heightWait = curH + 1
	r.init()
	r.wg.Run(r.watchNodeChange)
	r.wg.Run(r.fetchBlock)
	atomic.StoreInt32(&r.state, receptorStateStarted)
	r.logger.Info("receptor started")
	return nil
}

// Stop the receptor
// Only receptor in the started state can be successfully stopped,
// otherwise, an error will be returned.
// Trigger stop signal and wait for all goroutines to finish.
// Clear the connection pool and endpoint pool.
func (r *receptor) Stop() error {
	state := atomic.LoadInt32(&r.state)
	if state != receptorStateStarted && state != receptorStatePaused {
		return fmt.Errorf("receptor state[%d] can't be stopped", state)
	}
	if !atomic.CompareAndSwapInt32(&r.state, state, receptorStateStopped) {
		return fmt.Errorf("receptor stopped failed")
	}
	r.logger.Info("receptor is stopping")
	close(r.stopCh)
	//唤醒等待的cond
	r.putStreamGroup(wakeUpSg)
	r.wg.Wait()
	//缓存池清理
	r.endPool.clearAll()
	r.logger.Info("receptor stopped")
	return nil
}

// watchNodeChange monitors endpoint information changes.
// If an add event is received, add the endpoint to the endpoint pool and trigger a adjust signal.
// If an delete event is received, remove the endpoint from endpoint pool,
// and close the connection with the endpoint and trigger a adjust signal.
// If an update event is received, update the endpoint in the endpoint pool only.
func (r *receptor) watchNodeChange() {
	defer func() {
		r.logger.Info("watch node change exit")
	}()
	watcher := r.informer.Watch()
	for {
		select {
		case <-r.stopCh:
			watcher.Stop()
			return
		case e, ok := <-watcher.ResultChan():
			if !ok {
				return
			}
			// long silence event，no events received for a long time
			// it may be that there are indeed no events or there is no event notification
			// because the height of the node has not changed which may cause the fetchBlock process to block
			// due to waiting for an available stream group.
			// one case: sync block from one node with unchanged height, then the stream group becomes
			// unavailable due to network problems and wait for a new stream group, but the node was not offline，
			// there is no event notification due to the unchanged height, and no new stream group is
			// established, so it(fetchBlock) remains blocked.
			// add the long silence event here to avoid this situation.
			if e.EventType() == eventTypeLongSilence {
				r.notifyAdjustStream(e)
				continue
			}

			inform := e.EventNode()
			if !r.isPreferNode(inform.Id) {
				continue
			}
			switch e.EventType() {
			case types.EventAddNode: //添加
				r.logger.Infof("add node: %v\n", inform)
				r.endPool.AddEndpoint(inform.Id, blockState{
					height:        inform.Height,
					archiveHeight: inform.ArchiveHeight,
				})
			case types.EventUpdateNode: //更新
				// fmt.Printf("update node: %+v\n", *inform)
				r.endPool.UpdateEndpoint(inform.Id, blockState{
					height:        inform.Height,
					archiveHeight: inform.ArchiveHeight,
				})
			case types.EventDelNode: //删除 有延迟，如果精确可以从registry中再查询一下
				r.logger.Infof("delete node: %v\n", inform)
				r.endPool.MarkDead(inform.Id)
			}
			r.notifyAdjustStream(e)
		}
	}
}

// init the stream group. it will be called when the receptor starts or waiting for a stream group to appear.
// fetch did not obtain a valid stream group and waited， init will be called when a node is added or updated
// or timing detection to prevent blocking.
func (r *receptor) init() {
	infos := r.informer.List()
	for _, info := range infos {
		if r.isPreferNode(info.Info().GetId()) {
			r.endPool.AddEndpoint(info.Info().Id, blockState{
				height:        info.Info().Height,
				archiveHeight: info.Info().ArchiveHeight,
			})
		}
	}
	r.initStreamWithHeight(r.heightWait)
}

// putStreamGroup put the streamGroup "sg" to streamList and wake up the waiter.
func (r *receptor) putStreamGroup(sg *streamGroup) {
	r.streamList.Push(sg)
}

// fetchBlock the main logic to obtain the blocks from the remote.
// Initially, a push stream group will be constructed.
// During the work process, the push stream group needs to be adjusted in the following situations:
// 1. stream in the stream group is unavailable
// 2. the addition of many new nodes leads to the need to expand the stream group.
// But up to two stream groups can be maintained at the same time.
//
// nolint
func (r *receptor) fetchBlock() {
	var (
		node         *streamLinkedNode
		endHeight    uint64
		change              = true
		adjustHeight uint64 = math.MaxUint64
		checker             = newStreamChecker(5)
		reset               = func() {
			endHeight = math.MaxUint64
			adjustHeight = math.MaxUint64
		}
		pause = func() {
			r.streamList.ClearAll()
			r.logger.Infof("handle paused sync, next height [%d]", r.heightWait)
			select {
			case r.pauseCompleteCh <- struct{}{}:
			default:
			}
		}
	)
	r.logger.Infof("begin to fetch block, wait height [%d]", r.heightWait)
	defer func() {
		r.logger.Infof("exit fetch block, wait height [%d]", r.heightWait)
		close(r.blockOut)
	}()
	for {

		select {
		case <-r.stopCh:
			return
		default:
		}
		//change means stream group has been changed, need to change a new one.
		if change {
			reset()
			if node != nil {
				r.streamList.Remove(node)
				node = nil
			}
			for {
				select {
				case <-r.stopCh:
					return
				case <-r.pauseCh:
					pause()
				default:
				}
				r.logger.Infof("wait for new stream group to be created at [%d]", r.heightWait)
				// if there are no elements in the list, wait.
				node = r.streamList.Front()
				r.logger.Infof("new stream group has been created at [%d], len [%d]",
					r.heightWait, node.sg.len())
				//if sg is wakeUpSg means just waking up the process,
				// such as process need to been pause or stop.
				if node.sg == wakeUpSg {
					continue
				}
				break
			}
			if !r.isRunning() {
				change = true
				continue
			}
			//Because we only maintain at most two stream groups,
			//each switch to a new stream group requires adjustment detection.
			//If only one stream group. Need to detect whether the stream group needs to be adjusted or expanded.
			if node.Next() == nil {
				if node.sg.hasInvalidStream() {
					for _, st := range node.sg.invalidStreams() {
						height := st.heightReceived()
						if height > adjustHeight {
							adjustHeight = height
						}
					}
					r.logger.Debugf("new effective stream group has invalid member,need adjust at[%d]", adjustHeight)
				} else if h := r.checkNeedScaleAt(node.sg); h < adjustHeight {
					adjustHeight = h
					r.logger.Debugf("new effective stream group can be scaled up at[%d]", adjustHeight)
				}
			}
		}
		//如果同步到了最新区块，则等待。。。
		if node.Next() == nil && r.checkUpToHighest() {
			r.logger.Infof("sync to latest height[%d], waiting...", r.heightWait-1)
			if ok, h := r.waitForSync(); ok {
				r.heightWait = h + 1
				r.logger.Infof("new blocks need to be synchronized, wait height[%d]", r.heightWait)
				//如果流组没有同步到当前，认为其不具有再同步能力，则重新生成
				if _, max := node.sg.heightReceived(); max < r.heightWait {
					r.streamList.ClearAll()
					r.initStreamWithHeight(r.heightWait)
					change = true
					continue
				}
			}
		}

		select {
		case <-r.stopCh:
			return
		case <-r.pauseCh: //收到暂停信号，清理掉所有的节点，goroutine hang在等待新node产生
			pause()
			change = true
			continue
		case e := <-r.adjustCh:
			if node.Next() == nil {
				switch e.EventType() {
				case types.EventAddNode:
					if h := r.checkNeedScaleAt(node.sg); h < adjustHeight {
						r.logger.Debugf("stream group can be scaled up at[%d]", h)
						adjustHeight = h
					}
				case types.EventDelNode:
					h := r.checkStreamClosedAt(r.streamList.Back())
					if h < adjustHeight {
						adjustHeight = h + 1
					}
				}
			}
		default:
		}
		//endHeight == math.MaxUint64 means that no next stream group ready.
		//adjustHeight != math.MaxUint64 means that a new stream group needs to be generated
		//Adjust stream group if the block height of the current stream group reaches the adjustHeight.
		//Because if you switch without reaching it, there may be new situations
		//between height differences that need to adjust the group.
		if endHeight == math.MaxUint64 {
			if adjustHeight != math.MaxUint64 {
				min, _ := node.sg.heightReceived()
				r.logger.Debugf("adjust stream group at height [%d], received height [%d], wait height [%d]",
					adjustHeight, min, r.heightWait)
				if min == 0 {
					min = r.heightWait
				}
				if min >= adjustHeight-1 {
					if adjustHeight < r.heightWait {
						adjustHeight = r.heightWait
					}
					hasNew := r.adjustStreamGroup(adjustHeight)
					if adjustHeight == r.heightWait && hasNew {
						adjustHeight = math.MaxUint64
						change = true
						continue
					}
					adjustHeight = math.MaxUint64
				}
			}

			if node.Next() != nil {
				endHeight = node.Next().sg.fromHeight - 1
			}
		}

		blockData := node.sg.FetchAllFragments()
		//同步到最高区块后，通过共识追加区块，将内部缓存的旧数据疏导出去
		if blockData.height < r.heightWait {
			continue
		}
		block := r.handleScatteredData(blockData)

		if block == nil {
			//检测是否流被关闭了
			r.checkStreamClosedAt(node)
			//如果流全部失效的话，需要进行重新组合，可能所有端点不可用
			if len(node.sg.invalidStreams()) == node.sg.len() {
				r.logger.Infof("stream group has been invalid at [%d]", r.heightWait)
				r.streamList.ClearAll()
				r.initStreamWithHeight(r.heightWait)
				change = true
				continue
			}
			if block = r.tryPullBlock(blockData.height, 500*time.Millisecond, 0); block == nil {
				r.logger.Warnf("try to pull block [%d] failed", blockData.height)
				r.streamList.ClearAll()
				change = true
				continue
			}
		}

		r.putBlock(block)
		//有节点丢失块了
		//对于已经构造好下一个流组的情况，对丢失情况不再做处理
		if node.Next() == nil && (len(blockData.diss) > 0 || len(blockData.invalids) > 0 || node.sg.len() == 0) {
			//如果流组不存在流，则进行调整
			needAdjust := node.sg.len() == 0
			for _, id := range blockData.invalids {
				r.logger.Debugf("fetch block [%d], invalid stream[%s]", blockData.height, id)
				node.sg.makeInvalid(id)
				checker.clearRecord(id)
				needAdjust = true
			}
			for _, id := range blockData.diss {
				if checker.check(id, blockData.height) {
					r.logger.Debugf("fetch block [%d], censure stream[%s]", blockData.height, id)
					node.sg.makeInvalid(id)
					checker.clearRecord(id)

					if end := r.endPool.GetEndpoint(id); end != nil {
						end.FailFor(blockData.height, metricTypeGet)
					}
					needAdjust = true
				}
			}
			if needAdjust {
				adjustHeight = r.adjustStreamGroupAt(node)
				// adjustHeight, _ = node.sg.heightReceived()
				r.logger.Debugf("fetch block [%d], need adjust stream group, adjustHeight:[%d]", blockData.height, adjustHeight)
			}
		}
		change = blockData.height == endHeight
	}
}

// handleScatteredData handles the scattered block data.
// If the scattered data is a whole block, it will be merged and stored in the ledger.
// If the scattered data is incomplete, it will try to pull the whole block.
func (r *receptor) handleScatteredData(blockData blockScattered) (block *Block) {
	var err error
	if len(blockData.fragments) == 0 { //推送组中没有流存在
		r.logger.Infof("fetch block [%d], no any fragments", blockData.height)
		block, err = r.loopPull(blockData.height, r.withRWSet)
		if err != nil {
			r.logger.Warnf("no any fragments, pull the whole block[%d] failed: %v", blockData.height, err)
		}
	} else if len(blockData.miss) > 0 {
		r.logger.Infof("fetch block [%d], have fragments miss %+v", blockData.height, blockData.miss)
		block, err = r.loopPull(blockData.height, r.withRWSet)
		if err != nil {
			r.logger.Warnf("miss fragment, pull the whole block[%d] failed: %v", blockData.height, err)
		}
	} else {
		// merge blockData.fragments
		r.logger.Infof("block from slice merge, height = %v", blockData.height)
		block, err = r.mergeBlock(blockData.fragments)
		if err != nil {
			r.logger.Warnf("merge Block[%d] failed: %v", blockData.height, err)
		}
	}
	return
}

// mergeBlock merges the given fragments into a whole block.
// The fragments are merged into a buffer and then parsed into a block.
func (r *receptor) mergeBlock(fragments [][]byte) (*Block, error) {
	// Discard the current buffer.
	r.buffer.Discard()
	// Merge the given fragments into a buffer.
	block, err := r.fragmentMerger.MergeBlockFragmentWithBuffer(r.buffer, fragments)
	if err != nil {
		return nil, err
	}
	// Create a new block with the merged data.
	return newBlock("", block, r.endPool), nil
}

// triggerJumpOut returns a channel that is closed when the receptor is stopped or paused.
func (r *receptor) triggerJumpOut() <-chan struct{} {
	ch := make(chan struct{})
	go func() {
		defer close(ch)
		select {
		case <-r.stopCh:
		case e := <-r.pauseCh: //收到暂停信号，清理掉所有的节点，goroutine hang在等待新node产生
			select {
			case r.pauseCh <- e:
			default:
			}
		}
	}()
	return ch
}

// putBlock put the block into blockOut channel, if blocked，wait for signal to be woken up.
// if the block is nil, it means the program is stopped or paused.
func (r *receptor) putBlock(block *Block) {
	if block == nil {
		select {
		case <-r.overLoop:
			return
		default:
		}
	}

	select {
	case <-r.overLoop:
		return
	case r.blockOut <- block:
		r.logger.Infof("put block[%d] into block watch channel", r.heightWait)
		r.heightWait++
	}
}

// checkUpToHighest check if the local height has reached the maximum height in the remote nodes.
func (r *receptor) checkUpToHighest() bool {
	maxHeight := r.endPool.GetMaxHeight()
	currentHeight, err := r.ledgerCache.CurrentHeight()
	if err != nil {
		r.logger.Warnf("checkUpToHighest to get height failed: %v", err)
		return false
	}
	if r.heightWait > currentHeight+1 {
		currentHeight = r.heightWait - 1
	}
	return currentHeight >= maxHeight
}

// waitForSync wait until new blocks are available to sync or the program stops or pauses.
// The Boolean value returned indicates whether there are new blocks to sync, if has, return true,
// if the program has been stopped or paused return false.
// The returned uint64 value indicates the current height of the local ledger.
func (r *receptor) waitForSync() (bool, uint64) {
	var (
		maxHeight     uint64
		currentHeight uint64
		err           error
		timer         *time.Timer
		waitPeriod    = 5 * time.Second
		loopNum       int
		sentinel      = 8
	)
	if r.conf.WaitPeriodSecondsAfterLatest > 0 {
		waitPeriod = time.Duration(r.conf.WaitPeriodSecondsAfterLatest) * time.Second
	}

	defer func() {
		if timer != nil {
			timer.Stop()
		}
	}()

	for {
		maxHeight = r.endPool.GetMaxHeight()
		currentHeight, err = r.ledgerCache.CurrentHeight()
		if err != nil {
			continue
		}

		if r.heightWait > currentHeight+1 {
			currentHeight = r.heightWait - 1
		}

		r.logger.Infof("wait for sync, currentHeight:[%d], peer max height[%d]", currentHeight, maxHeight)
		if currentHeight >= maxHeight {
			diff := currentHeight - uint64(sentinel)
			if diff > currentHeight { //overflow
				diff = 0
			}
			//If there is no data to be synchronized for a long time, release the resources.
			if sentinel > 0 && (loopNum >= sentinel || r.heightWait <= diff) {
				r.logger.Debugf("wait for a long time to release push streams, sentinel: %d", sentinel)
				if node := r.streamList.Front(); node != nil {
					r.streamList.Remove(node)
				}
				r.buffer.Reset()
				sentinel = 0
			}

			if timer == nil {
				timer = time.NewTimer(waitPeriod)
			} else {
				timer.Reset(waitPeriod)
			}
			//等待'waitTime's
			select {
			case <-r.overLoop:
				return false, currentHeight
			case <-timer.C:
				loopNum++
				r.logger.Debugf("sup to hightest and loop wait %v", loopNum)
				continue
			}
		}
		return true, currentHeight
	}

}

// checkNeedScaleAt determines whether the stream group needs scaling at a certain height.
// It returns the height at which scaling is needed or math.MaxUint64 if no scaling is needed.
func (r *receptor) checkNeedScaleAt(sg *streamGroup) uint64 {
	// Get the minimum height currently received by the stream group.
	h, _ := sg.heightReceived()

	// If no blocks have been received, use the current waiting height.
	if h == 0 {
		h = r.heightWait
	} else {
		// Otherwise, increment the height to check the next block.
		h++
	}

	// Check if additional endpoints are needed. If not, return MaxUint64.
	if r.scaleNeedEndpoints(sg.len(), len(r.selectNoPushEndpoints(h))) <= 0 {
		return math.MaxUint64
	}

	return h
}

func (r *receptor) tryPullBlock(height uint64, duration time.Duration, times int) *Block {
	timer := time.NewTimer(duration)
	defer timer.Stop()
	for {
		select {
		case <-r.overLoop:
			return nil
		case <-timer.C:
			block, err := r.loopPull(height, r.withRWSet)
			if err == nil {
				return block
			}
			if err == errNoAvailableNodes {
				r.logger.Warnf("tryPullBlock block[%d] failed: %v", height, err)
				return nil
			}
			times--
			if times == 0 {
				return nil
			}
			timer.Reset(duration)
		}
	}
}

func (r *receptor) isPreferNode(nodeID string) bool {
	if len(r.conf.FromNodes) == 0 {
		return true
	}
	for _, id := range r.conf.FromNodes {
		if id == nodeID {
			return true
		}
	}
	return false
}

// selectAvailableEndpoints select all available endpoints that block height meets height 'h'.
func (r *receptor) selectAvailableEndpoints(h uint64) []*endpoint {
	var heightFilter endpointFilterFunc = func(e *endpoint) bool {
		return e.IsValidFor(h)
	}
	return getValidEndpointsSorted(h, r.endPool.Select(heightFilter))
}

// selectNoPushEndpoints picks the endpoints without pushing blocks.
// Endpoints with connection cached will be placed at the front of the array,
// other idle endpoints are behind, then return.
func (r *receptor) selectNoPushEndpoints(h uint64) []*endpoint {
	var freeFilter endpointFilterFunc = func(e *endpoint) bool {
		return e.IsValidAndNoPushFor(h)
	}
	ends := r.endPool.Select(freeFilter)
	return getValidEndpointsSorted(h, ends)
}

// WatchBlock watch new block being generated
func (r *receptor) WatchBlock() (types.BlockReveal, bool) {
	block, ok := <-r.blockOut
	if !ok {
		return nil, false
	}
	return block, true
}

func (r *receptor) loopPull(height uint64, withRWSet bool) (*Block, error) {
	var (
		ends  = r.selectAvailableEndpoints(height)
		block *Block
		err   error
	)

	if len(ends) == 0 {
		return nil, errNoAvailableNodes
	}

	for _, end := range ends {
		block, err = r.pullBlockFrom(end, height, withRWSet)
		if err == nil {
			return block, nil
		}
	}
	return nil, err //fmt.Errorf("loopPull block [%d] failed", height)
}

func (r *receptor) pullBlockFrom(end *endpoint, height uint64, withRWSet bool) (*Block, error) {
	cc, err := r.getClientConnFrom(end, height)
	if err != nil {
		return nil, err
	}
	defer func() {
		if err := cc.release(); err != nil {
			r.logger.Warnf("release connection %s failed: %v", cc.nodeID(), err)
		}
	}()
	return r.pullOneBlock(cc, height, withRWSet)
}

// selectOneAvailableConnection selects one available client connection based on the provided height 'h'.
// It iterates over the sorted list of available endpoints and attempts to obtain a client connection.
// Returns the first successfully obtained client connection or nil if no connections are available.
func (r *receptor) selectOneAvailableConnection(h uint64) *clientConn {
	// Retrieve all available endpoints sorted by availability score
	ends := r.selectAvailableEndpoints(h)
	for _, end := range ends {
		// Attempt to get a client connection from the endpoint
		cc, err := r.getClientConnFrom(end, h)
		if err != nil {
			// If obtaining the connection fails, continue to the next endpoint
			continue
		}
		// Return the obtained client connection
		return cc
	}
	// Return nil if no connection could be obtained
	return nil
}

// PullBlock pick an available connection and pull a block with height 'h' from the connection.
func (r *receptor) PullBlock(h uint64, withRWSet bool) (types.BlockReveal, error) {
	conn := r.selectOneAvailableConnection(h)
	if conn == nil {
		return nil, fmt.Errorf("no connection available")
	}
	defer func() {
		if err := conn.release(); err != nil {
			r.logger.Warnf("PullBlock release connection %s failed: %v", conn.nodeID(), err)
		}
	}()
	return r.pullOneBlock(conn, h, withRWSet)
}

// pullOneBlock pull a block with height h from the connection 'cc'.
func (r *receptor) pullOneBlock(cc *clientConn, h uint64, withRWSet bool) (*Block, error) {
	mode := setting.NewShardingMode(1, beginIndex, 0)
	ctx, cancel := context.WithTimeout(context.Background(), r.timeout)
	defer cancel()
	fragments, err := cc.pull(ctx, types.BlockSyncRequest{
		Height:    h,
		Num:       1,
		WithRWSet: withRWSet,
		ModeData:  mode.ToModeData(),
	})
	if err != nil {
		if code, ok := err.(errors.ErrCode); ok && code.Terminate() {
			cc.ep.MakeInvalidFor(h, err)
		} else {
			cc.ep.FailFor(h, metricTypeGet)
		}
		r.logger.Infof("pull block [%d] from [%s] failed: %v", h, cc.nodeID(), err)
		return nil, err
	}
	data, err := bytesToSliceData(fragments[0].Data)
	if err != nil {
		return nil, err
	}
	block := new(store.BlockWithRWSet)
	if err := proto.Unmarshal(data.Data, block); err != nil {
		return nil, err
	}
	return newBlock(cc.nodeID(), block, r.endPool), nil
}

func (r *receptor) isRunning() bool {
	return atomic.LoadInt32(&r.state) == receptorStateStarted
}

// notifyAdjustStream notify that an endpoint has been added or deleted.
func (r *receptor) notifyAdjustStream(event types.Event) { //(t int8, inform *syncPb.NodeInform) {
	if r.streamList.isWaiting() && r.isRunning() {
		switch event.EventType() {
		case types.EventAddNode, types.EventUpdateNode, eventTypeLongSilence:
			curH, err := r.ledgerCache.CurrentHeight()
			if err != nil {
				r.logger.Errorf("get current height failed: %v", err)
				return
			}
			r.heightWait = curH + 1
			r.init()
		}
		return
	}
	if event.EventType() == eventTypeLongSilence {
		return
	}
	select {
	case r.adjustCh <- event:
	default:
	}
}

// checkStreamClosed checks whether some streams has been closed in the back group.
// If has, return the min received block height of those closed streams.
// Otherwise return the maxUint64.
func (r *receptor) checkStreamClosedAt(node *streamLinkedNode) uint64 {
	var heightAdjust uint64 = math.MaxUint64
	if node != nil {
		for _, st := range node.sg.check() {
			if st.reason.Code.Terminate() {
				st.conn.ep.MakeInvalidFor(st.reason.Sent+1, st.reason.Code)
			}

			height := st.heightReceived()
			r.logger.Debugf("stream [%s] closed at height [%d] for [%s]", st.nodeID(),
				height, st.reason.Code.Error())
			if height < heightAdjust {
				heightAdjust = height
			}
		}
	}
	return heightAdjust
}

func (r *receptor) adjustStreamGroupAt(node *streamLinkedNode) uint64 {
	adjustHeight := r.checkStreamClosedAt(node)
	if adjustHeight != math.MaxUint64 {
		return adjustHeight + 1
	}
	adjustHeight, _ = node.sg.heightReceived()
	if adjustHeight == 0 {
		adjustHeight = r.heightWait
	} else {
		adjustHeight++
	}
	return adjustHeight
}

// scaleUseEndpoint if the scale condition is met, return the endpoints for scale.
func (r *receptor) scaleUseEndpoint(streamNum int, height uint64) []*endpoint {
	ends := r.selectNoPushEndpoints(height)
	n := r.scaleNeedEndpoints(streamNum, len(ends))
	if n <= 0 {
		return nil
	}
	return ends[:n]
}

// scaleNeedEndpoints calculate the number of idle endpoints required to trigger scaling.
// The number of idle endpoints is more than half of the currently used endpoints by stream group.
func (r *receptor) scaleNeedEndpoints(streamNum int, idleEp int) int {
	var (
		total     = streamNum + idleEp
		expectNum = r.config.ExposeConf.MaxNodesSelectedCount
	)
	scale := 3
	if total <= 4 {
		scale = 4
	}
	alternateEp := total / scale
	// if total%scale != 0 {
	// 	alternateEp++
	// }
	totalStream := total - alternateEp

	if expectNum > 0 && totalStream > expectNum {
		totalStream = expectNum
	}

	return totalStream - streamNum
}

// adjustStreamGroup adjusts stream group based on the back group in streamList.
// If the back group is not existing, a new group will be created, then build it with some connections.
// If exists, the fromHeight of the back group is equal to the parameter 'fromHeight',
// just the back group itself.
// Otherwise, clone a new one from the back group and adjust the newly cloned group.
// Adjustment does this, if group has invalid streams do replace, not, do scale up.
func (r *receptor) adjustStreamGroup(fromHeight uint64) bool {
	node := r.streamList.Back()
	if node == nil {
		conns := r.getNoPushConnsAtMostN(fromHeight, int(math.MaxInt32))
		sg := newStreamGroup(fromHeight, streamConf{
			withRWSet:      r.withRWSet,
			timeout:        r.timeout,
			windowInitSize: r.config.pushWindowSize,
		})
		sg.build(conns...)
		if sg.len() > 0 {
			r.putStreamGroup(sg)
		}
		return true
	}

	var (
		sg    *streamGroup
		newly = node.sg.fromHeight != fromHeight
	)
	if newly {
		sg = node.sg.clone(fromHeight)
	} else {
		sg = node.sg
	}
	invalidStreams := sg.invalidStreams()
	il := len(invalidStreams)
	exceptNodes := make([]string, 0, il)
	for _, st := range invalidStreams {
		exceptNodes = append(exceptNodes, st.nodeID())
	}
	var conns []*clientConn
	//check是否需要扩容
	if il > 0 {
		conns = r.getNoPushConnsAtMostN(fromHeight, il, exceptNodes...)
	} else {
		for _, end := range r.scaleUseEndpoint(sg.len(), fromHeight) {
			cc, err := r.getClientConnFrom(end, fromHeight)
			if err != nil {
				r.logger.Debugf("get connection from endpoint [%s] failed for scale: %v", end.id, err)
				continue
			}
			conns = append(conns, cc)
		}
	}
	r.logger.Debugf("adjust stream group at[%d], invalid[%d], add[%d]", fromHeight, il, len(conns))
	//no need change
	if il == 0 && len(conns) == 0 {
		if newly {
			sg.release()
		}
		return false
	}
	sg.rebuild(conns...)
	if newly {
		r.putStreamGroup(sg)
	}
	return newly
}

// getNoPushConnsAtMostN get up to N connections without push stream.
// Select the endpoints without push stream first and create up to N connections.
func (r *receptor) getNoPushConnsAtMostN(fromHeight uint64, n int, exceptNodes ...string) []*clientConn {
	var (
		ends    = r.selectNoPushEndpoints(fromHeight)
		conns   = make([]*clientConn, 0, n)
		notNeed = func(id string) bool {
			for _, nodeID := range exceptNodes {
				if id == nodeID {
					return true
				}
			}
			return false
		}
	)
	for _, end := range ends {
		if notNeed(end.id) {
			continue
		}
		cc, err := r.getClientConnFrom(end, fromHeight)
		if err != nil {
			continue
		}
		conns = append(conns, cc)
		if n == len(conns) {
			break
		}
	}
	return conns
}

// Pause receiving data if the receptor is started.
func (r *receptor) Pause() error {
	if !atomic.CompareAndSwapInt32(&r.state, receptorStateStarted, receptorStatePausing) {
		return fmt.Errorf("pause failed, state:[%d]", r.state)
	}
	r.logger.Info("receptor is pausing")
	r.pauseCh <- struct{}{}
	//anyway to wake up the stream processing goroutine.
	r.putStreamGroup(wakeUpSg)
	<-r.pauseCompleteCh
	atomic.StoreInt32(&r.state, receptorStatePaused)
	r.logger.Info("receptor is paused")
	return nil
}

// Resume receiving data if the receptor is paused.
// Get the height of the local ledger and initialize the receiving stream.
func (r *receptor) Resume() error {
	h, err := r.ledgerCache.CurrentHeight()
	if err != nil {
		return err
	}
	if !atomic.CompareAndSwapInt32(&r.state, receptorStatePaused, receptorStateStarting) {
		return fmt.Errorf("resume failed, state:[%d]", r.state)
	}
	r.overLoop = r.triggerJumpOut()
	r.logger.Info("receptor is resuming")
	r.heightWait = h + 1
	r.initStreamWithHeight(r.heightWait)
	atomic.StoreInt32(&r.state, receptorStateStarted)
	r.logger.Info("receptor is resumed")
	return nil
}

// func (r *receptor) initStream() error {
// 	h, err := r.ledgerCache.CurrentHeight()
// 	if err != nil {
// 		r.logger.Errorf("get current height failed for init stream: %v", err)
// 		return err
// 	}
// 	r.heightWait = h + 1
// 	r.initStreamWithHeight(r.heightWait)
// 	return nil
// }

// initStreamWithHeight find all endpoints those are alive
// and no push stream established between the local and the endpoint.
// Then establish connections with these endpoints and build a stream group with these connections.
func (r *receptor) initStreamWithHeight(h uint64) {
	var conns []*clientConn
	ends := r.selectNoPushEndpoints(h)
	n := r.scaleNeedEndpoints(0, len(ends))
	actives := ends[:n]
	// bench := ends[n:]
	for _, end := range actives {
		cc, err := r.getClientConnFrom(end, h)
		if err != nil {
			continue
		}
		conns = append(conns, cc)
	}

	if len(conns) == 0 {
		r.logger.Warnf("init stream failed at[%d], no connection available for active endpoints[%d]",
			h, len(actives))
		return
	}

	sg := newStreamGroup(h, streamConf{
		withRWSet:      r.withRWSet,
		timeout:        r.timeout,
		windowInitSize: r.config.pushWindowSize,
	})
	sg.build(conns...)
	if sg.len() == 0 {
		r.logger.Warnf("no push stream built for conns count [%d]", len(conns))
		return
	}
	r.putStreamGroup(sg)
}

func (r *receptor) getClientConnFrom(end *endpoint, height uint64) (*clientConn, error) {
	ctx, cancel := context.WithTimeout(context.Background(), r.timeout)
	defer cancel()
	cc, err := end.GetConn(ctx, height, r.transport)
	if err != nil {
		r.logger.Infof("create connection with node [%s] failed: %v", end.id, err)
	}
	return cc, err
}

// HeightHasBeenSynced returns the height that the receptor has synced to.
func (r *receptor) HeightHasBeenSynced() uint64 {
	return r.heightWait
}

// BlocksInQueue returns the number of blocks in the queue waiting to be processed.
func (r *receptor) BlocksInQueue() int {
	return len(r.blockOut)
}

// ShowConfigJSON returns the config of the receptor in json format.
func (r *receptor) ShowConfigJSON() string {
	return r.config.String()
}
