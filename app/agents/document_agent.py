"""
Document Agent — explains immigration letters and forms in plain English.

When someone receives a letter from INIS or needs to understand
a form, this agent explains what it means and what action is needed.
"""
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app.core.config import get_settings
from app.core.logging import get_logger
from app.graph.state import NavigatorState
from app.rag.retriever import retriever

logger = get_logger(__name__)
settings = get_settings()

DOCUMENT_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert Irish immigration assistant. "
        "Explain immigration documents, letters, and forms in plain English.\n\n"
        "When explaining a document or answering a document-related question:\n"
        "1. Explain what the document/situation means in simple terms\n"
        "2. State clearly what action the person needs to take\n"
        "3. Give any relevant deadlines or time limits\n"
        "4. Point to the official source for more information\n\n"
        "Use the provided context from official sources. "
        "Be clear, calm, and reassuring — immigration letters can be stressful.",
    ),
    (
        "human",
        "Context from official Irish government sources:\n\n"
        "{context}\n\n"
        "Question or document to explain: {question}\n\n"
        "Please explain in plain English what this means and what action "
        "the person should take.",
    ),
])


class DocumentAgent:
    def __init__(self) -> None:
        self.llm = ChatGroq(
            model=settings.groq_model,
            api_key=settings.groq_key,
            temperature=0.1,
        )
        self.chain = DOCUMENT_PROMPT | self.llm

    async def explain(self, state: NavigatorState) -> NavigatorState:
        """Explain an immigration document or letter."""
        logger.info("document_agent_called", question=state.question[:80])

        chunks = retriever.search(state.question, top_k=5)

        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[Source {i}: {chunk['title']}]\n{chunk['text']}"
            )
        context = "\n\n---\n\n".join(context_parts) if context_parts else (
            "No specific context found. Answer based on general Irish "
            "immigration knowledge."
        )

        try:
            response = await self.chain.ainvoke({
                "context": context,
                "question": state.question,
            })

            state.answer = response.content

            seen_urls: set[str] = set()
            sources = []
            for chunk in chunks:
                if chunk["url"] not in seen_urls:
                    seen_urls.add(chunk["url"])
                    sources.append({
                        "title": chunk["title"],
                        "url": chunk["url"],
                        "category": chunk["category"],
                        "relevance_score": round(chunk["relevance_score"], 3),
                    })
            state.sources = sources

            logger.info(
                "document_explained",
                answer_length=len(state.answer),
            )

        except Exception as e:
            logger.error("document_agent_failed", error=str(e))
            state.answer = (
                "I encountered an error explaining this document. "
                "Please try again or contact Citizens Information directly."
            )

        return state