package web

import (
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// These tests use real export samples downloaded from public GitHub repos.
// They validate that our parsers work with actual provider data, not just synthetic fixtures.
// Files are expected at /tmp/sage-import-samples/ — skip if not present.

const sampleDir = "/tmp/sage-import-samples/"

func readSample(t *testing.T, name string) []byte {
	t.Helper()
	path := sampleDir + name
	data, err := os.ReadFile(path)
	if err != nil {
		t.Skipf("sample file not available: %s (run curl commands to download)", path)
	}
	return data
}

func TestRealData_ChatGPT(t *testing.T) {
	data := readSample(t, "chatgpt.json")

	records, source, errs, err := detectAndParseJSON(data)
	require.NoError(t, err)
	assert.Equal(t, "chatgpt", source, "should detect as ChatGPT format")
	assert.NotEmpty(t, records, "should produce at least 1 record")
	t.Logf("ChatGPT: %d records, %d errors", len(records), len(errs))
	for i, r := range records {
		t.Logf("  Record %d: domain=%s, confidence=%.2f, content[:80]=%q",
			i, r.DomainTag, r.ConfidenceScore, truncStr(r.Content, 80))
		assert.Equal(t, "chatgpt-history", r.DomainTag)
		assert.NotEmpty(t, r.Content)
		assert.LessOrEqual(t, len(r.Content), maxMemoryContent)
	}
}

func TestRealData_ClaudeMulti(t *testing.T) {
	data := readSample(t, "claude-multi.json")

	records, source, errs, err := detectAndParseJSON(data)
	require.NoError(t, err)
	assert.Equal(t, "claude", source, "should detect as Claude format")
	assert.NotEmpty(t, records, "should produce at least 1 record")
	t.Logf("Claude Multi: %d records, %d errors", len(records), len(errs))
	for i, r := range records {
		t.Logf("  Record %d: domain=%s, content[:80]=%q",
			i, r.DomainTag, truncStr(r.Content, 80))
		assert.Equal(t, "claude-history", r.DomainTag)
		assert.NotEmpty(t, r.Content)
	}
}

func TestRealData_ClaudeThinking(t *testing.T) {
	data := readSample(t, "claude-thinking.json")

	records, source, errs, err := detectAndParseJSON(data)
	require.NoError(t, err)
	assert.Equal(t, "claude", source, "should detect as Claude format")
	assert.NotEmpty(t, records, "should produce at least 1 record")
	t.Logf("Claude Thinking: %d records, %d errors", len(records), len(errs))
	for i, r := range records {
		t.Logf("  Record %d: domain=%s, content[:100]=%q",
			i, r.DomainTag, truncStr(r.Content, 100))
		assert.Equal(t, "claude-history", r.DomainTag)
		assert.NotEmpty(t, r.Content)
		// Should contain actual text, not be empty (the old parser would fail here)
		assert.Contains(t, r.Content, "Hello there")
		// Should NOT contain thinking block content
		assert.NotContains(t, r.Content, "The user asked for a greeting")
	}
}

func TestRealData_Grok(t *testing.T) {
	data := readSample(t, "grok.json")

	records, source, errs, err := detectAndParseJSON(data)
	require.NoError(t, err)
	assert.Equal(t, "grok", source, "should detect as Grok format")
	assert.NotEmpty(t, records, "should produce at least 1 record")
	t.Logf("Grok: %d records, %d errors", len(records), len(errs))
	for i, r := range records {
		t.Logf("  Record %d: domain=%s, content[:100]=%q",
			i, r.DomainTag, truncStr(r.Content, 100))
		assert.Equal(t, "grok-history", r.DomainTag)
		assert.NotEmpty(t, r.Content)
		assert.Contains(t, r.Content, "photosynthesis")
	}
}

func TestRealData_FinetuningJSONL(t *testing.T) {
	data := readSample(t, "finetune.jsonl")

	records, source, errs, err := parseJSONL(data)
	require.NoError(t, err)
	assert.Equal(t, "jsonl", source, "should detect as fine-tuning JSONL")
	assert.NotEmpty(t, records, "should produce at least 1 record")
	t.Logf("JSONL: %d records, %d errors", len(records), len(errs))
	for i, r := range records {
		t.Logf("  Record %d: domain=%s, content[:80]=%q",
			i, r.DomainTag, truncStr(r.Content, 80))
		assert.NotEmpty(t, r.Content)
	}
}

func truncStr(s string, n int) string {
	if len(s) <= n {
		return s
	}
	return s[:n] + "..."
}
