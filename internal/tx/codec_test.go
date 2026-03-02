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

	p1 := signingPayload(tx1)
	p2 := signingPayload(tx2)

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
