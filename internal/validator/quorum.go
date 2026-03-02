package validator

import "sort"

// QuorumThreshold is the minimum fraction of weighted votes required for quorum.
const QuorumThreshold = 2.0 / 3.0

// CheckQuorum determines if a quorum has been reached given a set of votes and weights.
// votes maps validator ID to accept (true) or reject (false).
// weights maps validator ID to their PoE weight.
// Returns whether quorum was reached, the total weight of accepting votes, and the total weight.
func CheckQuorum(votes map[string]bool, weights map[string]float64) (reached bool, acceptWeight float64, totalWeight float64) {
	// Sort keys for deterministic iteration
	ids := make([]string, 0, len(weights))
	for id := range weights {
		ids = append(ids, id)
	}
	sort.Strings(ids)

	for _, id := range ids {
		w := weights[id]
		totalWeight += w
		if accepted, voted := votes[id]; voted && accepted {
			acceptWeight += w
		}
	}

	reached = HasQuorum(acceptWeight, totalWeight)
	return
}

// HasQuorum checks if the accept weight meets or exceeds the 2/3 quorum threshold.
func HasQuorum(acceptWeight, totalWeight float64) bool {
	if totalWeight == 0 {
		return false
	}
	return acceptWeight/totalWeight >= QuorumThreshold
}
