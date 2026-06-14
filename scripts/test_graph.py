"""Test the full LangGraph multi-agent workflow."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.logging import configure_logging
from app.rag.retriever import retriever
from app.graph.workflow import navigator_graph
from app.graph.state import NavigatorState


async def test(question: str, nationality: str | None = None) -> None:
    print(f"\n{'='*60}")
    print(f"QUESTION: {question}")
    print("="*60)

    initial_state = NavigatorState(
        question=question,
        nationality=nationality,
    )

    result = await navigator_graph.ainvoke(initial_state)

    print(f"AGENT USED: {result['agent_used']}")
    print(f"\nANSWER:\n{result['answer']}")

    if result.get("checklist_steps"):
        print(f"\nCHECKLIST STEPS: {len(result['checklist_steps'])}")
        for step in result["checklist_steps"]:
            print(f"  Step {step.get('step_number')}: {step.get('title')}")

    print(f"\nSOURCES:")
    for s in result.get("sources", []):
        print(f"  - {s['title']} (score: {s['relevance_score']})")


async def main() -> None:
    configure_logging()
    retriever.load()

    # Test 1 — factual question → should route to RAG agent
    await test(
        "Can I work while on a student visa in Ireland?",
        nationality="Indian",
    )

    # Test 2 — checklist request → should route to checklist agent
    await test(
        "What steps do I need to take to apply for a Critical Skills "
        "Employment Permit?",
        nationality="Indian",
    )

    # Test 3 — document explanation → should route to document agent
    await test(
        "I received a letter saying my Stamp 2 visa is expiring in 30 days. "
        "What does this mean and what should I do?",
    )


if __name__ == "__main__":
    asyncio.run(main())