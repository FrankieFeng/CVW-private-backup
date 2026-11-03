package conn

import (
	"context"
	"fmt"
	"sync"
	"testing"
	"time"

	"chainmaker.org/chainmaker/sync/v2/internal/errors"
	"chainmaker.org/chainmaker/sync/v2/internal/test"
	un "chainmaker.org/chainmaker/sync/v2/net"
	"github.com/golang/mock/gomock"
)

type dialOnce func(ctx context.Context) (*frameConn, error)

func initTwoNodesConnEnv(ctx context.Context, ctrl *gomock.Controller) (dialOnce, chan *frameConn) {
	ns := test.NewWorkNS(ctrl)
	var (
		serverChan = make(chan *frameConn)
	)
	localNode := ns.NewMockNode("localhost", cLogger)
	remoteNode := ns.NewMockNode(remoteNodeID, cLogger)
	lsn := un.NewMessageBusListener(un.NewBlockSyncTransport(remoteNode.MessageBus()))
	_ = lsn.Listen()
	if ctx.Done() != nil {
		go func() {
			<-ctx.Done()
			lsn.Close()
			ns.Release()
		}()
	}
	go func() {
		for {
			conn, err := lsn.Accept()
			if err != nil {
				fmt.Println("listen exit for ", err)
				close(serverChan)
				return
			}
			fmt.Println("server")
			serverChan <- newFrameConn(conn)
		}
	}()

	dialer := un.NewMessageBusDialer(un.NewBlockSyncTransport(localNode.MessageBus()))
	return func(ctx context.Context) (*frameConn, error) {
		cc, err := dialer.Dial(ctx, remoteNodeID)
		if err != nil {
			fmt.Printf("dialer error: %v", err)
			return nil, err
		}
		return newFrameConn(cc), nil
	}, serverChan
}

func TestConn_handshake(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	wg := sync.WaitGroup{}
	defer wg.Wait()

	ctxe, cancele := context.WithCancel(context.Background())
	defer cancele()
	doDial, serverChan := initTwoNodesConnEnv(ctxe, ctrl)

	wg.Add(1)
	go func() {
		defer wg.Done()
		for {
			fconn, ok := <-serverChan
			if !ok {
				return
			}
			wg.Add(1)
			go func() {
				defer wg.Done()
				defer fconn.Close()
				serverConn := hsServer(fconn, func(height uint64) BlockSupportResult {
					// return l.handler(conn.RemoteAddr().String(), height)
					return BlockSupportResult{
						BlockNum: -1,
						Code:     errors.ErrCodeNon,
					}
				})
				ctx, cancel := context.WithTimeout(context.Background(), handshakeTimeout)
				defer cancel()
				state, err := serverConn.Handshake(ctx)
				if err != nil {
					fmt.Println("handshake to client err: ", err)
					t.Fail()
					return
				}
				t.Logf("server handshake success %+v\n", state)
			}()
		}
	}()

	ctx, cancel := context.WithTimeout(context.Background(), handshakeTimeout)
	defer cancel()
	fconn, err := doDial(ctx)
	if err != nil {
		t.Logf("dialer error: %v", err)
		t.Fail()
		return
	}
	defer fconn.Close()
	client := hsClient(fconn, &handshakeConfig{
		FromHeight: 1,
		// Versions:           []uint16{1, 2, 3},
		CompressionAlgTypes: []CompressionAlgType{CompressionNone},
		DataFormats:         []uint16{DataFormatNone},
		NodeDetect:          extractNodeCheckFuncFromCtx(ctx),
	})
	state, err := client.Handshake(ctx)
	if err != nil {
		t.Logf("client handshake error: %v", err)
		t.Fail()
		return
	}
	time.Sleep(time.Second)
	t.Logf("client handshake success %+v\n", state)
}
