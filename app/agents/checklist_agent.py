"""
Checklist Agent — generates personalised step-by-step immigration plans.

Takes the user's goal, nationality, and current status,
retrieves relevant documents from the knowledge base,
and generates a structured action plan.

Output is structured JSON so it can be rendered
as a proper checklist in the frontend — not free-form text.
"""
import json

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app.core.config import get_settings
from app.core.logging import get_logger
from app.graph.state import NavigatorState
from app.rag.retriever import retriever

logger = get_logger(__name__)
settings = get_settings()

CHECKLIST_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert Irish immigration assistant. "
        "Generate a detailed step-by-step checklist based on the official "
        "context provided.\n\n"
        "Return a JSON object with this exact structure:\n"
        "{{\n"
        '  "steps": [\n'
        "    {{\n"
        '      "step_number": 1,\n'
        '      "title": "Short step title",\n'
        '      "description": "Detailed description of what to do",\n'
        '      "documents_required": ["document 1", "document 2"],\n'
        '      "estimated_time": "2-4 weeks",\n'
        '      "fee": "€1,000",\n'
        '      "official_link": "https://..."\n'
        "    }}\n"
        "  ],\n"
        '  "total_estimated_time": "3-6 months",\n'
        '  "total_estimated_cost": "€1,500",\n'
        '  "important_notes": ["note 1", "note 2"]\n'
        "}}\n\n"
        "Use ONLY information from the provided context. "
        "If a field is unknown, use null. "
        "Return ONLY valid JSON, no markdown, no explanation.",
    ),
    (
        "human",
        "Context from official Irish government sources:\n\n"
        "{context}\n\n"
        "Generate a checklist for:\n"
        "Goal: {goal}\n"
        "Nationality: {nationality}\n"
        "Current status: {current_status}\n\n"
        "Return JSON only.",
    ),
])


class ChecklistAgent:
    def __init__(self) -> None:
        self.llm = ChatGroq(
            model=settings.groq_model,
            api_key=settings.groq_key,
            temperature=0.1,
        )
        self.chain = CHECKLIST_PROMPT | self.llm

    async def generate(self, state: NavigatorState) -> NavigatorState:
        """Generate a personalised checklist based on the user's goal."""
        goal = state.checklist_goal or state.question
        nationality = state.nationality or "Non-EEA national"
        current_status = state.current_visa or "Not specified"

        logger.info(
            "checklist_agent_called",
            goal=goal[:80],
            nationality=nationality,
        )

        chunks = await retriever.search_async(goal, top_k=6)

        if not chunks:
            state.answer = (
                "I could not find enough information to generate a checklist "
                "for your request. Please visit irishimmigration.ie directly."
            )
            state.sources = []
            return state

        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[Source {i}: {chunk['title']}]\n{chunk['text']}"
            )
        context = "\n\n---\n\n".join(context_parts)

        try:
            response = await self.chain.ainvoke({
                "context": context,
                "goal": goal,
                "nationality": nationality,
                "current_status": current_status,
            })

            content = response.content
            if isinstance(content, list):
                parts = []
                for item in content:
                    if isinstance(item, str):
                        parts.append(item)
                    elif isinstance(item, dict):
                        parts.append(
                            item.get("content")
                            or item.get("text")
                            or json.dumps(item)
                        )
                    else:
                        parts.append(str(item))
                raw = "\n".join(parts).strip()
            else:
                raw = str(content).strip()

            if raw.startswith("```"):
                parts = raw.split("```")
                if len(parts) >= 2:
                    raw = parts[1]
                    if raw.startswith("json"):
                        raw = raw[4:]
                    raw = raw.strip()

            checklist_steps: list[dict] = []
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, dict):
                    checklist_steps = parsed.get("steps", []) or []
                elif isinstance(parsed, list):
                    checklist_steps = parsed
                else:
                    checklist_steps = []
            except json.JSONDecodeError:
                logger.warning(
                    "checklist_response_json_parse_failed",
                    raw=raw[:500],
                )
                checklist_steps = []

            if not isinstance(checklist_steps, list):
                checklist_steps = []

            state.checklist_steps = checklist_steps
            state.answer = raw

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
                "checklist_generated",
                num_steps=len(state.checklist_steps),
            )

        except Exception as e:
            logger.error("checklist_agent_failed", error=str(e))
            state.answer = (
                "I encountered an error generating the checklist. "
                "Please try again or visit irishimmigration.ie directly."
            )
            state.checklist_steps = []
            state.sources = []

        return state