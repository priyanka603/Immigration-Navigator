from typing import Annotated

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from pydantic import BaseModel


class NavigatorState(BaseModel):
    messages: Annotated[list[BaseMessage], add_messages] = []
    question: str = ""
    nationality: str | None = None
    current_visa: str | None = None
    retrieved_chunks: list[dict] = []
    answer: str = ""
    agent_used: str = ""
    sources: list[dict] = []
    checklist_goal: str | None = None
    checklist_steps: list[dict] = []
    requires_checklist: bool = False
    error: str | None = None