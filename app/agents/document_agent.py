"""
Document Agent — explains immigration letters and forms in plain English.

When someone receives a letter from INIS or needs to understand
a form, this agent explains what it means and what action is needed.
"""
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app.core.config import get_settings
from pydantic import SecretStr
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
        "FORMATTING RULES:\n"
        "- Start with a short summary of what the document/situation means\n"
        "- Use **bold** for important actions, deadlines, and key terms\n"
        "- Use bullet points for action steps\n"
        "- Never include source URLs inline\n"
        "- Never say 'According to Source X'\n\n"
        "When explaining a document:\n"
        "1. What it means — in one or two plain English sentences\n"
        "2. What action the person needs to take — as bullet points\n"
        "3. Any deadlines or time limits — in bold\n"
        "4. Where to go for more information — official site name only, no URL",
    ),
    (
        "human",
        "Context from official Irish government sources:\n\n"
        "{context}\n\n"
        "Question or document to explain: {question}\n\n"
        "Explain clearly using the formatting rules above.",
    ),
])


class DocumentAgent:
    def __init__(self) -> None:
        self.llm = ChatGroq(
            model=settings.groq_model,
            api_key=SecretStr(settings.groq_key) if settings.groq_key is not None else None,
            temperature=0.1,
        )
        self.chain = DOCUMENT_PROMPT | self.llm

    async def explain(self, state: NavigatorState) -> NavigatorState:
        """Explain an immigration document or letter."""
        logger.info("document_agent_called", question=state.question[:80])

        chunks = await retriever.search_async(state.question, top_k=5)

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

            state.answer = (
                response.content
                if isinstance(response.content, str)
                else str(response.content)
            )

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