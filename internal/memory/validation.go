package memory

import (
	"crypto/sha256"
	"fmt"
)

// ValidateMemoryRecord validates all fields of a memory record.
func ValidateMemoryRecord(r *MemoryRecord) error {
	if r.Content == "" {
		return fmt.Errorf("content must not be empty")
	}
	if r.SubmittingAgent == "" {
		return fmt.Errorf("submitting_agent must not be empty")
	}
	if !IsValidMemoryType(r.MemoryType) {
		return fmt.Errorf("invalid memory_type: %s", r.MemoryType)
	}
	if r.DomainTag == "" {
		return fmt.Errorf("domain_tag must not be empty")
	}
	if r.ConfidenceScore < 0 || r.ConfidenceScore > 1 {
		return fmt.Errorf("confidence_score must be between 0 and 1, got %f", r.ConfidenceScore)
	}
	if !IsValidStatus(r.Status) {
		return fmt.Errorf("invalid status: %s", r.Status)
	}
	return nil
}

// ComputeContentHash computes the SHA-256 hash of memory content.
func ComputeContentHash(content string) []byte {
	h := sha256.Sum256([]byte(content))
	return h[:]
}
