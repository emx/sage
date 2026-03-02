package abci

import (
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/l33tdawg/sage/internal/store"
)

func setupTestBadger(t *testing.T) *store.BadgerStore {
	dir, err := os.MkdirTemp("", "sage-test-badger")
	require.NoError(t, err)
	t.Cleanup(func() { os.RemoveAll(dir) })

	bs, err := store.NewBadgerStore(dir)
	require.NoError(t, err)
	t.Cleanup(func() { bs.CloseBadger() })

	return bs
}

func TestAppHashDeterministic(t *testing.T) {
	bs := setupTestBadger(t)

	bs.SetMemoryHash("mem-1", []byte("hash1"), "proposed")
	bs.SetMemoryHash("mem-2", []byte("hash2"), "committed")

	h1, err := ComputeAppHash(bs)
	require.NoError(t, err)

	h2, err := ComputeAppHash(bs)
	require.NoError(t, err)

	assert.Equal(t, h1, h2)
}

func TestAppHashChanges(t *testing.T) {
	bs := setupTestBadger(t)

	bs.SetMemoryHash("mem-1", []byte("hash1"), "proposed")
	h1, _ := ComputeAppHash(bs)

	bs.SetMemoryHash("mem-1", []byte("hash1"), "committed")
	h2, _ := ComputeAppHash(bs)

	assert.NotEqual(t, h1, h2)
}

func TestSaveLoadState(t *testing.T) {
	bs := setupTestBadger(t)

	state := &AppState{
		Height:   42,
		AppHash:  []byte("testhash"),
		EpochNum: 3,
	}

	err := SaveState(bs, state)
	require.NoError(t, err)

	loaded, err := LoadState(bs)
	require.NoError(t, err)

	assert.Equal(t, state.Height, loaded.Height)
	assert.Equal(t, state.AppHash, loaded.AppHash)
	assert.Equal(t, state.EpochNum, loaded.EpochNum)
}
