"""
RAG Agent — answers immigration questions grounded in official sources.

Flow:
  1. Retrieve relevant chunks from FAISS
  2. Build a prompt with the chunks as context
  3. Call Groq to generate a grounded answer
  4. Return answer with source citations

The agent never answers from training data alone.
If the retriever finds nothing relevant, it says so.
"""
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app.core.config import get_settings
from app.core.logging import get_logger
from app.rag.retriever import retriever

logger = get_logger(__name__)
settings = get_settings()

RAG_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert Irish immigration assistant. "
        "Answer questions using ONLY the provided context from official Irish "
        "government sources. Be accurate, clear, and helpful.\n\n"
        "Rules:\n"
        "- Only use information from the provided context\n"
        "- If the context does not contain enough information, say so clearly\n"
        "- Always mention which source the information comes from\n"
        "- Use plain English, not legal jargon\n"
        "- If requirements have changed recently, advise the user to verify "
        "directly with the official source\n\n"
        "IMPORTANT: This is for guidance only. Always verify with official "
        "sources before making immigration decisions.",
    ),
    (
        "human",
        "Context from official Irish government sources:\n\n"
        "{context}\n\n"
        "Question: {question}\n\n"
        "Please answer based on the context above.",
    ),
])


class RAGAgent:
    def __init__(self) -> None:
        self.llm = ChatGroq(
            model=settings.groq_model,
            api_key=settings.groq_key,
            temperature=0.1,
        )
        self.chain = RAG_PROMPT | self.llm

    async def answer(self, question: str, top_k: int = 5) -> dict:
        """
        Answer an immigration question grounded in official sources.

        Returns:
            answer: the response text
            sources: list of source documents used
            has_context: whether relevant context was found
        """
        log = logger.bind(question=question[:80])
        log.info("rag_agent_called")

        # Step 1 — Retrieve relevant chunks
        chunks = retriever.search(question, top_k=top_k)

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
            }

        # Step 2 — Build context string with source attribution
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[Source {i}: {chunk['title']}]\n"
                f"URL: {chunk['url']}\n"
                f"{chunk['text']}"
            )
        context = "\n\n---\n\n".join(context_parts)

        # Step 3 — Generate answer
        try:
            response = await self.chain.ainvoke({
                "context": context,
                "question": question,
            })

            # Deduplicate sources
            seen_urls = set()
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
            }