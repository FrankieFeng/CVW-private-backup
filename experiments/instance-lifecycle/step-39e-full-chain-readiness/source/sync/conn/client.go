/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

/*
Package conn provides connection-related functionality.
*/
package conn

import (
	"context"
	"fmt"
	"io"
	"sync/atomic"
	"time"

	"chainmaker.org/chainmaker/protocol/v2"
	"chainmaker.org/chainmaker/sync/v2/internal/controller"
	ierrs "chainmaker.org/chainmaker/sync/v2/internal/errors"
	"chainmaker.org/chainmaker/sync/v2/internal/rand"
	sp "chainmaker.org/chainmaker/sync/v2/setting"
	"chainmaker.org/chainmaker/sync/v2/types"
	"golang.org/x/sync/singleflight"
)

// ClientConn a connection for retrieving blocks from remote nodes.
type ClientConn struct {
	//stat the connection stat
	state connState
	//conn the underlying connection for sending and receiving net messages.
	conn FrameConn
	//pushStream a message stream for receiving block pushed.
	pushStream *PushStream
	//settingVersion the push setting version number，random initialization and increment.
	settingVersion uint32
	//rFrameCh the channel to receive read frame messages.
	rFrameCh chan readFrameResult
	//wFrameCh the channel to receive write frame messages.
	wFrameCh chan frameWriteRequest
	//closeCh for closing the connection
	closeCh chan struct{}
	//done signals the end of the connection lifetime
	// done chan struct{}
	//settingWriter the push setting frame waiting to be sent. if it is not nil, it will be sent immediately.
	// settingWriter frameWriterRequest
	settingWrCh chan frameWriteRequest
	//singleCall restricts the operation of pulling the same block.
	singleCall *singleflight.Group
	//requests represents which requests are waiting for a response.
	requests *waiterQueue
	// logger
	logger protocol.Logger
	// requestID is the ID of the request.
	requestID uint32
	rGroup    *controller.GoRoutineGroup
}

func newClientConn(conn FrameConn, logger protocol.Logger) *ClientConn {
	c := &ClientConn{
		state:       stateOpen,
		conn:        conn,
		rFrameCh:    make(chan readFrameResult, frameBufferSize),
		wFrameCh:    make(chan frameWriteRequest, frameBufferSize),
		settingWrCh: make(chan frameWriteRequest, 8),
		closeCh:     make(chan struct{}),
		singleCall:  &singleflight.Group{},
		requests:    newWaiterQueue(),
		logger:      logger,
		rGroup:      controller.NewGoRoutineGroup(),
	}
	go c.serve()
	return c
}

// NodeID the ID of the peer node
func (c *ClientConn) NodeID() string {
	return c.conn.RemoteAddr().String()
}

// Serve start the read and write process
// Setting frames have higher priority and need to be written first.
// The loop will exit if the peer connection or the local is closed
func (c *ClientConn) serve() {
	c.logger.Debugf("client connection[%p] serves for node: %s", c, c.NodeID())
	defer func() {
		c.conn.Close()
		c.rGroup.Wait()
		c.logger.Debugf("client connection[%p] exits serve for node: %s", c, c.NodeID())
	}()

	// notice other goroutine to exit
	// defer close(c.done)
	c.rGroup.Run(c.loopReadFrame)
	for {
		select {
		case <-c.closeCh:
			return
		case wfr := <-c.settingWrCh:
			c.writeFrameRequest(wfr)
			continue
		default:
		}

		select {
		case wfr := <-c.wFrameCh:
			c.writeFrameRequest(wfr)
		case result := <-c.rFrameCh:
			if !c.processFrameResult(result) {
				c.logger.Debugf("connection [%s] read frame EOF, to close", c.NodeID())
				c.closeByRemote()
				return
			}
		case wfr := <-c.settingWrCh:
			c.writeFrameRequest(wfr)
		case <-c.closeCh:
			c.state = stateClose
			return
		}
	}
}

// writeFrameRequest write the frame to net and notify those waiting for the write result
// If the frame is "syncDataPushEndWriter" close the push stream
// "syncFinishWriter" close the connection
func (c *ClientConn) writeFrameRequest(fwr frameWriteRequest) {
	frame := fwr.req.getFrame()
	err := c.conn.Write(frame)

	if fwr.done != nil {
		select {
		case fwr.done <- err:
		default:
		}
	}
	// c.logger.Infof("write frame [%v] to [%s]", c.pfr.framer.wbuf[:7], c.NodeID())
	switch frame := frame.(type) {
	case dataPushFrame:
		if frame.isEnd() {
			if c.pushStream != nil {
				c.pushStream.closeByLocal()
			}
		}
	case finishFrame:
		c.closeByLocal()
	}
}

// OpenPush Open a channel to push block data.
// parameters 'fromHeight' is block height to start pushing.
// parameters 'kvs' is the settings for pushing.
// If there is no push stream the settingVersion of client conn is zero.
// Then randomly initialize the setting version number with a non-zero value.
// No push setting ack message received within 1s means that open push failed and return error.
// Opening stream repeatedly will return "already open" error
// #nosec G404
func (c *ClientConn) OpenPush(ctx context.Context, fromHeight uint64, kvs ...sp.Setting) (*PushStream, error) {
	if atomic.LoadUint32(&c.settingVersion) != 0 {
		return nil, ErrPushStreamAlreadyOpen
	}
	randVersion := rand.Uint32()
	for randVersion == 0 {
		randVersion = rand.Uint32()
	}

	if !atomic.CompareAndSwapUint32(&c.settingVersion, 0, randVersion) {
		return nil, ErrPushStreamAlreadyOpen
	}

	sts := c.genSettings(c.settingVersion, fromHeight, kvs...)

	c.logger.Debugf("connection [%s] open push, setting version [%d], content: [%v]", c.NodeID(),
		c.settingVersion, sts)

	if err := c.sendSettingFrameRequest(ctx, c.settingVersion, pushSettingInitWriter(sts), func() {
		c.pushStream = newPushStream(c, genSetting(sts))
	}); err != nil {
		c.logger.Debugf("connection [%s] open push, setting version [%d] failed: %v", c.NodeID(),
			c.settingVersion, err)
		c.settingVersion = 0
		return nil, err
	}
	return c.pushStream, nil
}

// Ping sends a ping message to test connection.
// #nosec G404
func (c *ClientConn) Ping(ctx context.Context) error {
	var p [8]byte
	for {
		if _, err := rand.Read(p[:]); err != nil {
			return err
		}
		writer := syncPingWriter(p[:])
		_, err := c.requestNormalFrameRequest(ctx, string(p[:]), writer)
		if err == errAlreadyExists {
			continue
		}
		return err
	}
}

func (c *ClientConn) genSettings(version uint32, height uint64, kvs ...sp.Setting) []syncSetting {
	settings := make([]syncSetting, 0, len(kvs)+2)
	settings = append(settings, syncSetting{
		ID:  idSyncSettingVersion,
		Val: uint64(version),
	})
	settings = append(settings, syncSetting{
		ID:  idSyncSettingBlockHeight,
		Val: height,
	})
	settings = append(settings, kvs...)
	return settings
}

// pushToRespWaiterList push who waiting the ack message into waiter queue.
// Wake the ack timeout processing goroutine if the length of queue from 0 to 1.
// Return error if waiter is pushed into queue repeatedly.
func (c *ClientConn) addRequest(w waiter) error {
	if existed := c.requests.Push(w); existed {
		return errAlreadyExists
	}
	return nil
}

// sendNormalFrameForResponse send a request to the remote node and add the request to the request list
// to wait for the response.
// If an error occurred when writing the frame, the request will be removed from the request list.
func (c *ClientConn) sendNormalFrameForResponse(ctx context.Context, req writeRequest) error {
	respWaiter := newResponseWaiter(req)
	if err := c.addRequest(respWaiter); err != nil {
		return err
	}
	done := make(chan error, 1)
	if err := c.writeFrameAsync(ctx, frameWriteRequest{req: req, done: done}, c.wFrameCh); err != nil {
		c.notifyAndRmRequest(req.id(), err)
		return err
	}
	if err := c.waitWriteAsyncResult(ctx, done); err != nil {
		c.notifyAndRmRequest(req.id(), err)
		return err
	}
	select {
	case <-ctx.Done():
		c.notifyAndRmRequest(req.id(), ctx.Err())
	case <-respWaiter.done():
	case <-c.closeCh:
		c.notifyAndRmRequest(req.id(), ErrConnClosed)
	}
	return nil
}

// sendNormalFrame send a request to the remote node and wait for sending to complete.
func (c *ClientConn) sendNormalFrame(ctx context.Context, req writeRequest) error {
	done := make(chan error, 1)
	if err := c.writeFrameAsync(ctx, frameWriteRequest{req: req, done: done}, c.wFrameCh); err != nil {
		return err
	}
	return c.waitWriteAsyncResult(ctx, done)
}

// sendNormalFrameAsync send a request to the remote node without caring whether it is sent successfully.
func (c *ClientConn) sendNormalFrameAsync(ctx context.Context, req writeRequest) error {
	return c.writeFrameAsync(ctx, frameWriteRequest{req: req}, c.wFrameCh)
}

func (c *ClientConn) writeFrameAsync(ctx context.Context, req frameWriteRequest, to chan<- frameWriteRequest) error {
	select {
	case to <- req:
	case <-ctx.Done():
		return ctx.Err()
	case <-c.closeCh:
		return ErrConnClosed
	}
	return nil
}

func (c *ClientConn) waitWriteAsyncResult(ctx context.Context, done <-chan error) error {
	select {
	case err := <-done:
		return err
	case <-ctx.Done():
		return ctx.Err()
	case <-c.closeCh:
		return ErrConnClosed
	}
}

// sendSettingFrame send a setting frame request to the remote node and wait for the response.
func (c *ClientConn) sendSettingFrame(ctx context.Context, req writeRequest) error {
	respWaiter := newResponseWaiter(req)
	if err := c.addRequest(respWaiter); err != nil {
		return err
	}
	done := make(chan error, 1)
	if err := c.writeFrameAsync(ctx, frameWriteRequest{req: req, done: done}, c.settingWrCh); err != nil {
		c.notifyAndRmRequest(req.id(), err)
		return err
	}
	if err := c.waitWriteAsyncResult(ctx, done); err != nil {
		c.notifyAndRmRequest(req.id(), err)
		return err
	}

	select {
	case <-ctx.Done():
		c.notifyAndRmRequest(req.id(), ctx.Err())
	case <-respWaiter.done():
	case <-c.closeCh:
		c.notifyAndRmRequest(req.id(), ErrConnClosed)
	}
	return nil
}

// updatePushSetting Every time the push setting is updated,
// the setting version number will be incremented by 1.
func (c *ClientConn) updatePushSetting(ctx context.Context, height uint64,
	callback func([]syncSetting), kvs ...sp.Setting) ([]syncSetting, error) {
	version := atomic.AddUint32(&c.settingVersion, 1)
	settings := c.genSettings(version, height, kvs...)
	w := pushSettingUpdateWriter(settings)

	c.logger.Debugf("connection [%s] update push, setting version [%d], content: [%v]",
		c.NodeID(), c.settingVersion, settings)

	if err := c.sendSettingFrameRequest(ctx, version, w, func() {
		if callback != nil {
			callback(settings)
		}
	}); err != nil {
		return nil, err
	}
	return settings, nil
}

func (c *ClientConn) updateWindowSize(h uint64, s uint16) error {
	w := syncPushWindowUpdateWriter(h, s)
	return c.sendNormalFrameRequest(w)
}

// allow data wraparound
func (c *ClientConn) getRequestID() uint16 {
	return uint16(atomic.AddUint32(&c.requestID, 1))
}

// PullBlock Initiate a pull block request to the remote node.
// Requests with the same block height and the same sync mode are considered as one request,
// and only processed once.
func (c *ClientConn) PullBlock(ctx context.Context, req types.BlockSyncRequest) ([]types.DataFragment, error) {
	if req.Num <= 0 {
		return nil, fmt.Errorf("request.Num must be positive value")
	}
	inReq := toInternalSyncRequest(req)
	// generate unique key which is used to identify the request
	k := inReq.Key()
	v, err, _ := c.singleCall.Do(k, func() (interface{}, error) {
		id := c.getRequestID()
		requestKey, frame := inReq.syncDataPullWriter(id)
		// writer who knows how to serialize the request.
		resp, err := c.requestNormalFrameRequest(ctx, requestKey, frame)
		if err != nil {
			return nil, err
		}
		if result, ok := resp.([][]byte); ok {
			if len(result) == 0 {
				c.logger.Warnf("pull block[%d] from [%s] failed, no data", req.Height, c.NodeID())
				return nil, fmt.Errorf("no data")
			}
			fragments := make([]types.DataFragment, 0, len(result))
			for i, d := range result {
				fragments = append(fragments, types.DataFragment{
					Height: req.Height + uint64(i),
					Data:   d,
				})
			}
			return fragments, nil
		}
		return nil, fmt.Errorf("failed to pull block")

	})
	if err != nil {
		return nil, err
	}
	return v.([]types.DataFragment), nil
}

// requestNormalFrameRequest send a request to the remote node and wait for the response.
// If the writer returns an error when writing the frame, this function will return
// the error immediately. If the response is received, this function will return
// the response and nil error. If the response is not received within the
// given deadline, this function will return ErrConnClosed.
func (c *ClientConn) requestNormalFrameRequest(ctx context.Context, key string,
	writer frameWriter) (interface{}, error) {
	req := newFrameRequest(key, writer)
	resp, err := req.Request(ctx, SenderFunc(c.sendNormalFrameForResponse))
	if err != nil {
		c.requests.Remove(key)
	}
	return resp, err
}

// sendNormalFrameRequest send a request to the remote node and wait the result to be sent.
func (c *ClientConn) sendNormalFrameRequest(writer frameWriter) error {
	req := newFrameRequestWithoutKey(writer)
	return req.Send(context.TODO(), SenderFunc(c.sendNormalFrame))
}

// sendNormalFrameRequestAsync send a request to the remote node without waiting for the response.
func (c *ClientConn) sendNormalFrameRequestAsync(writer frameWriter) error {
	req := newFrameRequestWithoutKey(writer)
	return req.Send(context.TODO(), SenderFunc(c.sendNormalFrameAsync))
}

// sendSettingFrameRequest send a setting frame request to the remote node and wait for the response.
func (c *ClientConn) sendSettingFrameRequest(ctx context.Context, version uint32,
	frame frameWriter, call func()) error {
	req := newSettingFrameRequest(version, frame, call)
	return req.Request(ctx, SenderFunc(c.sendSettingFrame))
}

func (c *ClientConn) loopReadFrame() {
	for {
		select {
		case <-c.closeCh:
			c.logger.Infof("read frame from [%s] EOF", c.NodeID())
			return
		default:
		}
		frame, err := c.conn.Read()
		select {
		case c.rFrameCh <- readFrameResult{frame, err}:
		case <-c.closeCh:
			c.logger.Infof("read frame from [%s] EOF", c.NodeID())
			return
		}
	}
}

// func (c *ClientConn) check() error {
// 	switch c.state {
// 	case stateOpen:
// 		return nil
// 	case stateHalfCloseRemote, stateHalfCloseLocal, stateClose:
// 		return ErrConnClosed
// 	default:
// 		return ErrBadConnState
// 	}
// }

// processFrameResult process the frames received.
// If error occurred when reading will ignore this frame,
// EOF error means the connection is closed by remote,
// then the local side connection needs to exit the service.
// No error, process the frame according to the proto type.
// Return true to continue reading, otherwise stop.
func (c *ClientConn) processFrameResult(result readFrameResult) bool {
	err := result.err
	if err != nil {
		if err == io.EOF {
			c.logger.Infof("read frame from [%s] end: %v", c.NodeID(), err)
			return false
		}
		c.logger.Errorf("received frame from [%s] error: %v", c.NodeID(), err)
		return true
	}
	frm := result.frame

	// c.logger.Infof("received frame[%v] from [%s]", frm.Header(), c.NodeID())

	switch frm.Header().Type {
	case typeDataPush:
		err = c.processPushDataFrame(frm.(dataPushFrame))
	case typeDataPull:
		err = c.processPullDataFrame(frm.(dataPullFrame))
	case typeFinish:
		err = c.processFinishFrame(frm.(finishFrame))
	case typePing:
		err = c.processPingFrame(frm.(pingFrame))
	}
	if err != nil {
		c.logger.Warnf("client connect[%s] process message[%d][%d], error: %v",
			c.NodeID(), frm.Header().Type, frm.Header().Flag, err)
	}
	return true
}

// settingAck processes the acknowledgment for a settings frame.
// It ensures that there is exactly one setting and that its ID matches the expected version ID.
// If the version ID does not match, or if the response cannot be notified, an error is returned.
func (c *ClientConn) settingAck(ss *settings) error {
	// Check that there is exactly one setting in the settings frame
	if ss.SettingNum() != 1 {
		return errBadValue
	}

	var stn syncSetting
	// Extract the setting from the settings frame
	ss.ForEach(func(st syncSetting) {
		stn = st
	})

	// Verify that the setting ID is the expected sync setting version ID
	if stn.ID != idSyncSettingVersion {
		return errBadValue
	}

	// Notify the response with the version value
	if !c.notifyAndRmRequest(fmt.Sprintf("%d", uint32(stn.Val)), nil) {
		return fmt.Errorf("version %d not exist", stn.Val)
	}

	return nil
}

// processPushDataFrame process the push data frame.
// Respond push reset message when local push stream is closed.
// Frame with push end flag or push reset flag means the peer's push has been closed,
// close the local push stream.
// Normally, send data to the push stream.
func (c *ClientConn) processPushDataFrame(pf dataPushFrame) error {
	if pf.isSettingAck() {
		settings, _ := pf.Payload().(*settings)
		return c.settingAck(settings)
	}

	if c.pushStream == nil {
		// c.logger.Debugf("connection [%s] receive push data, but push stream doesn't exist", c.NodeID())
		_ = c.sendNormalFrameRequestAsync(syncDataPushResetWriter())
		return nil
	}

	if pf.isData() {
		d := pf.PushData()
		c.pushStream.push(dataWithVersion{
			settingVersion: d.version,
			data: types.DataFragment{
				Height: d.height,
				Data:   d.d,
			},
		})
		return nil
	}

	if pf.isReset() {
		c.pushStream.closeByRemote(ierrs.ErrCodeNon)
		return nil
	}
	if pf.isEnd() {
		c.pushStream.closeByRemote(ierrs.ErrCode(pf.PushEndInfo().code))
		return nil
	}
	return nil
}

// processPullDataFrame process data pull frame with ack flag.
// Send the data to the waiter.
func (c *ClientConn) processPullDataFrame(pf dataPullFrame) error {
	if !pf.isAck() {
		return errIllegalMessage
	}
	resp := pf.pullData()
	k := keyOf(resp)
	if resp.errCode == 0 {
		c.notifyAndRmRequest(k, resp.datas)
	} else { //errCode != 0 means error occurred at server side should been known by client.
		c.notifyAndRmRequest(k, ierrs.ErrCode(resp.errCode))
	}

	return nil
}

func (c *ClientConn) notifyAndRmRequest(key string, resp interface{}) bool {
	if w := c.requests.Remove(key); w != nil {
		w.notify(resp)
		return true
	}
	return false
}

// processFinishFrame close connection when received the finish frame.
func (c *ClientConn) processFinishFrame(_ finishFrame) error {
	c.closeByRemote()
	return nil
}

// processPingFrame process ping frame with ack.
func (c *ClientConn) processPingFrame(pf pingFrame) error {
	if pf.IsAck() {
		c.notifyAndRmRequest(string(pf.Key()), nil)
		return nil
	}
	w := syncPingAckWriter(pf.Key())
	return c.sendNormalFrameRequestAsync(w)
}

func (c *ClientConn) destroyPushStream() {
	if c.pushStream != nil {
		c.pushStream = nil
		c.settingVersion = 0
	}
}

// Close send a finish frame to the peer if the state of conn is open.
// When the message is actually sent out,
// close the connection and don't care whether there is an error in sending.
func (c *ClientConn) Close() error {
	if c.state == stateOpen {
		c.logger.Infof("close the connection [%s]", c.NodeID())
		return c.sendNormalFrameRequest(syncFinishWriter())
	}
	return nil
}

func (c *ClientConn) closeByLocal() {
	c.close(stateHalfCloseLocal)
}

func (c *ClientConn) closeByRemote() {
	c.close(stateHalfCloseRemote)
}

func (c *ClientConn) close(state connState) {
	if c.pushStream != nil {
		c.pushStream.closeByLocal()
	}
	if c.state == stateOpen {
		c.logger.Debugf("close the connection [%s] with state[%s]", c.NodeID(), state)
		c.state = state
		close(c.closeCh)
	}
}

// CloseReason represents the reason of  stream close
type CloseReason struct {
	Sent uint64 // At is the height of the block
	Code ierrs.ErrCode
}

// PushStream represents a push channel.
type PushStream struct {
	conn         *ClientConn
	state        connState
	fromHeight   uint64
	wc           *windowController //ring buffer
	settings     *settingList
	settingAvail [2]*settingLinker
	// expectCh     chan uint64
	closeCh chan CloseReason //remote close channel
	// assist       bool
	heightReceived uint64
	// the reason of close
	closeCode ierrs.ErrCode
}

func newPushStream(conn *ClientConn, s *setting) *PushStream {
	height := s.blockHeight
	ps := &PushStream{
		conn:           conn,
		wc:             newWindowController(height, s.WindowSize),
		fromHeight:     height,
		state:          stateOpen,
		settings:       newSettingList(),
		closeCh:        make(chan CloseReason, 1),
		heightReceived: height - 1,
	}
	ps.settings.Push(s)
	ps.settingAvail[0] = ps.settings.Front()
	return ps
}

func (s *PushStream) valid() bool {
	return s.state == stateOpen
}

// push First, check whether the pushed data is valid data by comparing  the version number of push setting,
// if yes, put data in the window otherwise discard it.
// If the expected height is not greater then the data's height, trigger assisted pull.
// Switch setting if the expected height reaches the height of the next setting to take effect.
func (s *PushStream) push(fragment dataWithVersion) {
	if !s.fragmentValid(fragment.data.Height, fragment.settingVersion) {
		s.conn.logger.Debugf("invalid fragment, height[%d], version[%d],current version: %d",
			fragment.data.Height, fragment.settingVersion, s.settingAvail[0].version)
		return
	}

	expect, _ := s.wc.put(fragment.data)
	// s.conn.logger.Debugf("push fragment, height[%d], version[%d], expect: %d, current version: %d",
	// 	fragment.data.Height, fragment.settingVersion, expect, s.settingAvail[0].version)
	if s.settingAvail[1] != nil && expect >= s.settingAvail[1].blockHeight {
		s.settings.Remove(s.settingAvail[0])
		s.settingAvail[0] = s.settingAvail[1]
		s.settingAvail[1] = s.settingAvail[0].Next()
	}
	if s.heightReceived < fragment.data.Height {
		s.heightReceived = fragment.data.Height
	}
}

// assistPull assist in pulling block height data is lost during push
// through height-corresponding setting items.
// Pull failure will ignore this height.
// func (s *PushStream) assistPull() {
// 	for {
// 		h, ok := <-s.expectCh
// 		if !ok {
// 			return
// 		}
// 		sett := s.settings.GetByHeight(h)
// 		if sett == nil {
// 			continue
// 		}
// 		datas, err := s.conn.PullBlock(types.BlockSyncRequest{
// 			Height: h,
// 			Num:    1,
// 			NodePattern: types.NodePattern{
// 				NodesTotal: sett.nodes,
// 				Index:      sett.index,
// 			},
// 		})
// 		fmt.Println("assistPull---", h)
// 		if err != nil || len(datas) == 0 {
// 			continue
// 		}
// 		s.window.put(datas[0])
// 	}
// }

// fragmentValid Compare whether the version number is consistent with
// the version number of the setting item corresponding to the height
func (s *PushStream) fragmentValid(height uint64, version uint32) bool {
	if height >= s.settingAvail[0].blockHeight {
		if s.settingAvail[1] == nil || height < s.settingAvail[1].blockHeight {
			return s.settingAvail[0].version == version
		}
	}
	sett := s.settings.GetByHeight(height)
	if sett == nil {
		return false
	}
	return sett.version == version
}

// UpdateSetting update setting item and update setting item in use.
func (s *PushStream) UpdateSetting(ctx context.Context, height uint64, kvs ...sp.Setting) error {
	if !s.valid() {
		return fmt.Errorf("invalid stream, you can new another")
	}
	_, err := s.conn.updatePushSetting(ctx, height, func(settings []syncSetting) {
		s.settings.Push(genSetting(settings))
		// reset the window, if the excepted height is greater than or equal to the height,
		// the new setting takes effect.
		if except := s.wc.reset(height); except >= height {
			s.settings.Remove(s.settingAvail[0])
		}
		s.settingAvail[0] = s.settings.Front()
		s.settingAvail[1] = s.settingAvail[0].Next()
		if s.heightReceived >= height {
			s.heightReceived = height - 1
		}
	}, kvs...)

	if err != nil {
		s.conn.logger.Warnf("connection [%s] update push setting error: %v", s.conn.NodeID(), err)
		return err
	}
	return nil
}

// note: 边界问题，pushStream关闭和发送窗口更新的空窗期
func (s *PushStream) increaseWindow(h uint64, n uint16) {
	if s.valid() {
		if err := s.conn.updateWindowSize(h, n); err != nil {
			s.conn.logger.Errorf("connection [%s] increase window size error: %v", s.conn.NodeID(), err)
		}
	}
}

// IsClosed check whether the stream is closed.
// If the stream is closed, return close reason
func (s *PushStream) IsClosed() (bool, CloseReason) {
	return !s.valid(), CloseReason{
		Sent: s.heightReceived,
		Code: s.closeCode,
	}
}

// Fetch get data arranged by height one by one from the cache window.
// If data does not exist make a pull attempt.
// The bool returned is false means the data is not exist.
func (s *PushStream) Fetch() (types.DataFragment, bool) {
	d, ok := s.wc.fetch()
	if height, size := s.wc.needUpdateWindow(); size > 0 {
		s.increaseWindow(height, size)
	}

	if !ok && s.valid() {
		sett := s.settings.GetByHeight(d.Height)
		ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
		defer cancel()
		pds, err := s.conn.PullBlock(ctx, types.BlockSyncRequest{
			Height:    d.Height,
			Num:       1,
			WithRWSet: sett.WithRWSet,
			ModeData:  sett.ModeData,
		})
		s.conn.logger.Debugf("connection [%s] fetch to pull block[%d], version:%d",
			s.conn.NodeID(), d.Height, sett.version)
		if err == nil {
			return pds[0], true
		}
	}
	return d, ok
}

// ListenClose listen to the event triggered by the close the push stream.
func (s *PushStream) ListenClose() <-chan CloseReason {
	return s.closeCh
}

// HeightReadable next read height in the push stream window
func (s *PushStream) HeightReadable() uint64 {
	return s.wc.readHeight()
}

// HeightWritten maximum height already written in push stream window ignoring data holes
func (s *PushStream) HeightWritten() uint64 {
	return s.wc.writeMaxHeight()
}

// Close close the push stream. Send a push end frame if the state of push stream is open.
// Close without caring whether the message notification has been received by the peer.
func (s *PushStream) Close() {
	if s.state == stateOpen {
		s.conn.logger.Debugf("close the push stream of connection [%s]", s.conn.NodeID())
		_ = s.conn.sendNormalFrameRequestAsync(syncDataPushEndWriter(0))
	}
}

func (s *PushStream) closeByLocal() {
	s.close(stateHalfCloseLocal, ierrs.ErrCodeNon)
}

func (s *PushStream) closeByRemote(code ierrs.ErrCode) {
	s.close(stateHalfCloseRemote, code)
}

func (s *PushStream) close(state connState, code ierrs.ErrCode) {
	if s.state == stateOpen {
		// fmt.Println("close push stream with:", state)
		s.conn.logger.Debugf("stream of connect [%s] closed with [%s] for [%s]", s.conn.NodeID(), state, code)
		s.state = state
		s.closeCode = code
		select {
		case s.closeCh <- CloseReason{Sent: s.heightReceived, Code: code}:
		default:
		}
		s.conn.destroyPushStream()
	}
}

type ringEle struct {
	valid bool
	data  types.DataFragment
}
