#!/usr/bin/env python3
"""Cross-node memory verification test.

Submits a memory to node0, reads from node1 (and vice versa).
Uses Ed25519 auth with PyNaCl matching SAGE's signing scheme:
  signed_message = SHA-256(body_bytes) + struct.pack(">q", timestamp)
"""

import hashlib
import json
import struct
import time
import sys

import requests
from nacl.signing import SigningKey

NODES = {
    "node0": "http://localhost:8080",
    "node1": "http://localhost:8081",
    "node2": "http://localhost:8082",
    "node3": "http://localhost:8083",
}


class Agent:
    """SAGE agent with Ed25519 keypair and request signing."""

    def __init__(self):
        self.signing_key = SigningKey.generate()
        self.verify_key = self.signing_key.verify_key
        self.agent_id = self.verify_key.encode().hex()

    def sign_request(self, body_bytes: bytes, timestamp: int) -> str:
        body_hash = hashlib.sha256(body_bytes).digest()
        ts_bytes = struct.pack(">q", timestamp)
        message = body_hash + ts_bytes
        signed = self.signing_key.sign(message)
        return signed.signature.hex()

    def headers(self, body_bytes: bytes) -> dict:
        ts = int(time.time())
        sig = self.sign_request(body_bytes, ts)
        return {
            "Content-Type": "application/json",
            "X-Agent-ID": self.agent_id,
            "X-Signature": sig,
            "X-Timestamp": str(ts),
        }

    def submit_memory(self, base_url: str, content: str, domain: str = "test") -> dict:
        payload = {
            "content": content,
            "memory_type": "fact",
            "domain_tag": domain,
            "confidence_score": 0.85,
        }
        body = json.dumps(payload).encode()
        resp = requests.post(
            f"{base_url}/v1/memory/submit",
            data=body,
            headers=self.headers(body),
            timeout=10,
        )
        return {"status_code": resp.status_code, "body": resp.json()}

    def get_memory(self, base_url: str, memory_id: str) -> dict:
        body = b""
        resp = requests.get(
            f"{base_url}/v1/memory/{memory_id}",
            headers=self.headers(body),
            timeout=10,
        )
        return {"status_code": resp.status_code, "body": resp.json()}


def check_health():
    """Verify all 4 nodes are healthy."""
    print("Checking health on all nodes...")
    for name, url in NODES.items():
        try:
            r = requests.get(f"{url}/health", timeout=3)
            status = r.json().get("status", "unknown")
            print(f"  {name} ({url}): {status}")
            if status != "healthy":
                print(f"  FAIL: {name} is not healthy")
                return False
        except Exception as e:
            print(f"  FAIL: {name} unreachable: {e}")
            return False
    return True


def test_submit_node0_read_node1():
    """Submit memory to node0, read from node1."""
    print("\n--- Test: Submit to node0, read from node1 ---")
    agent = Agent()
    print(f"Agent ID: {agent.agent_id[:16]}...")

    # Submit to node0
    result = agent.submit_memory(NODES["node0"], "Cross-node test fact: Earth orbits the Sun")
    print(f"Submit to node0: HTTP {result['status_code']}")
    assert result["status_code"] in (200, 201, 202), f"Submit failed: {result}"

    memory_id = result["body"].get("memory_id")
    assert memory_id, f"No memory_id in response: {result['body']}"
    print(f"Memory ID: {memory_id}")

    # Wait for block finalization + PostgreSQL sync
    print("Waiting 5s for block finalization...")
    time.sleep(5)

    # Read from node1
    read_result = agent.get_memory(NODES["node1"], memory_id)
    print(f"Read from node1: HTTP {read_result['status_code']}")
    assert read_result["status_code"] == 200, f"Read from node1 failed: {read_result}"

    content = read_result["body"].get("content", "")
    print(f"Content from node1: {content}")
    assert "Earth orbits" in content, f"Content mismatch: {content}"
    print("PASS")


def test_submit_node1_read_node0():
    """Submit memory to node1, read from node0."""
    print("\n--- Test: Submit to node1, read from node0 ---")
    agent = Agent()
    print(f"Agent ID: {agent.agent_id[:16]}...")

    # Submit to node1
    result = agent.submit_memory(NODES["node1"], "Cross-node test fact: Water is H2O")
    print(f"Submit to node1: HTTP {result['status_code']}")
    assert result["status_code"] in (200, 201, 202), f"Submit failed: {result}"

    memory_id = result["body"].get("memory_id")
    assert memory_id, f"No memory_id in response: {result['body']}"
    print(f"Memory ID: {memory_id}")

    # Wait for block finalization + PostgreSQL sync
    print("Waiting 5s for block finalization...")
    time.sleep(5)

    # Read from node0
    read_result = agent.get_memory(NODES["node0"], memory_id)
    print(f"Read from node0: HTTP {read_result['status_code']}")
    assert read_result["status_code"] == 200, f"Read from node0 failed: {read_result}"

    content = read_result["body"].get("content", "")
    print(f"Content from node0: {content}")
    assert "H2O" in content, f"Content mismatch: {content}"
    print("PASS")


def test_submit_node0_read_all():
    """Submit memory to node0, verify readable from all other nodes."""
    print("\n--- Test: Submit to node0, read from all nodes ---")
    agent = Agent()

    result = agent.submit_memory(NODES["node0"], "Cross-node broadcast: SAGE consensus works")
    assert result["status_code"] in (200, 201, 202), f"Submit failed: {result}"
    memory_id = result["body"].get("memory_id")
    assert memory_id, f"No memory_id: {result['body']}"
    print(f"Submitted to node0, memory_id={memory_id}")

    print("Waiting 5s for block finalization...")
    time.sleep(5)

    for name, url in NODES.items():
        read_result = agent.get_memory(url, memory_id)
        status = read_result["status_code"]
        print(f"  Read from {name}: HTTP {status}")
        assert status == 200, f"Read from {name} failed: {read_result}"
    print("PASS")


if __name__ == "__main__":
    if not check_health():
        print("\nNetwork not healthy, aborting.")
        sys.exit(1)

    failures = 0
    for test_fn in [test_submit_node0_read_node1, test_submit_node1_read_node0, test_submit_node0_read_all]:
        try:
            test_fn()
        except AssertionError as e:
            print(f"FAIL: {e}")
            failures += 1
        except Exception as e:
            print(f"ERROR: {e}")
            failures += 1

    print(f"\n{'='*50}")
    if failures == 0:
        print("All cross-node tests PASSED")
    else:
        print(f"{failures} test(s) FAILED")
        sys.exit(1)
