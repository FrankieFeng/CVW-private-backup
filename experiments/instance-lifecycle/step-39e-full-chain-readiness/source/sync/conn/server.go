/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package conn

import (
	"context"
	"io"
	"sync"

	"chainmaker.org/chainmaker/sync/v2/internal/controller"
	"chainmaker.org/chainmaker/sync/v2/internal/rand"
	sp "chainmaker.org/chainmaker/sync/v2/setting"

	"chainmaker.org/chainmaker/protocol/v2"
	"chainmaker.org/chainmaker/sync/v2/internal/errors"
	"chainmaker.org/chainmaker/sync/v2/types"
)

// BlockHandler handle the block sync request.
type BlockHandler interface {
	// ServeBlock handle the block sync request and write response to BlockWriter.
	ServeBlock(BlockWriter, *types.BlockSyncRequest)
}

// BlockWriter a interface to write data or error.
type BlockWriter interface {
	// Write writes a types.DataFragment to a destination and returns an error if any.
	Write(types.DataFragment) error
	// If the data processing process is terminated unexpectedly,
	//the termination error will be notified to the peer
	Terminate(err errors.ErrCode)
	// Get the id of the peer node
	NodeID() string
}

// BlockFlusher a interface to flush data
type BlockFlusher interface {
	// Flush the data cached to underlay io.
	Flush() error
}

// ServerConn a server connection
type ServerConn struct {
	state    connState
	conn     FrameConn
	rFrameCh chan readFrameResult
	wFrameCh chan frameWriteRequest
	closeCh  chan struct{}
	pusher   *pusher
	handler  BlockHandler
	// logger
	logger protocol.Logger
	mu     sync.Mutex //guard pings
	pings  map[string]chan struct{}
	rGroup *controller.GoRoutineGroup
}

// NewServerConn create a server connection.
func NewServerConn(conn FrameConn, logger protocol.Logger) *ServerConn {
	sc := &ServerConn{
		conn:     conn,
		rFrameCh: make(chan readFrameResult, frameBufferSize),
		wFrameCh: make(chan frameWriteRequest, frameBufferSize),
		closeCh:  make(chan struct{}),
		pings:    make(map[string]chan struct{}),
		rGroup:   controller.NewGoRoutineGroup(),
		logger:   logger,
	}
	return sc
}

// Serve start the read and write process
// The parameter "h" must not be nil.
// The loop will exit if the peer connection or the local is closed
func (c *ServerConn) Serve(h BlockHandler) error {
	if c.state == stateOpen {
		return ErrConnAlreadyServe
	}
	if h == nil {
		return ErrBlockHandlerNil
	}

	c.state = stateOpen
	c.handler = h

	c.logger.Debugf("server connection[%p] serves for node: %s", c, c.NodeID())
	defer func() {
		if c.pusher != nil {
			c.pusher.closeByLocal()
		}
		_ = c.conn.Close()
		c.rGroup.Wait()
		c.logger.Debugf("server connection[%p] exits serve for node: %s", c, c.NodeID())
	}()
	// start the read goroutine
	c.rGroup.Run(c.readFrame)
	for {
		select {
		case <-c.closeCh:
			return ErrConnClosed
		default:
		}
		select {
		case wr := <-c.wFrameCh:
			c.writeFrameRequest(wr)
		case result := <-c.rFrameCh:
			if !c.processFrameResult(result) {
				c.closeByRemote()
				return errCloseRemote
			}
		case <-c.closeCh:
			return ErrConnClosed
		}
	}
}

// writeFrameRequest write the frame to net and notify those waiting for the write result
// If the frame is "syncDataPushEndWriter" close the push stream
// "syncFinishWriter" close the connection
func (c *ServerConn) writeFrameRequest(wr frameWriteRequest) {
	_ = c.writeFrameAndNotify(wr.req.getFrame(), wr.done)
}

// writeFrame write the frame to net.
// It can be called directly in the main process to send messages as soon as possible.
// If the frame is "syncDataPushEndWriter" closes the push stream,
// if "syncFinishWriter" closes the connection
func (c *ServerConn) writeFrame(frame frameWriter) error {
	return c.writeFrameAndNotify(frame, nil)
}

func (c *ServerConn) writeFrameAndNotify(frame frameWriter, done chan<- error) error {
	err := c.conn.Write(frame)

	if done != nil {
		select {
		case done <- err:
		default:
		}
	}
	// c.logger.Infof("write frame [%v] to [%s]", c.pfr.framer.wbuf[:7], c.NodeID())
	switch frame := frame.(type) {
	case dataPushFrame:
		if frame.isEnd() {
			if c.pusher != nil {
				c.pusher.closeByLocal()
			}
		}
	case finishFrame:
		c.closeByLocal()
	}
	return err

}

// NodeID the ID of the peer node
func (c *ServerConn) NodeID() string {
	return c.conn.RemoteAddr().String()
}

func (c *ServerConn) readFrame() {
	for {
		select {
		case <-c.closeCh:
			c.logger.Infof("exit read frame from [%s]", c.NodeID())
			return
		default:
		}

		fr, err := c.conn.Read()
		select {
		case c.rFrameCh <- readFrameResult{fr, err}:
		case <-c.closeCh:
			c.logger.Infof("exit read frame from [%s]", c.NodeID())
			return
		}
	}
}

// sendFrame send a request to the remote node and wait for sending to complete.
// Do not call it in the "Serve" main process, which will cause the main process to be blocked.
func (c *ServerConn) sendFrame(frame frameWriter) error {
	select {
	case <-c.closeCh:
		return ErrConnClosed
	default:
	}

	done := make(chan error, 1)
	select {
	case c.wFrameCh <- frameWriteRequest{req: newFrameRequestWithoutKey(frame), done: done}:
	case <-c.closeCh:
		return ErrConnClosed
	}

	select {
	case err := <-done:
		return err
	case <-c.closeCh:
		return ErrConnClosed
	}
}

// sendFrameAsync send a request to the remote node without caring whether it is sent successfully.
func (c *ServerConn) sendFrameAsync(frame frameWriter) error {
	select {
	case <-c.closeCh:
		return ErrConnClosed
	case c.wFrameCh <- frameWriteRequest{req: newFrameRequestWithoutKey(frame)}:
		return nil
	}
}

// processFrameResult process the frames received.
// If error occurred when reading will ignore this frame,
// EOF error means the connection is closed by remote,
// then the local side connection needs to exit the service.
// No error, process the frame according to the proto type.
// Return true to continue reading, otherwise stop.
func (c *ServerConn) processFrameResult(result readFrameResult) bool {
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
	// case typePushSetting:
	// 	err = c.processPushSettingFrame(frm.(pushSettingFrame))
	case typeDataPush:
		err = c.processPushDataFrame(frm.(dataPushFrame))
	case typeDataPull:
		err = c.processPullDataFrame(frm.(dataPullFrame))
	case typePushWindowUpdate:
		err = c.processPushWindowUpdate(frm.(pushWindowUpdateFrame))
	case typePing:
		err = c.processPingFrame(frm.(pingFrame))
	// case syncProtoReset:
	// 	return false
	case typeFinish:
		err = c.processConnFinish(frm.(finishFrame))
	}
	if err != nil {
		c.logger.Warnf("server connect[%s] process message[%d][%d], error: %v",
			c.NodeID(), frm.Header().Type, frm.Header().Flag, err)
	}
	return true
}

// Ping send a ping message to test connection.
// #nosec G404
func (c *ServerConn) Ping(ctx context.Context) error {
	ch := make(chan struct{})
	var p [8]byte
	for {
		if _, err := rand.Read(p[:]); err != nil {
			return err
		}
		c.mu.Lock()
		k := string(p[:])
		// check for dup before insert
		if _, found := c.pings[k]; !found {
			c.pings[k] = ch
			c.mu.Unlock()
			defer func() {
				c.mu.Lock()
				delete(c.pings, k)
				c.mu.Unlock()
			}()
			break
		}
		c.mu.Unlock()
	}

	if err := c.sendFrame(syncPingWriter(p[:])); err != nil {
		c.logger.Warnf("server connect[%s] send ping error: %v", c.NodeID(), err)
		return err
	}

	select {
	case <-ch:
		return nil
	case <-ctx.Done():
		return ctx.Err()
	case <-c.closeCh:
		// connection closed
		return ErrConnClosed
	}
}

// processPushSettingFrame process the push setting frame.
// Both cases are legal:
// 1. the frame with init flag and pusher does not exist, then create a pusher and start push.
// 2. pusher already exists and the frame with update flag, then update the pusher's setting item.
// func (c *ServerConn) processPushSettingFrame(sf pushSettingFrame) error {
// 	if sf.isInit() || sf.isUpdate() {
// 		var (
// 			version    uint32
// 			initWindow int32
// 		)
// 		ss := *(sf.Payload().(*settings))
// 		ss.ForEach(func(setting syncSetting) {
// 			if setting.ID == idSyncSettingVersion {
// 				version = uint32(setting.Val)
// 			} else if setting.ID == idSyncSettingInitWindow {
// 				initWindow = int32(setting.Val)
// 			}
// 		})

// 		if sf.isInit() && c.pusher != nil {
// 			c.logger.Warnf("connection [%s] receive init setting [%d], but stream already exist", c.NodeID(), version)
// 			return errUnexpectedMessage
// 		}
// 		if sf.isUpdate() && c.pusher == nil {
// 			c.writeFrame(frameWriterRequestNoWait(pushSettingAckWriter(version)))
// 			c.writeFrame(frameWriterRequestNoWait(syncDataPushResetWriter()))
// 			c.logger.Warnf("connection [%s] receive updated setting [%d], but stream doesn't exist", c.NodeID(), version)
// 			return errUnexpectedMessage
// 		}

// 		// if err := c.checkSettings(settings); err != nil {
// 		// 	return err
// 		// }
// 		if sf.isInit() {
// 			c.logger.Debugf("create new push stream[%s] version [%d], content: [%v]",
// 				c.NodeID(), version, ss)
// 			c.pusher = newPusher(c, genSetting(ss))
// 			c.pusher.updateWindowSize(initWindow)
// 			go c.pusher.serve(c.handler)
// 		} else {
// 			c.logger.Debugf("push stream[%s] update setting version [%d], content: [%v]",
// 				c.NodeID(), version, ss)
// 			c.pusher.updateSetting(genSetting(ss))
// 		}

// 		c.writeFrame(frameWriterRequestNoWait(pushSettingAckWriter(version)))
// 		return nil
// 	}
// 	return errIllegalMessage
// }

// processPushDataFrame just processes the frame with the push end flag and push reset flag.
// If pusher exists, close it.
func (c *ServerConn) processPushDataFrame(pf dataPushFrame) error {
	if pf.isInit() {
		return c.initPushStream(pf)
	}
	if pf.isUpdate() {
		return c.updatePushStream(pf)
	}

	if pf.isEnd() || pf.isReset() {
		if c.pusher != nil {
			c.logger.Debugf("connection [%s] stream closed by client", c.NodeID())
			c.pusher.closeByRemote()
		}
	}
	return nil
}

func (c *ServerConn) initPushStream(pf dataPushFrame) error {
	var (
		version    uint32
		initWindow int32
	)
	ss := *(pf.Payload().(*settings))
	ss.ForEach(func(setting syncSetting) {
		if setting.ID == idSyncSettingVersion {
			version = uint32(setting.Val)
		} else if setting.ID == sp.IdSyncSettingInitWindow {
			initWindow = int32(setting.Val)
		}
	})

	if c.pusher != nil {
		c.logger.Warnf("connection [%s] receive init setting [%d], but stream already exist", c.NodeID(), version)
		return errUnexpectedMessage
	}

	c.logger.Debugf("create new push stream[%s] version [%d], content: [%v]",
		c.NodeID(), version, ss)
	c.pusher = newPusher(c, genSetting(ss))
	c.pusher.updateWindowSize(initWindow)
	_ = c.writeFrame(pushSettingAckWriter(version))

	go c.pusher.serve(c.handler)
	return nil
}

// updatePushStream just processes the data push frame.
// Look for the push version from the settings and ack with it.
// If the push stream doesn't exist, send a ack first, because the client is waiting for the ack, then
// send a reset frame to close the push stream by client.
func (c *ServerConn) updatePushStream(pf dataPushFrame) error {
	var (
		version uint32
	)
	ss := *(pf.Payload().(*settings))
	ss.ForEach(func(setting syncSetting) {
		if setting.ID == idSyncSettingVersion {
			version = uint32(setting.Val)
		}
	})

	if c.pusher == nil {
		_ = c.sendFrameAsync(pushSettingAckWriter(version))
		_ = c.sendFrameAsync(syncDataPushResetWriter())
		c.logger.Warnf("connection [%s] receive updated setting [%d], but stream doesn't exist", c.NodeID(), version)
		return errUnexpectedMessage
	}

	c.logger.Debugf("push stream[%s] update setting version [%d], content: [%v]",
		c.NodeID(), version, ss)
	c.pusher.updateSetting(genSetting(ss))
	_ = c.sendFrameAsync(pushSettingAckWriter(version))
	// c.writeFrame(frameWriterRequestNoWait(pushSettingAckWriter(version)))
	return nil
}

// func (c *ServerConn) checkSettings(settings []syncSetting) error {
// 	// var (
// 	// 	detecte = [...]struct {
// 	// 		expect bool
// 	// 	}{
// 	// 		SyncSettingNodes: {
// 	// 			expect: true,
// 	// 		},
// 	// 	}
// 	// )
// 	// for _, s := range settings {
// 	// 	if detecte[s.ID].expect {
// 	// 		// detecte[s.ID].got = s.Val > 0
// 	// 		if s.Val <= 0 {
// 	// 			return ErrBadValue
// 	// 		}
// 	// 	}
// 	// }
// 	return nil
// }

// processPullDataFrame just processes the data pull frame without ack flag.
func (c *ServerConn) processPullDataFrame(pf dataPullFrame) error {
	if pf.isAck() {
		return errIllegalMessage
	}
	req := pf.pullRequest()
	go func() {
		sr := types.BlockSyncRequest{
			Height:    req.height,
			Num:       int(req.num),
			WithRWSet: req.withRWSet,
			ModeData:  sp.SyncModeData(req.mode),
		}
		w := &pullWriter{
			id:   req.id,
			conn: c,
			req:  toInternalSyncRequest(sr),
		}
		// Instead of calling flush in defer, it is called by the user so that
		// the user can perceive whether there is an error in flush
		// defer func() {
		// 	// w.flush()
		// }()
		c.handler.ServeBlock(w, &sr)
	}()
	return nil
}

// processPushWindowUpdate just processes the window update frame.
// If pusher exists, update the window size, otherwise send a push reset frame.
func (c *ServerConn) processPushWindowUpdate(pf pushWindowUpdateFrame) error {
	if c.pusher == nil {
		_ = c.writeFrame(syncDataPushResetWriter())
		return nil
	}
	// ws := pf.Increment()
	height, size := pf.window()
	// absolute window size
	if pf.isReset() {
		c.pusher.resetWindowSize(height, int32(size))
	} else {
		c.pusher.updateWindowSize(int32(size))
	}
	return nil
}

func (c *ServerConn) processConnFinish(pf finishFrame) error {
	c.closeByRemote()
	return nil
}

func (c *ServerConn) processPingFrame(pf pingFrame) error {
	if pf.IsAck() {
		c.mu.Lock()
		defer c.mu.Unlock()
		if c, ok := c.pings[string(pf.Key())]; ok {
			close(c)
		}
		return nil
	}
	w := syncPingAckWriter(pf.Key())
	return c.sendFrameAsync(w)
}

// Close send a finish frame to the peer if the state of conn is open.
// When the message is actually sent out,
// close the connection and don't care whether there is an error in sending.
func (c *ServerConn) Close() error {
	if c.state == stateOpen {
		return c.sendFrame(syncFinishWriter())
	}
	return nil
}

// closeByLocal close the connection by self
func (c *ServerConn) closeByLocal() {
	c.close(stateHalfCloseLocal)
}

// closeByRemote close the connection by remote
func (c *ServerConn) closeByRemote() {
	c.close(stateHalfCloseRemote)
}

func (c *ServerConn) close(state connState) {
	if c.state == stateOpen {
		c.logger.Debugf("close the connection [%s] with state[%s]", c.NodeID(), state)
		c.state = state
		close(c.closeCh)
	}
}

type pusher struct {
	conn         *ServerConn
	settings     *settingList
	settingInUse *setting
	nextSetting  *setting
	flow         *pushFlowWithHeight
	state        connState
	windowInit   int
}

// newPusher create a new pusher for a connection with the init push setting
// and start a goroutine to process the push request
func newPusher(conn *ServerConn, setting *setting) *pusher {
	settings := newSettingList()
	settings.Push(setting)
	p := &pusher{
		conn:        conn,
		settings:    settings,
		nextSetting: setting,
		flow:        newPushFlowWithHeight(setting.blockHeight - 1),
		state:       stateOpen,
		windowInit:  setting.WindowSize,
	}
	return p
}

// serve let the block handler process the push request in turn according the list of vaild settings.
// The loop will exit when the handler is finished processing and no setting items are available
// or the stream is closed by local or remote.
func (p *pusher) serve(handler BlockHandler) {
	var abortCode errors.ErrCode
	defer func() {
		if p.state == stateOpen {
			_ = p.conn.sendFrameAsync(syncDataPushEndWriter(uint32(abortCode)))
		}
	}()
	for {
		if p.state != stateOpen || p.nextSetting == nil {
			return
		}
		p.settingInUse = p.nextSetting
		p.nextSetting = p.getNextValidSetting()
		writer := &pushWriter{
			pusher:  p,
			version: p.settingInUse.version,
		}
		handler.ServeBlock(writer, &types.BlockSyncRequest{
			Height:    p.settingInUse.blockHeight,
			WithRWSet: p.settingInUse.WithRWSet,
			ModeData:  p.settingInUse.ModeData,
		})
		if writer.errCode > 0 {
			abortCode = writer.errCode
			return
		}
	}
}

func (p *pusher) getNextValidSetting() *setting {
	for linker := p.settings.Front(); linker != nil; {
		if linker.Setting().version > p.settingInUse.version {
			return linker.Setting()
		}
		t := linker
		linker = t.Next()
		p.settings.Remove(t)
	}
	return nil
}

func (p *pusher) updateSetting(s *setting) {
	p.settings.Push(s)
	nextSetting := p.getNextValidSetting()
	if p.nextSetting != nextSetting {
		p.nextSetting = nextSetting
		p.flow.fallBack(nextSetting.blockHeight - 1) // wake up those waiting for push token
	}
}

func (p *pusher) updateWindowSize(n int32) {
	p.flow.add(n)
}

func (p *pusher) resetWindowSize(h uint64, n int32) {
	p.flow.reset(h, n)
}

// pushBlock push the block data to peer until the push is closed or the setting item invalid.
func (p *pusher) pushBlock(d dataWithVersion) error {

	check := func() error {
		if p.state != stateOpen {
			return errors.ErrPushEOF
		}
		//check if a new configuration is in effect, if so, current EOF.
		if p.nextSetting != nil && d.data.Height >= p.nextSetting.blockHeight {
			p.conn.logger.Debugf("pusher[%s] witch to setting[%d], has sent to[%d]",
				p.conn.NodeID(), p.nextSetting.blockHeight, d.data.Height)
			p.flow.fallBack(p.nextSetting.blockHeight - 1)
			return errors.ErrPushEOF
		}
		return nil
	}
	// Because "take" call will wait, call take first to avoid missing environment changes after waiting.
	// If "check" call first, we can't check right away when environment changes occur while waiting
	_ = p.flow.take(d.data.Height)
	if err := check(); err != nil {
		return err
	}

	return p.conn.sendFrame(syncDataPushWriter(&dataPushMessage{
		height:  d.data.Height,
		version: d.settingVersion,
		d:       d.data.Data,
	}))
}

func (p *pusher) closeByLocal() {
	p.close(stateHalfCloseLocal)
}

func (p *pusher) closeByRemote() {
	p.close(stateHalfCloseRemote)
}

func (p *pusher) close(state connState) {
	if p.state == stateOpen {
		p.conn.logger.Debugf("close the pusher of connection[%s] with state[%s]", p.conn.NodeID(), state)
		p.state = state
		// p.flow.add(int32(p.windowInit)) //唤醒阻塞在等待窗口的流程
		p.flow.fallBack(0)
		p.conn.pusher = nil
		return
	}
}

type pushWriter struct {
	pusher  *pusher
	version uint32
	errCode errors.ErrCode
}

// Write writes a data fragment to the pusher.
// It calls pushBlock with a dataWithVersion struct that contains the writer's version and the data fragment.
func (w *pushWriter) Write(d types.DataFragment) error {
	return w.pusher.pushBlock(dataWithVersion{
		settingVersion: w.version,
		data:           d,
	})
}

// If a terminating error occurs, the stream will be forcibly closed and the peer notified of the closing error
func (w *pushWriter) Terminate(code errors.ErrCode) {
	w.errCode = code
}

func (w *pushWriter) NodeID() string {
	return w.pusher.conn.NodeID()
}

type pullWriter struct {
	id        uint16
	conn      *ServerConn
	req       blockSyncRequest
	fragments [][]byte
	errCode   errors.ErrCode
}

// Write append the data to cache without sending
func (w *pullWriter) Write(d types.DataFragment) error {
	w.fragments = append(w.fragments, d.Data)
	return nil
}

// Flush send the cached batch data to peer.
func (w *pullWriter) Flush() error {
	msg := &dataPullAckMessage{
		id:      w.id,
		errCode: uint32(w.errCode),
	}
	if w.errCode == errors.ErrCodeNon {
		msg.datas = w.fragments
	}
	return w.conn.sendFrame(syncDataPullAckWriter(msg))
}

func (w *pullWriter) NodeID() string {
	return w.conn.NodeID()
}

// If a termination error occurs, the buffered data will not be sent
func (w *pullWriter) Terminate(code errors.ErrCode) {
	w.errCode = code
}
