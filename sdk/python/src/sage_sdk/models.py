"""SAGE SDK Pydantic models."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class MemoryType(str, Enum):
    fact = "fact"
    observation = "observation"
    inference = "inference"


class MemoryStatus(str, Enum):
    proposed = "proposed"
    validated = "validated"
    committed = "committed"
    challenged = "challenged"
    deprecated = "deprecated"


class KnowledgeTriple(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    subject: str
    predicate: str
    object_: str = Field(alias="object")


class MemoryRecord(BaseModel):
    memory_id: str
    submitting_agent: str
    content: str
    content_hash: str
    memory_type: MemoryType
    domain_tag: str
    confidence_score: float = Field(ge=0, le=1)
    status: MemoryStatus
    parent_hash: str | None = None
    created_at: datetime
    committed_at: datetime | None = None
    deprecated_at: datetime | None = None
    votes: list | None = None
    corroborations: list | None = None
    similarity_score: float | None = None


class MemorySubmitRequest(BaseModel):
    content: str
    memory_type: MemoryType
    domain_tag: str
    confidence_score: float = Field(ge=0, le=1)
    embedding: list[float] | None = None
    knowledge_triples: list[KnowledgeTriple] | None = None
    parent_hash: str | None = None


class MemorySubmitResponse(BaseModel):
    memory_id: str
    tx_hash: str
    status: str


class MemoryQueryRequest(BaseModel):
    embedding: list[float]
    domain_tag: str | None = None
    min_confidence: float | None = None
    status_filter: str | None = None
    top_k: int = 10
    cursor: str | None = None


class MemoryQueryResponse(BaseModel):
    results: list[MemoryRecord]
    next_cursor: str | None = None
    total_count: int


class VoteRequest(BaseModel):
    decision: Literal["accept", "reject", "abstain"]
    rationale: str | None = None


class ChallengeRequest(BaseModel):
    reason: str
    evidence: str | None = None


class CorroborateRequest(BaseModel):
    evidence: str | None = None


class AgentProfile(BaseModel):
    agent_id: str
    poe_weight: float
    vote_count: int


class ProblemDetails(BaseModel):
    type: str
    title: str
    status: int
    detail: str
    instance: str | None = None


class AccessRequestModel(BaseModel):
    target_domain: str
    justification: str | None = None
    requested_level: int = 1


class AccessGrantModel(BaseModel):
    grantee_id: str
    domain: str
    level: int = 1
    expires_at: int = 0
    request_id: str | None = None


class AccessRevokeModel(BaseModel):
    grantee_id: str
    domain: str
    reason: str | None = None


class DomainRegisterModel(BaseModel):
    name: str
    description: str | None = None
    parent: str | None = None


class DomainInfo(BaseModel):
    domain_name: str
    owner_agent_id: str
    parent_domain: str | None = None
    description: str | None = None
    created_height: int
    created_at: datetime | None = None


class AccessGrantInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    domain: str
    grantee_id: str
    granter_id: str
    access_level: int = Field(alias="level", default=1)
    expires_at: datetime | None = None
    created_at: datetime | None = None
    revoked_at: datetime | None = None


# --- Department RBAC Models ---

class DeptRegisterRequest(BaseModel):
    name: str
    description: str | None = None
    parent_dept: str | None = None


class DeptRegisterResponse(BaseModel):
    status: str
    dept_id: str
    tx_hash: str


class DeptAddMemberRequest(BaseModel):
    agent_id: str
    clearance: int = 1
    role: str = "member"


class DeptAddMemberResponse(BaseModel):
    status: str
    tx_hash: str


class DeptInfo(BaseModel):
    org_id: str
    dept_id: str
    dept_name: str
    description: str | None = None
    parent_dept: str | None = None
    created_height: int | None = None


class DeptMemberInfo(BaseModel):
    org_id: str
    dept_id: str
    agent_id: str
    clearance: int = 1
    role: str = "member"
