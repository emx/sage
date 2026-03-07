# (S)AGE Memory for ChatGPT — Store Listing

## Short Description (132 chars max for Chrome)
Give ChatGPT persistent memory. (S)AGE stores AI memories locally with AES-256 encryption. Your data never leaves your machine.

## Full Description

### Give your AI a secure, permanent memory

Every time you close a ChatGPT conversation, it forgets everything — your projects, your preferences, every lesson it learned. SAGE fixes that.

(S)AGE Memory for ChatGPT is a browser extension that connects ChatGPT's free web interface to (S)AGE, an open-source AI memory system that runs entirely on your computer.

**How it works:**
- A sidebar panel inside ChatGPT shows your memory stats, connection status, and quick actions
- Tell ChatGPT about (S)AGE tools with one click — it learns to save and recall memories
- All 10 (S)AGE memory tools available: remember, recall, reflect, turn-by-turn learning, and more
- Responses are monitored for (S)AGE tool calls and executed automatically

**Security first:**
- Every API request is Ed25519 cryptographically signed
- All data stored locally on your machine — nothing sent to any cloud
- AES-256-GCM encryption at rest
- Open source: https://github.com/l33tdawg/sage

**Requirements:**
- (S)AGE must be running locally (download from https://l33tdawg.github.io/sage/)
- Works with ChatGPT free and paid plans on chat.openai.com

**What your AI gains:**
- Persistent memory across conversations
- Consensus-validated knowledge (BFT governance)
- Semantic search across all past experiences
- Self-improvement through reflection (proven in 4 published research papers)
- Works with any AI model — memories are model-agnostic

Built by the (S)AGE project — open source, Apache 2.0 licensed.

## Category
Productivity

## Tags/Keywords
AI, memory, ChatGPT, persistent memory, AI assistant, privacy, local-first, MCP

## Privacy Policy

(S)AGE Memory for ChatGPT does not collect, transmit, or store any user data on external servers.

All data processing occurs locally:
- Memory data is stored in a local SQLite database on your computer (~/.sage/)
- The extension communicates only with your local (S)AGE server (default: localhost:8080)
- No analytics, telemetry, or tracking of any kind
- No user accounts required
- Ed25519 keypair is generated and stored locally in the browser

The extension requests the following permissions:
- activeTab: To inject the SAGE sidebar into ChatGPT pages
- storage: To save your SAGE server URL and cryptographic keys locally
- Host permissions for localhost:8080: To communicate with your local SAGE server
- Host permissions for chatgpt.com/chat.openai.com: To inject the content script

Source code: https://github.com/l33tdawg/sage/tree/main/extension/chrome
License: Apache 2.0

## Screenshots Needed
1. SAGE sidebar open in ChatGPT showing connection status and memory stats
2. Quick action buttons (Wake Up, Turn, Recall, Status)
3. Tool call log showing executed SAGE calls
4. Popup with connection status and server config
5. ChatGPT conversation using SAGE memory tools
