package step35c

import (
	"context"
	"errors"
	"sync"
)

type Gate struct {
	mu      sync.Mutex
	closing bool
	n       int
	idle    chan struct{}
	done    chan struct{}
}

func (g *Gate) Begin() (func(), error) {
	g.mu.Lock()
	defer g.mu.Unlock()
	if g.closing {
		return nil, errors.New("lifecycle admission closed")
	}
	if g.n == 0 {
		g.idle = make(chan struct{})
	}
	g.n++
	var once sync.Once
	return func() {
		once.Do(func() {
			g.mu.Lock()
			defer g.mu.Unlock()
			g.n--
			if g.n == 0 {
				close(g.idle)
			}
		})
	}, nil
}
func (g *Gate) Drain(ctx context.Context) error {
	g.mu.Lock()
	g.closing = true
	if g.n == 0 {
		g.mu.Unlock()
		return nil
	}
	idle := g.idle
	g.mu.Unlock()
	select {
	case <-idle:
		return nil
	case <-ctx.Done():
		return ctx.Err()
	}
}
func (g *Gate) Count() int { g.mu.Lock(); defer g.mu.Unlock(); return g.n }
