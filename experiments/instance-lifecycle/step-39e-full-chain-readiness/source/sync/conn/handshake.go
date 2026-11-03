package conn

import (
	"context"
	"fmt"
	"sync"
	"time"

	"chainmaker.org/chainmaker/sync/v2/internal/errors"
)

type (
	handshakeState struct {
		compressAlg     CompressionAlgType
		protocolVersion uint16
		dataFormat      uint16
		isCompleted     bool
	}
	// Negotiator negotiates the sync mechanism.
	Negotiator interface {
		Handshake(context.Context) (*handshakeState, error)
	}
)

// Client negotiates the sync mechanism as a client.
func hsClient(conn FrameConn, conf *handshakeConfig) Negotiator {
	c := &hsConn{
		conn:     conn,
		conf:     conf,
		isClient: true,
	}
	c.handshakeFnLocked = c.clientHandshake
	return c
}

// Server negotiates the sync mechanism as a server.
func hsServer(conn FrameConn, heightCheck func(height uint64) BlockSupportResult) Negotiator {
	c := &hsConn{
		conn: conn,
	}
	c.handshakeFnLocked = c.serverHandshake(heightCheck)
	return c
}

// Conn uses the underlying connection to negotiate and agree on the sync mechanism.
type hsConn struct {
	conn              FrameConn
	conf              *handshakeConfig
	handshakeMutex    sync.Mutex
	handshakeFnLocked func() error
	isClient          bool
	state             handshakeState
}

func (c *hsConn) Handshake(ctx context.Context) (*handshakeState, error) {
	if err := c.handshake(ctx); err != nil {
		return nil, err
	}
	state := c.state
	return &state, nil
}

// handshake implements the handshake process.
// It first checks if the connection is nil or if the client config is nil.
// Then it checks if the handshake is already completed.
// If the context is done, it sets the read deadline of the connection
// to the current time and waits for the handshake to finish.
// Otherwise it calls the handshake function.
func (c *hsConn) handshake(ctx context.Context) (ret error) {
	if c == nil {
		return fmt.Errorf("nil client connection")
	}
	if c.isClient && c.conf == nil {
		return fmt.Errorf("nil client config")
	}
	c.handshakeMutex.Lock()
	defer c.handshakeMutex.Unlock()
	if c.state.isCompleted {
		return nil
	}
	handshakeCtx, handshakeCancel := context.WithCancel(ctx)
	defer handshakeCancel()

	// If the context is done, set the read deadline of the connection
	// to the current time and wait for the handshake to finish.
	// Otherwise call the handshake function.
	if ctx.Done() != nil {
		done := make(chan struct{})
		interruptError := make(chan error, 1)
		defer func() {
			close(done)
			if err := <-interruptError; err != nil {
				_ = c.conn.SetReadDeadline(time.Time{})
			}
		}()

		go func() {
			select {
			case <-handshakeCtx.Done():
				_ = c.conn.SetReadDeadline(time.Now())
				interruptError <- handshakeCtx.Err()
			case <-done:
				interruptError <- nil
			}
		}()
	}

	return c.handshakeFnLocked()
}

// clientHandshake implements the handshake process as a client.
// It sends a handshake message to the server and waits for the server's response.
// It checks if the server's response is valid and then sends a handshake done message to the server.
func (c *hsConn) clientHandshake() error {
	// Construct the handshake message and send it to the server.
	msg := c.makeClientMsg(c.conf)
	if err := c.writeHandshakeFrame(clientHandshakeFrame(msg)); err != nil {
		return err
	}

	// Read the server's response and check if it is valid.
	respMsg, err := c.readHandshakeFrame()
	if err != nil {
		// fmt.Printf("client handshake error: %v\n", err)
		return err
	}
	serverMsg, ok := respMsg.(*serverHandshakeMsg)
	if !ok {
		// If the response is not a valid server handshake message, send an alert to the server.
		if err = c.sendAlert(alertUnexpectedMessage); err != nil {
			return err
		}
		// Return an error indicating that the handshake failed.
		return fmt.Errorf("invalid server handshake message")
	}

	// Check if the server is available.
	nodeDetect := c.conf.NodeDetect
	if nodeDetect == nil {
		// If the node detect function is not set, use the default one.
		nodeDetect = defaultNodeDetectFn
	}
	if err = nodeDetect(serverMsg.BlockSupportResult); err != nil {
		// If the node is not available, send an alert to the server.
		if err1 := c.sendAlert(alertNodeCantBeenUsed); err1 != nil {
			return err1
		}
		// Return an error indicating that the node is not available.
		return err
	}

	// Check if the handshake result is valid.
	if err := c.checkHandshakeResult(msg, serverMsg); err != nil {
		// fmt.Printf("client check handshake result error: %v\n", err)
		return errors.ErrCodeProtoIncompatible
	}

	// Send a handshake done message to the server.
	if err := c.writeHandshakeFrame(handshakeDoneFrame()); err != nil {
		return err
	}

	// Complete the handshake by setting the connection state.
	c.completeHandshake(serverMsg)
	return nil
}

// serverHandshake handles the server-side handshake process. It reads a handshake frame
// from the client, validates the message, performs a height check, and responds with
// a server handshake message. If any step fails, it sends an alert and returns an error.
func (c *hsConn) serverHandshake(heightCheck func(height uint64) BlockSupportResult) func() error {
	return func() error {
		// Read the client's handshake message
		msg, err := c.readHandshakeFrame()
		if err != nil {
			return err
		}

		// Assert the message is of type clientHandshakeMsg
		clientMsg, ok := msg.(*clientHandshakeMsg)
		if !ok {
			return fmt.Errorf("unexpected message type[%T], expect: clientHandshakeMsg", msg)
		}

		// Perform a height check and get the block support result
		resp := heightCheck(clientMsg.Height)
		if resp.Code.Occurred() {
			// Send an alert if the synchronization is unsupported
			if err = c.sendAlert(alertUnsupportedSync); err != nil {
				return err
			}
			return resp.Code
		}

		// Construct the server's handshake message with the support result
		serverMsg := c.makeServerMsg(clientMsg)
		serverMsg.BlockSupportResult = resp

		// Send the server handshake message back to the client
		if err = c.writeHandshakeFrame(serverHandshakeFrame(serverMsg)); err != nil {
			return err
		}

		// Read the client's handshake done message
		msg, err = c.readHandshakeFrame()
		if err != nil {
			return err
		}

		// Assert the message is of type handshakeDoneMsg
		_, ok = msg.(*handshakeDoneMsg)
		if !ok {
			// Send an alert if the message is unexpected
			if err := c.sendAlert(alertUnexpectedMessage); err != nil {
				return err
			}
			return fmt.Errorf("unexpected message type: handshakeDoneMsg")
		}

		// Complete the handshake process
		c.completeHandshake(serverMsg)
		return nil
	}
}

// makeClientMsg constructs a client handshake message based on the configuration.
// It takes the configuration as an argument and returns a pointer to a clientHandshakeMsg.
// The clientHandshakeMsg is constructed by copying the fields from the configuration.
// If the configuration does not specify a version, the default version is used.
// If the configuration does not specify a compression algorithm, the default compression algorithms are used.
func (c *hsConn) makeClientMsg(conf *handshakeConfig) *clientHandshakeMsg {
	var (
		compressionAlgs = conf.CompressionAlgTypes
	)
	msg := &clientHandshakeMsg{
		Height:             conf.FromHeight,
		SupportProtocol:    conf.Versions,
		SupportDataFormats: conf.DataFormats,
	}

	// If the configuration does not specify a version, use the default version.
	if len(msg.SupportProtocol) == 0 {
		msg.SupportProtocol = supportVersions
	}

	// If the configuration does not specify a compression algorithm, use the default compression algorithms.
	if len(compressionAlgs) == 0 {
		compressionAlgs = defaultCompressionAlgTypes
	}
	for _, alg := range compressionAlgs {
		msg.CompressionAlgs |= uint16(alg)
	}
	// If the configuration does not specify a data format, use the default data formats.
	if len(msg.SupportDataFormats) == 0 {
		msg.SupportDataFormats = defaultDataFormats
	}
	return msg
}

func (c *hsConn) makeServerMsg(clientMsg *clientHandshakeMsg) *serverHandshakeMsg {
	serverMsg := &serverHandshakeMsg{}
	for _, v := range clientMsg.SupportProtocol {
		for _, v2 := range supportVersions {
			if v == v2 {
				serverMsg.Protocol = v
			}
		}
	}

	for _, v := range clientMsg.SupportDataFormats {
		for _, v2 := range defaultDataFormats {
			if v == v2 {
				serverMsg.DataFormat = v
			}
		}
	}

	for _, v := range defaultCompressionAlgTypes {
		alg := uint16(v)
		if clientMsg.CompressionAlgs&alg == alg {
			serverMsg.CompressionAlg = alg
		}
	}

	return serverMsg
}

// checkHandshakeResult checks the handshake result.
// It checks if the protocol version is valid and if the compression algorithm is supported.
// It returns an error if the handshake result is invalid.
func (c *hsConn) checkHandshakeResult(cm *clientHandshakeMsg, sm *serverHandshakeMsg) error {
	// Check if the protocol version is valid.
	if err := func() error {
		// Iterate over the supported protocol versions and check if the server's protocol version
		//  matches one of them.
		for _, v := range cm.SupportProtocol {
			if v == sm.Protocol {
				// If the protocol version matches, return nil.
				return nil
			}
		}
		// If the protocol version does not match, return an error.
		return alertUnexpectedProtocol
	}(); err != nil {
		return err
	}

	// Check if the data format is valid.
	if err := func() error {
		// Iterate over the supported data formats and check if the server's data format matches one of them.
		for _, v := range cm.SupportDataFormats {
			if v == sm.DataFormat {
				// If the data format matches, return nil.
				return nil
			}
		}
		// If the data format does not match, return an error.
		return alertUnexpectedDataFormat
	}(); err != nil {
		return err
	}

	// Check if the compression algorithm is supported.
	return func() error {
		// If the compression algorithm is zero or a power of two, and the server's
		// compression algorithm matches it, return nil.
		if (cm.CompressionAlgs == 0 || isPowerOf2(cm.CompressionAlgs)) &&
			cm.CompressionAlgs&sm.CompressionAlg == sm.CompressionAlg {
			return nil
		}
		// If the compression algorithm does not match, return an error.
		return alertUnexpectedCompressor
	}()
}

func (c *hsConn) completeHandshake(serverMsg *serverHandshakeMsg) {
	c.state = handshakeState{
		compressAlg:     CompressionAlgType(serverMsg.CompressionAlg),
		protocolVersion: serverMsg.Protocol,
		dataFormat:      serverMsg.DataFormat,
		isCompleted:     true,
	}
}

func (c *hsConn) writeHandshakeFrame(msg frameWriter) error {
	return c.conn.Write(msg)
}

func (c *hsConn) readHandshakeFrame() (interface{}, error) {
	fr, err := c.conn.Read()
	if err != nil {
		return nil, err
	}
	hf, _ := fr.(handshakeFrame)
	if hf.alert() {
		return nil, fmt.Errorf("handshake alert: %v", alert(fr.Payload().(*handshakeAlertMsg).Alert[1]))
	}
	return fr.Payload(), nil
}

// sendAlert sends an alert message to the peer. It constructs a handshake alert message
// with the specified alert code and writes it using the handshake frame writer.
func (c *hsConn) sendAlert(err alert) error {
	// Create a handshake alert message with the given alert code
	msg := &handshakeAlertMsg{
		Alert: [2]byte{0, byte(err)}, // Alert type is set to 0, followed by the alert code
	}
	// Write the handshake alert frame to the connection
	return c.writeHandshakeFrame(handshakeAlertFrame(msg))
}

func isPowerOf2(n uint16) bool {
	return n != 0 || n&(n-1) == 0
}
