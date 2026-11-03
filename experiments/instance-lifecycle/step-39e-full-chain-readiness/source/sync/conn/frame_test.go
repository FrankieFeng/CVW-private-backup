/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package conn

import (
	"fmt"
	"io"
	"math/rand"
	"testing"
	"time"

	"github.com/test-go/testify/require"
)

func Test_syncDataPullWriter_writeFrame(t *testing.T) {
	rd, wr := io.Pipe()
	type fields struct {
		height    uint64
		num       uint32
		withRWSet bool
		model     uint64
	}
	type args struct {
		fr *framer
	}
	tests := []struct {
		name    string
		fields  fields
		args    args
		wantErr bool
	}{
		{
			name: "test1",
			fields: fields{
				height:    1,
				num:       1,
				withRWSet: true,
				model:     0,
			},
			args: args{fr: &framer{
				r: rd,
				w: wr,
			}},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			sw := syncDataPullWriter(&dataPullMessage{
				height:    tt.fields.height,
				num:       tt.fields.num,
				withRWSet: tt.fields.withRWSet,
			})
			ch := make(chan frame)
			go func() {
				fr, err := tt.args.fr.readFrame()
				require.NoError(t, err)
				t.Log(fr)
				ch <- fr
			}()
			if err := sw.writeFrame(tt.args.fr); (err != nil) != tt.wantErr {
				t.Errorf("syncDataPullWriter.writeFrame() error = %v, wantErr %v", err, tt.wantErr)
			}
			fr := <-ch
			req := fr.(dataPullFrame).pullRequest()
			t.Log(req)
		})
	}
}

func Test_L2B(t *testing.T) {
	rand.Seed(time.Now().UnixNano())
	var bytes [4]byte
	for i := 0; i < 1000; i++ {
		// #nosec G404
		bNum := rand.Intn(30)
		for i := 0; i < 1000; i++ {
			// #nosec G404
			num := rand.Intn(1 << bNum)
			n, r := lenToBytesLE(num)
			bytes = [4]byte{
				r[3],
				r[2],
				r[1],
				r[0],
			}
			m, l := bytesBEToLen(bytes[4-n:])
			if l != num {
				fmt.Printf("%d, %d\n", num, l)
				panic("aaaa")
			}
			fmt.Printf("%d, %d\n", m, l)
		}
	}

	// num := 245354
	// n, r := lenToBytesLE(num)
	// fmt.Printf("%d, %d\n", n, r[0])
	// bytes := make([]byte, n)
	// for i := 0; i < n; i++ {
	// 	bytes[i] = r[n-1-i]
	// }
	// m, l := bytesBEToLen(bytes[:n])
	// if l != num {
	// 	panic("aaaa")
	// }
	// fmt.Printf("%d, %d\n", m, l)
}
