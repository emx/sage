//go:build byzantine

package byzantine

import (
	"encoding/json"
	"fmt"
	"net/http"
	"testing"
	"time"
)

func waitForBlocks(t *testing.T, n int) {
	duration := time.Duration(n*3+2) * time.Second
	t.Logf("Waiting %v for %d blocks...", duration, n)
	time.Sleep(duration)
}

func isNodeUp(rpcURL string) bool {
	resp, err := http.Get(rpcURL + "/status")
	if err != nil {
		return false
	}
	defer resp.Body.Close()
	return resp.StatusCode == http.StatusOK
}

func getBlockHeightSafe(rpcURL string) int64 {
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
