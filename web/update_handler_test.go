package web

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestSemverGreater(t *testing.T) {
	tests := []struct {
		a, b string
		want bool
	}{
		{"3.6.0", "3.5.0", true},
		{"3.5.0", "3.6.0", false},
		{"3.6.0", "3.6.0", false},  // equal, not greater
		{"3.10.0", "3.9.0", true},  // 10 > 9 (not string compare)
		{"4.0.0", "3.99.99", true},
		{"3.6.1", "3.6.0", true},
		{"3.6.0", "3.6.1", false},
		{"1.0.0", "0.99.0", true},
		{"3.7.0", "3.6.0", true},   // the real scenario: latest > current
		{"3.5.0", "3.5.0", false},  // same version
		{"dev", "3.6.0", false},    // dev parses as 0.0.0
		{"3.6.0-rc1", "3.5.0", true}, // pre-release suffix stripped
	}

	for _, tt := range tests {
		t.Run(tt.a+"_vs_"+tt.b, func(t *testing.T) {
			assert.Equal(t, tt.want, semverGreater(tt.a, tt.b))
		})
	}
}

func TestParseSemver(t *testing.T) {
	tests := []struct {
		input string
		want  [3]int
	}{
		{"3.6.0", [3]int{3, 6, 0}},
		{"v3.6.0", [3]int{3, 6, 0}},
		{"3.10.1", [3]int{3, 10, 1}},
		{"3.6.0-rc1", [3]int{3, 6, 0}},
		{"3.6.0+build123", [3]int{3, 6, 0}},
		{"dev", [3]int{0, 0, 0}},
		{"1.0", [3]int{1, 0, 0}},
		{"", [3]int{0, 0, 0}},
	}

	for _, tt := range tests {
		t.Run(tt.input, func(t *testing.T) {
			assert.Equal(t, tt.want, parseSemver(tt.input))
		})
	}
}

func TestFindAssetName(t *testing.T) {
	name := findAssetName("3.7.0")
	assert.Contains(t, name, "sage-gui_3.7.0_")
	assert.True(t, len(name) > 20)
}
