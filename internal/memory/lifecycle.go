package memory

import (
	"fmt"
	"time"
)

// validTransitions defines the allowed state transitions.
var validTransitions = map[MemoryStatus][]MemoryStatus{
	StatusProposed:   {StatusValidated, StatusDeprecated},
	StatusValidated:  {StatusCommitted, StatusDeprecated},
	StatusCommitted:  {StatusChallenged, StatusDeprecated},
	StatusChallenged: {StatusCommitted, StatusDeprecated},
}

// ValidTransition checks if a state transition is allowed.
func ValidTransition(from, to MemoryStatus) bool {
	allowed, ok := validTransitions[from]
	if !ok {
		return false
	}
	for _, s := range allowed {
		if s == to {
			return true
		}
	}
	return false
}

// Transition attempts to transition a memory record to a new status.
func Transition(record *MemoryRecord, to MemoryStatus, now time.Time) error {
	if !ValidTransition(record.Status, to) {
		return fmt.Errorf("invalid transition from %s to %s", record.Status, to)
	}

	record.Status = to

	switch to {
	case StatusCommitted:
		record.CommittedAt = &now
	case StatusDeprecated:
		record.DeprecatedAt = &now
	}

	return nil
}
