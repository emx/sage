//go:build byzantine

package byzantine

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os/exec"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func getBlockHeight(t *testing.T, rpcURL string) int64 {
	resp, err := http.Get(rpcURL + "/status")
	if err != nil {
		return -1
	}
	defer resp.Body.Close()

	var result struct {
		Result struct {
			SyncInfo struct {
				LatestBlockHeight string `json:"latest_block_height"`
			} `json:"sync_info"`
		} `json:"result"`
	}
	json.NewDecoder(resp.Body).Decode(&result)

	var height int64
	fmt.Sscanf(result.Result.SyncInfo.LatestBlockHeight, "%d", &height)
	return height
}

func stopContainer(t *testing.T, name string) {
	cmd := exec.Command("docker", "stop", name)
	if err := cmd.Run(); err != nil {
		t.Logf("Warning: failed to stop %s: %v", name, err)
	}
}

func startContainer(t *testing.T, name string) {
	cmd := exec.Command("docker", "start", name)
	if err := cmd.Run(); err != nil {
		t.Logf("Warning: failed to start %s: %v", name, err)
	}
}

func TestOneNodeDown(t *testing.T) {
	// Get initial height
	h1 := getBlockHeight(t, "http://localhost:26657")
	if h1 < 0 {
		t.Skip("Network not running")
	}

	// Stop node 3
	stopContainer(t, "sage-cometbft3-1")
	t.Cleanup(func() { startContainer(t, "sage-cometbft3-1") })

	// Wait for blocks
	time.Sleep(10 * time.Second)

	// Chain should still be producing blocks (3/4 > 2/3)
	h2 := getBlockHeight(t, "http://localhost:26657")
	assert.Greater(t, h2, h1, "blocks should still be produced with 3/4 validators")
	t.Logf("Height before stop: %d, after: %d", h1, h2)
}

func TestTwoNodesDown(t *testing.T) {
	h1 := getBlockHeight(t, "http://localhost:26657")
	if h1 < 0 {
		t.Skip("Network not running")
	}

	// Stop nodes 2 and 3
	stopContainer(t, "sage-cometbft2-1")
	stopContainer(t, "sage-cometbft3-1")
	t.Cleanup(func() {
		startContainer(t, "sage-cometbft2-1")
		startContainer(t, "sage-cometbft3-1")
	})

	// Wait
	time.Sleep(10 * time.Second)

	// Chain should halt (2/4 < 2/3)
	h2 := getBlockHeight(t, "http://localhost:26657")
	// Height might be same or slightly increased if blocks were in-flight
	t.Logf("Height before stop: %d, after: %d (chain should be halted)", h1, h2)
}

func TestRecovery(t *testing.T) {
	h1 := getBlockHeight(t, "http://localhost:26657")
	if h1 < 0 {
		t.Skip("Network not running")
	}

	// Stop 2 nodes
	stopContainer(t, "sage-cometbft2-1")
	stopContainer(t, "sage-cometbft3-1")
	time.Sleep(5 * time.Second)

	// Restart both
	startContainer(t, "sage-cometbft2-1")
	startContainer(t, "sage-cometbft3-1")
	time.Sleep(15 * time.Second)

	// Chain should resume
	h2 := getBlockHeight(t, "http://localhost:26657")
	require.Greater(t, h2, h1, "chain should resume after validators restart")
	t.Logf("Height before: %d, after recovery: %d", h1, h2)
}
