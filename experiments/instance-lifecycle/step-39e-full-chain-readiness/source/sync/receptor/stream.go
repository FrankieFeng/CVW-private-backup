/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package receptor

import (
	"container/list"
	"context"
	"fmt"
	"math"
	"math/rand"
	"sync"
	"sync/atomic"
	"time"

	syncPb "chainmaker.org/chainmaker/pb-go/v2/sync"
	"chainmaker.org/chainmaker/sync/v2/conn"
	sp "chainmaker.org/chainmaker/sync/v2/setting"
	"chainmaker.org/chainmaker/sync/v2/types"
)

type (
	//clientPushStream is the stream that receives data fragments.
	//There is a one-to-one correspondence between streams and connections.
	clientPushStream struct {
		//Pointer to the client connection which open the stream.
		conn *clientConn
		//An instance of the client stream
		stream clientStream
		//ref is the reference count to this stream.
		//the stream will be closed when ref is zero.
		ref int32
		//Boolean indicating whether the stream is closed.
		closed bool
	}

	blockScattered struct {
		height     uint64
		fragments  [][]byte
		totalBytes int
		miss       []uint16
		diss       []string
		invalids   []string
		reward     []string
		ruleID     uint64
	}

	//clientStreamWithIndex different index values can be assigned to the same stream.
	clientStreamWithIndex struct {
		index int
		*clientPushStream
		reason   conn.CloseReason
		invalid  bool
		released bool
	}
)

const (
	beginIndex = 0
)

func newClientStreamWithIndex(idx int, st *clientPushStream) *clientStreamWithIndex {
	return &clientStreamWithIndex{
		index:            idx,
		clientPushStream: st,
	}
}

func newClientStream(conn *clientConn, st clientStream) *clientPushStream {
	return &clientPushStream{
		conn:   conn,
		stream: st,
		ref:    1,
	}
}

type clientStream interface {
	Fetch() (types.DataFragment, bool)
	HeightReadable() uint64
	HeightWritten() uint64
	UpdateSetting(ctx context.Context, height uint64, kvs ...sp.Setting) error
	Close()
	IsClosed() (bool, conn.CloseReason)
	ListenClose() <-chan conn.CloseReason
}

type streamConf struct {
	//withRWSet indicates whether the block data has a read-write set
	withRWSet bool
	//the timeout of the connection
	timeout time.Duration
	// the push stream window init size
	windowInitSize int
}

// streamGroup consists of streams created using the same set of setting information.
type streamGroup struct {
	//fromHeight the starting height of stream group creation.
	fromHeight uint64
	//withRWSet indicates whether the block data has a read-write set
	// withRWSet bool
	//streams collection of streams.
	streams []*clientStreamWithIndex
	//curHeight current fetch height.
	curHeight     uint64
	conf          streamConf
	maxGID        uint64
	maxGidStreams []int
}

func newStreamGroup(height uint64, conf streamConf) *streamGroup {
	return &streamGroup{
		fromHeight: height,
		curHeight:  height,
		conf:       conf,
	}
}

func (sg *streamGroup) openStream(conn *clientConn, sett pushSetting) (*clientPushStream, error) {
	sett.windowSize = sg.conf.windowInitSize
	ctx, cancel := context.WithTimeout(context.Background(), sg.conf.timeout)
	defer cancel()
	return conn.openStream(ctx, sg.curHeight, sett)
}

func (sg *streamGroup) updateStream(st *clientStreamWithIndex, sett pushSetting) error {
	ctx, cancel := context.WithTimeout(context.Background(), sg.conf.timeout)
	defer cancel()
	return st.update(ctx, sg.curHeight, sett)
}

// build the stream group from the specified connections.
// If the stream group contains historical streams,
// the stream group will be reconstructed based on previously available streams and new incoming connections.
func (sg *streamGroup) build(conns ...*clientConn) {
	var (
		expect      = sg.len() + len(conns)
		idx         int
		failStreams = make(map[string]*clientStreamWithIndex)
		failConns   = make(map[string]*clientConn)
		streams     []*clientStreamWithIndex
		fail        bool
	)
	// First find out all the streams that have expired
	for _, st := range sg.streams {
		if st.isInvalid() {
			failStreams[st.nodeID()] = st
		}
	}
	// the number of all nodes expected to be available
	total := expect - len(failStreams)
	streams = make([]*clientStreamWithIndex, 0, total)

	for {
		idx = beginIndex
		streams = streams[:0]
		//If a failure is encountered during the build process, it will jump out,
		//so the desired amount will be reduced by 1.
		if fail {
			total = expect - len(failStreams) - len(failConns)
		}
		fail = false
		//Update settings for active streams, and mark the stream as failed if an error occurs and break.
		for _, st := range sg.streams {
			if _, ok := failStreams[st.nodeID()]; ok {
				continue
			}
			err := sg.updateStream(st, pushSetting{
				totalNum:  total,
				rankedNo:  idx,
				withRWSet: sg.conf.withRWSet,
			})
			if err != nil {
				failStreams[st.nodeID()] = st
				fail = true
				break
			}
			st.index = idx
			streams = append(streams, st)
			idx++
		}
		// update settings for streams fail, restart the next round of attempts
		if fail {
			continue
		}
		// Create a stream from a connection, marking the connection as failed and break if it fails.
		for i, conn := range conns {
			if _, ok := failConns[conn.nodeID()]; ok {
				continue
			}
			st, err := sg.openStream(conn, pushSetting{
				totalNum:  total,
				rankedNo:  idx,
				withRWSet: sg.conf.withRWSet,
			})
			if err != nil {
				failConns[conn.nodeID()] = conn
				conns = conns[i+1:]
				fail = true
				break
			}
			streams = append(streams, newClientStreamWithIndex(idx, st))
			idx++
		}
		sg.streams = streams
		//If the build is successful, exit the build process.
		if !fail {
			break
		}
	}
	//release the invalid stream
	for _, st := range failStreams {
		st.release()
	}
	// release the invalid connection
	for _, conn := range failConns {
		if err := conn.release(); err != nil {
			conn.logger.Warnf("Failed to release connection [%s]: %v", conn.nodeID(), err)
		}
	}
}

// rebuild the invalid streams from the specified connection.
// The length of conns is less than the length of the invalid streams
// means that the rebuild operation is useless, so execute the build process directly.
func (sg *streamGroup) rebuild(conns ...*clientConn) {
	if len(conns) == 0 {
		sg.build()
		return
	}

	var (
		total       = sg.len()
		failStreams []*clientStreamWithIndex
	)
	for _, st := range sg.streams {
		if st.isInvalid() {
			failStreams = append(failStreams, st)
		}
	}
	if len(failStreams) > 0 && len(conns) >= len(failStreams) {
		sg.resetMaxGID()
		connIdx := 0
		for i := 0; i < len(failStreams); i++ {
			var (
				st        = failStreams[i]
				replaceOk bool
			)
			// 失效的流数少于等于连接的数量，表示还可进行替换尝试
			for len(failStreams)-i <= len(conns)-connIdx {
				conn := conns[connIdx]
				newSt, err := sg.openStream(conn, pushSetting{
					totalNum:  total,
					rankedNo:  st.index,
					withRWSet: sg.conf.withRWSet,
				})
				connIdx++
				if err != nil {
					// failConns = append(failConns, conn)
					continue
				}
				sg.streams[st.index-beginIndex] = newClientStreamWithIndex(st.index, newSt)
				replaceOk = true
				break
			}

			if !replaceOk {
				// fmt.Println("replace failed connection", "to do build")
				sg.build()
				return
			}
		}
	} else {
		sg.build(conns...)
	}
}

// heightReceived get the minimum and maximum block height currently received by the stream group
func (sg *streamGroup) heightReceived() (uint64, uint64) {
	var (
		minHeight uint64 = math.MaxUint64
		maxHeight uint64
	)
	for _, st := range sg.streams {
		height := st.stream.HeightWritten()
		if height < minHeight {
			minHeight = height
		}
		if height > maxHeight {
			maxHeight = height
		}
	}
	return minHeight, maxHeight
}

// clone a new stream group from the current stream group,
// this behavior generally occurs when a new stream group is constructed based on the current stream group.
// For example: newSg := sg.clone(), newSg.build(conns...)
func (sg *streamGroup) clone(height uint64) *streamGroup {
	streams := make([]*clientStreamWithIndex, len(sg.streams))
	for i, st := range sg.streams {
		streams[i] = st.clone()
	}
	return &streamGroup{
		streams:    streams,
		fromHeight: height,
		curHeight:  height,
		conf:       sg.conf,
	}
}

// check for signals that all streams are closed.
// returns the streams that were detected to be closed.
func (sg *streamGroup) check() []*clientStreamWithIndex {
	var closeSts []*clientStreamWithIndex
	for _, st := range sg.streams {
		select {
		case r := <-st.stream.ListenClose():
			st.reason = r
			st.closed = true
			closeSts = append(closeSts, st)
		default:
		}
	}
	return closeSts
}

// len the stream group contains the number of streams
func (sg *streamGroup) len() int {
	return len(sg.streams)
}

// hasInvalidStream does the stream group contain invalid streams.
func (sg *streamGroup) hasInvalidStream() bool {
	for _, st := range sg.streams {
		if st.isInvalid() {
			return true
		}
	}
	return false
}

// invalidStreams get all invalid streams
func (sg *streamGroup) invalidStreams() []*clientStreamWithIndex {
	var sts []*clientStreamWithIndex
	for _, st := range sg.streams {
		if st.isInvalid() {
			sts = append(sts, st)
		}
	}
	return sts
}

// release the stream group and release each stream in the stream group.
func (sg *streamGroup) release() {
	for _, st := range sg.streams {
		st.release()
	}
	sg.streams = nil
}

func (sg *streamGroup) makeInvalid(id string) {
	for _, st := range sg.streams {
		if st.nodeID() == id {
			st.invalid = true
		}
	}
}

func (sg *streamGroup) resetMaxGID() {
	sg.maxGID = 0
	if sg.maxGidStreams != nil {
		sg.maxGidStreams = sg.maxGidStreams[:0]
	}
}

func (sg *streamGroup) pull(conn *clientConn, req types.BlockSyncRequest) ([]types.DataFragment, error) {
	ctx, cancel := context.WithTimeout(context.Background(), sg.conf.timeout)
	defer cancel()
	return conn.pull(ctx, req)
}

// tryPull tries to pull data from all streams in the stream group.
// It will try to pull data from all streams and put them into the dataCache.
// If the data pulled from a stream is invalid, it will be replaced with data from
// another stream that has the same rule id.
// If a stream doesn't have any data, it will be put into the miss list.
// If the data pulled from a stream has a rule id that is greater than the current
// maxGid, the maxGid will be updated and the list of streams that have the same
// rule id will be updated.
func (sg *streamGroup) tryPull(height uint64, streamIdx int) (nodeID string, data *syncPb.SliceData, err error) {
	// if there are streams that have the same rule id as the maxGid, try to pull data from them first.
	if len(sg.maxGidStreams) > 0 {
		// randomly select a stream from the maxGidStreams list and try to pull data from it.
		// #nosec G404
		begin := rand.Intn(len(sg.maxGidStreams))
		for i := begin; i < begin+len(sg.maxGidStreams); i++ {
			stIndex := sg.maxGidStreams[i%len(sg.maxGidStreams)]
			cc := sg.streams[stIndex].conn
			if !cc.closed {
				mode := sp.NewShardingMode(sg.len(), streamIdx, 0)
				fragments, iErr := sg.pull(cc, types.BlockSyncRequest{
					Height:    height,
					Num:       1,
					WithRWSet: sg.conf.withRWSet,
					ModeData:  mode.ToModeData(),
				})
				// fmt.Printf("tryPull from [%d][%s] for fragment: [%d], error: %v\n", i, cc.nodeID(), streamIdx, iErr)
				if iErr != nil || len(fragments) == 0 {
					continue
				}
				data, err = bytesToSliceData(fragments[0].Data)
				if err != nil {
					continue
				}
				nodeID = cc.nodeID()
				return
			}
		}
	}

	err = fmt.Errorf("try pull failed")
	return
}

// FetchAllFragments fetches all fragments from all streams in the stream group.
// It tries to pull data from all streams and put them into the dataCache.
// If the data pulled from a stream is invalid, it will be replaced with data from
// another stream that has the same rule id.
// If a stream doesn't have any data, it will be put into the miss list.
// If the data pulled from a stream has a rule id that is greater than the current
// maxGid, the maxGid will be updated and the list of streams that have the same
// rule id will be updated.
func (sg *streamGroup) FetchAllFragments() blockScattered {
	var (
		dataCache = make([]sliceData, 0, sg.len())

		block = blockScattered{
			height:    sg.curHeight,
			fragments: make([][]byte, 0, len(sg.streams)),
		}

		maxGidChanged = false
	)
	for i, st := range sg.streams {
		bf, err := st.fetchData()
		if bf.Data.miss() {
			st.conn.logger.Debugf("fetch block[%d], miss [%d][%s] for %v\n", bf.Height, i, st.nodeID(), err)
		}
		if bf.Height != sg.curHeight {
			st.conn.logger.Errorf("fetch block[%d], expected [%d], got [%d]\n",
				bf.Height, sg.curHeight, bf.Height)
			bf.Data = sliceData{}
		}
		dataCache = append(dataCache, bf.Data)
		if !bf.Data.miss() && bf.Data.RuleId > sg.maxGID {
			sg.maxGID = bf.Data.RuleId
			maxGidChanged = true
		}
	}
	block.ruleID = sg.maxGID

	if !maxGidChanged && sg.maxGID == 0 && len(sg.maxGidStreams) == 0 {
		maxGidChanged = true
	}

	if maxGidChanged {
		sg.maxGidStreams = sg.maxGidStreams[:0]
		for i, data := range dataCache {
			if !data.miss() && data.RuleId == sg.maxGID {
				sg.maxGidStreams = append(sg.maxGidStreams, sg.streams[i].index)
			}
		}
	}

	for i, data := range dataCache {
		if data.miss() || data.RuleId < sg.maxGID {
			if data.invalid() {
				block.invalids = append(block.invalids, sg.streams[i].nodeID())
			} else {
				block.diss = append(block.diss, sg.streams[i].nodeID())
			}

			nodeID, newData, err := sg.tryPull(sg.curHeight, sg.streams[i].index)
			if err == nil {
				data = sliceData{
					SliceData: newData,
				}
				block.reward = append(block.reward, nodeID)
			}
		}
		if data.miss() {
			block.miss = append(block.miss, uint16(i))
			block.fragments = append(block.fragments, nil)
		} else {
			block.fragments = append(block.fragments, data.Data)
			block.totalBytes += len(data.Data)
		}
	}

	sg.curHeight++
	return block
}

// release release the stream and the connection if the ref count is 0.
func (st *clientPushStream) release() {
	// Decrement the ref count.
	// If the ref count is 0, the stream is closed and the connection is closed and released.
	if atomic.AddInt32(&st.ref, -1) == 0 {
		st.closed = true
		// Close the stream.
		st.conn.closeStream()
		// Release the connection.
		if err := st.conn.release(); err != nil {
			// Log the error if the connection cannot be released.
			st.conn.logger.Warnf("release stream [%s] error: %v", st.nodeID(), err)
		}
	}
}

func (st *clientPushStream) nodeID() string {
	return st.conn.nodeID()
}

func (st *clientPushStream) retain() error {
	if atomic.AddInt32(&st.ref, 1) <= 1 {
		return fmt.Errorf("stream has already closed")
	}
	return nil
}

func (st *clientPushStream) isInvalid() bool {
	return st.closed
}

func (st *clientPushStream) update(ctx context.Context, height uint64, set pushSetting) error {
	return st.stream.UpdateSetting(ctx, height, set.toSettings()...)
}

func (st *clientPushStream) heightReceived() uint64 {
	return st.stream.HeightWritten()
}

type sliceData struct {
	*syncPb.SliceData
}

func (sd sliceData) miss() bool {
	return sd.SliceData == nil || sd.SliceData == invalidFragment
}

// invalid indicates the stream that generated the sliceData is no longer available
func (sd sliceData) invalid() bool {
	return sd.SliceData == invalidFragment
}

type blockFragment struct {
	Height uint64
	Data   sliceData
}

var invalidFragment = &syncPb.SliceData{}

func (st *clientPushStream) fetchData() (blockFragment, error) {
	fragment, ok := st.stream.Fetch()
	bf := blockFragment{
		Height: fragment.Height,
	}
	if !ok {
		if closed, reason := st.stream.IsClosed(); closed {
			if reason.Sent <= fragment.Height {
				bf.Data.SliceData = invalidFragment
				return bf, reason.Code
			}
		}
		return bf, nil
	}
	data, err := bytesToSliceData(fragment.Data)
	if err != nil {
		return bf, err
	}
	bf.Data.SliceData = data
	return bf, nil
}

type streamLinkedList struct {
	lst *list.List
}

func newStreamLinkedList() *streamLinkedList {
	return &streamLinkedList{
		lst: list.New(),
	}
}

// Push push the stream to the linked list.
func (l *streamLinkedList) Push(n *streamGroup) {
	l.lst.PushBack(n)
}

// Front get the first stream from the linked list.
func (l *streamLinkedList) Front() *streamLinkedNode {
	e := l.lst.Front()
	if e == nil {
		return nil
	}
	return &streamLinkedNode{
		sg:  e.Value.(*streamGroup),
		ele: e,
	}
}

// Back get the last stream from the linked list.
func (l *streamLinkedList) Back() *streamLinkedNode {
	e := l.lst.Back()
	if e == nil {
		return nil
	}
	return &streamLinkedNode{
		sg:  e.Value.(*streamGroup),
		ele: e,
	}
}

// ClearAll clear all streams from the linked list.
func (l *streamLinkedList) ClearAll() {
	for node := l.Front(); node != nil; node = l.Front() {
		l.Remove(node)
	}
}

// Remove remove the stream from the linked list.
func (l *streamLinkedList) Remove(ln *streamLinkedNode) {
	l.lst.Remove(ln.ele)
	ln.destroy()
}

// Len get the length of the linked list.
func (l *streamLinkedList) Len() int {
	return l.lst.Len()
}

type streamLinkedNode struct {
	sg  *streamGroup
	ele *list.Element
}

func (ln *streamLinkedNode) destroy() {
	ln.sg.release()
}

func (ln *streamLinkedNode) Next() *streamLinkedNode {
	e := ln.ele.Next()
	if e == nil {
		return nil
	}
	return &streamLinkedNode{
		sg:  e.Value.(*streamGroup),
		ele: e,
	}
}

type streamChecker struct {
	mu         sync.Mutex
	dissRecord map[string]uint64
	boundary   int
}

func newStreamChecker(boundary int) *streamChecker {
	return &streamChecker{
		boundary:   boundary,
		dissRecord: make(map[string]uint64),
	}
}

func (c *streamChecker) check(nodeID string, h uint64) bool {
	c.mu.Lock()
	defer c.mu.Unlock()
	recordH, exist := c.dissRecord[nodeID]
	if !exist {
		c.dissRecord[nodeID] = h
		return false
	}
	return math.Abs(float64(h-recordH)) <= float64(c.boundary)
}

func (c *streamChecker) clearRecord(nodeID string) {
	c.mu.Lock()
	defer c.mu.Unlock()
	delete(c.dissRecord, nodeID)
}

type streamLinkedListLocked struct {
	*streamLinkedList
	status int
	mu     sync.Mutex
	cond   *sync.Cond
}

func newStreamLinkedListLocked() *streamLinkedListLocked {
	list := &streamLinkedListLocked{
		streamLinkedList: newStreamLinkedList(),
	}
	list.cond = sync.NewCond(&list.mu)
	return list
}

func (l *streamLinkedListLocked) Front() *streamLinkedNode {
	l.mu.Lock()
	defer l.mu.Unlock()
	for {
		f := l.streamLinkedList.Front()
		if f == nil {
			l.status = 1
			l.cond.Wait()
			continue
		}
		l.status = 0
		return f
	}
}

func (l *streamLinkedListLocked) Push(n *streamGroup) {
	l.mu.Lock()
	defer l.mu.Unlock()
	l.streamLinkedList.Push(n)
	l.status = 0
	l.cond.Broadcast()
}

func (l *streamLinkedListLocked) Remove(n *streamLinkedNode) {
	l.mu.Lock()
	defer l.mu.Unlock()
	l.streamLinkedList.Remove(n)
}

func (l *streamLinkedListLocked) isWaiting() bool {
	l.mu.Lock()
	defer l.mu.Unlock()
	return l.status == 1
}

func (l *streamLinkedListLocked) ClearAll() {
	l.mu.Lock()
	defer l.mu.Unlock()
	l.streamLinkedList.ClearAll()
}

func (st *clientStreamWithIndex) isInvalid() bool {
	return st.invalid || st.clientPushStream.isInvalid()
}

func (st *clientStreamWithIndex) release() {
	if st.released {
		return
	}
	st.released = true
	st.clientPushStream.release()
}

func (st *clientStreamWithIndex) clone() *clientStreamWithIndex {
	_ = st.clientPushStream.retain()
	return &clientStreamWithIndex{
		index:            st.index,
		clientPushStream: st.clientPushStream,
		invalid:          st.invalid,
	}
}
