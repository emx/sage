package abci

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

// Full app tests require PostgreSQL — these are basic sanity checks.

func TestComputeBlockHash(t *testing.T) {
	h1 := computeBlockHash([]string{"a", "b", "c"}, 1)
	h2 := computeBlockHash([]string{"c", "b", "a"}, 1) // Different order, same result (sorted)
	h3 := computeBlockHash([]string{"a", "b", "c"}, 2) // Different height

	assert.Equal(t, h1, h2, "should be deterministic regardless of input order")
	assert.NotEqual(t, h1, h3, "different height should produce different hash")
}
