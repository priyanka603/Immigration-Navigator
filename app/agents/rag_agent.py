"""
RAG Agent — answers immigration questions grounded in official sources.
"""
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app.core.config import get_settings
from app.core.logging import get_logger
from app.graph.state import NavigatorState
from app.rag.retriever import retriever

logger = get_logger(__name__)
settings = get_settings()

RAG_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert Irish immigration assistant. "
        "Answer questions using ONLY the provided context from official Irish "
        "government sources.\n\n"
        "FORMATTING RULES — always follow these:\n"
        "- Write in clear, plain English — no legal jargon\n"
        "- Use short paragraphs, never one long block of text\n"
        "- Use bullet points for lists of requirements, documents, or steps\n"
        "- Use **bold** for important terms, deadlines, amounts, and key facts\n"
        "- For processing times, present as a clean table or clearly spaced list\n"
        "- Never include source URLs inline — sources are shown separately\n"
        "- Never say 'According to Source 1' or 'According to Source 2' — "
        "just answer directly\n"
        "- End with a one-line note if the user should verify directly\n\n"
        "CONTENT RULES:\n"
        "- Only use information from the provided context\n"
        "- If the user has provided their nationality and current visa status, "
        "use that information to give a specific, personalised answer rather "
        "than a generic one covering all cases\n"
        "- If context does not contain enough information, say so clearly\n"
        "- For questions about CURRENT processing times: always direct the user to "
        "check the official page as times change weekly\n\n"
        "IMPORTANT: This is for guidance only. Always verify with official "
        "sources before making immigration decisions.",
    ),
    (
        "human",
        "User's nationality: {nationality}\n"
        "User's current visa/status: {current_visa}\n\n"
        "Context from official Irish government sources:\n\n"
        "{context}\n\n"
        "Question: {question}\n\n"
        "Answer clearly and concisely using the formatting rules above. "
        "If nationality or visa status is provided above (not 'Not specified'), "
        "tailor the answer specifically to that situation.",
    ),
])


class RAGAgent:
    def __init__(self) -> None:
        self.llm = ChatGroq(
            model=settings.groq_model,
            api_key=settings.groq_key, # type: ignore
            temperature=0.1,
        )
        self.chain = RAG_PROMPT | self.llm

    async def answer_from_state(self, state: NavigatorState) -> NavigatorState:
        """Called by LangGraph — reads question from state, writes answer to state."""
        result = await self.answer(
            state.question,
            nationality=state.nationality,
            current_visa=state.current_visa,
        )
        state.answer = result["answer"]
        state.sources = result["sources"]
        state.retrieved_chunks = result.get("chunks", [])
        return state

    async def answer(
        self,
        question: str,
        top_k: int = 5,
        nationality: str | None = None,
        current_visa: str | None = None,
    ) -> dict:
        """Direct call — used for testing outside the graph."""
        log = logger.bind(question=question[:80])
        log.info("rag_agent_called")

        chunks = await retriever.search_async(question, top_k=top_k)

        if not chunks:
            log.warning("no_context_found")
            return {
                "answer": (
                    "I could not find relevant information in my knowledge base "
                    "for that question. Please check directly with the Irish "
                    "Immigration Service at irishimmigration.ie or Citizens "
                    "Information at citizensinformation.ie."
                ),
                "sources": [],
                "has_context": False,
                "chunks": [],
            }

        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[Source {i}: {chunk['title']}]\n"
                f"URL: {chunk['url']}\n"
                f"{chunk['text']}"
            )
        context = "\n\n---\n\n".join(context_parts)

        try:
            response = await self.chain.ainvoke({
                "context": context,
                "question": question,
                "nationality": nationality or "Not specified",
                "current_visa": current_visa or "Not specified",
            })

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

            log.info(
                "rag_answer_generated",
                num_sources=len(sources),
                answer_length=len(response.content),
            )

            return {
                "answer": response.content,
                "sources": sources,
                "has_context": True,
                "chunks": chunks,
            }

        except Exception as e:
            log.error("rag_agent_failed", error=str(e))
            return {
                "answer": (
                    "I encountered an error generating a response. "
                    "Please try again or visit irishimmigration.ie directly."
                ),
                "sources": [],
                "has_context": False,
                "chunks": [],
            }