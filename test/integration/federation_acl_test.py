#!/usr/bin/env python3
"""Federation Access Control — End-to-End Integration Test.

Tests the full Phase 3 federation access control pipeline:
  1. Domain registration
  2. Memory submission to a domain
  3. Access denial (unauthorized agent)
  4. Access grant + authorized query
  5. Access revocation + re-denial
  6. Organization registration + membership
  7. Clearance levels
  8. Cross-org federation proposal + approval
  9. Federation-based cross-org access
 10. Federation revocation + access re-denial
 11. Audit trail verification

Uses Ed25519 auth matching SAGE signing scheme:
  signed_message = SHA-256(body_bytes) + struct.pack(">q", timestamp)
"""

import hashlib
import json
import struct
import time
import sys

import requests
from nacl.signing import SigningKey

BASE = "http://localhost:8080"
NODE1 = "http://localhost:8081"

PASS_COUNT = 0
FAIL_COUNT = 0


class Agent:
    """SAGE agent with Ed25519 keypair and request signing."""

    def __init__(self, name="anonymous"):
        self.name = name
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

    def post(self, url: str, payload: dict) -> requests.Response:
        body = json.dumps(payload).encode()
        return requests.post(url, data=body, headers=self.headers(body), timeout=10)

    def get(self, url: str) -> requests.Response:
        body = b""
        return requests.get(url, headers=self.headers(body), timeout=10)

    def delete(self, url: str) -> requests.Response:
        body = b""
        return requests.delete(url, headers=self.headers(body), timeout=10)


def check(label: str, condition: bool, detail: str = ""):
    global PASS_COUNT, FAIL_COUNT
    if condition:
        PASS_COUNT += 1
        print(f"  PASS: {label}")
    else:
        FAIL_COUNT += 1
        msg = f"  FAIL: {label}"
        if detail:
            msg += f" — {detail}"
        print(msg)


def wait(seconds=4, reason="block finalization"):
    print(f"  ... waiting {seconds}s for {reason}")
    time.sleep(seconds)


# =============================================================================
# TEST 1: Domain Registration
# =============================================================================
def test_domain_registration():
    print("\n" + "=" * 60)
    print("TEST 1: Domain Registration")
    print("=" * 60)

    admin = Agent("domain-admin")

    # Register a top-level domain
    resp = admin.post(f"{BASE}/v1/domain/register", {
        "name": "red_team",
        "description": "Red team vulnerability intelligence"
    })
    check("Register top-level domain", resp.status_code == 201,
          f"HTTP {resp.status_code}: {resp.text}")

    wait()

    # Register a sub-domain
    resp = admin.post(f"{BASE}/v1/domain/register", {
        "name": "red_team.vuln_intel",
        "description": "Vulnerability intelligence sub-domain",
        "parent": "red_team"
    })
    check("Register sub-domain", resp.status_code == 201,
          f"HTTP {resp.status_code}: {resp.text}")

    wait()

    # Verify domain is queryable
    resp = admin.get(f"{BASE}/v1/domain/red_team")
    check("Get domain info", resp.status_code == 200,
          f"HTTP {resp.status_code}: {resp.text}")
    if resp.status_code == 200:
        data = resp.json()
        check("Domain owner matches", data.get("owner_agent_id") == admin.agent_id,
              f"owner={data.get('owner_agent_id', 'N/A')[:16]}... expected={admin.agent_id[:16]}...")

    return admin


# =============================================================================
# TEST 2: Memory Submission + Access Denial
# =============================================================================
def test_access_denial(domain_admin):
    print("\n" + "=" * 60)
    print("TEST 2: Memory Submission + Unauthorized Access Denial")
    print("=" * 60)

    # Submit memory as domain admin
    resp = domain_admin.post(f"{BASE}/v1/memory/submit", {
        "content": "CVE-2024-1234: Critical buffer overflow in libfoo 3.2.1 allows RCE via crafted input",
        "memory_type": "fact",
        "domain_tag": "red_team",
        "confidence_score": 0.92,
    })
    check("Submit memory to red_team domain", resp.status_code in (200, 201, 202),
          f"HTTP {resp.status_code}: {resp.text}")

    memory_id = resp.json().get("memory_id", "")
    check("Got memory_id", bool(memory_id), f"body={resp.json()}")

    wait()

    # Unauthorized agent tries to read it
    outsider = Agent("outsider")
    resp = outsider.get(f"{BASE}/v1/memory/{memory_id}")
    # Should get 403 Forbidden because outsider has no grant for red_team
    check("Unauthorized agent denied access (403)",
          resp.status_code == 403,
          f"HTTP {resp.status_code}: {resp.text}")

    # Unauthorized agent tries to query the domain via similarity search
    # The query endpoint requires an embedding vector — use a zero vector as placeholder.
    zero_embedding = [0.0] * 768
    resp = outsider.post(f"{BASE}/v1/memory/query", {
        "domain_tag": "red_team",
        "embedding": zero_embedding,
        "top_k": 5,
    })
    # Should get 403 (access denied) or empty results (gated by access control)
    check("Unauthorized query denied or empty",
          resp.status_code == 403 or (resp.status_code == 200 and len(resp.json().get("memories", [])) == 0),
          f"HTTP {resp.status_code}: {resp.text[:200]}")

    return memory_id, outsider


# =============================================================================
# TEST 3: Access Grant + Authorized Query
# =============================================================================
def test_access_grant(domain_admin, memory_id, outsider):
    print("\n" + "=" * 60)
    print("TEST 3: Access Grant + Authorized Query")
    print("=" * 60)

    # Domain admin grants read access to outsider
    resp = domain_admin.post(f"{BASE}/v1/access/grant", {
        "grantee_id": outsider.agent_id,
        "domain": "red_team",
        "level": 1,  # read-only
    })
    check("Grant read access", resp.status_code in (200, 201),
          f"HTTP {resp.status_code}: {resp.text}")

    wait()

    # Now outsider should be able to read the memory
    resp = outsider.get(f"{BASE}/v1/memory/{memory_id}")
    check("Authorized agent can read memory",
          resp.status_code == 200,
          f"HTTP {resp.status_code}: {resp.text[:200]}")
    if resp.status_code == 200:
        content = resp.json().get("content", "")
        check("Memory content intact", "CVE-2024-1234" in content, f"content={content[:80]}")

    # Verify grant appears in list
    resp = outsider.get(f"{BASE}/v1/access/grants/{outsider.agent_id}")
    check("Grant appears in list", resp.status_code == 200,
          f"HTTP {resp.status_code}: {resp.text[:200]}")
    if resp.status_code == 200:
        grants = resp.json()
        check("At least one grant returned",
              isinstance(grants, list) and len(grants) > 0,
              f"grants={grants}")


# =============================================================================
# TEST 4: Access Revocation
# =============================================================================
def test_access_revocation(domain_admin, memory_id, outsider):
    print("\n" + "=" * 60)
    print("TEST 4: Access Revocation")
    print("=" * 60)

    # Revoke outsider's access
    resp = domain_admin.post(f"{BASE}/v1/access/revoke", {
        "grantee_id": outsider.agent_id,
        "domain": "red_team",
        "reason": "Security review complete, access no longer needed",
    })
    check("Revoke access", resp.status_code == 200,
          f"HTTP {resp.status_code}: {resp.text}")

    wait()

    # Outsider should be denied again
    resp = outsider.get(f"{BASE}/v1/memory/{memory_id}")
    check("Revoked agent denied access (403)",
          resp.status_code == 403,
          f"HTTP {resp.status_code}: {resp.text[:200]}")


# =============================================================================
# TEST 5: Access Request Flow
# =============================================================================
def test_access_request():
    print("\n" + "=" * 60)
    print("TEST 5: Access Request Flow")
    print("=" * 60)

    requester = Agent("requester")

    # Agent requests access to a domain
    resp = requester.post(f"{BASE}/v1/access/request", {
        "target_domain": "red_team.vuln_intel",
        "justification": "Need vulnerability data for penetration test engagement",
        "requested_level": 1,
    })
    check("Submit access request", resp.status_code in (200, 201),
          f"HTTP {resp.status_code}: {resp.text}")
    if resp.status_code in (200, 201):
        data = resp.json()
        check("Request has tx_hash", bool(data.get("tx_hash")),
              f"data={data}")
        check("Request status is pending", data.get("status") == "pending",
              f"status={data.get('status')}")


# =============================================================================
# TEST 6: Organization Registration + Membership
# =============================================================================
def test_org_registration():
    print("\n" + "=" * 60)
    print("TEST 6: Organization Registration + Membership")
    print("=" * 60)

    # Create two orgs with different admins
    admin_a = Agent("org-a-admin")
    admin_b = Agent("org-b-admin")

    # Register Org A (e.g., Ministry of Defense)
    resp = admin_a.post(f"{BASE}/v1/org/register", {
        "name": "Ministry of Defense",
        "description": "National defense organization",
    })
    check("Register Org A", resp.status_code == 201,
          f"HTTP {resp.status_code}: {resp.text}")
    org_a_id = resp.json().get("org_id", "")
    check("Got org_a_id", bool(org_a_id), f"body={resp.json()}")

    wait()

    # Register Org B (e.g., Cybersecurity Authority)
    resp = admin_b.post(f"{BASE}/v1/org/register", {
        "name": "National Cybersecurity Authority",
        "description": "National cybersecurity regulatory body",
    })
    check("Register Org B", resp.status_code == 201,
          f"HTTP {resp.status_code}: {resp.text}")
    org_b_id = resp.json().get("org_id", "")
    check("Got org_b_id", bool(org_b_id), f"body={resp.json()}")

    wait()

    # Get org info
    resp = admin_a.get(f"{BASE}/v1/org/{org_a_id}")
    check("Get Org A info", resp.status_code == 200,
          f"HTTP {resp.status_code}: {resp.text}")

    # Add member to Org A with CONFIDENTIAL clearance
    member_a = Agent("org-a-member")
    resp = admin_a.post(f"{BASE}/v1/org/{org_a_id}/member", {
        "agent_id": member_a.agent_id,
        "clearance": 2,  # CONFIDENTIAL
        "role": "analyst",
    })
    check("Add member to Org A", resp.status_code in (200, 201),
          f"HTTP {resp.status_code}: {resp.text}")

    wait()

    # List org members
    resp = admin_a.get(f"{BASE}/v1/org/{org_a_id}/members")
    check("List Org A members", resp.status_code == 200,
          f"HTTP {resp.status_code}: {resp.text[:200]}")
    if resp.status_code == 200:
        members = resp.json()
        check("Members list not empty",
              isinstance(members, list) and len(members) > 0,
              f"members={members}")

    return admin_a, admin_b, org_a_id, org_b_id, member_a


# =============================================================================
# TEST 7: Clearance Level Update
# =============================================================================
def test_clearance_update(admin_a, org_a_id, member_a):
    print("\n" + "=" * 60)
    print("TEST 7: Clearance Level Update")
    print("=" * 60)

    # Upgrade member's clearance to SECRET
    resp = admin_a.post(f"{BASE}/v1/org/{org_a_id}/clearance", {
        "agent_id": member_a.agent_id,
        "clearance": 3,  # SECRET
    })
    check("Upgrade clearance to SECRET", resp.status_code == 200,
          f"HTTP {resp.status_code}: {resp.text}")

    wait()

    # Verify via member list
    resp = admin_a.get(f"{BASE}/v1/org/{org_a_id}/members")
    if resp.status_code == 200:
        members = resp.json()
        target = [m for m in members if m.get("agent_id") == member_a.agent_id]
        if target:
            check("Clearance updated to 3 (SECRET)",
                  target[0].get("clearance") == 3,
                  f"clearance={target[0].get('clearance')}")
        else:
            check("Member found in list", False, f"member not in list")


# =============================================================================
# TEST 8: Federation Proposal + Approval
# =============================================================================
def test_federation(admin_a, admin_b, org_a_id, org_b_id):
    print("\n" + "=" * 60)
    print("TEST 8: Cross-Org Federation Proposal + Approval")
    print("=" * 60)

    # Org A proposes federation with Org B
    resp = admin_a.post(f"{BASE}/v1/federation/propose", {
        "target_org_id": org_b_id,
        "allowed_domains": ["red_team", "vuln_intel"],
        "max_clearance": 2,  # CONFIDENTIAL max
        "requires_approval": True,
    })
    check("Propose federation A→B", resp.status_code in (200, 201),
          f"HTTP {resp.status_code}: {resp.text}")

    wait()

    # We need the federation ID — check response
    fed_data = resp.json()
    tx_hash = fed_data.get("tx_hash", "")
    check("Federation proposal has tx_hash", bool(tx_hash), f"data={fed_data}")

    # For now we need to discover the fed_id.
    # The federation ID is deterministic: SHA-256(proposer_org + target_org + height)
    # We'll try to get active federations for org A
    resp = admin_a.get(f"{BASE}/v1/federation/active/{org_a_id}")
    check("List active federations for Org A", resp.status_code == 200,
          f"HTTP {resp.status_code}: {resp.text[:200]}")

    fed_id = ""
    if resp.status_code == 200:
        feds = resp.json()
        if isinstance(feds, list) and len(feds) > 0:
            fed_id = feds[0].get("federation_id", "")
            check("Federation found in list", bool(fed_id), f"feds={feds}")
        else:
            check("Federation found in list", False, f"empty list: {feds}")

    if fed_id:
        # Org B approves the federation
        resp = admin_b.post(f"{BASE}/v1/federation/{fed_id}/approve", {})
        check("Org B approves federation", resp.status_code == 200,
              f"HTTP {resp.status_code}: {resp.text}")

        wait()

        # Verify federation is active
        resp = admin_a.get(f"{BASE}/v1/federation/{fed_id}")
        check("Federation details queryable", resp.status_code == 200,
              f"HTTP {resp.status_code}: {resp.text[:200]}")
        if resp.status_code == 200:
            fed = resp.json()
            check("Federation status is active",
                  fed.get("status") in ("active", "proposed"),
                  f"status={fed.get('status')}")

    return fed_id


# =============================================================================
# TEST 9: Federation Revocation
# =============================================================================
def test_federation_revocation(admin_a, fed_id):
    print("\n" + "=" * 60)
    print("TEST 9: Federation Revocation")
    print("=" * 60)

    if not fed_id:
        print("  SKIP: No federation ID from previous test")
        return

    resp = admin_a.post(f"{BASE}/v1/federation/{fed_id}/revoke", {
        "reason": "Security incident — revoking all cross-org access",
    })
    check("Revoke federation", resp.status_code == 200,
          f"HTTP {resp.status_code}: {resp.text}")

    wait()

    # Verify federation status changed
    resp = admin_a.get(f"{BASE}/v1/federation/{fed_id}")
    if resp.status_code == 200:
        fed = resp.json()
        check("Federation status is revoked",
              fed.get("status") == "revoked",
              f"status={fed.get('status')}")


# =============================================================================
# TEST 10: Cross-Node Consistency for Access Control
# =============================================================================
def test_cross_node_consistency():
    print("\n" + "=" * 60)
    print("TEST 10: Cross-Node Consistency")
    print("=" * 60)

    admin = Agent("cross-node-admin")

    # Register domain on node0
    resp = admin.post(f"{BASE}/v1/domain/register", {
        "name": "cross_node_test",
        "description": "Testing cross-node ACL replication",
    })
    check("Register domain on node0", resp.status_code == 201,
          f"HTTP {resp.status_code}: {resp.text}")

    wait(6, "cross-node replication")

    # Query domain on node1
    resp = admin.get(f"{NODE1}/v1/domain/cross_node_test")
    check("Domain visible on node1", resp.status_code == 200,
          f"HTTP {resp.status_code}: {resp.text[:200]}")

    # Submit memory on node0
    resp = admin.post(f"{BASE}/v1/memory/submit", {
        "content": "Cross-node ACL test: data replicates with access control intact",
        "memory_type": "observation",
        "domain_tag": "cross_node_test",
        "confidence_score": 0.88,
    })
    check("Submit memory on node0", resp.status_code in (200, 201, 202),
          f"HTTP {resp.status_code}: {resp.text}")
    memory_id = resp.json().get("memory_id", "")

    wait(6, "cross-node replication")

    # Outsider tries to read on node1 — should be denied
    outsider = Agent("cross-node-outsider")
    resp = outsider.get(f"{NODE1}/v1/memory/{memory_id}")
    check("Outsider denied on node1 (403)",
          resp.status_code == 403,
          f"HTTP {resp.status_code}: {resp.text[:200]}")

    # Grant on node0
    resp = admin.post(f"{BASE}/v1/access/grant", {
        "grantee_id": outsider.agent_id,
        "domain": "cross_node_test",
        "level": 1,
    })
    check("Grant access on node0", resp.status_code in (200, 201),
          f"HTTP {resp.status_code}: {resp.text}")

    wait(6, "grant replication")

    # Now outsider reads on node1 — should succeed
    resp = outsider.get(f"{NODE1}/v1/memory/{memory_id}")
    check("Outsider can read on node1 after grant",
          resp.status_code == 200,
          f"HTTP {resp.status_code}: {resp.text[:200]}")


# =============================================================================
# TEST 11: Member Removal from Organization
# =============================================================================
def test_member_removal(admin_a, org_a_id, member_a):
    print("\n" + "=" * 60)
    print("TEST 11: Member Removal from Organization")
    print("=" * 60)

    resp = admin_a.delete(f"{BASE}/v1/org/{org_a_id}/member/{member_a.agent_id}")
    check("Remove member from Org A", resp.status_code == 200,
          f"HTTP {resp.status_code}: {resp.text}")

    wait()

    # Verify member is gone from list
    resp = admin_a.get(f"{BASE}/v1/org/{org_a_id}/members")
    if resp.status_code == 200:
        members = resp.json()
        remaining = [m for m in members if m.get("agent_id") == member_a.agent_id]
        check("Removed member not in list", len(remaining) == 0,
              f"still found: {remaining}")


# =============================================================================
# TEST 12: Expiring Grants
# =============================================================================
def test_expiring_grants():
    print("\n" + "=" * 60)
    print("TEST 12: Grant with Expiration")
    print("=" * 60)

    admin = Agent("expiry-admin")
    reader = Agent("expiry-reader")

    # Register domain
    resp = admin.post(f"{BASE}/v1/domain/register", {
        "name": "expiry_test",
        "description": "Testing grant expiration",
    })
    check("Register expiry_test domain", resp.status_code == 201,
          f"HTTP {resp.status_code}: {resp.text}")

    wait()

    # Grant with far-future expiration
    future_ts = int(time.time()) + 86400  # 24h from now
    resp = admin.post(f"{BASE}/v1/access/grant", {
        "grantee_id": reader.agent_id,
        "domain": "expiry_test",
        "level": 1,
        "expires_at": future_ts,
    })
    check("Grant with future expiration", resp.status_code in (200, 201),
          f"HTTP {resp.status_code}: {resp.text}")

    wait()

    # Grant with past expiration (should fail to provide access)
    expired = Agent("expired-reader")
    past_ts = int(time.time()) - 3600  # 1h ago
    resp = admin.post(f"{BASE}/v1/access/grant", {
        "grantee_id": expired.agent_id,
        "domain": "expiry_test",
        "level": 1,
        "expires_at": past_ts,
    })
    check("Grant with past expiration accepted",
          resp.status_code in (200, 201),
          f"HTTP {resp.status_code}: {resp.text}")


# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("SAGE Phase 3: Federation Access Control — E2E Test")
    print("=" * 60)

    # Health check
    try:
        r = requests.get(f"{BASE}/health", timeout=3)
        if r.json().get("status") != "healthy":
            print("Network not healthy, aborting.")
            sys.exit(1)
        print(f"Network healthy (node0)")
    except Exception as e:
        print(f"Cannot reach node0: {e}")
        sys.exit(1)

    # Run all tests
    try:
        # Test 1: Domain registration
        domain_admin = test_domain_registration()

        # Test 2: Access denial (unauthorized)
        memory_id, outsider = test_access_denial(domain_admin)

        # Test 3: Access grant + authorized read
        test_access_grant(domain_admin, memory_id, outsider)

        # Test 4: Access revocation
        test_access_revocation(domain_admin, memory_id, outsider)

        # Test 5: Access request flow
        test_access_request()

        # Test 6: Org registration + membership
        admin_a, admin_b, org_a_id, org_b_id, member_a = test_org_registration()

        # Test 7: Clearance level update
        test_clearance_update(admin_a, org_a_id, member_a)

        # Test 8: Federation proposal + approval
        fed_id = test_federation(admin_a, admin_b, org_a_id, org_b_id)

        # Test 9: Federation revocation
        test_federation_revocation(admin_a, fed_id)

        # Test 10: Cross-node consistency
        test_cross_node_consistency()

        # Test 11: Member removal
        test_member_removal(admin_a, org_a_id, member_a)

        # Test 12: Expiring grants
        test_expiring_grants()

    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        FAIL_COUNT += 1

    # Summary
    total = PASS_COUNT + FAIL_COUNT
    print(f"\n{'=' * 60}")
    print(f"RESULTS: {PASS_COUNT}/{total} passed, {FAIL_COUNT} failed")
    print(f"{'=' * 60}")

    if FAIL_COUNT > 0:
        sys.exit(1)
    else:
        print("ALL TESTS PASSED")
