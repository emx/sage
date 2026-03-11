package tx

import (
	"crypto/ed25519"
	"crypto/rand"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func testKeypair(t *testing.T) (ed25519.PublicKey, ed25519.PrivateKey) {
	t.Helper()
	pub, priv, err := ed25519.GenerateKey(rand.Reader)
	require.NoError(t, err)
	return pub, priv
}

func sampleSubmitTx() *ParsedTx {
	return &ParsedTx{
		Type: TxTypeMemorySubmit,
		MemorySubmit: &MemorySubmit{
			MemoryID:        "mem-001",
			ContentHash:     []byte("abcdef1234567890abcdef1234567890"),
			EmbeddingHash:   []byte("fedcba0987654321fedcba0987654321"),
			MemoryType:      MemoryTypeFact,
			DomainTag:       "crypto",
			ConfidenceScore: 0.85,
			Content:         "Bitcoin halving occurs every 210,000 blocks",
			ParentHash:      "",
		},
		Nonce:     1,
		Timestamp: time.Date(2025, 1, 1, 0, 0, 0, 0, time.UTC),
	}
}

func sampleVoteTx() *ParsedTx {
	return &ParsedTx{
		Type: TxTypeMemoryVote,
		MemoryVote: &MemoryVote{
			MemoryID:  "mem-001",
			Decision:  VoteDecisionAccept,
			Rationale: "Verified against blockchain data",
		},
		Nonce:     2,
		Timestamp: time.Date(2025, 1, 1, 0, 0, 1, 0, time.UTC),
	}
}

func sampleChallengeTx() *ParsedTx {
	return &ParsedTx{
		Type: TxTypeMemoryChallenge,
		MemoryChallenge: &MemoryChallenge{
			MemoryID: "mem-001",
			Reason:   "Outdated information",
			Evidence: "Post-2024 halving schedule changed",
		},
		Nonce:     3,
		Timestamp: time.Date(2025, 1, 1, 0, 0, 2, 0, time.UTC),
	}
}

func sampleCorroborateTx() *ParsedTx {
	return &ParsedTx{
		Type: TxTypeMemoryCorroborate,
		MemoryCorroborate: &MemoryCorroborate{
			MemoryID: "mem-001",
			Evidence: "Confirmed via Bitcoin Core source code",
		},
		Nonce:     4,
		Timestamp: time.Date(2025, 1, 1, 0, 0, 3, 0, time.UTC),
	}
}

func TestEncodeDecode(t *testing.T) {
	tests := []struct {
		name string
		tx   *ParsedTx
	}{
		{"MemorySubmit", sampleSubmitTx()},
		{"MemoryVote", sampleVoteTx()},
		{"MemoryChallenge", sampleChallengeTx()},
		{"MemoryCorroborate", sampleCorroborateTx()},
		{"MemoryReassign", &ParsedTx{
			Type: TxTypeMemoryReassign,
			MemoryReassign: &MemoryReassign{
				SourceAgentID: "source-orphan",
				TargetAgentID: "target-registered",
			},
			Nonce:     10,
			Timestamp: time.Date(2025, 1, 1, 0, 0, 10, 0, time.UTC),
		}},

	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			encoded, err := EncodeTx(tt.tx)
			require.NoError(t, err)
			require.NotEmpty(t, encoded)

			decoded, err := DecodeTx(encoded)
			require.NoError(t, err)

			assert.Equal(t, tt.tx.Type, decoded.Type)
			assert.Equal(t, tt.tx.Nonce, decoded.Nonce)
			assert.Equal(t, tt.tx.Timestamp.UnixNano(), decoded.Timestamp.UnixNano())

			switch tt.tx.Type {
			case TxTypeMemorySubmit:
				assert.Equal(t, tt.tx.MemorySubmit.MemoryID, decoded.MemorySubmit.MemoryID)
				assert.Equal(t, tt.tx.MemorySubmit.ContentHash, decoded.MemorySubmit.ContentHash)
				assert.Equal(t, tt.tx.MemorySubmit.EmbeddingHash, decoded.MemorySubmit.EmbeddingHash)
				assert.Equal(t, tt.tx.MemorySubmit.MemoryType, decoded.MemorySubmit.MemoryType)
				assert.Equal(t, tt.tx.MemorySubmit.DomainTag, decoded.MemorySubmit.DomainTag)
				assert.Equal(t, tt.tx.MemorySubmit.ConfidenceScore, decoded.MemorySubmit.ConfidenceScore)
				assert.Equal(t, tt.tx.MemorySubmit.Content, decoded.MemorySubmit.Content)
				assert.Equal(t, tt.tx.MemorySubmit.ParentHash, decoded.MemorySubmit.ParentHash)
			case TxTypeMemoryVote:
				assert.Equal(t, tt.tx.MemoryVote.MemoryID, decoded.MemoryVote.MemoryID)
				assert.Equal(t, tt.tx.MemoryVote.Decision, decoded.MemoryVote.Decision)
				assert.Equal(t, tt.tx.MemoryVote.Rationale, decoded.MemoryVote.Rationale)
			case TxTypeMemoryChallenge:
				assert.Equal(t, tt.tx.MemoryChallenge.MemoryID, decoded.MemoryChallenge.MemoryID)
				assert.Equal(t, tt.tx.MemoryChallenge.Reason, decoded.MemoryChallenge.Reason)
				assert.Equal(t, tt.tx.MemoryChallenge.Evidence, decoded.MemoryChallenge.Evidence)
			case TxTypeMemoryCorroborate:
				assert.Equal(t, tt.tx.MemoryCorroborate.MemoryID, decoded.MemoryCorroborate.MemoryID)
				assert.Equal(t, tt.tx.MemoryCorroborate.Evidence, decoded.MemoryCorroborate.Evidence)
			case TxTypeMemoryReassign:
				require.NotNil(t, decoded.MemoryReassign)
				assert.Equal(t, tt.tx.MemoryReassign.SourceAgentID, decoded.MemoryReassign.SourceAgentID)
				assert.Equal(t, tt.tx.MemoryReassign.TargetAgentID, decoded.MemoryReassign.TargetAgentID)
			}
		})
	}
}

func TestSignVerifyTx(t *testing.T) {
	_, priv := testKeypair(t)
	tx := sampleSubmitTx()

	err := SignTx(tx, priv)
	require.NoError(t, err)
	assert.Len(t, tx.Signature, ed25519.SignatureSize)
	assert.Len(t, tx.PublicKey, ed25519.PublicKeySize)

	valid, err := VerifyTx(tx)
	require.NoError(t, err)
	assert.True(t, valid)
}

func TestVerifyTxTampered(t *testing.T) {
	_, priv := testKeypair(t)
	tx := sampleSubmitTx()

	err := SignTx(tx, priv)
	require.NoError(t, err)

	// Tamper with the tx after signing
	tx.MemorySubmit.Content = "TAMPERED CONTENT"

	valid, err := VerifyTx(tx)
	require.NoError(t, err)
	assert.False(t, valid)
}

func TestDecodeInvalidBytes(t *testing.T) {
	tests := []struct {
		name string
		data []byte
	}{
		{"nil", nil},
		{"empty", []byte{}},
		{"too_short", []byte{0x01}},
		{"garbage", []byte{0xFF, 0xFF, 0xFF, 0xFF, 0xFF}},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			_, err := DecodeTx(tt.data)
			assert.Error(t, err)
		})
	}
}

func TestSigningPayloadDeterministic(t *testing.T) {
	tx1 := sampleSubmitTx()
	tx2 := sampleSubmitTx()

	p1, err1 := signingPayload(tx1)
	require.NoError(t, err1)
	p2, err2 := signingPayload(tx2)
	require.NoError(t, err2)

	assert.Equal(t, p1, p2, "identical transactions must produce identical signing payloads")
	assert.Len(t, p1, 32, "signing payload should be SHA-256 hash (32 bytes)")
}

func TestSignVerifyAllTxTypes(t *testing.T) {
	_, priv := testKeypair(t)

	txs := []*ParsedTx{
		sampleSubmitTx(),
		sampleVoteTx(),
		sampleChallengeTx(),
		sampleCorroborateTx(),
	}

	for _, tx := range txs {
		err := SignTx(tx, priv)
		require.NoError(t, err)

		valid, err := VerifyTx(tx)
		require.NoError(t, err)
		assert.True(t, valid, "verify should pass for tx type %d", tx.Type)
	}
}

func TestVerifyTxBadPublicKeyLength(t *testing.T) {
	tx := sampleSubmitTx()
	tx.Signature = make([]byte, ed25519.SignatureSize)
	tx.PublicKey = []byte{0x01, 0x02} // too short

	_, err := VerifyTx(tx)
	assert.ErrorIs(t, err, ErrPublicKeyLength)
}

func TestVerifyTxBadSignatureLength(t *testing.T) {
	tx := sampleSubmitTx()
	tx.PublicKey = make([]byte, ed25519.PublicKeySize)
	tx.Signature = []byte{0x01, 0x02} // too short

	_, err := VerifyTx(tx)
	assert.ErrorIs(t, err, ErrSignatureLength)
}

func TestMemoryReassignRoundTrip(t *testing.T) {
	original := &ParsedTx{
		Type:      TxTypeMemoryReassign,
		Nonce:     50,
		Timestamp: time.Now().Truncate(time.Nanosecond),
		MemoryReassign: &MemoryReassign{
			SourceAgentID: "orphaned-agent-id-from-per-project-session",
			TargetAgentID: "registered-agent-id-in-dashboard",
		},
	}

	encoded, err := EncodeTx(original)
	require.NoError(t, err)
	require.NotEmpty(t, encoded)

	decoded, err := DecodeTx(encoded)
	require.NoError(t, err)
	require.NotNil(t, decoded.MemoryReassign)

	assert.Equal(t, TxTypeMemoryReassign, decoded.Type)
	assert.Equal(t, original.MemoryReassign.SourceAgentID, decoded.MemoryReassign.SourceAgentID)
	assert.Equal(t, original.MemoryReassign.TargetAgentID, decoded.MemoryReassign.TargetAgentID)
	assert.Equal(t, original.Nonce, decoded.Nonce)
}

func TestMemoryReassignEmptyFields(t *testing.T) {
	// Empty source/target should still encode/decode cleanly
	original := &ParsedTx{
		Type:      TxTypeMemoryReassign,
		Nonce:     51,
		Timestamp: time.Now().Truncate(time.Nanosecond),
		MemoryReassign: &MemoryReassign{
			SourceAgentID: "",
			TargetAgentID: "",
		},
	}

	encoded, err := EncodeTx(original)
	require.NoError(t, err)

	decoded, err := DecodeTx(encoded)
	require.NoError(t, err)
	require.NotNil(t, decoded.MemoryReassign)

	assert.Empty(t, decoded.MemoryReassign.SourceAgentID)
	assert.Empty(t, decoded.MemoryReassign.TargetAgentID)
}

func TestMemoryReassignSignAndVerify(t *testing.T) {
	_, privKey, err := ed25519.GenerateKey(nil)
	require.NoError(t, err)

	ptx := &ParsedTx{
		Type:      TxTypeMemoryReassign,
		Nonce:     52,
		Timestamp: time.Now().Truncate(time.Nanosecond),
		MemoryReassign: &MemoryReassign{
			SourceAgentID: "source-agent",
			TargetAgentID: "target-agent",
		},
	}

	require.NoError(t, SignTx(ptx, privKey))
	require.NotEmpty(t, ptx.Signature)
	require.NotEmpty(t, ptx.PublicKey)

	valid, err := VerifyTx(ptx)
	require.NoError(t, err)
	assert.True(t, valid)

	// Tamper and verify failure
	ptx.MemoryReassign.TargetAgentID = "tampered-target"
	encoded, err := EncodeTx(ptx)
	require.NoError(t, err)
	decoded, err := DecodeTx(encoded)
	require.NoError(t, err)
	valid, err = VerifyTx(decoded)
	require.NoError(t, err)
	assert.False(t, valid)
}

func TestAgentRegisterRoundTrip(t *testing.T) {
	original := &ParsedTx{
		Type:      TxTypeAgentRegister,
		Nonce:     42,
		Timestamp: time.Now().Truncate(time.Nanosecond),
		AgentRegister: &AgentRegister{
			AgentID:    "abc123def456",
			Name:       "Research Agent",
			Role:       "member",
			BootBio:    "Autonomous research agent for knowledge synthesis",
			Provider:   "claude-code",
			P2PAddress: "192.168.1.100:26656",
		},
	}

	encoded, err := EncodeTx(original)
	require.NoError(t, err)
	require.NotEmpty(t, encoded)

	decoded, err := DecodeTx(encoded)
	require.NoError(t, err)
	require.NotNil(t, decoded.AgentRegister)

	assert.Equal(t, TxTypeAgentRegister, decoded.Type)
	assert.Equal(t, original.AgentRegister.AgentID, decoded.AgentRegister.AgentID)
	assert.Equal(t, original.AgentRegister.Name, decoded.AgentRegister.Name)
	assert.Equal(t, original.AgentRegister.Role, decoded.AgentRegister.Role)
	assert.Equal(t, original.AgentRegister.BootBio, decoded.AgentRegister.BootBio)
	assert.Equal(t, original.AgentRegister.Provider, decoded.AgentRegister.Provider)
	assert.Equal(t, original.AgentRegister.P2PAddress, decoded.AgentRegister.P2PAddress)
}

func TestAgentUpdateRoundTrip(t *testing.T) {
	original := &ParsedTx{
		Type:      TxTypeAgentUpdate,
		Nonce:     43,
		Timestamp: time.Now().Truncate(time.Nanosecond),
		AgentUpdateTx: &AgentUpdate{
			AgentID: "abc123def456",
			Name:    "Updated Agent Name",
			BootBio: "Updated bio description",
		},
	}

	encoded, err := EncodeTx(original)
	require.NoError(t, err)
	require.NotEmpty(t, encoded)

	decoded, err := DecodeTx(encoded)
	require.NoError(t, err)
	require.NotNil(t, decoded.AgentUpdateTx)

	assert.Equal(t, TxTypeAgentUpdate, decoded.Type)
	assert.Equal(t, original.AgentUpdateTx.AgentID, decoded.AgentUpdateTx.AgentID)
	assert.Equal(t, original.AgentUpdateTx.Name, decoded.AgentUpdateTx.Name)
	assert.Equal(t, original.AgentUpdateTx.BootBio, decoded.AgentUpdateTx.BootBio)
}

func TestAgentSetPermissionRoundTrip(t *testing.T) {
	original := &ParsedTx{
		Type:      TxTypeAgentSetPermission,
		Nonce:     44,
		Timestamp: time.Now().Truncate(time.Nanosecond),
		AgentSetPermission: &AgentSetPermission{
			AgentID:       "abc123def456",
			Clearance:     3,
			DomainAccess:  `[{"domain":"security","read":true,"write":false}]`,
			VisibleAgents: `["agent1","agent2"]`,
			OrgID:         "org-001",
			DeptID:        "dept-eng",
		},
	}

	encoded, err := EncodeTx(original)
	require.NoError(t, err)
	require.NotEmpty(t, encoded)

	decoded, err := DecodeTx(encoded)
	require.NoError(t, err)
	require.NotNil(t, decoded.AgentSetPermission)

	assert.Equal(t, TxTypeAgentSetPermission, decoded.Type)
	assert.Equal(t, original.AgentSetPermission.AgentID, decoded.AgentSetPermission.AgentID)
	assert.Equal(t, uint8(3), decoded.AgentSetPermission.Clearance)
	assert.Equal(t, original.AgentSetPermission.DomainAccess, decoded.AgentSetPermission.DomainAccess)
	assert.Equal(t, original.AgentSetPermission.VisibleAgents, decoded.AgentSetPermission.VisibleAgents)
	assert.Equal(t, original.AgentSetPermission.OrgID, decoded.AgentSetPermission.OrgID)
	assert.Equal(t, original.AgentSetPermission.DeptID, decoded.AgentSetPermission.DeptID)
}

func TestAgentRegisterEmptyFields(t *testing.T) {
	// Test with minimal fields (only AgentID and Name required in practice)
	original := &ParsedTx{
		Type:      TxTypeAgentRegister,
		Nonce:     45,
		Timestamp: time.Now().Truncate(time.Nanosecond),
		AgentRegister: &AgentRegister{
			AgentID: "minimal-agent",
			Name:    "Minimal",
		},
	}

	encoded, err := EncodeTx(original)
	require.NoError(t, err)

	decoded, err := DecodeTx(encoded)
	require.NoError(t, err)
	require.NotNil(t, decoded.AgentRegister)

	assert.Equal(t, "minimal-agent", decoded.AgentRegister.AgentID)
	assert.Equal(t, "Minimal", decoded.AgentRegister.Name)
	assert.Empty(t, decoded.AgentRegister.Role)
	assert.Empty(t, decoded.AgentRegister.BootBio)
	assert.Empty(t, decoded.AgentRegister.Provider)
	assert.Empty(t, decoded.AgentRegister.P2PAddress)
}

func TestAgentRegisterSignAndVerify(t *testing.T) {
	_, privKey, err := ed25519.GenerateKey(nil)
	require.NoError(t, err)

	ptx := &ParsedTx{
		Type:      TxTypeAgentRegister,
		Nonce:     100,
		Timestamp: time.Now().Truncate(time.Nanosecond),
		AgentRegister: &AgentRegister{
			AgentID:  "signed-agent",
			Name:     "Signed Agent",
			Role:     "admin",
			Provider: "claude-code",
		},
	}

	require.NoError(t, SignTx(ptx, privKey))
	require.NotEmpty(t, ptx.Signature)
	require.NotEmpty(t, ptx.PublicKey)

	valid, err := VerifyTx(ptx)
	require.NoError(t, err)
	assert.True(t, valid)

	// Tamper with the payload and verify signature fails
	ptx.AgentRegister.Name = "Tampered"
	encoded, err := EncodeTx(ptx)
	require.NoError(t, err)
	decoded, err := DecodeTx(encoded)
	require.NoError(t, err)
	valid, err = VerifyTx(decoded)
	require.NoError(t, err)
	assert.False(t, valid)
}
