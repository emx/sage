package web

import (
	"archive/zip"
	"bytes"
	"encoding/json"
	"strings"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// ---------------------------------------------------------------------------
// ChatGPT parser tests
// ---------------------------------------------------------------------------

func TestImport_ParseChatGPTJSON_ValidTreeConversation(t *testing.T) {
	rootID := "root-node"
	userID := "user-node"
	assistantID := "assistant-node"

	conv := chatGPTConversation{
		Title:      "Test Conversation",
		CreateTime: 1700000000,
		Mapping: map[string]chatGPTNode{
			rootID: {
				ID:       rootID,
				Message:  nil, // root has no message
				Parent:   nil,
				Children: []string{userID},
			},
			userID: {
				ID: userID,
				Message: &chatGPTMsg{
					Author:  chatGPTAuthor{Role: "user"},
					Content: chatGPTContent{Parts: []interface{}{"Hello, how are you?"}},
				},
				Parent:   strPtr(rootID),
				Children: []string{assistantID},
			},
			assistantID: {
				ID: assistantID,
				Message: &chatGPTMsg{
					Author:  chatGPTAuthor{Role: "assistant"},
					Content: chatGPTContent{Parts: []interface{}{"I'm doing great, thanks!"}},
				},
				Parent:   strPtr(userID),
				Children: nil,
			},
		},
	}

	data, err := json.Marshal([]chatGPTConversation{conv})
	require.NoError(t, err)

	records, errs, err := parseChatGPTJSON(data)
	require.NoError(t, err)
	assert.Empty(t, errs)
	require.Len(t, records, 1)

	assert.Contains(t, records[0].Content, "[Test Conversation]")
	assert.Contains(t, records[0].Content, "user: Hello, how are you?")
	assert.Contains(t, records[0].Content, "assistant: I'm doing great, thanks!")
	assert.Equal(t, "chatgpt-history", records[0].DomainTag)
	assert.Equal(t, 0.85, records[0].ConfidenceScore)
	assert.Equal(t, importAgent, records[0].SubmittingAgent)
}

func TestImport_ParseChatGPTJSON_MultipleTurns(t *testing.T) {
	// Build a chain: root -> user1 -> asst1 -> user2 -> asst2
	conv := chatGPTConversation{
		Title:      "Multi Turn",
		CreateTime: 1700000000,
		Mapping: map[string]chatGPTNode{
			"root": {ID: "root", Parent: nil, Children: []string{"u1"}},
			"u1": {
				ID:       "u1",
				Message:  &chatGPTMsg{Author: chatGPTAuthor{Role: "user"}, Content: chatGPTContent{Parts: []interface{}{"First question"}}},
				Parent:   strPtr("root"),
				Children: []string{"a1"},
			},
			"a1": {
				ID:       "a1",
				Message:  &chatGPTMsg{Author: chatGPTAuthor{Role: "assistant"}, Content: chatGPTContent{Parts: []interface{}{"First answer"}}},
				Parent:   strPtr("u1"),
				Children: []string{"u2"},
			},
			"u2": {
				ID:       "u2",
				Message:  &chatGPTMsg{Author: chatGPTAuthor{Role: "user"}, Content: chatGPTContent{Parts: []interface{}{"Second question"}}},
				Parent:   strPtr("a1"),
				Children: []string{"a2"},
			},
			"a2": {
				ID:       "a2",
				Message:  &chatGPTMsg{Author: chatGPTAuthor{Role: "assistant"}, Content: chatGPTContent{Parts: []interface{}{"Second answer"}}},
				Parent:   strPtr("u2"),
				Children: nil,
			},
		},
	}

	data, err := json.Marshal([]chatGPTConversation{conv})
	require.NoError(t, err)

	records, errs, err := parseChatGPTJSON(data)
	require.NoError(t, err)
	assert.Empty(t, errs)
	require.Len(t, records, 1)

	content := records[0].Content
	assert.Contains(t, content, "First question")
	assert.Contains(t, content, "First answer")
	assert.Contains(t, content, "Second question")
	assert.Contains(t, content, "Second answer")

	// Verify ordering: user questions come before assistant answers
	assert.True(t, strings.Index(content, "First question") < strings.Index(content, "First answer"))
	assert.True(t, strings.Index(content, "Second question") < strings.Index(content, "Second answer"))
}

func TestImport_ParseChatGPTJSON_SkipsSystemMessages(t *testing.T) {
	conv := chatGPTConversation{
		Title:      "System Skip Test",
		CreateTime: 1700000000,
		Mapping: map[string]chatGPTNode{
			"root": {ID: "root", Parent: nil, Children: []string{"sys"}},
			"sys": {
				ID:       "sys",
				Message:  &chatGPTMsg{Author: chatGPTAuthor{Role: "system"}, Content: chatGPTContent{Parts: []interface{}{"You are a helpful assistant"}}},
				Parent:   strPtr("root"),
				Children: []string{"u1"},
			},
			"u1": {
				ID:       "u1",
				Message:  &chatGPTMsg{Author: chatGPTAuthor{Role: "user"}, Content: chatGPTContent{Parts: []interface{}{"Hi"}}},
				Parent:   strPtr("sys"),
				Children: nil,
			},
		},
	}

	data, err := json.Marshal([]chatGPTConversation{conv})
	require.NoError(t, err)

	records, _, err := parseChatGPTJSON(data)
	require.NoError(t, err)
	require.Len(t, records, 1)

	assert.NotContains(t, records[0].Content, "system:")
	assert.NotContains(t, records[0].Content, "You are a helpful assistant")
	assert.Contains(t, records[0].Content, "user: Hi")
}

func TestImport_ParseChatGPTJSON_SkipsEmptyMessages(t *testing.T) {
	conv := chatGPTConversation{
		Title:      "Empty Msg Test",
		CreateTime: 1700000000,
		Mapping: map[string]chatGPTNode{
			"root": {ID: "root", Parent: nil, Children: []string{"u1"}},
			"u1": {
				ID:       "u1",
				Message:  &chatGPTMsg{Author: chatGPTAuthor{Role: "user"}, Content: chatGPTContent{Parts: []interface{}{""}}},
				Parent:   strPtr("root"),
				Children: []string{"u2"},
			},
			"u2": {
				ID:       "u2",
				Message:  &chatGPTMsg{Author: chatGPTAuthor{Role: "user"}, Content: chatGPTContent{Parts: []interface{}{"Real message"}}},
				Parent:   strPtr("u1"),
				Children: nil,
			},
		},
	}

	data, err := json.Marshal([]chatGPTConversation{conv})
	require.NoError(t, err)

	records, _, err := parseChatGPTJSON(data)
	require.NoError(t, err)
	require.Len(t, records, 1)
	assert.Contains(t, records[0].Content, "Real message")
}

func TestImport_ParseChatGPTJSON_LongContentTruncated(t *testing.T) {
	// Create many turns to exceed maxMemoryContent
	nodes := map[string]chatGPTNode{
		"root": {ID: "root", Parent: nil, Children: []string{"u0"}},
	}

	longText := strings.Repeat("A", 300) // each turn is ~310 chars with role prefix
	numTurns := 20                        // 20 turns x ~310 chars = ~6200 >> 2000

	for i := 0; i < numTurns; i++ {
		uID := "u" + strings.Repeat("0", i+1)
		aID := "a" + strings.Repeat("0", i+1)
		parentID := "root"
		if i > 0 {
			parentID = "a" + strings.Repeat("0", i)
		}

		nextChild := aID
		nodes[uID] = chatGPTNode{
			ID:       uID,
			Message:  &chatGPTMsg{Author: chatGPTAuthor{Role: "user"}, Content: chatGPTContent{Parts: []interface{}{longText}}},
			Parent:   strPtr(parentID),
			Children: []string{nextChild},
		}

		var children []string
		if i < numTurns-1 {
			children = []string{"u" + strings.Repeat("0", i+2)}
		}
		nodes[aID] = chatGPTNode{
			ID:       aID,
			Message:  &chatGPTMsg{Author: chatGPTAuthor{Role: "assistant"}, Content: chatGPTContent{Parts: []interface{}{longText}}},
			Parent:   strPtr(uID),
			Children: children,
		}

		if i == 0 {
			nodes["root"] = chatGPTNode{ID: "root", Parent: nil, Children: []string{uID}}
		}
	}

	conv := chatGPTConversation{
		Title:      "Long Conversation",
		CreateTime: 1700000000,
		Mapping:    nodes,
	}

	data, err := json.Marshal([]chatGPTConversation{conv})
	require.NoError(t, err)

	records, _, err := parseChatGPTJSON(data)
	require.NoError(t, err)
	require.Len(t, records, 1)

	assert.LessOrEqual(t, len(records[0].Content), maxMemoryContent,
		"content should be truncated to maxMemoryContent")
}

func TestImport_ParseChatGPTJSON_EmptyConversations(t *testing.T) {
	data := []byte(`[]`)
	records, errs, err := parseChatGPTJSON(data)
	require.NoError(t, err)
	assert.Empty(t, records)
	assert.Empty(t, errs)
}

func TestImport_ParseChatGPTJSON_NoMessages(t *testing.T) {
	// Conversation with mapping but no user/assistant messages
	conv := chatGPTConversation{
		Title:   "Empty Chat",
		Mapping: map[string]chatGPTNode{"root": {ID: "root", Parent: nil}},
	}
	data, _ := json.Marshal([]chatGPTConversation{conv})

	records, errs, err := parseChatGPTJSON(data)
	require.NoError(t, err)
	assert.Empty(t, records)
	assert.Len(t, errs, 1)
	assert.Contains(t, errs[0], "no messages")
}

func TestImport_ParseChatGPTJSON_InvalidJSON(t *testing.T) {
	_, _, err := parseChatGPTJSON([]byte(`not json`))
	require.Error(t, err)
	assert.Contains(t, err.Error(), "invalid ChatGPT JSON")
}

func TestImport_ParseChatGPTJSON_DefaultTitle(t *testing.T) {
	conv := chatGPTConversation{
		Title:      "", // empty title
		CreateTime: 1700000000,
		Mapping: map[string]chatGPTNode{
			"root": {ID: "root", Parent: nil, Children: []string{"u1"}},
			"u1": {
				ID:       "u1",
				Message:  &chatGPTMsg{Author: chatGPTAuthor{Role: "user"}, Content: chatGPTContent{Parts: []interface{}{"Hi"}}},
				Parent:   strPtr("root"),
				Children: nil,
			},
		},
	}
	data, _ := json.Marshal([]chatGPTConversation{conv})

	records, _, err := parseChatGPTJSON(data)
	require.NoError(t, err)
	require.Len(t, records, 1)
	assert.Contains(t, records[0].Content, "[Conversation 1]")
}

// ---------------------------------------------------------------------------
// ChatGPT ZIP parser tests
// ---------------------------------------------------------------------------

func TestImport_ParseChatGPTZip_Valid(t *testing.T) {
	conv := chatGPTConversation{
		Title:      "ZIP Conversation",
		CreateTime: 1700000000,
		Mapping: map[string]chatGPTNode{
			"root": {ID: "root", Parent: nil, Children: []string{"u1"}},
			"u1": {
				ID:       "u1",
				Message:  &chatGPTMsg{Author: chatGPTAuthor{Role: "user"}, Content: chatGPTContent{Parts: []interface{}{"Hello from ZIP"}}},
				Parent:   strPtr("root"),
				Children: nil,
			},
		},
	}
	jsonData, err := json.Marshal([]chatGPTConversation{conv})
	require.NoError(t, err)

	zipData := createZip(t, "conversations.json", jsonData)

	records, errs, err := parseChatGPTZip(zipData)
	require.NoError(t, err)
	assert.Empty(t, errs)
	require.Len(t, records, 1)
	assert.Contains(t, records[0].Content, "Hello from ZIP")
}

func TestImport_ParseChatGPTZip_NestedPath(t *testing.T) {
	// conversations.json inside a subdirectory should still be found
	conv := chatGPTConversation{
		Title:      "Nested",
		CreateTime: 1700000000,
		Mapping: map[string]chatGPTNode{
			"root": {ID: "root", Parent: nil, Children: []string{"u1"}},
			"u1": {
				ID:       "u1",
				Message:  &chatGPTMsg{Author: chatGPTAuthor{Role: "user"}, Content: chatGPTContent{Parts: []interface{}{"Nested hello"}}},
				Parent:   strPtr("root"),
				Children: nil,
			},
		},
	}
	jsonData, _ := json.Marshal([]chatGPTConversation{conv})

	zipData := createZip(t, "export/conversations.json", jsonData)

	records, _, err := parseChatGPTZip(zipData)
	require.NoError(t, err)
	require.Len(t, records, 1)
	assert.Contains(t, records[0].Content, "Nested hello")
}

func TestImport_ParseChatGPTZip_MissingConversationsJSON(t *testing.T) {
	zipData := createZip(t, "other.json", []byte(`{}`))

	_, _, err := parseChatGPTZip(zipData)
	require.Error(t, err)
	assert.Contains(t, err.Error(), "conversations.json not found")
}

func TestImport_ParseChatGPTZip_InvalidZipData(t *testing.T) {
	_, _, err := parseChatGPTZip([]byte("not a zip file"))
	require.Error(t, err)
	assert.Contains(t, err.Error(), "invalid zip")
}

// ---------------------------------------------------------------------------
// Gemini parser tests
// ---------------------------------------------------------------------------

func TestImport_ParseGeminiJSON_Valid(t *testing.T) {
	entries := []geminiEntry{
		{
			Header:   "Gemini Apps",
			Title:    "What is the capital of France?",
			Time:     "2024-01-15T10:30:00Z",
			Products: []string{"Gemini"},
		},
		{
			Header:   "Gemini Apps",
			Title:    "Explain quantum computing",
			Time:     "2024-01-16T14:00:00Z",
			Products: []string{"Gemini"},
		},
	}

	data, err := json.Marshal(entries)
	require.NoError(t, err)

	records, errs, err := parseGeminiJSON(data)
	require.NoError(t, err)
	assert.Empty(t, errs)
	require.Len(t, records, 2)

	assert.Equal(t, "What is the capital of France?", records[0].Content)
	assert.Equal(t, "gemini-history", records[0].DomainTag)
	assert.Equal(t, 0.80, records[0].ConfidenceScore)
	assert.Equal(t, "Explain quantum computing", records[1].Content)
}

func TestImport_ParseGeminiJSON_SkipsEmptyTitle(t *testing.T) {
	entries := []geminiEntry{
		{Header: "Gemini Apps", Title: "", Time: "2024-01-15T10:30:00Z"},
		{Header: "Gemini Apps", Title: "Valid entry", Time: "2024-01-15T10:30:00Z"},
	}

	data, _ := json.Marshal(entries)
	records, _, err := parseGeminiJSON(data)
	require.NoError(t, err)
	require.Len(t, records, 1)
	assert.Equal(t, "Valid entry", records[0].Content)
}

func TestImport_ParseGeminiJSON_TruncatesLongContent(t *testing.T) {
	longTitle := strings.Repeat("B", 3000)
	entries := []geminiEntry{
		{Header: "Gemini Apps", Title: longTitle, Time: "2024-01-15T10:30:00Z"},
	}

	data, _ := json.Marshal(entries)
	records, _, err := parseGeminiJSON(data)
	require.NoError(t, err)
	require.Len(t, records, 1)
	assert.Len(t, records[0].Content, maxMemoryContent)
}

func TestImport_ParseGeminiJSON_NoValidEntries(t *testing.T) {
	entries := []geminiEntry{{Header: "Gemini Apps", Title: ""}}
	data, _ := json.Marshal(entries)

	records, errs, err := parseGeminiJSON(data)
	require.NoError(t, err)
	assert.Empty(t, records)
	assert.Contains(t, errs[0], "no valid entries found")
}

func TestImport_ParseGeminiJSON_InvalidJSON(t *testing.T) {
	_, _, err := parseGeminiJSON([]byte(`{invalid`))
	require.Error(t, err)
	assert.Contains(t, err.Error(), "invalid Gemini JSON")
}

// ---------------------------------------------------------------------------
// Claude.ai parser tests
// ---------------------------------------------------------------------------

func TestImport_ParseClaudeJSON_Valid(t *testing.T) {
	convos := []claudeConversation{
		{
			UUID:      "uuid-1",
			Name:      "Claude Chat About Go",
			CreatedAt: "2024-02-20T09:00:00Z",
			UpdatedAt: "2024-02-20T09:30:00Z",
			ChatMessages: []claudeChatMessage{
				{Sender: "human", Text: "How do I write tests in Go?", CreatedAt: "2024-02-20T09:00:00Z"},
				{Sender: "assistant", Text: "You can use the testing package.", CreatedAt: "2024-02-20T09:01:00Z"},
			},
		},
	}

	data, err := json.Marshal(convos)
	require.NoError(t, err)

	records, errs, err := parseClaudeJSON(data)
	require.NoError(t, err)
	assert.Empty(t, errs)
	require.Len(t, records, 1)

	assert.Contains(t, records[0].Content, "[Claude Chat About Go]")
	assert.Contains(t, records[0].Content, "human: How do I write tests in Go?")
	assert.Contains(t, records[0].Content, "assistant: You can use the testing package.")
	assert.Equal(t, "claude-history", records[0].DomainTag)
	assert.Equal(t, 0.85, records[0].ConfidenceScore)
}

func TestImport_ParseClaudeJSON_SkipsEmptyMessages(t *testing.T) {
	convos := []claudeConversation{
		{
			Name:      "Chat",
			CreatedAt: "2024-02-20T09:00:00Z",
			ChatMessages: []claudeChatMessage{
				{Sender: "human", Text: "", CreatedAt: "2024-02-20T09:00:00Z"},
				{Sender: "assistant", Text: "Hi there!", CreatedAt: "2024-02-20T09:01:00Z"},
			},
		},
	}

	data, _ := json.Marshal(convos)
	records, _, err := parseClaudeJSON(data)
	require.NoError(t, err)
	require.Len(t, records, 1)
	// Only the assistant message should appear (human text was empty)
	assert.NotContains(t, records[0].Content, "human:")
	assert.Contains(t, records[0].Content, "assistant: Hi there!")
}

func TestImport_ParseClaudeJSON_NoMessages(t *testing.T) {
	convos := []claudeConversation{
		{
			Name:         "Empty Chat",
			CreatedAt:    "2024-02-20T09:00:00Z",
			ChatMessages: []claudeChatMessage{},
		},
	}

	data, _ := json.Marshal(convos)
	records, errs, err := parseClaudeJSON(data)
	require.NoError(t, err)
	assert.Empty(t, records)
	assert.Len(t, errs, 1)
	assert.Contains(t, errs[0], "no messages")
}

func TestImport_ParseClaudeJSON_DefaultTitle(t *testing.T) {
	convos := []claudeConversation{
		{
			Name:      "",
			CreatedAt: "2024-02-20T09:00:00Z",
			ChatMessages: []claudeChatMessage{
				{Sender: "human", Text: "Hello", CreatedAt: "2024-02-20T09:00:00Z"},
			},
		},
	}

	data, _ := json.Marshal(convos)
	records, _, err := parseClaudeJSON(data)
	require.NoError(t, err)
	require.Len(t, records, 1)
	assert.Contains(t, records[0].Content, "[Conversation 1]")
}

func TestImport_ParseClaudeJSON_InvalidJSON(t *testing.T) {
	_, _, err := parseClaudeJSON([]byte(`not json`))
	require.Error(t, err)
	assert.Contains(t, err.Error(), "invalid Claude JSON")
}

// ---------------------------------------------------------------------------
// Generic parser tests
// ---------------------------------------------------------------------------

func TestImport_ParseGenericJSON_Valid(t *testing.T) {
	entries := []genericEntry{
		{Content: "Some memory content", Title: "My Note", Time: "2024-03-01T12:00:00Z"},
		{Content: "", Title: "Title as fallback", Time: "2024-03-02T12:00:00Z"},
	}

	data, _ := json.Marshal(entries)
	records, errs, err := parseGenericJSON(data)
	require.NoError(t, err)
	assert.Empty(t, errs)
	require.Len(t, records, 2)

	assert.Equal(t, "Some memory content", records[0].Content)
	assert.Equal(t, "Title as fallback", records[1].Content)
	assert.Equal(t, "generic-import", records[0].DomainTag)
	assert.Equal(t, 0.75, records[0].ConfidenceScore)
}

func TestImport_ParseGenericJSON_SkipsEmptyEntries(t *testing.T) {
	entries := []genericEntry{
		{Content: "", Title: ""},
		{Content: "Real content"},
	}

	data, _ := json.Marshal(entries)
	records, _, err := parseGenericJSON(data)
	require.NoError(t, err)
	require.Len(t, records, 1)
	assert.Equal(t, "Real content", records[0].Content)
}

func TestImport_ParseGenericJSON_TruncatesLongContent(t *testing.T) {
	entries := []genericEntry{
		{Content: strings.Repeat("C", 3000)},
	}

	data, _ := json.Marshal(entries)
	records, _, err := parseGenericJSON(data)
	require.NoError(t, err)
	require.Len(t, records, 1)
	assert.Len(t, records[0].Content, maxMemoryContent)
}

func TestImport_ParseGenericJSON_NoValidEntries(t *testing.T) {
	entries := []genericEntry{{Content: "", Title: ""}}
	data, _ := json.Marshal(entries)

	records, errs, err := parseGenericJSON(data)
	require.NoError(t, err)
	assert.Empty(t, records)
	assert.Contains(t, errs[0], "no entries with content found")
}

func TestImport_ParseGenericJSON_InvalidJSON(t *testing.T) {
	_, _, err := parseGenericJSON([]byte(`{bad`))
	require.Error(t, err)
	assert.Contains(t, err.Error(), "invalid JSON array")
}

// ---------------------------------------------------------------------------
// Format detection tests
// ---------------------------------------------------------------------------

func TestImport_DetectAndParseJSON_ChatGPTFormat(t *testing.T) {
	conv := chatGPTConversation{
		Title:      "Detected ChatGPT",
		CreateTime: 1700000000,
		Mapping: map[string]chatGPTNode{
			"root": {ID: "root", Parent: nil, Children: []string{"u1"}},
			"u1": {
				ID:       "u1",
				Message:  &chatGPTMsg{Author: chatGPTAuthor{Role: "user"}, Content: chatGPTContent{Parts: []interface{}{"Hi"}}},
				Parent:   strPtr("root"),
				Children: nil,
			},
		},
	}
	data, _ := json.Marshal([]chatGPTConversation{conv})

	records, source, _, err := detectAndParseJSON(data)
	require.NoError(t, err)
	assert.Equal(t, "chatgpt", source)
	require.NotEmpty(t, records)
}

func TestImport_DetectAndParseJSON_GeminiFormat(t *testing.T) {
	entries := []geminiEntry{
		{Header: "Gemini Apps", Title: "Test query", Time: "2024-01-15T10:30:00Z"},
	}
	data, _ := json.Marshal(entries)

	records, source, _, err := detectAndParseJSON(data)
	require.NoError(t, err)
	assert.Equal(t, "gemini", source)
	require.NotEmpty(t, records)
}

func TestImport_DetectAndParseJSON_ClaudeFormat(t *testing.T) {
	convos := []claudeConversation{
		{
			Name:      "Test",
			CreatedAt: "2024-02-20T09:00:00Z",
			ChatMessages: []claudeChatMessage{
				{Sender: "human", Text: "Hello", CreatedAt: "2024-02-20T09:00:00Z"},
			},
		},
	}
	data, _ := json.Marshal(convos)

	records, source, _, err := detectAndParseJSON(data)
	require.NoError(t, err)
	assert.Equal(t, "claude", source)
	require.NotEmpty(t, records)
}

func TestImport_DetectAndParseJSON_GenericFallback(t *testing.T) {
	entries := []genericEntry{
		{Content: "Some content", Time: "2024-01-01T00:00:00Z"},
	}
	data, _ := json.Marshal(entries)

	records, source, _, err := detectAndParseJSON(data)
	require.NoError(t, err)
	assert.Equal(t, "generic", source)
	require.NotEmpty(t, records)
}

func TestImport_DetectAndParseJSON_NotJSONArray(t *testing.T) {
	_, _, _, err := detectAndParseJSON([]byte(`{"key": "value"}`))
	require.Error(t, err)
	assert.Contains(t, err.Error(), "not a JSON array")
}

func TestImport_DetectAndParseJSON_EmptyArray(t *testing.T) {
	_, _, _, err := detectAndParseJSON([]byte(`[]`))
	require.Error(t, err)
	assert.Contains(t, err.Error(), "empty JSON array")
}

func TestImport_DetectAndParseJSON_InvalidFirstElement(t *testing.T) {
	_, _, _, err := detectAndParseJSON([]byte(`["just a string"]`))
	require.Error(t, err)
	assert.Contains(t, err.Error(), "not a JSON object")
}

func TestImport_DetectAndParseJSON_GeminiHeaderWrongValue(t *testing.T) {
	// Has "header" key but not "Gemini Apps" -- should NOT be detected as Gemini
	data := []byte(`[{"header": "Not Gemini", "title": "Something", "content": "fallback"}]`)

	_, source, _, err := detectAndParseJSON(data)
	require.NoError(t, err)
	assert.Equal(t, "generic", source, "non-Gemini header should fall through to generic")
}

// ---------------------------------------------------------------------------
// Helper function tests
// ---------------------------------------------------------------------------

func TestImport_WalkChatGPTTree_EmptyMapping(t *testing.T) {
	conv := chatGPTConversation{Mapping: nil}
	turns := walkChatGPTTree(conv)
	assert.Nil(t, turns)
}

func TestImport_WalkChatGPTTree_FallbackRoot(t *testing.T) {
	// All nodes have a parent set, but one parent doesn't exist in mapping.
	// That node should be treated as root.
	conv := chatGPTConversation{
		Mapping: map[string]chatGPTNode{
			"orphan": {
				ID:       "orphan",
				Parent:   strPtr("nonexistent"),
				Message:  &chatGPTMsg{Author: chatGPTAuthor{Role: "user"}, Content: chatGPTContent{Parts: []interface{}{"I am root"}}},
				Children: nil,
			},
		},
	}

	turns := walkChatGPTTree(conv)
	require.Len(t, turns, 1)
	assert.Equal(t, "I am root", turns[0].Content)
}

func TestImport_FormatConversation_AllTurnsFit(t *testing.T) {
	turns := []conversationTurn{
		{Role: "user", Content: "Hello"},
		{Role: "assistant", Content: "Hi there"},
	}

	result := formatConversation("My Chat", turns)
	assert.Contains(t, result, "[My Chat]")
	assert.Contains(t, result, "user: Hello")
	assert.Contains(t, result, "assistant: Hi there")
	assert.NotContains(t, result, "[...truncated...]")
}

func TestImport_FormatConversation_Truncation(t *testing.T) {
	// Create turns that will exceed maxMemoryContent
	var turns []conversationTurn
	for i := 0; i < 30; i++ {
		turns = append(turns, conversationTurn{
			Role:    "user",
			Content: strings.Repeat("X", 100),
		})
		turns = append(turns, conversationTurn{
			Role:    "assistant",
			Content: strings.Repeat("Y", 100),
		})
	}

	result := formatConversation("Long Chat", turns)
	assert.LessOrEqual(t, len(result), maxMemoryContent)
	assert.Contains(t, result, "[...truncated...]")
	assert.Contains(t, result, "[Long Chat]")
}

func TestImport_FormatConversation_SingleTurn(t *testing.T) {
	turns := []conversationTurn{
		{Role: "user", Content: "Solo message"},
	}

	result := formatConversation("Solo", turns)
	assert.Equal(t, "[Solo]\nuser: Solo message\n", result)
}

func TestImport_ExtractParts_Mixed(t *testing.T) {
	parts := []interface{}{
		"Hello",
		map[string]interface{}{"type": "image"}, // should be skipped
		"World",
		"",    // empty strings skipped
	}

	result := extractParts(parts)
	assert.Equal(t, "Hello\nWorld", result)
}

func TestImport_ExtractParts_Empty(t *testing.T) {
	result := extractParts(nil)
	assert.Equal(t, "", result)
}

func TestImport_MakeRecord(t *testing.T) {
	rec := makeRecord("test content", "test-domain", 0.9, fixedTime())
	assert.NotEmpty(t, rec.MemoryID)
	assert.Equal(t, "test content", rec.Content)
	assert.Equal(t, "test-domain", rec.DomainTag)
	assert.Equal(t, 0.9, rec.ConfidenceScore)
	assert.Equal(t, importAgent, rec.SubmittingAgent)
	assert.NotEmpty(t, rec.ContentHash)
	assert.NotNil(t, rec.Embedding)
}

// ---------------------------------------------------------------------------
// Test helpers
// ---------------------------------------------------------------------------

func strPtr(s string) *string {
	return &s
}

func fixedTime() time.Time {
	t, _ := time.Parse(time.RFC3339, "2024-06-15T12:00:00Z")
	return t
}

func createZip(t *testing.T, filename string, content []byte) []byte {
	t.Helper()
	var buf bytes.Buffer
	w := zip.NewWriter(&buf)
	f, err := w.Create(filename)
	require.NoError(t, err)
	_, err = f.Write(content)
	require.NoError(t, err)
	require.NoError(t, w.Close())
	return buf.Bytes()
}
