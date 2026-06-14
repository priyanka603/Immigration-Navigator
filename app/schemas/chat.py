from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class AgentType(StrEnum):
    RAG = "rag"
    CHECKLIST = "checklist"
    DOCUMENT = "document"


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


class Source(BaseModel):
    title: str
    url: str
    category: str
    relevance_score: float


class ChatMessage(BaseModel):
    role: MessageRole
    content: str


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's immigration question",
        examples=["How do I apply for a Critical Skills Employment Permit?"],
    )
    session_id: str | None = Field(
        None,
        description="Session ID for conversation continuity",
    )
    nationality: str | None = Field(
        None,
        description="User's nationality for personalised answers",
        examples=["Indian", "Brazilian", "Chinese"],
    )
    current_visa: str | None = Field(
        None,
        description="User's current visa status if in Ireland",
        examples=["Student Stamp 2", "Critical Skills EP", "None"],
    )


class ChatResponse(BaseModel):
    answer: str
    agent_used: AgentType
    sources: list[Source]
    session_id: str
    has_context: bool
    disclaimer: str = (
        "This information is sourced from publicly available Irish government "
        "websites and is for general guidance only. Immigration rules change "
        "frequently. Always verify requirements directly with the Irish "
        "Immigration Service (irishimmigration.ie) or Citizens Information "
        "(citizensinformation.ie) before making decisions."
    )


class ChecklistRequest(BaseModel):
    goal: str = Field(
        ...,
        description="What the user wants to achieve",
        examples=["Apply for Critical Skills Employment Permit"],
    )
    nationality: str = Field(
        ...,
        description="User's nationality",
        examples=["Indian"],
    )
    current_status: str = Field(
        ...,
        description="Current immigration status in Ireland",
        examples=["Student Stamp 2", "Not in Ireland yet"],
    )


class ChecklistStep(BaseModel):
    step_number: int
    title: str
    description: str
    documents_required: list[str]
    estimated_time: str | None = None
    fee: str | None = None
    official_link: str | None = None


class ChecklistResponse(BaseModel):
    goal: str
    nationality: str
    current_status: str
    steps: list[ChecklistStep]
    total_estimated_time: str | None = None
    total_estimated_cost: str | None = None
    important_notes: list[str]
    sources: list[Source]
    disclaimer: str = (
        "This checklist is for general guidance only based on publicly "
        "available information. Always verify with official sources before "
        "submitting any application."
    )