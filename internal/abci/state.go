package abci

import (
	"crypto/sha256"
	"encoding/binary"
	"fmt"
	"sort"

	"github.com/l33tdawg/sage/internal/store"
)

// AppState holds the application's consensus state.
type AppState struct {
	Height   int64  `json:"height"`
	AppHash  []byte `json:"app_hash"`
	EpochNum int64  `json:"epoch_num"`
}

// stateHeightKey is the BadgerDB key for the block height.
const stateHeightKey = "height"
const stateAppHashKey = "app_hash"
const stateEpochKey = "epoch"

// SaveState persists the app state to BadgerDB.
func SaveState(bs *store.BadgerStore, state *AppState) error {
	heightBytes := make([]byte, 8)
	binary.BigEndian.PutUint64(heightBytes, uint64(state.Height))
	if err := bs.SetState(stateHeightKey, heightBytes); err != nil {
		return fmt.Errorf("save height: %w", err)
	}
	if err := bs.SetState(stateAppHashKey, state.AppHash); err != nil {
		return fmt.Errorf("save app hash: %w", err)
	}
	epochBytes := make([]byte, 8)
	binary.BigEndian.PutUint64(epochBytes, uint64(state.EpochNum))
	if err := bs.SetState(stateEpochKey, epochBytes); err != nil {
		return fmt.Errorf("save epoch: %w", err)
	}
	return nil
}

// LoadState loads the app state from BadgerDB.
func LoadState(bs *store.BadgerStore) (*AppState, error) {
	state := &AppState{}

	heightBytes, err := bs.GetState(stateHeightKey)
	if err != nil {
		return state, nil // Fresh start
	}
	if heightBytes != nil && len(heightBytes) == 8 {
		state.Height = int64(binary.BigEndian.Uint64(heightBytes))
	}

	appHash, err := bs.GetState(stateAppHashKey)
	if err == nil && appHash != nil {
		state.AppHash = appHash
	}

	epochBytes, err := bs.GetState(stateEpochKey)
	if err == nil && epochBytes != nil && len(epochBytes) == 8 {
		state.EpochNum = int64(binary.BigEndian.Uint64(epochBytes))
	}

	return state, nil
}

// ComputeAppHash computes a deterministic hash over all on-chain state.
// CRITICAL: Must be identical across all nodes.
func ComputeAppHash(bs *store.BadgerStore) ([]byte, error) {
	return bs.ComputeAppHash()
}

// computeBlockHash computes a hash for the current block's changes.
func computeBlockHash(memoryIDs []string, height int64) []byte {
	h := sha256.New()

	// Sort memory IDs for determinism
	sorted := make([]string, len(memoryIDs))
	copy(sorted, memoryIDs)
	sort.Strings(sorted)

	for _, id := range sorted {
		h.Write([]byte(id))
	}

	heightBytes := make([]byte, 8)
	binary.BigEndian.PutUint64(heightBytes, uint64(height))
	h.Write(heightBytes)

	return h.Sum(nil)
}
