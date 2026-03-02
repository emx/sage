package poe

import "time"

// ValidatorState holds the PoE state for a single validator.
type ValidatorState struct {
	ID                 string
	EWMA               *EWMATracker
	Expertise          *ExpertiseProfile
	LastActive         time.Time
	CorroborationCount int
}
