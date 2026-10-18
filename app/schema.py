"""Shared data contract between ingestion/retrieval and the agent/UI.

Mirrors CHUNK_SCHEMA.md. Change both together and bump SCHEMA_VERSION.
"""
from typing import Literal, Optional

from pydantic import BaseModel, Field

SCHEMA_VERSION = "0.6"

SourceType = Literal["policy", "ticket", "email", "slack", "confluence"]
SourceSystem = Literal["confluence", "servicenow", "outlook", "slack"]
Sensitivity = Literal["public", "internal", "restricted"]


class Signals(BaseModel):
    """Derived at ingest from real fields only; never from the dataset's answer-key fields."""
    days_since_update: int
    # Owners (author / assignee / policy team lead) who have exited or are on leave.
    owners_inactive: list[str] = Field(default_factory=list)
    # Inactive people named in the text, by full name or by a role title only they held.
    inactive_people_mentioned: list[str] = Field(default_factory=list)
    # Open/in-progress/on-hold `policy-update` tickets that name this record.
    open_update_request_ids: list[str] = Field(default_factory=list)
    # Records that mention/reference this one and are newer than its last update.
    later_mention_ids: list[str] = Field(default_factory=list)


class Chunk(BaseModel):
    chunk_id: str  # "<record_id>#<chunk_index>"
    record_id: str
    chunk_index: int
    source_type: SourceType
    source_system: SourceSystem
    title: str
    text: str
    department_id: str
    sensitivity: Sensitivity
    created_date: str
    last_updated: str
    last_referenced_date: Optional[str] = None
    owner_employee_ids: list[str] = Field(default_factory=list)
    owner_team_id: Optional[str] = None
    # Everyone involved in the record: ticket requester/on-behalf-of/assignee/approvers, email and Slack
    # participants, document authors. Drives need-to-know access to confidential records.
    participant_employee_ids: list[str] = Field(default_factory=list)
    # Confidential = labelled restricted at source OR found at ingest to contain personal data
    # (pay, health, leave reasons, performance, disciplinary, personal contact details).
    confidential: bool = False
    personal_data: bool = False  # the ingest-time check found personal data in this record
    # pay | health_or_leave_reason | performance_or_disciplinary | exit_details | personal_contact_or_ids | other
    personal_data_category: Optional[str] = None
    # Business domain, used by role grants: security | finance | hr | commercial | legal | general
    data_domain: str = "general"
    confidential_reason: Optional[str] = None
    event_id: Optional[str] = None
    status: Optional[str] = None
    kind: Optional[str] = None
    category: Optional[str] = None  # ticket category (e.g. "vpn", "hr-query"); used to group similar past cases
    referenced_ids: list[str] = Field(default_factory=list)
    related_policy_ids: list[str] = Field(default_factory=list)
    related_system_ids: list[str] = Field(default_factory=list)
    signals: Signals


class Citation(BaseModel):
    n: int
    chunk_id: str
    record_id: str
    title: str
    source_system: SourceSystem
    date: str
    confidential: bool = False
    access_basis: Optional[str] = None  # for confidential records: the rule that let this user see it


ConflictKind = Literal["policy_vs_practice", "conflicting_resolutions", "source_vs_source"]


class Conflict(BaseModel):
    kind: ConflictKind
    summary: str
    record_ids: list[str]
    current_view: Optional[str] = None  # record_id the agent judges authoritative, if any


class StalenessFlag(BaseModel):
    record_id: str
    reason: str


class Fallback(BaseModel):
    needed: bool = False
    contact_employee_id: Optional[str] = None
    contact_name: Optional[str] = None
    contact_role: Optional[str] = None
    reason: Optional[str] = None


class ToolCall(BaseModel):
    tool: str
    args: dict
    summary: str  # e.g. "8 hits, 6 related, 2 withheld"
    secs: float = 0.0


class AnswerMeta(BaseModel):
    model: str
    user_id: str  # employee_id of the signed-in user the answer was scoped to
    confidence: Literal["high", "medium", "low"]
    latency_s: float
    model_calls: int
    input_tokens: int = 0
    output_tokens: int = 0
    dropped_citations: list[str] = Field(default_factory=list)  # IDs the model cited but never retrieved
    model_call_secs: list[float] = Field(default_factory=list)  # duration of each agent-model round trip
    tool_secs: float = 0.0  # total time spent inside tools (retrieval, case comparison)
    cached: bool = False  # served from the answer cache (same question + user asked before)
    # Every record the agent was shown for this answer; a stored answer is re-shown only if all are still visible.
    retrieved_record_ids: list[str] = Field(default_factory=list)


class AgentResponse(BaseModel):
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    conflicts: list[Conflict] = Field(default_factory=list)
    staleness: list[StalenessFlag] = Field(default_factory=list)
    fallback: Fallback = Field(default_factory=Fallback)
    access_note: Optional[str] = None
    trace: list[ToolCall] = Field(default_factory=list)
    meta: Optional[AnswerMeta] = None
    chat_id: Optional[str] = None  # the conversation this answer belongs to (set by /api/chat)
