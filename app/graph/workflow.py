"""
LangGraph workflow — the multi-agent orchestration graph.

Graph structure:
  START → supervisor → [rag | checklist | document] → END

The supervisor reads the question and routes to the right agent.
Each agent updates the shared state with its answer.
LangGraph manages the state transitions between nodes.

Why LangGraph over a simple if/else router:
  - State is managed and typed
  - Easy to add new agents as new nodes
  - Conditional edges make routing explicit and testable
  - Built-in support for streaming and async
"""
from langgraph.graph import END, START, StateGraph

from app.agents.checklist_agent import ChecklistAgent
from app.agents.document_agent import DocumentAgent
from app.agents.rag_agent import RAGAgent
from app.agents.supervisor import SupervisorAgent
from app.core.logging import get_logger
from app.graph.state import NavigatorState

logger = get_logger(__name__)


def route_after_supervisor(state: NavigatorState) -> str:
    """
    Conditional edge — decides which node to go to after the supervisor.
    Returns the name of the next node.
    """
    agent = state.agent_used
    logger.info("routing_to_agent", agent=agent)

    if agent == "checklist":
        return "checklist_agent"
    if agent == "document":
        return "document_agent"
    return "rag_agent"


def build_graph() -> StateGraph:
    """
    Build and compile the LangGraph workflow.

    Nodes: supervisor, rag_agent, checklist_agent, document_agent
    Edges: START → supervisor → [conditional] → agent → END
    """
    supervisor = SupervisorAgent()
    rag_agent = RAGAgent()
    checklist_agent = ChecklistAgent()
    document_agent = DocumentAgent()

    graph = StateGraph(NavigatorState)

    # ── Add nodes ─────────────────────────────────────────
    graph.add_node("supervisor", supervisor.route)
    graph.add_node("rag_agent", rag_agent.answer_from_state)
    graph.add_node("checklist_agent", checklist_agent.generate)
    graph.add_node("document_agent", document_agent.explain)

    # ── Add edges ─────────────────────────────────────────
    graph.add_edge(START, "supervisor")

    graph.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {
            "rag_agent": "rag_agent",
            "checklist_agent": "checklist_agent",
            "document_agent": "document_agent",
        },
    )

    graph.add_edge("rag_agent", END)
    graph.add_edge("checklist_agent", END)
    graph.add_edge("document_agent", END)

    return graph.compile()


navigator_graph = build_graph()