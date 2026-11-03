/*
 * Copyright (C) THL A29 Limited, a Tencent company. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package receptor

import (
	"math"
	"math/bits"
)

type metricType int

const (
	metricTypeGet metricType = iota + 1
	metricTypeVerify
	metricTypeRuleNotMeet
)

// Metric records the behavior of the node based on block height.
type Metric interface {
	Good(uint64)
	Bad(uint64)
	BadRecords(uint64) []uint64
}

// Bit64Metric records the behavior of the node with 64-bit bytes
type Bit64Metric struct {
	from uint64
	log  uint64
}

// Set marks the block at height h as bad.
func (m *Bit64Metric) set(h uint64) {
	// If the height is less than the from, return.
	if h < m.from {
		return
	}
	// If the from is 0, or the height difference is greater than 128, reset the from and log.
	if m.from == 0 || h-m.from >= 128 {
		m.from = h
		m.log = 0
	}
	// Calculate the position of the block in the log.
	pos := h - m.from
	// If the position is greater than 64, shift the log right and add 8 to the from.
	for pos >= 64 {
		m.log >>= 8
		m.from += 8
		pos -= 8
	}
	// Set the bit at the position in the log.
	m.log |= 1 << pos
}

func (m *Bit64Metric) bits(h uint64) int {
	if h-m.from >= 64 {
		return 0
	}
	return bits.OnesCount64(m.log)
}

// BlockMetric records the behavior of the node with 64-bit bytes
type BlockMetric struct {
	Bit64Metric
}

// Bad record a bad record
func (m *BlockMetric) Bad(h uint64) {
	m.set(h)
}

// Good record a good record
func (m *BlockMetric) Good(_ uint64) {}

// BadRecords return the bad records in the range [from, to] which to is exclusive.
// The bad records are the blocks that have bad behavior and are recorded in the bit map.
func (m *BlockMetric) BadRecords(h uint64) []uint64 {
	// get the bad count
	bCount := m.bits(h)
	if bCount == 0 {
		return nil
	}

	records := make([]uint64, bCount)
	log := m.log
	from := m.from

	// traverse the log and get the bad records
	for i := 0; i < bCount; i++ {
		// get the trailing zeros
		trailing0s := bits.TrailingZeros64(log)
		records[i] = from + uint64(trailing0s)
		// xor the log to remove the bad record
		log ^= 1 << trailing0s
	}
	return records
}

var (
	// confinementPeriod indicates the duration that a node stays in the blacklist.
	confinementPeriod = 20
	// decayPeriod indicates the fractional calculation decay period.
	// for example: node has a bad behavior at block height 10, 20 points will be deducted from the score.
	// When the block height reaches 15, the points will be reduced to 20 * 80%（衰减度） points
	decayPeriod = 5
)

// MetricStat statistics of all status indicators including network, block verification, node availability.
type MetricStat struct {
	net      Metric //网络统计指标
	validate Metric
	notMeet  Metric
}

// NewMetricStat create a new metric stat
func NewMetricStat() *MetricStat {
	return &MetricStat{
		net:      &BlockMetric{},
		validate: &BlockMetric{},
		notMeet:  &BlockMetric{},
	}
}

// Bad record a bad record, h is the block height that records bad behavior
// metricType is the type of bad record
func (ms *MetricStat) Bad(h uint64, metricType metricType) {
	switch metricType {
	case metricTypeGet:
		ms.net.Bad(h)
	case metricTypeVerify:
		ms.validate.Bad(h)
	case metricTypeRuleNotMeet:
		ms.notMeet.Bad(h)
	}
}

// Score calculates the score based on the bad behavior before height h
func (ms *MetricStat) Score(h uint64) int {
	score := 100
	records := ms.validate.BadRecords(h)
	if len(records) > 0 {
		last := records[len(records)-1]
		//禁闭期内，不可用
		unban := int(h-last) - confinementPeriod
		if unban < 0 {
			return 0
		}
		deduct := 100 * math.Pow(0.8, float64(unban/decayPeriod))
		score -= int(deduct)
		if score <= 0 {
			return 0
		}
	}
	records = ms.notMeet.BadRecords(h)
	if len(records) > 0 {
		last := records[len(records)-1]
		unban := int(last) - confinementPeriod
		if unban < 0 {
			return 0
		}
		deduct := 100 * math.Pow(0.8, float64(unban/decayPeriod))
		score -= int(deduct)
		if score <= 0 {
			return 0
		}
	}
	records = ms.net.BadRecords(h)
	if len(records) > 0 {
		score -= 5 * len(records)
	}
	if score <= 0 {
		return 1 // avoid that there are no node to use.
	}
	return score
}
