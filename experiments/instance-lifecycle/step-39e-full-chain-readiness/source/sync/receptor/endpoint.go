/*
Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.

SPDX-License-Identifier: Apache-2.0
*/

package receptor

import (
	"context"
	"fmt"
	"sort"
	"sync"

	"chainmaker.org/chainmaker/protocol/v2"
	"chainmaker.org/chainmaker/sync/v2/internal/errors"
)

var (
	errEpDown = fmt.Errorf("endpoint down")
)

// endpointStat the type of endpoint state
type endpointStatus int8

const (
	//statusLiving indicates the endpoint is living.
	statusLiving endpointStatus = iota + 1
	//statusDead indicates the endpoint is dead.
	statusDead
)

type (
	dialer interface {
		Dial(addr string, height uint64) (*connection, error)
	}

	blockState struct {
		height        uint64
		archiveHeight uint64
	}
	//endpoint an endpoint represents a peer node
	endpoint struct {
		mu      sync.Mutex
		id      string
		state   blockState
		status  endpointStatus
		metrics *MetricStat
		conn    *clientConn
		logger  protocol.Logger
	}

	endpointWithScore struct {
		*endpoint
		score int
	}
	//endpointPool cache all nodes it knows about
	endpointPool struct {
		mu        sync.RWMutex
		t         *transport
		ends      map[string]*endpoint
		logger    protocol.Logger
		maxHeight uint64
	}
	//endpointFilter selector interface for selecting endpoints
	//if match return true, otherwise return false.
	endpointFilter interface {
		match(*endpoint) bool
	}
	//endpointFilterFunc function type that implements the selector interface
	endpointFilterFunc func(*endpoint) bool
)

func (f endpointFilterFunc) match(e *endpoint) bool {
	return f(e)
}

// newEndpoint create a new endpoint
func newEndpoint(id string, state blockState, logger protocol.Logger) *endpoint {
	return &endpoint{
		id:      id,
		state:   state,
		status:  statusLiving,
		metrics: NewMetricStat(),
		logger:  logger,
	}
}

// FailFor records a bad behavior to the endpoint
func (e *endpoint) FailFor(h uint64, t metricType) {
	e.mu.Lock()
	defer e.mu.Unlock()
	e.failForLocked(h, t)
}

func (e *endpoint) failForLocked(h uint64, t metricType) {
	e.metrics.Bad(h, t)
}

// Score get the score of the endpoint to the specified height
func (e *endpoint) Score(h uint64) int {
	e.mu.Lock()
	defer e.mu.Unlock()
	if !e.isLiving() {
		return -1
	}
	return e.metrics.Score(h)
}

// NoPush check the endpoint is pushing or not
func (e *endpoint) noPushLocked() bool {
	if e.conn != nil && e.conn.isClosed() {
		e.conn = nil
	}
	return e.conn == nil || !e.conn.isPushing()
}

// Height get height of the endpoint
func (e *endpoint) Height() uint64 {
	return e.state.height
}

// ArchiveHeight get archive height of the endpoint
func (e *endpoint) ArchiveHeight() uint64 {
	return e.state.archiveHeight
}

func (e *endpoint) IsValidFor(h uint64) bool {
	e.mu.Lock()
	defer e.mu.Unlock()
	return e.isLiving() && e.state.height >= h && e.state.archiveHeight < h
}

// IsValidAndNoPushFor check the endpoint is valid and not pushing.
func (e *endpoint) IsValidAndNoPushFor(h uint64) bool {
	e.mu.Lock()
	defer e.mu.Unlock()
	return e.isLiving() && e.noPushLocked() && e.state.height >= h && e.state.archiveHeight < h
}

// isLiving check the endpoint is living or not
func (e *endpoint) isLiving() bool {
	return e.status == statusLiving
}

func (e *endpoint) makeLiving() {
	e.mu.Lock()
	defer e.mu.Unlock()
	e.status = statusLiving
}

// markDead mark the endpoint as dead
func (e *endpoint) markDead() {
	e.mu.Lock()
	defer e.mu.Unlock()
	e.status = statusDead
	e.closeConnectFor(errEpDown)
}

func (e *endpoint) destroy() {
	e.mu.Lock()
	defer e.mu.Unlock()
	e.closeConnectFor(fmt.Errorf("localhost close"))
}

func (e *endpoint) closeConnectFor(err error) {
	if e.conn != nil {
		_ = e.conn.closeForError(err)
		e.conn = nil
	}
}

// MakeInvalidFor mark the endpoint as invalid
func (e *endpoint) MakeInvalidFor(h uint64, err error) {
	e.mu.Lock()
	defer e.mu.Unlock()
	e.makeInvalidForLocked(h, err)
}

func (e *endpoint) makeInvalidForLocked(h uint64, err error) {
	e.closeConnectFor(err)
	e.failForLocked(h, metricTypeRuleNotMeet)
}

func (e *endpoint) GetConn(ctx context.Context, height uint64, dialer dialer) (*clientConn, error) {
	e.mu.Lock()
	defer e.mu.Unlock()
	if e.conn != nil {
		// Perform a health check on the existing connection.
		if e.conn.healthCheck(ctx) {
			// Try to retain the connection if it passes the health check.
			if err := e.conn.retain(); err == nil {
				return e.conn, nil
			}
		}
	}

	// Dial a new connection if none exists or the existing one is unhealthy.
	conn, err := dialer.Dial(e.id, height)
	if err != nil {
		if errCode, ok := err.(errors.ErrCode); ok {
			if errCode.Terminate() {
				e.makeInvalidForLocked(height, err)
			}
		}
		return nil, err
	}

	// Create a new client connection and add it to the pool.
	e.conn = newClientConn(conn, e, e.logger)
	return e.conn, nil
}

func newEndpointPool(tr *transport, logger protocol.Logger, ends ...*endpoint) *endpointPool {
	pool := &endpointPool{
		ends:   make(map[string]*endpoint),
		t:      tr,
		logger: logger,
	}
	for _, end := range ends {
		pool.ends[end.id] = end
	}
	return pool
}

// AddNew add a new endpoint to the endpoint pool.
// If this endpoint already exists, replace it and add loginIn record.
func (p *endpointPool) AddEndpoint(id string, state blockState) {
	p.mu.Lock()
	defer p.mu.Unlock()
	if state.height > p.maxHeight {
		p.maxHeight = state.height
	}
	if end, exist := p.ends[id]; exist {
		end.state = state
		end.makeLiving()
		return
	}
	e := newEndpoint(id, state, p.logger)
	p.ends[id] = e
}

// UpdateEndpoint update the endpoint of the id in the endpoint pool.
// If the endpoint is already in the pool, update its height and archive height.
// If the endpoint is not in the pool, add it to the pool.
func (p *endpointPool) UpdateEndpoint(id string, state blockState) {
	p.mu.Lock()
	defer p.mu.Unlock()
	if end, exist := p.ends[id]; exist {
		end.state = state
		if state.height > p.maxHeight {
			p.maxHeight = state.height
		}
	} else {
		p.ends[id] = newEndpoint(id, state, p.logger)
	}
}

// MarkDead mark the endpoint of the id as dead, and add the loginOut record to the endpoint.
func (p *endpointPool) MarkDead(id string) {
	p.mu.Lock()
	defer p.mu.Unlock()
	if end := p.ends[id]; end != nil {
		end.markDead()
		if end.state.height == p.maxHeight {
			p.maxHeight = 0
			for _, e := range p.ends {
				if e.isLiving() && e.state.height > p.maxHeight {
					p.maxHeight = e.state.height
				}
			}
		}
	}
}

// GetEndpoint get the endpoint with the specified id.
// If not found, return nil
func (p *endpointPool) GetEndpoint(id string) *endpoint {
	p.mu.RLock()
	defer p.mu.RUnlock()
	return p.ends[id]
}

// ForEach iterate over all endpoints in the pool,
// and return if the function fn return true or all nodes have been traversed
func (p *endpointPool) ForEach(fn func(*endpoint) bool) {
	p.mu.Lock()
	defer p.mu.Unlock()
	p.forEachLocked(fn)
}

func (p *endpointPool) forEachLocked(fn func(*endpoint) bool) {
	for _, end := range p.ends {
		if fn(end) {
			break
		}
	}
}

// Select all endpoints those match filter.
func (p *endpointPool) Select(filter endpointFilter) []*endpoint {
	var ends []*endpoint
	p.ForEach(func(e *endpoint) bool {
		if filter.match(e) {
			ends = append(ends, e)
		}
		return false
	})
	return ends
}

func (p *endpointPool) clearAll() {
	p.mu.Lock()
	defer p.mu.Unlock()
	for _, end := range p.ends {
		end.destroy()
	}
	p.ends = make(map[string]*endpoint)
}

// GetMaxHeight get the maximum height among all living nodes.
func (p *endpointPool) GetMaxHeight() uint64 {
	p.mu.Lock()
	defer p.mu.Unlock()
	return p.maxHeight
}

type endpointSort []endpointWithScore

func (s endpointSort) Len() int           { return len(s) }
func (s endpointSort) Less(i, j int) bool { return s[i].score > s[j].score }
func (s endpointSort) Swap(i, j int)      { s[i], s[j] = s[j], s[i] }

func getValidEndpointsSorted(height uint64, endpoints []*endpoint) []*endpoint {
	ends := make([]*endpoint, 0, len(endpoints))
	for _, ele := range getEndpointsWithScoreSorted(height, endpoints) {
		if ele.score > 0 {
			ends = append(ends, ele.endpoint)
		}
	}
	return ends
}

func getEndpointsWithScoreSorted(height uint64, endpoints []*endpoint) []endpointWithScore {
	var sorts endpointSort = make([]endpointWithScore, len(endpoints))
	for i, end := range endpoints {
		sorts[i] = endpointWithScore{
			endpoint: end,
			score:    end.Score(height),
		}
	}
	sort.Sort(sorts)
	return sorts
}
