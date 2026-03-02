package memory

import (
	"math"
	"time"
)

const (
	// DefaultDecayRate is the default confidence decay rate (per day).
	DefaultDecayRate = 0.005
)

// domainDecayRates maps domain tags to their specific decay rates.
var domainDecayRates = map[string]float64{
	"crypto":     0.001, // 693-day half-life
	"vuln_intel": 0.01,  // 69-day half-life
}

// GetDecayRate returns the decay rate for a given domain tag.
func GetDecayRate(domainTag string) float64 {
	if rate, ok := domainDecayRates[domainTag]; ok {
		return rate
	}
	return DefaultDecayRate
}

// ComputeConfidence calculates the current confidence of a memory.
// Formula: conf(M, t) = conf_0 * exp(-λ_M * Δt_days) * (1 + 0.1 * log(1 + corr_count))
func ComputeConfidence(initialConf float64, createdAt time.Time, now time.Time, corroborationCount int, domainTag string) float64 {
	lambda := GetDecayRate(domainTag)
	deltaDays := now.Sub(createdAt).Hours() / 24.0

	if deltaDays < 0 {
		deltaDays = 0
	}

	decay := math.Exp(-lambda * deltaDays)
	corrobBoost := 1.0 + 0.1*math.Log(1.0+float64(corroborationCount))

	confidence := initialConf * decay * corrobBoost

	// Clamp to [0, 1]
	if confidence > 1.0 {
		confidence = 1.0
	}
	if confidence < 0.0 {
		confidence = 0.0
	}

	return confidence
}
