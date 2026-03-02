package poe

import (
	"fmt"
	"math"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

func TestComputeWeight(t *testing.T) {
	w := ComputeWeight(0.8, 0.7, 0.9, 0.5)
	assert.Greater(t, w, 0.0)
	assert.Less(t, w, 1.0)
}

func TestLogSpaceEquivalence(t *testing.T) {
	a, d, r, s := 0.8, 0.7, 0.9, 0.5

	// Direct computation
	direct := math.Pow(a, AlphaAccuracy) * math.Pow(d, BetaDomain) *
		math.Pow(r, GammaRecency) * math.Pow(s, DeltaCorroboration)

	logSpace := ComputeWeight(a, d, r, s)
	assert.InDelta(t, direct, logSpace, 1e-10)
}

func TestEpsilonFloor(t *testing.T) {
	// Zero corroboration shouldn't zero the entire weight
	w := ComputeWeight(0.8, 0.7, 0.9, 0.0)
	assert.Greater(t, w, 0.0)
}

func TestRepCap(t *testing.T) {
	// Use enough validators (20) so the 10% cap is achievable
	weights := make(map[string]float64, 20)
	weights["v1"] = 1000.0 // dominant validator
	for i := 2; i <= 20; i++ {
		weights[fmt.Sprintf("v%d", i)] = 1.0
	}
	normalized := NormalizeWeights(weights)

	// The dominant validator should be capped at RepCap (10%)
	assert.LessOrEqual(t, normalized["v1"], RepCap+0.001)

	// Sum should be ~1.0
	var sum float64
	for _, w := range normalized {
		sum += w
	}
	assert.InDelta(t, 1.0, sum, 0.01)

	// With 4 validators, cap can't bring everyone below 10%.
	// Test that dominant weight is at least reduced relative to others.
	smallWeights := map[string]float64{
		"a": 100.0,
		"b": 1.0,
		"c": 1.0,
		"d": 1.0,
	}
	smallNormalized := NormalizeWeights(smallWeights)
	var smallSum float64
	for _, w := range smallNormalized {
		smallSum += w
	}
	assert.InDelta(t, 1.0, smallSum, 0.01)
	// Dominant validator should be reduced from 97% to at most 25%
	assert.Less(t, smallNormalized["a"], 0.30)
}

func TestEWMAConvergence(t *testing.T) {
	tracker := NewEWMATracker()

	// Feed consistently correct outcomes
	for i := 0; i < 50; i++ {
		tracker.Update(1.0)
	}
	assert.Greater(t, tracker.Accuracy(), 0.9)

	// Feed consistently wrong outcomes
	for i := 0; i < 100; i++ {
		tracker.Update(0.0)
	}
	assert.Less(t, tracker.Accuracy(), 0.3)
}

func TestColdStartBlend(t *testing.T) {
	tracker := NewEWMATracker()
	// With zero observations, should return prior
	assert.Equal(t, coldStartPrior, tracker.Accuracy())

	// With few observations, should be blended
	tracker.Update(1.0)
	acc := tracker.Accuracy()
	assert.Greater(t, acc, coldStartPrior)
	assert.Less(t, acc, 1.0)
}

func TestPhiCoefficient(t *testing.T) {
	tracker := NewPhiTracker(50)

	// Perfect correlation: both always agree
	for i := 0; i < 30; i++ {
		tracker.RecordJointVote("v1", "v2", true, true, false)
	}
	for i := 0; i < 20; i++ {
		tracker.RecordJointVote("v1", "v2", false, false, false)
	}

	phi := tracker.PhiCoefficient("v1", "v2")
	assert.Greater(t, phi, 0.8)
}

func TestCollusionDetection(t *testing.T) {
	tracker := NewPhiTracker(50)

	// High correlation
	for i := 0; i < 50; i++ {
		accept := i%3 != 0
		tracker.RecordJointVote("v1", "v2", accept, accept, false)
	}

	assert.True(t, tracker.IsCollusion("v1", "v2"))
}

func TestNoCollusionIndependent(t *testing.T) {
	tracker := NewPhiTracker(50)

	// Independent voting
	for i := 0; i < 50; i++ {
		tracker.RecordJointVote("v1", "v2", i%2 == 0, i%3 == 0, false)
	}

	assert.False(t, tracker.IsCollusion("v1", "v2"))
}

func TestEpochBoundary(t *testing.T) {
	assert.False(t, IsEpochBoundary(0))
	assert.False(t, IsEpochBoundary(50))
	assert.True(t, IsEpochBoundary(100))
	assert.False(t, IsEpochBoundary(150))
	assert.True(t, IsEpochBoundary(200))
}

func TestEpochNumber(t *testing.T) {
	assert.Equal(t, int64(0), EpochNumber(50))
	assert.Equal(t, int64(1), EpochNumber(100))
	assert.Equal(t, int64(1), EpochNumber(150))
	assert.Equal(t, int64(2), EpochNumber(200))
}

func TestRecencyDecay(t *testing.T) {
	now := time.Now()

	// Just active: score should be ~1.0
	recent := RecencyScore(now.Add(-1*time.Minute), now)
	assert.InDelta(t, 1.0, recent, 0.01)

	// 100 hours ago: should be lower
	old := RecencyScore(now.Add(-100*time.Hour), now)
	assert.Less(t, old, recent)
	assert.Greater(t, old, 0.0)
}

func TestCorroborationScore(t *testing.T) {
	s0 := CorroborationScore(0, 20)
	s5 := CorroborationScore(5, 20)
	s20 := CorroborationScore(20, 20)

	assert.Equal(t, 0.0, s0)
	assert.Greater(t, s5, s0)
	assert.InDelta(t, 1.0, s20, 0.001) // At max, score should be 1.0
	assert.Greater(t, s20, s5)
}
