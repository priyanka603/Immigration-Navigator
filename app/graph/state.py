"""
LangGraph state definition.

The state is the single source of truth that flows through
the entire agent graph. Every agent reads from it and writes to it.

Think of it as the conversation's working memory —
it carries everything from the user's question to the
final answer, passing through whichever agents are needed.
"""
from typing import Annotated
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage
from pydantic import BaseModel


class NavigatorState(BaseModel):
    """
    Shared state for the immigration navigator graph.

    Fields:
        messages: full conversation history (managed by LangGraph)
        question: the user's current question
        nationality: user's nationality if provided
        current_visa: user's current visa status if provided
        retrieved_chunks: documents found by the retriever
        answer: the generated answer
        agent_used: which agent handled the question
        sources: source documents for the answer
        checklist_goal: goal for checklist generation
        checklist_steps: generated checklist steps
        requires_checklist: whether to generate a checklist
        error: any error that occurred
    """
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