"""Tests for Department RBAC SDK methods."""

import pytest
import httpx
import respx

BASE_URL = "http://localhost:8080"

ORG_ID = "test-org-1"
DEPT_ID = "abc12345"
AGENT_ID = "b" * 64


@pytest.fixture
def client(agent_identity):
    from sage_sdk.client import SageClient
    return SageClient(base_url=BASE_URL, identity=agent_identity)


@pytest.fixture
def mock_api():
    with respx.mock(base_url=BASE_URL, assert_all_called=False) as respx_mock:
        yield respx_mock


# --- Sync client tests ---


def test_register_dept(client, mock_api):
    mock_api.post(f"/v1/org/{ORG_ID}/dept").mock(
        return_value=httpx.Response(201, json={
            "status": "registered",
            "dept_id": DEPT_ID,
            "tx_hash": "deadbeef" * 8,
        })
    )
    result = client.register_dept(ORG_ID, name="Engineering", description="Eng team")
    assert result["status"] == "registered"
    assert result["dept_id"] == DEPT_ID


def test_register_dept_with_parent(client, mock_api):
    mock_api.post(f"/v1/org/{ORG_ID}/dept").mock(
        return_value=httpx.Response(201, json={
            "status": "registered",
            "dept_id": "def67890",
            "tx_hash": "cafebabe" * 8,
        })
    )
    result = client.register_dept(
        ORG_ID, name="Security", description="Security team", parent_dept=DEPT_ID
    )
    assert result["status"] == "registered"


def test_get_dept(client, mock_api):
    dept_data = {
        "org_id": ORG_ID,
        "dept_id": DEPT_ID,
        "dept_name": "Engineering",
        "description": "Eng team",
        "parent_dept": "",
        "created_height": 42,
    }
    mock_api.get(f"/v1/org/{ORG_ID}/dept/{DEPT_ID}").mock(
        return_value=httpx.Response(200, json=dept_data)
    )
    result = client.get_dept(ORG_ID, DEPT_ID)
    assert result["dept_name"] == "Engineering"
    assert result["org_id"] == ORG_ID


def test_list_depts(client, mock_api):
    depts = [
        {"org_id": ORG_ID, "dept_id": DEPT_ID, "dept_name": "Engineering"},
        {"org_id": ORG_ID, "dept_id": "def67890", "dept_name": "Security"},
    ]
    mock_api.get(f"/v1/org/{ORG_ID}/depts").mock(
        return_value=httpx.Response(200, json=depts)
    )
    result = client.list_depts(ORG_ID)
    assert len(result) == 2
    assert result[0]["dept_name"] == "Engineering"


def test_add_dept_member(client, mock_api):
    mock_api.post(f"/v1/org/{ORG_ID}/dept/{DEPT_ID}/member").mock(
        return_value=httpx.Response(201, json={
            "status": "added",
            "tx_hash": "deadbeef" * 8,
        })
    )
    result = client.add_dept_member(ORG_ID, DEPT_ID, agent_id=AGENT_ID, clearance=2, role="admin")
    assert result["status"] == "added"


def test_add_dept_member_defaults(client, mock_api):
    mock_api.post(f"/v1/org/{ORG_ID}/dept/{DEPT_ID}/member").mock(
        return_value=httpx.Response(201, json={
            "status": "added",
            "tx_hash": "deadbeef" * 8,
        })
    )
    result = client.add_dept_member(ORG_ID, DEPT_ID, agent_id=AGENT_ID)
    assert result["status"] == "added"


def test_remove_dept_member(client, mock_api):
    mock_api.delete(f"/v1/org/{ORG_ID}/dept/{DEPT_ID}/member/{AGENT_ID}").mock(
        return_value=httpx.Response(200, json={
            "status": "removed",
            "tx_hash": "cafebabe" * 8,
        })
    )
    result = client.remove_dept_member(ORG_ID, DEPT_ID, AGENT_ID)
    assert result["status"] == "removed"


def test_list_dept_members(client, mock_api):
    members = [
        {"org_id": ORG_ID, "dept_id": DEPT_ID, "agent_id": AGENT_ID, "clearance": 2, "role": "admin"},
        {"org_id": ORG_ID, "dept_id": DEPT_ID, "agent_id": "c" * 64, "clearance": 1, "role": "member"},
    ]
    mock_api.get(f"/v1/org/{ORG_ID}/dept/{DEPT_ID}/members").mock(
        return_value=httpx.Response(200, json=members)
    )
    result = client.list_dept_members(ORG_ID, DEPT_ID)
    assert len(result) == 2
    assert result[0]["role"] == "admin"
    assert result[1]["clearance"] == 1


# --- Async client tests ---


import pytest_asyncio


@pytest_asyncio.fixture
async def async_client(agent_identity):
    from sage_sdk.async_client import AsyncSageClient
    client = AsyncSageClient(base_url=BASE_URL, identity=agent_identity)
    yield client
    await client.close()


@pytest.mark.asyncio
async def test_async_register_dept(async_client, mock_api):
    mock_api.post(f"/v1/org/{ORG_ID}/dept").mock(
        return_value=httpx.Response(201, json={
            "status": "registered",
            "dept_id": DEPT_ID,
            "tx_hash": "deadbeef" * 8,
        })
    )
    result = await async_client.register_dept(ORG_ID, name="Engineering")
    assert result["status"] == "registered"
    assert result["dept_id"] == DEPT_ID


@pytest.mark.asyncio
async def test_async_add_dept_member(async_client, mock_api):
    mock_api.post(f"/v1/org/{ORG_ID}/dept/{DEPT_ID}/member").mock(
        return_value=httpx.Response(201, json={
            "status": "added",
            "tx_hash": "deadbeef" * 8,
        })
    )
    result = await async_client.add_dept_member(ORG_ID, DEPT_ID, agent_id=AGENT_ID)
    assert result["status"] == "added"


@pytest.mark.asyncio
async def test_async_list_depts(async_client, mock_api):
    mock_api.get(f"/v1/org/{ORG_ID}/depts").mock(
        return_value=httpx.Response(200, json=[
            {"org_id": ORG_ID, "dept_id": DEPT_ID, "dept_name": "Engineering"},
        ])
    )
    result = await async_client.list_depts(ORG_ID)
    assert len(result) == 1


@pytest.mark.asyncio
async def test_async_remove_dept_member(async_client, mock_api):
    mock_api.delete(f"/v1/org/{ORG_ID}/dept/{DEPT_ID}/member/{AGENT_ID}").mock(
        return_value=httpx.Response(200, json={
            "status": "removed",
            "tx_hash": "cafebabe" * 8,
        })
    )
    result = await async_client.remove_dept_member(ORG_ID, DEPT_ID, AGENT_ID)
    assert result["status"] == "removed"


@pytest.mark.asyncio
async def test_async_list_dept_members(async_client, mock_api):
    mock_api.get(f"/v1/org/{ORG_ID}/dept/{DEPT_ID}/members").mock(
        return_value=httpx.Response(200, json=[
            {"org_id": ORG_ID, "dept_id": DEPT_ID, "agent_id": AGENT_ID, "clearance": 1, "role": "member"},
        ])
    )
    result = await async_client.list_dept_members(ORG_ID, DEPT_ID)
    assert len(result) == 1
    assert result[0]["agent_id"] == AGENT_ID
