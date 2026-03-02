"""SAGE asynchronous client."""

from __future__ import annotations

from typing import Any, Literal

import httpx

from sage_sdk.auth import AgentIdentity
from sage_sdk.exceptions import SageAPIError
from sage_sdk.models import (
    AgentProfile,
    ChallengeRequest,
    CorroborateRequest,
    KnowledgeTriple,
    MemoryQueryResponse,
    MemoryRecord,
    MemorySubmitRequest,
    MemorySubmitResponse,
    MemoryType,
    VoteRequest,
)


class AsyncSageClient:
    """Asynchronous SAGE API client."""

    def __init__(
        self,
        base_url: str,
        identity: AgentIdentity,
        timeout: float = 30.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._identity = identity
        self._client = httpx.AsyncClient(base_url=self._base_url, timeout=timeout)

    async def _request(
        self,
        method: str,
        path: str,
        json: Any = None,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response:
        body = None
        if json is not None:
            import json as json_mod

            body = json_mod.dumps(json, separators=(",", ":")).encode()

        headers = self._identity.sign_request(method, path, body)
        if body is not None:
            headers["Content-Type"] = "application/json"

        response = await self._client.request(
            method, path, content=body, headers=headers, params=params
        )
        self._handle_response(response)
        return response

    def _handle_response(self, response: httpx.Response) -> None:
        if response.status_code >= 400:
            raise SageAPIError.from_response(response)

    async def propose(
        self,
        content: str,
        memory_type: MemoryType | str,
        domain_tag: str,
        confidence: float,
        embedding: list[float] | None = None,
        knowledge_triples: list[KnowledgeTriple] | None = None,
        parent_hash: str | None = None,
    ) -> MemorySubmitResponse:
        """Submit a new memory proposal."""
        req = MemorySubmitRequest(
            content=content,
            memory_type=MemoryType(memory_type),
            domain_tag=domain_tag,
            confidence_score=confidence,
            embedding=embedding,
            knowledge_triples=knowledge_triples,
            parent_hash=parent_hash,
        )
        resp = await self._request("POST", "/v1/memory/submit", json=req.model_dump(mode="json", exclude_none=True, by_alias=True))
        return MemorySubmitResponse.model_validate(resp.json())

    async def query(
        self,
        embedding: list[float],
        domain_tag: str | None = None,
        min_confidence: float | None = None,
        top_k: int = 10,
        status_filter: str | None = None,
        cursor: str | None = None,
    ) -> MemoryQueryResponse:
        """Query memories by vector similarity."""
        body: dict[str, Any] = {"embedding": embedding, "top_k": top_k}
        if domain_tag is not None:
            body["domain_tag"] = domain_tag
        if min_confidence is not None:
            body["min_confidence"] = min_confidence
        if status_filter is not None:
            body["status_filter"] = status_filter
        if cursor is not None:
            body["cursor"] = cursor

        resp = await self._request("POST", "/v1/memory/query", json=body)
        return MemoryQueryResponse.model_validate(resp.json())

    async def get_memory(self, memory_id: str) -> MemoryRecord:
        """Get a single memory by ID."""
        resp = await self._request("GET", f"/v1/memory/{memory_id}")
        return MemoryRecord.model_validate(resp.json())

    async def vote(
        self,
        memory_id: str,
        decision: Literal["accept", "reject", "abstain"],
        rationale: str | None = None,
    ) -> dict:
        """Cast a vote on a proposed memory."""
        req = VoteRequest(decision=decision, rationale=rationale)
        resp = await self._request(
            "POST",
            f"/v1/memory/{memory_id}/vote",
            json=req.model_dump(exclude_none=True),
        )
        return resp.json()

    async def challenge(
        self,
        memory_id: str,
        reason: str,
        evidence: str | None = None,
    ) -> dict:
        """Challenge a committed memory."""
        req = ChallengeRequest(reason=reason, evidence=evidence)
        resp = await self._request(
            "POST",
            f"/v1/memory/{memory_id}/challenge",
            json=req.model_dump(exclude_none=True),
        )
        return resp.json()

    async def corroborate(
        self,
        memory_id: str,
        evidence: str | None = None,
    ) -> dict:
        """Corroborate an existing memory."""
        req = CorroborateRequest(evidence=evidence)
        resp = await self._request(
            "POST",
            f"/v1/memory/{memory_id}/corroborate",
            json=req.model_dump(exclude_none=True),
        )
        return resp.json()

    async def embed(self, text: str) -> list[float]:
        """Generate a vector embedding via the SAGE network's local Ollama.

        Agents can call this instead of running Ollama locally.
        All computation stays within the SAGE network — no cloud API calls.
        """
        resp = await self._request("POST", "/v1/embed", json={"text": text})
        data = resp.json()
        return data["embedding"]

    async def get_profile(self) -> AgentProfile:
        """Get the current agent's profile."""
        resp = await self._request("GET", "/v1/agent/me")
        return AgentProfile.model_validate(resp.json())

    async def request_access(self, domain: str, justification: str = "", level: int = 1) -> dict:
        """Request access to a domain."""
        body = {"target_domain": domain, "justification": justification, "requested_level": level}
        resp = await self._request("POST", "/v1/access/request", json=body)
        return resp.json()

    async def grant_access(
        self,
        grantee_id: str,
        domain: str,
        level: int = 1,
        expires_at: int = 0,
        request_id: str | None = None,
    ) -> dict:
        """Grant access to a domain (domain owner only)."""
        body: dict[str, Any] = {
            "grantee_id": grantee_id,
            "domain": domain,
            "level": level,
            "expires_at": expires_at,
        }
        if request_id:
            body["request_id"] = request_id
        resp = await self._request("POST", "/v1/access/grant", json=body)
        return resp.json()

    async def revoke_access(self, grantee_id: str, domain: str, reason: str = "") -> dict:
        """Revoke access to a domain (domain owner only)."""
        body = {"grantee_id": grantee_id, "domain": domain, "reason": reason}
        resp = await self._request("POST", "/v1/access/revoke", json=body)
        return resp.json()

    async def list_grants(self, agent_id: str | None = None) -> list[dict]:
        """List active access grants for an agent."""
        aid = agent_id or self._identity.agent_id
        resp = await self._request("GET", f"/v1/access/grants/{aid}")
        return resp.json()

    async def register_domain(self, name: str, description: str = "", parent: str = "") -> dict:
        """Register a new domain."""
        body: dict[str, Any] = {"name": name}
        if description:
            body["description"] = description
        if parent:
            body["parent"] = parent
        resp = await self._request("POST", "/v1/domain/register", json=body)
        return resp.json()

    async def get_domain(self, name: str) -> dict:
        """Get domain info."""
        resp = await self._request("GET", f"/v1/domain/{name}")
        return resp.json()

    # --- Department RBAC --------------------------------------------------------

    async def register_dept(self, org_id: str, name: str, description: str = "", parent_dept: str = "") -> dict:
        """Register a new department within an organization."""
        body: dict[str, Any] = {"name": name}
        if description:
            body["description"] = description
        if parent_dept:
            body["parent_dept"] = parent_dept
        resp = await self._request("POST", f"/v1/org/{org_id}/dept", json=body)
        return resp.json()

    async def get_dept(self, org_id: str, dept_id: str) -> dict:
        """Get department info."""
        resp = await self._request("GET", f"/v1/org/{org_id}/dept/{dept_id}")
        return resp.json()

    async def list_depts(self, org_id: str) -> list[dict]:
        """List all departments in an organization."""
        resp = await self._request("GET", f"/v1/org/{org_id}/depts")
        return resp.json()

    async def add_dept_member(
        self,
        org_id: str,
        dept_id: str,
        agent_id: str,
        clearance: int = 1,
        role: str = "member",
    ) -> dict:
        """Add an agent to a department."""
        body: dict[str, Any] = {"agent_id": agent_id, "clearance": clearance, "role": role}
        resp = await self._request("POST", f"/v1/org/{org_id}/dept/{dept_id}/member", json=body)
        return resp.json()

    async def remove_dept_member(self, org_id: str, dept_id: str, agent_id: str) -> dict:
        """Remove an agent from a department."""
        resp = await self._request("DELETE", f"/v1/org/{org_id}/dept/{dept_id}/member/{agent_id}")
        return resp.json()

    async def list_dept_members(self, org_id: str, dept_id: str) -> list[dict]:
        """List all members of a department."""
        resp = await self._request("GET", f"/v1/org/{org_id}/dept/{dept_id}/members")
        return resp.json()

    # --- Organization -----------------------------------------------------------

    async def register_org(self, name: str, description: str = "") -> dict:
        """Register a new organization."""
        body: dict[str, Any] = {"name": name, "description": description}
        resp = await self._request("POST", "/v1/org/register", json=body)
        return resp.json()

    async def get_org(self, org_id: str) -> dict:
        """Get organization info."""
        resp = await self._request("GET", f"/v1/org/{org_id}")
        return resp.json()

    async def list_org_members(self, org_id: str) -> list[dict]:
        """List all members of an organization."""
        resp = await self._request("GET", f"/v1/org/{org_id}/members")
        return resp.json()

    async def add_org_member(
        self,
        org_id: str,
        agent_id: str,
        clearance: int = 1,
        role: str = "member",
    ) -> dict:
        """Add an agent to an organization."""
        body: dict[str, Any] = {"agent_id": agent_id, "clearance": clearance, "role": role}
        resp = await self._request("POST", f"/v1/org/{org_id}/member", json=body)
        return resp.json()

    async def remove_org_member(self, org_id: str, agent_id: str) -> dict:
        """Remove an agent from an organization."""
        resp = await self._request("DELETE", f"/v1/org/{org_id}/member/{agent_id}")
        return resp.json()

    async def set_org_clearance(self, org_id: str, agent_id: str, clearance: int) -> dict:
        """Update an agent's clearance level within an organization."""
        body: dict[str, Any] = {"agent_id": agent_id, "clearance": clearance}
        resp = await self._request("POST", f"/v1/org/{org_id}/clearance", json=body)
        return resp.json()

    # --- Federation -------------------------------------------------------------

    async def propose_federation(
        self,
        target_org_id: str,
        allowed_domains: list[str] | None = None,
        allowed_depts: list[str] | None = None,
        max_clearance: int = 2,
        expires_at: int = 0,
        requires_approval: bool = True,
    ) -> dict:
        """Propose a federation agreement with another organization."""
        body: dict[str, Any] = {
            "target_org_id": target_org_id,
            "allowed_domains": allowed_domains or [],
            "allowed_depts": allowed_depts or [],
            "max_clearance": max_clearance,
            "expires_at": expires_at,
            "requires_approval": requires_approval,
        }
        resp = await self._request("POST", "/v1/federation/propose", json=body)
        return resp.json()

    async def approve_federation(self, federation_id: str) -> dict:
        """Approve a pending federation agreement."""
        resp = await self._request("POST", f"/v1/federation/{federation_id}/approve", json={})
        return resp.json()

    async def revoke_federation(self, federation_id: str, reason: str = "") -> dict:
        """Revoke an active federation agreement."""
        body: dict[str, Any] = {}
        if reason:
            body["reason"] = reason
        resp = await self._request("POST", f"/v1/federation/{federation_id}/revoke", json=body)
        return resp.json()

    async def get_federation(self, federation_id: str) -> dict:
        """Get federation agreement info."""
        resp = await self._request("GET", f"/v1/federation/{federation_id}")
        return resp.json()

    async def list_federations(self, org_id: str) -> list[dict]:
        """List active federation agreements for an organization."""
        resp = await self._request("GET", f"/v1/federation/active/{org_id}")
        return resp.json()

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> AsyncSageClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self._client.aclose()
