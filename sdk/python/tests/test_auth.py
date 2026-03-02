import os
import tempfile
import pytest


def test_generate_identity():
    from sage_sdk.auth import AgentIdentity
    identity = AgentIdentity.generate()
    assert identity.agent_id is not None
    assert len(identity.agent_id) == 64  # 32 bytes hex-encoded


def test_from_seed_deterministic():
    from sage_sdk.auth import AgentIdentity
    seed = b'\x42' * 32
    id1 = AgentIdentity.from_seed(seed)
    id2 = AgentIdentity.from_seed(seed)
    assert id1.agent_id == id2.agent_id


def test_sign_request(agent_identity):
    headers = agent_identity.sign_request("POST", "/v1/memory/submit", b'{"content":"test"}')
    assert "X-Agent-ID" in headers
    assert "X-Signature" in headers
    assert "X-Timestamp" in headers
    assert headers["X-Agent-ID"] == agent_identity.agent_id


def test_agent_id_format(agent_identity):
    agent_id = agent_identity.agent_id
    assert len(agent_id) == 64
    # Should be valid hex
    int(agent_id, 16)


def test_save_load_identity(agent_identity):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".key") as f:
        path = f.name
    try:
        agent_identity.to_file(path)
        from sage_sdk.auth import AgentIdentity
        loaded = AgentIdentity.from_file(path)
        assert loaded.agent_id == agent_identity.agent_id
    finally:
        os.unlink(path)


def test_different_identities_different_ids():
    from sage_sdk.auth import AgentIdentity
    id1 = AgentIdentity.generate()
    id2 = AgentIdentity.generate()
    assert id1.agent_id != id2.agent_id
