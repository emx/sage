package poe

import "math"

// DomainRegistry maps domain tags to vector indices.
type DomainRegistry struct {
	tagToIndex map[string]int
	tags       []string
}

// NewDomainRegistry creates a registry from a list of domain tags.
func NewDomainRegistry(tags []string) *DomainRegistry {
	m := make(map[string]int, len(tags))
	for i, tag := range tags {
		m[tag] = i
	}
	return &DomainRegistry{tagToIndex: m, tags: tags}
}

// Size returns the number of registered domains.
func (r *DomainRegistry) Size() int {
	return len(r.tags)
}

// DomainVector returns a one-hot vector for the given domain tag.
func (r *DomainRegistry) DomainVector(tag string) []float64 {
	vec := make([]float64, len(r.tags))
	if idx, ok := r.tagToIndex[tag]; ok {
		vec[idx] = 1.0
	}
	return vec
}

// ExpertiseProfile represents a validator's accumulated domain expertise.
type ExpertiseProfile struct {
	Vector []float64 `json:"vector"`
}

// NewExpertiseProfile creates a new empty expertise profile.
func NewExpertiseProfile(size int) *ExpertiseProfile {
	return &ExpertiseProfile{Vector: make([]float64, size)}
}

// UpdateExpertise accumulates accuracy-weighted domain expertise.
func UpdateExpertise(profile *ExpertiseProfile, domainVec []float64, accuracy float64) {
	if len(profile.Vector) == 0 {
		profile.Vector = make([]float64, len(domainVec))
	}
	for i := range domainVec {
		if i < len(profile.Vector) {
			profile.Vector[i] += domainVec[i] * accuracy
		}
	}
}

// CosineSimilarity computes cosine similarity between two vectors.
// Returns 0 if either vector is zero.
func CosineSimilarity(a, b []float64) float64 {
	if len(a) != len(b) || len(a) == 0 {
		return 0
	}

	var dot, normA, normB float64
	for i := range a {
		dot += a[i] * b[i]
		normA += a[i] * a[i]
		normB += b[i] * b[i]
	}

	if normA == 0 || normB == 0 {
		return 0
	}

	sim := dot / (math.Sqrt(normA) * math.Sqrt(normB))

	// Clamp to [0, 1]
	if sim < 0 {
		sim = 0
	}
	if sim > 1 {
		sim = 1
	}
	return sim
}
