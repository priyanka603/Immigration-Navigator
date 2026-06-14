import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agents.rag_agent import RAGAgent
from app.core.logging import configure_logging
from app.rag.retriever import retriever


async def main():
    configure_logging()
    retriever.load()

    agent = RAGAgent()
    result = await agent.answer(
        "How do I apply for a Critical Skills Employment Permit in Ireland?"
    )

    print("\nANSWER:")
    print(result["answer"])

    print("\nSOURCES:")
    for s in result["sources"]:
        print(f"  - {s['title']}")
        print(f"    {s['url']}")
        print(f"    relevance: {s['relevance_score']}")


if __name__ == "__main__":
    asyncio.run(main())