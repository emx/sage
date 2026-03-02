package validator

import (
	"crypto/ed25519"
	"crypto/rand"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func makeValidator(id string, power int64) *ValidatorInfo {
	pub, _, _ := ed25519.GenerateKey(rand.Reader)
	return &ValidatorInfo{
		ID:        id,
		PublicKey: pub,
		Power:     power,
		PoEWeight: 1.0,
	}
}

func TestAddRemoveValidator(t *testing.T) {
	vs := NewValidatorSet()

	v1 := makeValidator("validator-a", 100)
	v2 := makeValidator("validator-b", 200)

	// Add validators.
	require.NoError(t, vs.AddValidator(v1))
	require.NoError(t, vs.AddValidator(v2))
	assert.Equal(t, int64(300), vs.TotalPower())

	// Duplicate add should fail.
	err := vs.AddValidator(v1)
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "already exists")

	// Lookup.
	got, ok := vs.GetValidator("validator-a")
	assert.True(t, ok)
	assert.Equal(t, int64(100), got.Power)

	// Remove.
	require.NoError(t, vs.RemoveValidator("validator-a"))
	assert.Equal(t, int64(200), vs.TotalPower())

	_, ok = vs.GetValidator("validator-a")
	assert.False(t, ok)

	// Remove non-existent should fail.
	err = vs.RemoveValidator("validator-a")
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "not found")
}

func TestGetAllSorted(t *testing.T) {
	vs := NewValidatorSet()

	// Add in non-alphabetical order.
	require.NoError(t, vs.AddValidator(makeValidator("charlie", 100)))
	require.NoError(t, vs.AddValidator(makeValidator("alice", 100)))
	require.NoError(t, vs.AddValidator(makeValidator("bob", 100)))

	all := vs.GetAll()
	require.Len(t, all, 3)
	assert.Equal(t, "alice", all[0].ID)
	assert.Equal(t, "bob", all[1].ID)
	assert.Equal(t, "charlie", all[2].ID)
}

func TestPowerCapEnforcement(t *testing.T) {
	vs := NewValidatorSet()

	// 3 validators with equal power (100 each, total 300).
	require.NoError(t, vs.AddValidator(makeValidator("v1", 100)))
	require.NoError(t, vs.AddValidator(makeValidator("v2", 100)))
	require.NoError(t, vs.AddValidator(makeValidator("v3", 100)))

	// Max change allowed: 300/3 = 100.
	// Changing v1 from 100 to 200 = diff of 100, should be allowed.
	require.NoError(t, vs.UpdatePower("v1", 200))
	assert.Equal(t, int64(400), vs.TotalPower())

	// Now total is 400. Max change = 400/3 = 133.
	// Changing v1 from 200 to 400 = diff of 200, should be rejected.
	err := vs.UpdatePower("v1", 400)
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "exceeds max allowed")

	// Changing v1 from 200 to 333 = diff of 133, should be allowed.
	require.NoError(t, vs.UpdatePower("v1", 333))

	// Update non-existent validator.
	err = vs.UpdatePower("v99", 100)
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "not found")
}

func TestQuorumReached(t *testing.T) {
	// 4 validators with equal weight. 3 accept = 75% > 66.7% = quorum.
	weights := map[string]float64{
		"v1": 1.0,
		"v2": 1.0,
		"v3": 1.0,
		"v4": 1.0,
	}
	votes := map[string]bool{
		"v1": true,
		"v2": true,
		"v3": true,
		"v4": false,
	}

	reached, acceptW, totalW := CheckQuorum(votes, weights)
	assert.True(t, reached)
	assert.InDelta(t, 3.0, acceptW, 0.001)
	assert.InDelta(t, 4.0, totalW, 0.001)
}

func TestQuorumNotReached(t *testing.T) {
	// 4 validators with equal weight. 1 accept = 25% < 66.7% = no quorum.
	weights := map[string]float64{
		"v1": 1.0,
		"v2": 1.0,
		"v3": 1.0,
		"v4": 1.0,
	}
	votes := map[string]bool{
		"v1": true,
		"v2": false,
		"v3": false,
		"v4": false,
	}

	reached, acceptW, totalW := CheckQuorum(votes, weights)
	assert.False(t, reached)
	assert.InDelta(t, 1.0, acceptW, 0.001)
	assert.InDelta(t, 4.0, totalW, 0.001)
}

func TestWeightedQuorum(t *testing.T) {
	// Unequal weights: v1 has weight 10, others have 1 each (total 13).
	// Only v1 votes accept: 10/13 = 76.9% > 66.7% = quorum by weight.
	weights := map[string]float64{
		"v1": 10.0,
		"v2": 1.0,
		"v3": 1.0,
		"v4": 1.0,
	}
	votes := map[string]bool{
		"v1": true,
		"v2": false,
		"v3": false,
		"v4": false,
	}

	reached, acceptW, totalW := CheckQuorum(votes, weights)
	assert.True(t, reached, "quorum should be reached by weight, not by count")
	assert.InDelta(t, 10.0, acceptW, 0.001)
	assert.InDelta(t, 13.0, totalW, 0.001)
}

func TestHasQuorumZeroTotal(t *testing.T) {
	assert.False(t, HasQuorum(0, 0), "zero total weight should not be quorum")
}
