"""
Supervisor Agent — routes questions to the right specialist agent.

This is the entry point of the LangGraph workflow.
It reads the user's question and decides:
  - Is this a factual question? → RAG agent
  - Does the user need a step-by-step plan? → Checklist agent
  - Is the user asking about a document or letter? → Document agent

The routing decision is made by the LLM — not hardcoded rules.
This means it handles nuanced cases like:
  "I got a letter from INIS saying my visa is expiring, what do I do?"
  → Document agent first, then possibly checklist agent
"""
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app.core.config import get_settings
from app.core.logging import get_logger
from app.graph.state import NavigatorState

logger = get_logger(__name__)
settings = get_settings()

SUPERVISOR_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a routing supervisor for an Irish immigration assistant. "
        "Your job is to classify the user's question and route it to the "
        "right specialist.\n\n"
        "Available agents:\n"
        "- 'rag': for factual questions about visas, permits, rules, "
        "eligibility, fees, processing times\n"
        "- 'checklist': for requests about what steps to take, what documents "
        "are needed, how to apply, action plans\n"
        "- 'document': for requests to explain a letter, form, or official "
        "document the user has received\n\n"
        "Respond with ONLY one word: rag, checklist, or document.\n"
        "No explanation. No punctuation. Just the agent name.",
    ),
    (
        "human",
        "User question: {question}\n\n"
        "Which agent should handle this?",
    ),
])


class SupervisorAgent:
    def __init__(self) -> None:
        self.llm = ChatGroq(
            model=settings.groq_model,
            api_key=settings.groq_key,
            temperature=0,
        )
        self.chain = SUPERVISOR_PROMPT | self.llm

    async def route(self, state: NavigatorState) -> NavigatorState:
        """
        Determine which agent should handle the question.
        Updates state with the routing decision.
        """
        logger.info("supervisor_routing", question=state.question[:80])

        try:
            response = await self.chain.ainvoke({
                "question": state.question,
            })

            agent = response.content.strip().lower()

            if agent not in ("rag", "checklist", "document"):
                logger.warning(
                    "supervisor_invalid_route",
                    raw_response=agent,
                )
                agent = "rag"

            if agent == "checklist":
                state.requires_checklist = True
                state.checklist_goal = state.question

            logger.info("supervisor_routed", agent=agent)
            state.agent_used = agent
            return state

        except Exception as e:
            logger.error("supervisor_failed", error=str(e))
            state.agent_used = "rag"
            return state