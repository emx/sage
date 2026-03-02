# SAGE Phase 1 — Implementation Plan

## Permissioned BFT-Backed PoC

> **STATUS: PHASE 1 COMPLETE** — All components built, deployed, tested, and hardened.
> Built via 24-agent swarm (~90 min scaffold) + 5-agent swarm (quick wins + SDK) + manual integration.
> 16 post-build bugs identified and fixed through live network testing.

### Phase 1 Results Summary

| Target | Result | Status |
|--------|--------|--------|
| 4-validator BFT network | 9 containers (4 CometBFT + 4 ABCI + 1 PostgreSQL) running on sagenet | **DONE** |
| Memory lifecycle (submit/vote/challenge/corroborate) | All endpoints verified across all 4 nodes (ports 8080-8083) | **DONE** |
| PoE epoch scoring | Validator weights computed every 100 blocks, persisted to PostgreSQL | **DONE** |
| BFT fault tolerance | 1/4 down → chain continues, 2/4 down → chain halts, recovery verified | **DONE** |
| Throughput target: 50-200 mem/s | **956 req/s** submissions (4.8x above upper target) | **DONE** |
| P95 query latency target: <200ms | **21.6ms** P95 (9.3x faster than target) | **DONE** |
| Error rate | **0%** under load testing | **DONE** |
| Python SDK | Sync + Async clients, 21/21 tests pass, 4 examples verified against live network | **DONE** |
| Go unit tests | **48/48 pass**, `go vet` clean | **DONE** |
| Integration tests | 13 Go + 3 Python cross-node tests pass | **DONE** |
| Monitoring | Prometheus + Grafana with 3 dashboards, 5 alert rules | **DONE** |
| Validator persistence | Validators survive container restarts via BadgerDB | **DONE** |

### Remaining (deferred to Phase 2)
- Level Up agent integration (4 surfaces identified, SDK ready)
- PoE scores feeding into CometBFT validator power (dynamic weighting)
- HSM-backed key management
- 7+ geo-distributed validators

---

## Stack (Research-Confirmed)

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Consensus | CometBFT v0.38.x (latest patch) | BFT consensus, block production, validator management |
| State Machine | Go 1.22+ (ABCI 2.0 application) | Memory lifecycle, PoE scoring, state transitions |
| On-chain State | BadgerDB v4 (embedded) | Deterministic state for hashes, votes, status |
| Off-chain Storage | PostgreSQL 16 + pgvector (pgx v5 driver) | Full memory objects, embeddings, similarity search |
| API Gateway | Go (chi v5) + gRPC (buf) | Agent-facing REST + internal gRPC to ABCI |
| Transaction Format | Protobuf (deterministic serialization) | On-chain tx encoding with Ed25519 signatures |
| Agent SDK | Python (httpx + PyNaCl) | Sync + async clients for Level Up agents |
| Infrastructure | Docker Compose (9 containers: 4 CometBFT + 4 ABCI + 1 PostgreSQL) |
| Observability | Prometheus + Grafana | CometBFT native metrics + custom SAGE metrics |
| CI/CD | GitHub Actions + golangci-lint | Lint, test, build, Docker, integration |

### Key Technology Decisions (from research)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| REST framework | **chi v5** (not gin/echo) | stdlib-compatible (`net/http` handlers), CometBFT ecosystem alignment, lightweight |
| ABCI approach | **Raw CometBFT ABCI** (not Cosmos SDK) | No token/module overhead; SAGE is a custom protocol, not a blockchain |
| CometBFT transport | **In-process (local)** | One binary per node via `proxy.NewLocalClientCreator(app)` — simplest |
| Transaction codec | **Protobuf** | Deterministic serialization critical for hash consistency across nodes |
| API spec | **OpenAPI 3.1 + oapi-codegen** | Spec-first design, auto-generated Go server stubs |
| Python Ed25519 | **PyNaCl** (libsodium) | Battle-tested, compatible with Go's `crypto/ed25519` |
| Query endpoint | **POST /v1/memory/query** (not GET) | Embedding vectors (1536 floats) too large for query params |
| Error format | **RFC 7807 Problem Details** | Standard, machine-parseable, extensible |
| Pagination | **Cursor-based** | Efficient for append-heavy workloads |
| Load testing | **k6** (formal) + **hey** (quick) | Scriptable scenarios with thresholds |
| DB migrations | **goose** | Simple, SQL-based migrations |

---

## Repository Structure

```
sage/
├── cmd/
│   ├── amid/                    # ABCI application daemon (main.go)
│   └── sage-cli/                # CLI for admin + agent operations
├── internal/
│   ├── abci/                    # ABCI app (SageApp struct, CheckTx, FinalizeBlock, Commit)
│   │   ├── app.go               # ABCI method implementations
│   │   ├── state.go             # AppState, deterministic hash computation
│   │   └── state_test.go
│   ├── memory/                  # Memory domain model + lifecycle
│   │   ├── model.go             # MemoryRecord, MemoryStatus
│   │   ├── lifecycle.go         # State transitions (Proposed→Validated→Committed)
│   │   ├── confidence.go        # Confidence decay formula
│   │   └── lifecycle_test.go
│   ├── poe/                     # Proof of Experience scoring engine
│   │   ├── engine.go            # W_i formula (log-space computation)
│   │   ├── ewma.go              # EWMA accuracy tracker (3 values: weighted_sum, weight_denom, count)
│   │   ├── domain.go            # Fixed-vocabulary cosine similarity
│   │   ├── epoch.go             # Block-based epoch boundary logic
│   │   ├── collusion.go         # Phi coefficient + ring buffer per validator pair
│   │   └── engine_test.go
│   ├── store/                   # Storage implementations
│   │   ├── store.go             # Interface definition
│   │   ├── postgres.go          # PostgreSQL + pgvector (pgx v5 + pgvector-go)
│   │   └── postgres_test.go
│   ├── tx/                      # Transaction encoding/decoding
│   │   ├── codec.go             # Protobuf encode/decode + Ed25519 sign/verify
│   │   └── types.go             # Transaction type constants
│   ├── auth/                    # Ed25519 identity + request signing
│   │   └── ed25519.go           # Go stdlib crypto/ed25519 (no external crypto deps)
│   └── validator/               # Validator set management
│       └── manager.go
├── api/
│   ├── openapi.yaml             # OpenAPI 3.1 spec (source of truth)
│   ├── generated/               # oapi-codegen output
│   ├── rest/                    # chi router + handlers
│   │   ├── server.go            # Router setup, middleware stack
│   │   ├── memory_handler.go    # Memory CRUD + query endpoints
│   │   ├── vote_handler.go      # Validator voting
│   │   └── middleware/          # Auth (Ed25519 sig verify), logging, rate limit
│   ├── grpc/                    # gRPC service implementations
│   └── proto/                   # Protobuf definitions (buf-managed)
│       └── sage/v1/
│           ├── tx.proto         # SageTx envelope (MemorySubmit, MemoryVote, Challenge, Corrob)
│           └── query.proto      # Query service
├── sdk/
│   └── python/                  # sage-sdk package
│       ├── pyproject.toml       # PEP 621 (httpx, pydantic, pynacl)
│       └── src/sage_sdk/
│           ├── client.py        # Sync client (SageClient)
│           ├── async_client.py  # Async client (AsyncSageClient) — Level Up uses httpx
│           ├── auth.py          # AgentIdentity (Ed25519 keypair, request signing)
│           ├── models.py        # Pydantic models matching API types
│           └── exceptions.py    # SageAPIError, SageAuthError, SageNotFoundError
├── deploy/
│   ├── docker-compose.yml       # 9 containers: 4 CometBFT + 4 ABCI + 1 PostgreSQL
│   ├── Dockerfile.node          # CometBFT binary (built from source)
│   ├── Dockerfile.abci          # Go ABCI application
│   ├── init.sql                 # PostgreSQL schema + pgvector
│   ├── init-testnet.sh          # Generate 4-node configs via `cometbft testnet`
│   ├── .env                     # PERSISTENT_PEERS, POSTGRES_PASSWORD
│   ├── genesis/                 # Generated node configs (node0-3)
│   ├── monitoring/
│   │   ├── prometheus.yml       # Scrape CometBFT :26660 + ABCI :2112
│   │   ├── alerts.yml           # ValidatorDown, ConsensusStalled, HighRejectRate
│   │   └── grafana/             # Provisioned dashboards
│   └── scripts/
│       ├── backup-cometbft.sh
│       └── backup-postgres.sh
├── test/
│   ├── integration/             # testcontainers-go (real PostgreSQL + CometBFT)
│   ├── byzantine/               # Byzantine fault simulation
│   └── benchmark/               # k6 load test scripts
├── .github/workflows/ci.yml     # lint → test → build → docker → integration
├── .golangci.yml
├── go.mod
├── go.sum
├── Makefile
└── docs/
```

---

## go.mod Dependencies

```
github.com/cometbft/cometbft v0.38.x     # ABCI interface + node
github.com/jackc/pgx/v5                   # PostgreSQL driver
github.com/pgvector/pgvector-go           # pgvector support
github.com/dgraph-io/badger/v4            # On-chain state store
github.com/go-chi/chi/v5                  # REST router
github.com/go-chi/httprate                # Rate limiting
github.com/go-chi/cors                    # CORS
google.golang.org/grpc                    # gRPC
google.golang.org/protobuf                # Protobuf
github.com/prometheus/client_golang       # Custom metrics
github.com/rs/zerolog                     # Structured logging
github.com/stretchr/testify               # Test assertions
github.com/pressly/goose/v3              # DB migrations
# crypto/ed25519 — Go stdlib (no external crypto)
```

---

## PostgreSQL Schema (init.sql)

```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Core memory table (off-chain content)
CREATE TABLE memories (
    memory_id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    submitting_agent  TEXT NOT NULL,
    content           TEXT NOT NULL,
    content_hash      BYTEA NOT NULL,
    embedding         vector(1536),
    embedding_hash    BYTEA,
    memory_type       TEXT NOT NULL CHECK (memory_type IN ('fact','observation','inference')),
    domain_tag        TEXT NOT NULL,
    confidence_score  DOUBLE PRECISION NOT NULL CHECK (confidence_score BETWEEN 0 AND 1),
    status            TEXT NOT NULL DEFAULT 'proposed',
    parent_hash       TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    committed_at      TIMESTAMPTZ,
    deprecated_at     TIMESTAMPTZ
);

CREATE INDEX idx_memories_domain ON memories(domain_tag);
CREATE INDEX idx_memories_status ON memories(status);
CREATE INDEX idx_memories_embedding ON memories USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 200);

-- Knowledge graph triples
CREATE TABLE knowledge_triples (
    id         BIGSERIAL PRIMARY KEY,
    memory_id  UUID REFERENCES memories(memory_id),
    subject    TEXT NOT NULL,
    predicate  TEXT NOT NULL,
    object     TEXT NOT NULL
);

-- Validation votes
CREATE TABLE validation_votes (
    id            BIGSERIAL PRIMARY KEY,
    memory_id     UUID REFERENCES memories(memory_id),
    validator_id  TEXT NOT NULL,
    decision      TEXT NOT NULL CHECK (decision IN ('accept','reject','abstain')),
    rationale     TEXT,
    weight_at_vote DOUBLE PRECISION,
    block_height  BIGINT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX idx_votes_memory_validator ON validation_votes(memory_id, validator_id);

-- Corroborations
CREATE TABLE corroborations (
    id         BIGSERIAL PRIMARY KEY,
    memory_id  UUID REFERENCES memories(memory_id),
    agent_id   TEXT NOT NULL,
    evidence   TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Validator PoE state (loaded into ABCI app memory at startup)
CREATE TABLE validator_scores (
    validator_id    TEXT PRIMARY KEY,
    weighted_sum    DOUBLE PRECISION NOT NULL DEFAULT 0,
    weight_denom    DOUBLE PRECISION NOT NULL DEFAULT 0,
    vote_count      BIGINT NOT NULL DEFAULT 0,
    expertise_vec   DOUBLE PRECISION[] NOT NULL DEFAULT '{}',
    last_active_ts  TIMESTAMPTZ,
    current_weight  DOUBLE PRECISION NOT NULL DEFAULT 0,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Epoch score history (append-only audit trail)
CREATE TABLE epoch_scores (
    epoch_num         BIGINT NOT NULL,
    block_height      BIGINT NOT NULL,
    validator_id      TEXT NOT NULL,
    accuracy          DOUBLE PRECISION NOT NULL,
    domain_score      DOUBLE PRECISION NOT NULL,
    recency_score     DOUBLE PRECISION NOT NULL,
    corr_score        DOUBLE PRECISION NOT NULL,
    raw_weight        DOUBLE PRECISION NOT NULL,
    capped_weight     DOUBLE PRECISION NOT NULL,
    normalized_weight DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (epoch_num, validator_id)
);

-- Domain registry (controlled vocabulary)
CREATE TABLE domains (
    domain_tag   TEXT PRIMARY KEY,
    description  TEXT,
    decay_rate   DOUBLE PRECISION NOT NULL DEFAULT 0.005,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Agent registry
CREATE TABLE agents (
    agent_id      TEXT PRIMARY KEY,
    display_name  TEXT,
    organization  TEXT,
    domains       TEXT[],
    registered_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## ABCI Application Architecture

### Critical Implementation Notes (from research)

1. **ABCI 2.0 (v0.38+)**: `FinalizeBlock` replaces `BeginBlock`/`DeliverTx`/`EndBlock`. `PrepareProposal` and `ProcessProposal` are required (can be pass-through). `AppHash` is returned from `FinalizeBlock` (NOT `Commit`).

2. **Determinism is absolute**: No `map` iteration order, no `time.Now()` (use `req.Time`), no floating-point format differences. Docker ensures same Go version across nodes.

3. **State separation**: On-chain state (BadgerDB) for hashes/votes/status. Off-chain data (PostgreSQL) written in `Commit` only (after finalization), never in `FinalizeBlock`.

4. **Replay protection**: CometBFT does NOT deduplicate transactions. `CheckTx` must track nonces per agent.

5. **Epoch boundaries**: Block-based (every N blocks), not time-based. 100 blocks ≈ 5 minutes at 3s block time. Return `ValidatorUpdates` from `FinalizeBlock` (Phase 1: log only, Phase 2: wire to consensus power).

6. **Validator power cap**: CometBFT enforces max 1/3 total voting power change per block. Phase 2 PoE→power updates must cap change to ±10% per epoch.

### Transaction Types (Protobuf envelope)

```protobuf
message SageTx {
    oneof payload {
        MemorySubmitTx    memory_submit    = 1;
        MemoryVoteTx      memory_vote      = 2;
        MemoryChallengeTx memory_challenge = 3;
        MemoryCorrobTx    memory_corrob    = 4;
    }
    bytes signature = 10;    // Ed25519
    bytes public_key = 11;
    uint64 nonce = 12;       // Replay protection
    google.protobuf.Timestamp timestamp = 13;
}
```

### App Hash Computation

Deterministic SHA-256 over sorted state:
- Sorted memory keys → hash(id + content_hash + status)
- Sorted validator keys → hash(id + score)
- Epoch number

All nodes must produce identical app hash or the chain halts.

---

## PoE Engine Implementation Details

### EWMA Accuracy (internal/poe/ewma.go)
- **Storage**: 3 values per validator (weighted_sum, weight_denom, count) — no vote history needed
- **Update**: Age previous observations by η, add new outcome: `WeightedSum = WeightedSum*η + outcome; WeightDenom = WeightDenom*η + 1.0`
- **Cold-start**: Blend approach (smooth transition from A_prior=0.5 to real score) instead of hard K_min cutoff

### Domain Similarity (internal/poe/domain.go)
- **Phase 1**: Fixed-vocabulary one-hot vectors over controlled domain tags
- **ExpertiseProfile**: Dense vector accumulated from accuracy-weighted validation outcomes
- **Cosine similarity**: Standard dot product / (norm * norm), clamped to [0, 1]

### Geometric Mean (internal/poe/weight.go)
- **Log-space computation**: `W = exp(α·ln(A) + β·ln(D) + γ·ln(T) + δ·ln(S))` — avoids underflow
- **Zero factor handling**: Apply epsilon floor (0.01) to corroboration S factor for new memories (S=0 would zero entire weight)

### Collusion Detection (internal/poe/collusion.go)
- **Phi coefficient** (Matthews correlation) per validator pair
- **Ring buffer** (window=50 joint votes) per pair
- **Threshold**: φ > 0.85 → alert + auto weight reduction
- **Edge case**: Exclude unanimous memories from phi computation (both accept on high-quality memory is legitimate)

### Memory Confidence Decay (internal/memory/confidence.go)
- **Lazy evaluation**: Compute on query, not eagerly
- **Batch archival sweep**: Every epoch, flag memories below 0.2 threshold
- **Domain-specific λ_M**: crypto=0.001 (693-day half-life), vuln_intel=0.01 (69-day half-life)

---

## REST API Endpoints (/v1)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /v1/memory/submit | Agent | Submit memory proposal → ABCI tx |
| POST | /v1/memory/query | Agent | Similarity search (embedding in body) |
| GET | /v1/memory/{id} | Agent | Get memory + status + votes |
| POST | /v1/memory/{id}/vote | Validator | Vote accept/reject/abstain |
| POST | /v1/memory/{id}/challenge | Agent | Challenge committed memory |
| POST | /v1/memory/{id}/corroborate | Agent | Corroborate existing memory |
| GET | /v1/agent/me | Agent | Agent profile + reputation |
| GET | /v1/validator/pending | Validator | Pending memories for domain |
| GET | /v1/validator/epoch | Validator | Current epoch info + scores |
| GET | /health | None | Health check |
| GET | /ready | None | Readiness check |

### Authentication
- **Headers**: `X-Agent-ID` (hex Ed25519 pubkey), `X-Signature` (Ed25519 sig over SHA-256(body)+timestamp), `X-Timestamp` (Unix seconds, 5-min window)
- **Public key IS the agent ID** — no separate auth system
- **Rate limiting**: Per-agent via `X-Agent-ID` header (100 req/min)

---

## Docker Compose Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         sagenet (Docker bridge)                  │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ cometbft0│  │ cometbft1│  │ cometbft2│  │ cometbft3│       │
│  │ :26656   │←→│ :26656   │←→│ :26656   │←→│ :26656   │ P2P   │
│  │ :26657   │  │ :26657   │  │ :26657   │  │ :26657   │ RPC   │
│  │ :26660   │  │ :26660   │  │ :26660   │  │ :26660   │ Prom  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │ ABCI         │ ABCI        │ ABCI        │ ABCI         │
│  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐       │
│  │  abci0   │  │  abci1   │  │  abci2   │  │  abci3   │       │
│  │ :8080    │  │          │  │          │  │          │ REST  │
│  │ :2112    │  │ :2112    │  │ :2112    │  │ :2112    │ Prom  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       └──────────────┴──────────────┴──────────────┘             │
│                              │                                    │
│                     ┌────────┴────────┐                           │
│                     │    PostgreSQL   │                           │
│                     │ pgvector:pg16  │                           │
│                     │    :5432       │                           │
│                     └────────────────┘                           │
│                                                                  │
│  ┌────────────┐  ┌────────────┐                                 │
│  │ Prometheus │  │  Grafana   │                                 │
│  │   :9191    │  │   :3000    │                                 │
│  └────────────┘  └────────────┘                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Port Map (Host)

| Service | P2P | RPC | Prometheus | REST |
|---------|-----|-----|------------|------|
| Node 0 | 26656 | 26657 | 26660 | 8080 |
| Node 1 | 26756 | 26757 | 26761 | — |
| Node 2 | 26856 | 26857 | 26862 | — |
| Node 3 | 26956 | 26957 | 26963 | — |
| PostgreSQL | — | — | — | 5432 |
| Prometheus | — | — | 9191 | — |
| Grafana | — | — | — | 3000 |

### Network Config
- **Persistent peers** only (no seed nodes) — `pex = false`
- **`addr_book_strict = false`** and **`allow_duplicate_ip = true`** required for Docker
- **Block time**: `timeout_commit = "3s"` in config.toml

---

## Week-by-Week Plan

### Week 1-2: Foundation — CometBFT Network + ABCI Scaffold ✅ COMPLETE

**Goal**: 4-node CometBFT network running with skeleton ABCI app that accepts and commits transactions.

**Tasks**:
1. Initialize Go module (`github.com/l33tdawg/sage`), set up project structure
2. Implement minimal ABCI application (ABCI 2.0 interface):
   - `Info` — return last committed height + app hash (handshake)
   - `InitChain` — parse genesis validators, initialize state
   - `CheckTx` — validate tx format + Ed25519 signature + nonce
   - `FinalizeBlock` — process all txs atomically, return app hash + tx results
   - `Commit` — persist finalized state to BadgerDB + PostgreSQL
   - `PrepareProposal` / `ProcessProposal` — pass-through (Phase 1)
   - `Query` — path-based ABCI queries (/memory, /validator, /status)
3. Protobuf transaction definitions (`api/proto/sage/v1/tx.proto`) with buf
4. Genesis generation: `deploy/init-testnet.sh` using `cometbft testnet --v 4`
   - Chain ID: `sage-testnet-1`
   - 4 validators with equal power (100 each)
   - Ed25519 key pairs auto-generated
5. Docker Compose for 9-container network (4 CometBFT + 4 ABCI + PostgreSQL)
6. PostgreSQL schema (`deploy/init.sql`) with pgvector extension + HNSW indexes
7. Verify: submit protobuf tx → broadcast_tx_sync → block committed → state updated across all 4 nodes
8. Makefile targets: `init`, `up`, `down`, `down-clean`, `build`, `test`, `status`, `logs`

**Deliverable**: `make init && make up` launches 4-validator network, accepts transactions, produces blocks at ~3s intervals. **✅ VERIFIED**

---

### Week 3-4: Memory Model + APIs ✅ COMPLETE

**Goal**: Full memory lifecycle (Proposed → Committed) with REST submission and query APIs.

**Tasks**:
1. Memory domain model (`internal/memory/`):
   - `MemoryRecord` struct with all schema fields
   - State transition enforcement (Proposed → Validated → Committed → Challenged → Deprecated)
   - Validation: memory type enum, confidence range, domain tag against registry
2. On-chain state (BadgerDB): memory_id → (content_hash, embedding_hash, status, votes)
3. Off-chain storage (`internal/store/postgres.go` using pgx v5):
   - `InsertMemory` — full content + embedding vector + triples
   - `QuerySimilar` — pgvector cosine distance with domain/status filters
   - `UpdateStatus` — state transitions
   - `InsertTriples` — knowledge graph storage
   - RFC 8785 JCS for deterministic content hashing
4. REST API with chi v5 (`api/rest/`):
   - `POST /v1/memory/submit` → serialize protobuf → `broadcast_tx_sync` → return tx_hash + memory_id
   - `GET /v1/memory/{id}` → ABCI query (on-chain) + PostgreSQL (off-chain content)
   - `POST /v1/memory/query` → pgvector similarity search (embedding in request body)
   - `POST /v1/memory/{id}/challenge` → challenge tx → status transition
   - `POST /v1/memory/{id}/corroborate` → corroboration tx
5. Authentication middleware (`api/rest/middleware/auth.go`):
   - Ed25519 signature verification on every request
   - Timestamp window (5 min) for replay protection
   - Agent registration lookup
6. OpenAPI 3.1 spec (`api/openapi.yaml`) as source of truth
7. Transaction flow: REST handler → protobuf encode → CometBFT RPC `broadcast_tx_sync` → CheckTx → block → FinalizeBlock → Commit → PostgreSQL write

**Deliverable**: Agents can submit memories via REST, memories are BFT-committed and queryable via similarity search. **✅ VERIFIED** — full lifecycle: submit (201) → get (200) → vote → corroborate → challenge, plus pgvector similarity search with 1536-dim embeddings.

---

### Week 5: Proof of Experience Engine ✅ COMPLETE

**Goal**: Application-layer PoE scoring with epoch-based reputation updates.

**Tasks**:
1. EWMA accuracy tracker (`internal/poe/ewma.go`):
   - Incremental update: 3 stored values (weighted_sum, weight_denom, count)
   - Blend cold-start (smooth A_prior→real, not hard K_min cutoff)
   - η=0.9, A_prior=0.5, K_min=10
2. Domain relevance (`internal/poe/domain.go`):
   - Fixed-vocabulary domain registry (controlled tags from `domains` table)
   - ExpertiseProfile: dense vector accumulated from accuracy-weighted validations
   - Cosine similarity with zero-vector handling
3. PoE weight computation (`internal/poe/engine.go`):
   - Log-space geometric mean: `W = exp(0.4·ln(A) + 0.3·ln(D) + 0.15·ln(T) + 0.15·ln(S))`
   - Epsilon floor (0.01) on S factor to prevent zero-weight cliff for new memories
   - Reputation cap: no validator > 10% of total normalized weight
4. Epoch logic (`internal/poe/epoch.go`):
   - Block-based: every 100 blocks (~5 min at 3s block time)
   - Recalculate all PoE scores, store to `epoch_scores` table
   - Sort validators by ID before computation (determinism)
   - Phase 1: log scores only. Phase 2: return `ValidatorUpdates` from `FinalizeBlock`
5. Validator voting mechanism:
   - `MemoryVoteTx` (accept/reject/abstain with optional rationale)
   - Quorum: ≥ 2/3 total PoE weight → Proposed→Committed
   - Votes recorded on-chain + audit trail in `validation_votes` table
6. Anti-gaming (`internal/poe/collusion.go`):
   - Phi coefficient per validator pair (ring buffer, window=50)
   - φ > 0.85 → alert log + weight reduction
   - Exclude unanimous memories from phi computation
7. Memory confidence decay (`internal/memory/confidence.go`):
   - Lazy evaluation on query
   - Domain-specific λ_M (crypto: 0.001, vuln_intel: 0.01, default: 0.005)
   - Batch archival sweep at epoch boundaries

**Deliverable**: Validators vote, PoE scores diverge based on track record, memories committed by weighted quorum. **✅ VERIFIED** — epoch scoring runs every 100 blocks, validator weights computed and persisted to PostgreSQL.

---

### Week 6-7: Level Up Agent Integration + Performance Measurement 🔲 DEFERRED TO PHASE 2

**Goal**: Connect Level Up agents to SAGE, measure performance delta.

**Tasks**:
1. Python SDK (`sdk/python/` — `sage-sdk` package):
   - `SageClient` (sync, requests-style) + `AsyncSageClient` (async, httpx — matches Level Up's httpx)
   - `AgentIdentity` class (Ed25519 via PyNaCl, `sign_request()`, `from_file()`)
   - Pydantic models for all API types
   - `propose()`, `query()`, `corroborate()`, `dispute()` methods
   - Context manager support (`with SageClient(...) as sage:`)
2. Level Up integration points (specific hard-coded knowledge to replace):
   - **Designer agent** (`calibrator.py:CATEGORY_DIFFICULTY_CONTEXT`): Hard-coded per-category knowledge → query SAGE for institutional patterns
   - **Designer agent** (`designer.py:DIFFICULTY_GUIDANCE`): Hard-coded difficulty ranges → augment with SAGE observations
   - **Designer agent** — NEW: query `solver_feedback.{category}` domain for cross-agent experience from blind par solver
   - **Templates** (`templates/web.py`): 80+ lines of hard-coded difficulty patterns per category → replace with SAGE queries
   - **Calibrator agent**: Difficulty calibration insights → submit as `observation` memories
   - **Validator agent**: Exploit strategy observations → submit as `observation` memories
   - **Par Solver** (`exploit.py:run_par`): Submit structured feedback to `solver_feedback.{category}` domain after each blind solve attempt — what worked, what didn't, what was too easy/hard
   - **Orchestrator**: Query SAGE before each pipeline stage for relevant institutional knowledge
3. Three-way measurement framework:
   - **Control (No SAGE)**: agents use local memory only (current behavior with hard-coded dicts)
   - **Isolated SAGE**: each agent queries/submits to its own domains only (per-agent learning)
   - **Cross-Agent SAGE**: full feedback loop — solver feedback flows to designer, generation patterns flow to calibrator
   - Metrics: challenge gen success rate, calibration accuracy, par solve rate/time, quality scores
4. Embedding generation: Use OpenAI `text-embedding-3-small` (1536 dims) initially, swap to Falcon later
5. Memory examples to seed:
   - "Flask web challenges with SQLi require prepared statements bypass, not just basic injection" (fact)
   - "Forensics challenges above difficulty 2.0 need multi-artifact correlation" (observation)
   - "Smart contract challenges with reentrancy should use Hardhat + ethers v5 API" (fact)
6. Logging + metrics pipeline for performance comparison

**Deliverable**: Level Up agents submit and query institutional memory, measurable performance delta captured. **🔲 DEFERRED** — Python SDK ready, 4 integration surfaces identified (see below), awaiting Level Up wiring.

---

### Week 8: Adversarial Testing + Documentation ✅ COMPLETE

**Goal**: Validate BFT guarantees, document findings.

**Tasks**:
1. Byzantine fault simulation:
   - Kill 1 of 4 validators → system continues (f=1, n=4, 3f+1=4 ✓)
   - Kill 2 → system halts (expected, 2/4 < 2/3) → verify recovery on restart
   - Malicious validator submits contradictory votes → no safety violation
   - Replay attack (reuse signed tx) → rejected by CheckTx nonce check
   - Memory poisoning → rejected by honest quorum
   - Corrupted state on 1 node → wipe data, state sync from peers
2. PoE gaming tests:
   - Rubber-stamping (always accept) → accuracy score drops
   - Collusion (2 validators always agree) → phi coefficient alert triggered
   - Domain capture attempt → capped at 10% weight
3. Performance benchmarks (k6 scripts):
   - Throughput: memories committed per second under load (target: 50-200/s)
   - Latency: submit-to-finality time (target: ~3s at 3s block time)
   - Query: pgvector similarity search at scale (1K, 10K, 100K memories)
   - P95 query latency target: <200ms
4. Documentation:
   - Architecture decision records
   - API documentation (OpenAPI spec)
   - Deployment guide (local + multi-VM)
   - Phase 1 findings report: what worked, what needs Phase 2
   - Phase 2 upgrade path: PoE→consensus power, HSM, governance txs

**Deliverable**: Byzantine resilience validated, performance benchmarked, findings documented, Phase 2 upgrade path clear. **✅ VERIFIED** — BFT tests pass (1/4 down continues, 2/4 halts, recovery + state replication), 956 req/s submissions, 21.6ms P95 queries, 0% error rate, monitoring live.

---

## Level Up "Sage-ify" Integration Map

### Three Integration Surfaces

Level Up has three distinct agent systems that SAGE can enhance. Each produces different kinds of institutional memory:

#### Surface 1: Challenge Generation Pipeline (orchestrator.py)

Hard-coded knowledge to replace:

| Agent | Current Pattern | SAGE Memory Type | Domain Tag |
|-------|----------------|------------------|------------|
| Designer | `DIFFICULTY_GUIDANCE` dict | observation | `calibration.difficulty` |
| Designer | `_smart_contract_dockerfile()` | fact | `infrastructure.docker.smart_contract` |
| Calibrator | `CATEGORY_DIFFICULTY_CONTEXT` | observation | `calibration.{category}` |
| Templates | `web.py` 80+ lines per category | observation | `challenge_generation.{category}` |
| Orchestrator | Pipeline failure patterns | inference | `pipeline.failure_patterns` |

```
Level Up Pipeline
     │
     ├── INIT → query SAGE for domain context
     ├── GENERATE → designer queries SAGE for patterns, submits results
     ├── VALIDATE → validator submits exploit observations
     ├── CALIBRATE → calibrator queries SAGE, submits difficulty insights
     └── POST-PIPELINE → submit success/failure as institutional memory
```

#### Surface 2: Blind Par Solver (exploit.py → run_par)

**This is the biggest opportunity.** The `ExploitAgent.run_par()` method attempts to solve challenges *blind* — no source code, no solution, just the player-facing description and the category. It currently has **26 categories of hard-coded attack hints** (`CATEGORY_ATTACK_HINTS`, ~300 lines) telling the LLM what techniques to try for each category.

Current hard-coded hints:
- `sqli`: "Try `' OR 1=1 --`, UNION SELECT, blind SQLi..."
- `crypto_rsa`: "For small-e RSA (e=3): compute integer cube root..."
- `pwn_buffer_overflow`: "Calculate buffer offset: buffer size + saved EBP..."
- `command_injection`: "Space bypass: use `${IFS}`. Keyword bypass: glob patterns..."
- ...26 categories total

**The SAGE opportunity**: Every blind par run generates data — what attack strategy worked, which techniques failed, how many attempts needed, time to solve. This is exactly the kind of experiential knowledge that should accumulate:

| Par Run Outcome | SAGE Memory | Domain Tag | Impact |
|----------------|-------------|------------|--------|
| SQLi solved in 2 attempts via UNION SELECT on `/search` | `observation`: "SQLi challenges commonly expose injection via search/filter endpoints, not login forms. UNION SELECT with sqlite_master enumeration is most reliable first attempt." | `exploit.blind.sqli` | Future par runs try search endpoints first |
| XSS failed — all payloads filtered, but cookie-based flag found via DOM | `observation`: "XSS challenges at difficulty >1.5 typically filter `<script>` tags. Try event handlers (`onerror`, `onload`) and cookie exfiltration via `document.cookie` in fetch() payload." | `exploit.blind.xss` | Avoids wasting attempts on filtered payloads |
| Crypto RSA solved but took 4 attempts because Wiener's attack tried before cube root | `observation`: "For RSA with e=3, always try cube root attack FIRST (30s), not Wiener's (which is for large e). Check `e` value before choosing algorithm." | `exploit.blind.crypto_rsa` | Reorders attack priority |
| Smart contract par failed — ethers v6 API used | `fact`: "Hardhat node provides ethers v5 API. Use `new ethers.providers.JsonRpcProvider()` not `new ethers.JsonRpcProvider()`." | `exploit.blind.smart_contract` | Prevents repeated API mismatch failures |
| Command injection solved via `${IFS}` space bypass | `observation`: "Command injection challenges at difficulty >1.5 almost always filter spaces. `${IFS}` bypass should be in the first attempt, not the fallback." | `exploit.blind.command_injection` | Promotes bypass to primary strategy |

**How to wire it**:

```python
# In exploit.py — before blind attack
async def run_par(self, context):
    category = context["category"]

    # Query SAGE for accumulated exploit intelligence
    if sage_client:
        memories = await sage_client.query(
            embedding=get_embedding(f"{category} blind attack techniques"),
            domain=f"exploit.blind.{category}",
            top_k=5,
            min_confidence=0.3,
        )
        # Augment the hard-coded hints with institutional memory
        sage_hints = "\n".join([
            f"- [{m.similarity_score:.2f}] {m.content_preview}"
            for m in memories.results
        ])
        context["sage_exploit_context"] = sage_hints

    # ... existing attack logic ...

    # After par run completes (success or failure)
    if sage_client:
        observation = build_par_observation(
            category=category,
            success=result.success,
            time_seconds=result.time_seconds,
            attempts=result.attempts_used,
            steps=result.steps_taken,
            method=result.steps_taken[-1] if result.steps_taken else "",
        )
        await sage_client.propose(
            content=observation,
            domain=f"exploit.blind.{category}",
            memory_type="observation",
            embedding=get_embedding(observation),
            confidence=0.7 if result.success else 0.4,
        )
```

**Why this is the strongest SAGE proof point**: The par solver has a clear, measurable outcome (flag captured: yes/no, time, attempts). If SAGE-augmented par runs solve challenges faster with fewer attempts than cold-start runs, that's undeniable evidence of knowledge distillation working.

#### Surface 3: Nightly Evolution Loops (evolution.py)

The nightly evolution worker runs 5 loops (A-E). Several produce institutional knowledge:

| Loop | What It Learns | SAGE Memory | Domain Tag |
|------|---------------|-------------|------------|
| **A** (Mutation) | Which challenges are too easy (>90% solve) or too hard (<10% solve) | `observation`: "SQLi challenges at difficulty 0.5 are consistently too easy (>90% solve rate). Minimum effective difficulty for SQLi is ~0.75." | `evolution.difficulty_bands.{category}` |
| **B** (Calibration) | Actual vs predicted difficulty from real player data | `inference`: "Source-code analysis consistently underestimates XSS difficulty by 0.3-0.5 points. CSP bypass complexity not captured by step counting." | `evolution.calibration_bias.{category}` |
| **C** (Prompt Evolution) | Which prompt templates produce better challenges | `observation`: "Prompt version 3 for `sqli` has 78% success rate vs version 2's 45%. Key improvement: requiring explicit error handling in Dockerfile." | `evolution.prompt_effectiveness.{category}` |
| **D** (Gap Filling) | Which category × difficulty bands are underserved | `inference`: "Expert-level forensics (2.25-3.0) has persistent generation gap. Forensics challenges above 2.0 require multi-artifact evidence chains that LLMs struggle to produce." | `evolution.generation_gaps` |
| **E** (Retirement) | Which challenges drift out of calibration over time | `observation`: "Web auth_bypass challenges degrade faster than other categories — average lifespan before retirement is 45 days vs 90 days for crypto." | `evolution.challenge_lifecycle.{category}` |

**The evolution loops are perfect SAGE candidates because they already produce structured insights** (calibration deltas, solve rates, gap analyses) that are currently logged and discarded. With SAGE, these observations accumulate and inform future generation runs.

### Updated Validation Framework — Par Solver Experiment

The par solver is the cleanest A/B test surface because:
1. Clear binary outcome (solved/not solved)
2. Quantitative metrics (time, attempts)
3. No confounding from prompt template quality
4. 26 categories × multiple difficulty levels = rich sample space

**Experimental Design (replaces/extends the Week 6-7 plan)**:

| Phase | Runs | SAGE State | Expected Result |
|-------|------|-----------|-----------------|
| **Baseline** | 50 par runs across categories | Off | Establishes cold-start solve rate + avg attempts |
| **Cold SAGE** (runs 1-25) | 25 par runs | On, mostly empty | Similar to baseline; agents submit observations |
| **Warm SAGE** (runs 26-75) | 50 par runs | On, 25+ memories | Attack ordering should improve; fewer wasted attempts |
| **Mature SAGE** (runs 76-100) | 25 par runs | On, 75+ memories | Measurable improvement in solve rate and speed |

**Primary Metrics**:
- **Par solve rate**: % of challenges solved blind (currently ~40-60% depending on category)
- **Average attempts to solve**: Lower = better (max 5, current avg ~3)
- **Average solve time**: Faster = knowledge helped agent skip failed approaches
- **First-attempt success rate**: Did the first technique tried work? (SAGE should improve this by reordering attack priorities)

**Secondary Metrics**:
- Per-category breakdown (which categories benefit most from institutional memory?)
- Technique reuse rate (how often does a SAGE-suggested technique actually succeed?)
- Knowledge graph growth curve (memories committed over time, by domain)

**The Narrative — Per-Agent Learning**:

> "After 100 blind par runs, the SAGE-augmented exploit agent solves 72% of challenges
> (vs 55% baseline), with an average of 1.8 attempts (vs 3.1 baseline). First-attempt
> success rate improved from 22% to 48%. The agent learned to try UNION SELECT on search
> endpoints before login forms for SQLi, cube root before Wiener's for RSA, and ${IFS}
> bypass as the primary strategy for command injection — all from its own accumulated
> experience, validated by consensus."

**The Narrative — Cross-Agent Learning (the headline)**:

> "The designer agent has never observed a solver run. Yet after 50 cross-agent SAGE
> cycles, the challenges it produces score 18% higher in quality (avg 74 vs 63) and
> the blind par solver takes 40% longer to crack them (avg 180s vs 128s). Why? Because
> the solver's feedback — 'XSS challenges with single-tag filters are trivially bypassed',
> 'reentrancy guards that work defeat the challenge purpose', 'flag placement in obvious
> database tables is unrealistic' — flows through SAGE into the designer's context.
> The designer doesn't just generate challenges from a static prompt anymore. It generates
> challenges informed by what a team of solvers actually struggled with. This is
> institutional learning — experience shared between agents that never directly communicate,
> mediated by consensus-validated memory."

### Surface 4: Cross-Agent Experience Loop (The Core Proof)

**This is SAGE's defining capability.** Surfaces 1-3 show individual agents getting smarter. Surface 4 shows agents sharing experience across roles — the designer learns from the solver's experience without ever "seeing" the solver run.

#### The Closed Feedback Loop

```
┌─────────────────────────────────────────────────────────────────┐
│                    SAGE Institutional Memory                     │
│                 (BFT-committed, consensus-validated)             │
│                                                                  │
│   ┌──────────────────────────────────────────────────────┐      │
│   │  "XSS challenges with single-tag <script> filters   │      │
│   │   are trivially solvable — solver bypassed in 12s    │      │
│   │   using onerror handler. Need multi-vector filtering │      │
│   │   for difficulty > 1.0"                              │      │
│   │   — domain: solver_feedback.xss                      │      │
│   │   — type: observation                                │      │
│   │   — confidence: 0.85 (validator-weighted)            │      │
│   └──────────────────────────────────────────────────────┘      │
│        ▲ WRITE                                   READ ▼          │
│        │                                         │               │
│  ┌─────┴──────┐                          ┌───────┴────────┐     │
│  │ 4AM Solver │                          │  Designer Agent │     │
│  │ (blind par)│                          │ (next generation)│    │
│  │            │                          │                  │    │
│  │ Solves the │    challenge produced    │ Queries SAGE for │    │
│  │ challenge ◄────────────────────────────  solver feedback │    │
│  │ blind      │                          │ before generating│    │
│  └────────────┘                          └──────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

#### What the Solver Feeds Back to the Designer

The 4AM blind par run produces rich experiential data that the designer has never had access to:

| Solver Experience | SAGE Memory Created | How Designer Uses It |
|-------------------|--------------------|--------------------|
| "Solved XSS in 12s — `<script>` tag filter trivially bypassed with `<img onerror>`" | `observation` in `solver_feedback.xss` | Designer adds multi-vector filtering, not just `<script>` tags |
| "Smart contract reentrancy guard was correctly implemented — no actual vulnerability to exploit" | `observation` in `solver_feedback.smart_contract` | Designer ensures vulnerability is genuinely exploitable, not accidentally patched |
| "SQLi challenge had injection point in login form but no interesting data to extract — flag was just in a table called 'flag'" | `observation` in `solver_feedback.sqli` | Designer creates richer data models so extraction feels like real pentesting |
| "Crypto RSA challenge: e=3 but N was too large for simple cube root. Good challenge." | `observation` in `solver_feedback.crypto_rsa` | Designer learns what parameter ranges produce good difficulty calibration |
| "Command injection: solved by reading `/etc/passwd` directly — challenge didn't restrict file reads, only command execution" | `observation` in `solver_feedback.command_injection` | Designer hardens file read restrictions, not just command filters |
| "Forensics: couldn't solve — description said 'find the hidden message' but 4 different steganography tools found nothing. Challenge may be broken." | `observation` in `solver_feedback.forensics` | Designer avoids overly obscure steganography techniques |
| "Par run took 4 attempts because description was misleading — said 'authentication bypass' but actual vuln was IDOR" | `observation` in `solver_feedback.{category}` | Designer aligns descriptions with actual vulnerability class |

#### How the Designer Queries Solver Feedback

```python
# In designer.py — before generating a challenge
async def generate_challenge(self, category, target_difficulty, ...):
    solver_feedback = []
    generation_patterns = []

    if sage_client:
        # Query 1: What has the solver team learned about this category?
        feedback = await sage_client.query(
            embedding=get_embedding(f"{category} solver experience feedback"),
            domain=f"solver_feedback.{category}",
            top_k=5,
            min_confidence=0.3,
        )
        solver_feedback = [m.content for m in feedback.results]

        # Query 2: What generation patterns work well?
        patterns = await sage_client.query(
            embedding=get_embedding(f"{category} challenge generation patterns"),
            domain=f"challenge_generation.{category}",
            top_k=5,
            min_confidence=0.3,
        )
        generation_patterns = [m.content for m in patterns.results]

    # Inject into the LLM system prompt
    if solver_feedback:
        feedback_block = "\n".join([f"- {fb}" for fb in solver_feedback])
        system_prompt += f"""

SOLVER TEAM FEEDBACK (from blind solving attempts on previous challenges):
{feedback_block}

Use this feedback to avoid known weaknesses in your challenge design.
Challenges that were too easily solved had specific flaws — don't repeat them.
"""

    if generation_patterns:
        pattern_block = "\n".join([f"- {p}" for p in generation_patterns])
        system_prompt += f"""

INSTITUTIONAL KNOWLEDGE (validated patterns from previous successful challenges):
{pattern_block}
"""
```

#### How the Solver Submits Feedback After Each Par Run

```python
# In exploit.py — after blind par run completes
async def _submit_solver_feedback(self, context, result):
    """Submit structured feedback that the designer can learn from."""
    if not sage_client:
        return

    category = context["category"]
    difficulty = context.get("calibrated_difficulty", context.get("target_difficulty"))

    if result.success:
        feedback = (
            f"Solved {category} challenge (difficulty {difficulty:.1f}) in "
            f"{result.time_seconds:.0f}s using {result.attempts_used} attempts. "
            f"Successful technique: {result.steps_taken[-1] if result.steps_taken else 'unknown'}. "
            f"{'Too easy — solved on first attempt in <30s. ' if result.time_seconds < 30 and result.attempts_used == 1 else ''}"
            f"Steps taken: {' → '.join(result.steps_taken)}."
        )
        confidence = 0.8
    else:
        feedback = (
            f"FAILED to solve {category} challenge (difficulty {difficulty:.1f}) "
            f"after {result.attempts_used} attempts over {result.time_seconds:.0f}s. "
            f"Techniques tried: {' → '.join(result.steps_taken)}. "
            f"Possible issues: challenge may be unsolvable, description may be "
            f"misleading, or attack surface may be insufficiently exposed."
        )
        confidence = 0.6  # Failures are valuable — higher confidence than you'd think

    await sage_client.propose(
        content=feedback,
        domain=f"solver_feedback.{category}",
        memory_type="observation",
        embedding=get_embedding(feedback),
        confidence=confidence,
        metadata={
            "source_agent": "exploit_par_solver",
            "target_agent": "designer",  # Explicit cross-agent intent
            "category": category,
            "difficulty": difficulty,
            "solved": result.success,
            "time_seconds": result.time_seconds,
            "attempts": result.attempts_used,
        },
    )
```

#### Why This Is the Core Proof of SAGE

1. **No other system does this.** Mem0, MemOS, LangChain Memory — all give individual agents memory. None of them enable consensus-validated cross-agent experience sharing.

2. **The designer has never "seen" the solver.** These are different Python processes, potentially running hours apart (designer in pipeline, solver in 4AM par run). They share experience *only* through SAGE institutional memory.

3. **The feedback is consensus-validated.** It's not just raw solver output — it's been committed through BFT consensus with PoE-weighted validator voting. Bad observations (hallucinated solve techniques, inaccurate difficulty assessments) get filtered out.

4. **It's measurable.** We can track:
   - Quality scores of challenges generated WITH solver feedback vs WITHOUT
   - Par solve times trending upward (challenges getting properly harder)
   - Calibration accuracy improving (designer learns what difficulty ranges actually mean from solver experience)
   - Reduction in "too easy" / "too hard" outliers

5. **It compounds.** Run 1: designer has no solver feedback. Run 50: designer has feedback from 49 solver runs across every category. Run 200: the institutional memory is rich enough that the designer rarely produces trivially solvable challenges.

#### Cross-Agent Experience Experiment Design

| Phase | What Happens | Expected Outcome |
|-------|-------------|-----------------|
| **Baseline** (50 runs) | Designer generates challenges with hard-coded knowledge only. Solver runs par. No SAGE. | Establishes baseline: avg quality score, par solve rate, calibration MAE |
| **Isolated SAGE** (50 runs) | Designer queries SAGE for generation patterns only (Surface 1). Solver queries SAGE for attack hints only (Surface 2). **No cross-agent sharing.** | Each agent improves individually but designer doesn't benefit from solver insights |
| **Cross-Agent SAGE** (50 runs) | Designer queries SAGE for BOTH generation patterns AND solver feedback. Solver submits feedback tagged for designer consumption. **Full loop.** | Designer produces harder-to-solve, better-calibrated challenges. Par solve time should increase (better challenges), quality scores should increase (fewer obvious flaws) |

**Key Metric**: The delta between "Isolated SAGE" and "Cross-Agent SAGE" isolates the value of inter-agent experience sharing. If Cross-Agent SAGE shows improvement over Isolated SAGE, that proves the feedback loop adds value *beyond* individual agent memory.

---

## Validation Framework — Proving It Works

This is the scientific backbone of the PoC. Three claims to prove:

1. **Consensus works**: BFT commits are deterministic, fault-tolerant, and tamper-resistant
2. **Knowledge distillation beats cold start**: Agents with SAGE institutional memory measurably outperform agents starting blind
3. **Cross-agent experience sharing adds value**: Inter-agent feedback loops (solver→designer) produce better outcomes than isolated per-agent memory

### Claim 1: Consensus Works

#### What "Works" Means (Concrete Evidence)

| Evidence | How to Demonstrate | When |
|----------|-------------------|------|
| **Deterministic finality** | Submit memory on node 0, query from nodes 1-3 within same block — identical state | Week 2 |
| **App hash agreement** | All 4 nodes produce identical app hash every block (Prometheus `cometbft_consensus_height`) | Week 2 onward |
| **Fault tolerance** | Kill 1 of 4 nodes → blocks continue. Kill 2 → halts (expected). Restart → resumes. | Week 8 |
| **Replay protection** | Resubmit same signed tx → CheckTx rejects with nonce error | Week 3 |
| **Tamper resistance** | Malicious validator submits contradictory votes → honest quorum rejects → no state corruption | Week 8 |
| **Memory integrity** | Content hash on-chain matches SHA-256 of off-chain content. Tamper with PostgreSQL → hash mismatch detected | Week 4 |
| **Quorum enforcement** | Memory only transitions Proposed→Committed when ≥2/3 weighted votes approve. Artificially withhold votes → stays Proposed | Week 5 |
| **State recovery** | Corrupt 1 node's data → wipe → state sync from peers → catches up to current height | Week 8 |

#### Consensus Validation Script (`test/integration/consensus_proof_test.go`)

Automated test that runs against the live 4-node network:

```
1. Submit 100 memories across all 4 nodes
2. Wait for finalization (1 block)
3. Query each node's ABCI /status endpoint
4. Assert: all 4 nodes have identical block height + app hash
5. Assert: all 100 memories queryable from any node
6. Kill node 3
7. Submit 10 more memories
8. Assert: blocks still produced (3/4 > 2/3)
9. Assert: new memories committed across remaining 3 nodes
10. Restart node 3
11. Assert: node 3 catches up and has all 110 memories
```

#### Consensus Metrics Dashboard (Grafana)

Permanent evidence via time-series:
- Block height progression (steady ~3s intervals)
- Validator participation (4/4 in commits)
- App hash consistency (all nodes match)
- Mempool → finality latency
- Byzantine evidence count (should be 0)

---

### Claim 2: Knowledge Distillation Beats Cold Start

This is the hard one. We need to show that agents consulting SAGE institutional memory produce measurably better outcomes than agents relying only on their hard-coded prompts.

#### Experimental Design

**Independent Variable**: Access to SAGE institutional memory (yes/no)

**Control Group ("Cold Start")**:
- Level Up pipeline runs with agents using ONLY their current hard-coded knowledge
- `DIFFICULTY_GUIDANCE`, `CATEGORY_DIFFICULTY_CONTEXT`, template patterns — all as-is
- No SAGE queries, no institutional memory
- This is the current production behavior — it's the baseline

**Treatment Group ("SAGE-Augmented")**:
- Same agents, same LLM, same categories, same difficulty targets
- Before each pipeline stage, agents query SAGE for relevant memories
- After each pipeline completion (success or failure), agents submit observations to SAGE
- Knowledge accumulates over successive runs

**Confound Controls**:
- Same LLM model and temperature for both groups
- Same category and difficulty distribution
- Randomized assignment: each pipeline run randomly assigned to control or treatment
- Run interleaved (not all control first, then all treatment)

#### Metrics to Compare (Level Up Already Tracks These)

Level Up's `PipelineRun` and quality scoring system give us rich per-run metrics:

| Metric | Source | What It Measures |
|--------|--------|-----------------|
| **Pipeline success rate** | `PipelineRun.status` (completed vs failed) | Does the challenge survive the full pipeline? |
| **Quality score** | `quality_score` (0-100) | Structural quality: solvability, build quality, description, complexity |
| **Calibration accuracy** | `|calibrated_difficulty - target_difficulty|` | How close does the generated difficulty match the target? |
| **Repair count** | `PipelineRun.results.repair_attempts` | How many times did the code need fixing? 0 = clean generation |
| **Build success rate** | VALIDATE stage pass/fail | Does the Docker container build and health check pass on first try? |
| **Verification level** | `verification_level` (solution_verified > flag_verified > smoke_tested) | How thoroughly was the challenge verified? |
| **Pipeline duration** | `PipelineRun.duration_seconds` | Total time from submission to completion |
| **Discard reason distribution** | `PipelineRun.error_message` | What's failing? Static analysis, Docker build, smoke test? |

#### The Knowledge Accumulation Curve

The key insight: SAGE doesn't help on run #1 (empty memory). The value emerges over time as institutional knowledge accumulates. The experiment must capture this curve.

**Phase A — Baseline Capture (before SAGE integration)**:
- Run 50 pipeline executions across all categories with current code (no SAGE)
- Record all metrics per run
- This establishes the cold-start baseline for each category

**Phase B — SAGE Cold Start (runs 1-20)**:
- Treatment group queries SAGE but memory is mostly empty
- Performance should be similar to baseline
- Agents submit observations after each run (both successes and failures)
- SAGE accumulates: "Docker build failed because X", "SQLi challenge at difficulty 2.0 needs Y"

**Phase C — SAGE Warm (runs 21-50)**:
- SAGE now has 20+ committed observations
- Treatment group queries return relevant institutional knowledge
- **This is where the delta should appear**
- Hypothesis: success rate, quality scores, and calibration accuracy improve

**Phase D — SAGE Mature (runs 51-100)**:
- Rich institutional memory across categories
- Treatment should significantly outperform control
- Knowledge graph enables cross-category learning (e.g., Docker patterns learned from web apply to crypto)

#### Concrete Examples of Knowledge That Should Help

| Run | Failure/Observation | SAGE Memory Created | Future Impact |
|-----|--------------------|--------------------|---------------|
| #3 | Flask SQLi challenge: Docker build fails because `requirements.txt` references missing package | `observation`: "Flask web challenges must include all pip dependencies inline in Dockerfile, not via requirements.txt" | Runs #10+ avoid this build failure |
| #7 | Smart contract challenge: ethers v6 API used but Hardhat provides v5 | `fact`: "Hardhat development environment uses ethers v5 API — use `providers.JsonRpcProvider` not `JsonRpcProvider`" | All future smart contract challenges use correct API |
| #12 | Calibrator rates XSS challenge at difficulty 1.0 but actual exploit takes 3 steps | `observation`: "XSS challenges with CSP bypass require difficulty ≥ 1.5 — source analysis underestimates CSP complexity" | Calibration accuracy improves for XSS |
| #18 | Forensics challenge at difficulty 2.5 discarded — quality score 35 | `observation`: "Forensics challenges above 2.0 need multi-artifact correlation and at least 3 evidence files to reach quality threshold" | Future high-difficulty forensics challenges include sufficient artifacts |
| #25 | Challenge generation succeeds but par time is way off | `inference`: "Predicted par times for crypto challenges at difficulty 2.0+ should use 180x human factor, not 60x — crypto requires more setup time" | Par time estimates become more accurate |

#### Statistical Analysis Plan

**Primary endpoint**: Pipeline success rate (completed / total)
- **Minimum detectable effect**: 15% improvement (e.g., 60% → 75%)
- **Sample size**: 50 runs per group (100 total) — sufficient for chi-squared test at α=0.05
- **Test**: Fisher's exact test (small sample) or chi-squared (larger sample)

**Secondary endpoints** (all compared between groups):
- Mean quality score: Two-sample t-test (or Mann-Whitney if non-normal)
- Calibration accuracy (MAE of difficulty): Two-sample t-test
- Mean repair count: Mann-Whitney U test (likely not normal)
- Build success rate: Fisher's exact test

**Time-series analysis**:
- Plot treatment group metrics as a function of SAGE memory count
- Fit a learning curve: `performance = baseline + improvement * (1 - exp(-k * memories))`
- If k > 0 with p < 0.05, knowledge accumulation is proven

#### Validation Milestones (Threaded Into Weekly Plan)

| Week | Consensus Proof Point | Knowledge Distillation Proof Point | Cross-Agent Proof Point |
|------|----------------------|-----------------------------------|------------------------|
| 2 | ✓ 4 nodes producing blocks, identical app hash | — | — |
| 3 | ✓ Memory submitted on node 0, queryable from node 3 | — | — |
| 4 | ✓ Content hash integrity verified across on-chain/off-chain | — | — |
| 5 | ✓ Quorum enforcement: 3/4 validators must approve | ✓ PoE scores diverge based on vote accuracy | — |
| 6 | — | ✓ Baseline captured: 50 pipeline + 50 par runs without SAGE | ✓ Solver feedback domain tags wired, memories flowing |
| 7 | — | ✓ Isolated SAGE runs complete (per-agent memory only) | ✓ Cross-Agent SAGE runs: designer queries solver feedback |
| 8 | ✓ Byzantine fault tests pass, state recovery works | ✓ Full three-way comparison: No SAGE vs Isolated vs Cross-Agent | ✓ Delta report: cross-agent feedback value quantified |

#### What the Report Should Show

The Phase 1 findings report (Week 8 deliverable) needs these sections:

**Section A: Consensus Proof**
- Block production chart (height over time, steady 3s intervals)
- App hash consistency log (all 4 nodes, every block)
- Fault tolerance test results (1-of-4 down, 2-of-4 down, recovery)
- Replay attack rejection evidence
- Memory integrity verification

**Section B: Knowledge Distillation Proof**
- Table: Control vs Treatment (success rate, quality score, calibration MAE, repair count)
- Learning curve chart: treatment group performance vs SAGE memory count
- P-values for all endpoints
- Specific examples: "This memory prevented this failure class" (3-5 case studies)
- Knowledge graph visualization: what topics have accumulated, how they connect
- Memory lifecycle examples: Proposed → Validated → Committed (show the voting)

**Section B2: Cross-Agent Experience Proof**
- Three-way comparison: No SAGE vs Isolated SAGE vs Cross-Agent SAGE
- Delta between Isolated and Cross-Agent isolates the inter-agent feedback value
- Solver→Designer feedback examples: specific observations that improved generation
- Par solve time trend: challenges should get harder to solve as designer learns from solver
- Quality score trend: challenges should score higher as designer avoids known flaws
- Case studies: "Solver reported X → Designer changed Y → Next challenge Z was measurably better"

**Section C: Operational Metrics**
- Submit-to-finality latency distribution
- Query latency at scale (1K, 10K, 100K memories)
- Throughput under load (memories/sec)
- Resource utilization (CPU, RAM, disk per node)

---

### Implementation: What to Add to Level Up

To run the experiment, Level Up's orchestrator needs minimal changes:

```python
# In orchestrator.py — add SAGE integration mode
class PipelineConfig:
    sage_enabled: bool = False        # Toggle per run
    sage_endpoint: str = ""
    sage_agent_identity: str = ""

# Before GENERATE stage:
if config.sage_enabled:
    memories = await sage.query(
        embedding=get_embedding(f"{category} challenge generation"),
        domain=f"challenge_generation.{category}",
        top_k=5,
    )
    context["sage_context"] = [m.content_preview for m in memories.results]

# After COMPLETE or DISCARD:
if config.sage_enabled:
    observation = build_observation(context, pipeline_run)
    await sage.propose(
        content=observation,
        domain=f"challenge_generation.{category}",
        memory_type="observation",
        embedding=get_embedding(observation),
    )
```

The `sage_enabled` flag lets us randomly assign runs to control/treatment groups without code branching. The `PipelineRun` table already records everything we need — we just add a `sage_enabled` boolean column.

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Overengineering before proving behavioral gain | Week 6-7 A/B test is the priority gate — if no agent improvement, reassess before Phase 2 |
| CometBFT operational complexity | Docker Compose abstracts it for dev; `cometbft testnet` auto-generates configs |
| Go unfamiliar | ABCI interface is ~10 methods (5 key + 5 pass-through); kvstore example is reference |
| Determinism bugs (chain halt) | Docker ensures identical Go version; sort all iterations; use req.Time not time.Now() |
| Level Up integration friction | Python SDK with async support matches Level Up's httpx stack |
| pgvector scale limits | HNSW indexes sufficient for PoC (100K+ vectors); Phase 2 evaluates alternatives |
| Zero S factor kills weights | Epsilon floor (0.01) on corroboration factor prevents zero-weight cliff |
| All validators agree (false collusion flag) | Exclude unanimous memories from phi computation |
| Phase 2 migration friction | Extensible epoch logic, abstracted validator interface, reserved challenge tx type from day 1 |
