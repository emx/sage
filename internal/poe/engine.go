package poe

import "math"

const (
	// PoE weight exponents
	AlphaAccuracy      = 0.4
	BetaDomain         = 0.3
	GammaRecency       = 0.15
	DeltaCorroboration = 0.15

	// EpsilonFloor prevents zero factors from zeroing the entire weight.
	EpsilonFloor = 0.01

	// RepCap is the maximum fraction of total weight any single validator can hold.
	RepCap = 0.10
)

// ComputeWeight calculates the PoE weight using log-space geometric mean.
// W = exp(α·ln(A) + β·ln(D) + γ·ln(T) + δ·ln(S))
func ComputeWeight(accuracy, domain, recency, corroboration float64) float64 {
	// Apply epsilon floor to prevent log(0)
	a := math.Max(accuracy, EpsilonFloor)
	d := math.Max(domain, EpsilonFloor)
	t := math.Max(recency, EpsilonFloor)
	s := math.Max(corroboration, EpsilonFloor)

	logWeight := AlphaAccuracy*math.Log(a) +
		BetaDomain*math.Log(d) +
		GammaRecency*math.Log(t) +
		DeltaCorroboration*math.Log(s)

	return math.Exp(logWeight)
}

// NormalizeWeights applies the reputation cap and normalizes weights to sum to 1.
func NormalizeWeights(weights map[string]float64) map[string]float64 {
	if len(weights) == 0 {
		return weights
	}

	// Copy input so we don't mutate the caller's map
	current := make(map[string]float64, len(weights))
	for id, w := range weights {
		current[id] = w
	}

	// Apply rep cap iteratively until stable
	for iterations := 0; iterations < 10; iterations++ {
		var total float64
		for _, w := range current {
			total += w
		}
		if total == 0 {
			return current
		}

		capped := false
		next := make(map[string]float64, len(current))
		for id, w := range current {
			normalized := w / total
			if normalized > RepCap {
				next[id] = RepCap * total
				capped = true
			} else {
				next[id] = w
			}
		}
		current = next

		if !capped {
			break
		}
	}

	// Final normalization
	var total float64
	for _, w := range current {
		total += w
	}
	if total == 0 {
		return current
	}

	for id := range current {
		current[id] /= total
	}

	return current
}
