package conn

import (
	"context"
	"io"
	"sync"
	"testing"
	"time"

	"github.com/golang/mock/gomock"
	"github.com/test-go/testify/require"
)

func Test_syncDataPusFrame(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()
	ctxe, cancele := context.WithCancel(context.Background())
	defer cancele()
	doDial, serverChan := initTwoNodesConnEnv(ctxe, ctrl)
	endCode := uint32(100)
	go func() {
		for {
			fconn, ok := <-serverChan
			if !ok {
				return
			}
			go func() {
				defer fconn.Close()
				end := false
				wg := sync.WaitGroup{}
				wg.Add(1)
				defer wg.Wait()
				go func() {
					defer wg.Done()
					frame, err := fconn.Read()
					if err != nil {
						t.Logf("server read frame error: %v", err)
						if err != io.EOF {
							t.Fail()
						}
						return
					}
					// t.Logf("server read frame: %+v\n", frame)
					pf := frame.(dataPushFrame)
					t.Logf("server read dataPushFrame: %+v\n", pf)
					require.True(t, pf.isEnd())
					require.Equal(t, pf.PushEndInfo().code, endCode)
					end = true

				}()
				for height := 100; height < 200; height++ {
					if end {
						t.Logf("server push end %d", height)
						break
					}
					if err := fconn.Write(syncDataPushWriter(&dataPushMessage{
						version: 1001,
						height:  uint64(height),
						d:       []byte("hello world"),
					})); err != nil {
						t.Errorf("write frame error: %v", err)
						return
					}
				}
				// if err := fconn.Write(syncDataPushEndWriter(endCode)); err != nil {
				// 	t.Logf("write frame error: %v", err)
				// 	return
				// }
				if err := fconn.Write(syncDataPushResetWriter()); err != nil {
					t.Errorf("write frame error: %v", err)
					return
				}
				time.Sleep(20 * time.Millisecond)
			}()
		}
	}()

	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()
	fconn, err := doDial(ctx)
	if err != nil {
		t.Errorf("dialer error: %v", err)
		return
	}
	defer fconn.Close()
	num := 0

	for {
		frame, err := fconn.Read()
		if err != nil {
			t.Errorf("client read frame error: %v", err)
			return
		}
		// t.Logf("client read frame: %+v\n", frame)
		pf := frame.(dataPushFrame)
		switch pf.Header().Flag {
		case flagNone:
			t.Logf("client read dataPushFrame: %+v\n", pf)
			require.True(t, !pf.isEnd())
			t.Logf("client read dataPushFrame: %+v\n", pf.PushData().height)
			num++
			if num == 10 {
				if err := fconn.Write(syncDataPushEndWriter(endCode)); err != nil {
					t.Errorf("client write frame error: %v", err)
					return
				}
			}
		case flagPushEnd:
			t.Logf("open push close: %+v\n", pf)
			return
		case flagPushReset:
			t.Logf("open push reset: %+v\n", pf)
			return

		}

	}
}

func Test_syncDataPusFrameReset(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()
	ctxe, cancele := context.WithCancel(context.Background())
	defer cancele()
	doDial, serverChan := initTwoNodesConnEnv(ctxe, ctrl)
	endCode := uint32(100)
	go func() {
		for {
			fconn, ok := <-serverChan
			if !ok {
				return
			}
			go func() {
				defer fconn.Close()
				// if err := fconn.Write(syncDataPushEndWriter(endCode)); err != nil {
				// 	t.Logf("write frame error: %v", err)
				// 	return
				// }
				if err := fconn.Write(syncDataPushResetWriter()); err != nil {
					t.Logf("write frame error: %v", err)
					return
				}
				time.Sleep(20 * time.Millisecond)
			}()
		}
	}()

	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()
	fconn, err := doDial(ctx)
	if err != nil {
		t.Logf("dialer error: %v", err)
		return
	}
	defer fconn.Close()
	num := 0

	for {
		frame, err := fconn.Read()
		if err != nil {
			t.Logf("client read frame error: %v", err)
			return
		}
		// t.Logf("client read frame: %+v\n", frame)
		pf := frame.(dataPushFrame)
		switch pf.Header().Flag {
		case flagNone:
			t.Logf("client read dataPushFrame: %+v\n", pf)
			require.True(t, !pf.isEnd())
			t.Logf("client read dataPushFrame: %+v\n", pf.PushData().height)
			num++
			if num == 10 {
				if err := fconn.Write(syncDataPushEndWriter(endCode)); err != nil {
					t.Logf("client write frame error: %v", err)
					return
				}
			}
		case flagPushEnd:
			t.Logf("open push close: %+v\n", pf)
			return
		case flagPushReset:
			t.Logf("open push reset: %+v\n", pf)
			return

		}

	}
}

func TestA(t *testing.T) {
	fr := newPushFrame(frameHeader{
		Type: typeDataPush,
		Flag: flagPushReset,
	}, dataPushResetMessage{})

	if fr.(dataPushFrame).isInit() {
		panic("AAAAAAA")
	}
}
