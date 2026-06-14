import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, status  # type: ignore[import]
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.database import get_db
from app.db.models.conversation import Conversation, Session
from app.graph.state import NavigatorState
from app.graph.workflow import navigator_graph
from app.schemas.chat import (
    AgentType,
    ChatRequest,
    ChatResponse,
    ChecklistRequest,
    ChecklistResponse,
    ChecklistStep,
    Source,
)

router = APIRouter(prefix="/chat", tags=["chat"])
logger = get_logger(__name__)


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask an immigration question",
)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    session_id = request.session_id or str(uuid.uuid4())

    log = logger.bind(
        session_id=session_id,
        message=request.message[:80],
    )
    log.info("chat_request_received")

    await _upsert_session(db, session_id, request)

    initial_state = NavigatorState(
        question=request.message,
        nationality=request.nationality,
        current_visa=request.current_visa,
    )

    try:
        result = await navigator_graph.ainvoke(initial_state)
    except Exception as e:
        logger.error("graph_failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process your question. Please try again.",
        ) from e

    answer = result.get("answer", "")
    agent_used = result.get("agent_used", "rag")
    raw_sources = result.get("sources", [])

    sources = [
        Source(
            title=s["title"],
            url=s["url"],
            category=s["category"],
            relevance_score=s["relevance_score"],
        )
        for s in raw_sources
    ]

    await _save_message(db, session_id, "user", request.message)
    await _save_message(
        db, session_id, "assistant", answer,
        agent_used=agent_used,
        sources=raw_sources,
    )

    log.info(
        "chat_response_sent",
        agent_used=agent_used,
        num_sources=len(sources),
    )

    return ChatResponse(
        answer=answer,
        agent_used=AgentType(agent_used),
        sources=sources,
        session_id=session_id,
        has_context=len(sources) > 0,
    )


@router.post(
    "/checklist",
    response_model=ChecklistResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate a personalised immigration checklist",
)
async def generate_checklist(
    request: ChecklistRequest,
    db: AsyncSession = Depends(get_db),
) -> ChecklistResponse:
    logger.info(
        "checklist_request",
        goal=request.goal[:80],
        nationality=request.nationality,
    )

    initial_state = NavigatorState(
        question=request.goal,
        nationality=request.nationality,
        current_visa=request.current_status,
        requires_checklist=True,
        checklist_goal=request.goal,
    )

    try:
        result = await navigator_graph.ainvoke(initial_state)
    except Exception as e:
        logger.error("checklist_graph_failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate checklist. Please try again.",
        ) from e

    raw_steps = result.get("checklist_steps", [])
    steps = [
    ChecklistStep(
        step_number=s.get("step_number", i + 1),
        title=s.get("title", ""),
        description=s.get("description", ""),
        documents_required=s.get("documents_required") or [],
        estimated_time=s.get("estimated_time"),
        fee=s.get("fee"),
        official_link=s.get("official_link"),
    )
    for i, s in enumerate(raw_steps)
    ]

    raw_sources = result.get("sources", [])
    sources = [
        Source(
            title=s["title"],
            url=s["url"],
            category=s["category"],
            relevance_score=s["relevance_score"],
        )
        for s in raw_sources
    ]

    answer = result.get("answer", "")
    notes = []
    if "Important notes:" in answer:
        notes_part = answer.split("Important notes:")[-1]
        notes = [n.strip() for n in notes_part.split(";") if n.strip()]

    return ChecklistResponse(
        goal=request.goal,
        nationality=request.nationality,
        current_status=request.current_status,
        steps=steps,
        important_notes=notes,
        sources=sources,
    )


@router.get(
    "/history/{session_id}",
    summary="Get conversation history for a session",
)
async def get_history(
    session_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await db.execute(
        select(Conversation)
        .where(Conversation.session_id == session_id)
        .order_by(Conversation.created_at)
    )
    messages = result.scalars().all()

    if not messages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No conversation found for session {session_id}",
        )

    return {
        "session_id": session_id,
        "messages": [
            {
                "role": m.role,
                "content": m.content,
                "agent_used": m.agent_used,
                "created_at": m.created_at.isoformat(),
            }
            for m in messages
        ],
        "total_messages": len(messages),
    }


async def _upsert_session(
    db: AsyncSession,
    session_id: str,
    request: ChatRequest,
) -> None:
    result = await db.execute(
        select(Session).where(Session.id == session_id)
    )
    existing = result.scalar_one_or_none()
    if existing is None:
        session = Session(
            id=session_id,
            nationality=request.nationality,
            current_visa=request.current_visa,
        )
        db.add(session)
        await db.flush()


async def _save_message(
    db: AsyncSession,
    session_id: str,
    role: str,
    content: str,
    agent_used: str | None = None,
    sources: list | None = None,
) -> None:
    message = Conversation(
        session_id=session_id,
        role=role,
        content=content,
        agent_used=agent_used,
        sources_json=json.dumps(sources) if sources else None,
    )
    db.add(message)
    await db.flush()