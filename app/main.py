import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import chat, health
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.db.database import Base, engine
from app.db.models import conversation  # noqa: F401
from app.rag.retriever import retriever

settings = get_settings()
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("app_starting", environment=settings.environment)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("database_tables_ready")

    loaded = retriever.load()
    if loaded:
        logger.info("knowledge_base_ready")
    else:
        logger.warning(
            "knowledge_base_not_found",
            hint="Run: python scripts/ingest.py",
        )

    yield

    await engine.dispose()
    logger.info("app_shutdown")


app = FastAPI(
    title="Irish Immigration Navigator",
    description=(
        "AI-powered Irish immigration assistant using LangGraph "
        "multi-agent system and RAG over official government sources."
    ),
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if not settings.is_production else [],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start = time.perf_counter()
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        method=request.method,
        path=request.url.path,
    )
    response = await call_next(request)
    latency_ms = round((time.perf_counter() - start) * 1000, 2)
    logger.info(
        "http_request",
        status_code=response.status_code,
        latency_ms=latency_ms,
    )
    response.headers["X-Response-Time-Ms"] = str(latency_ms)
    return response


app.include_router(chat.router, prefix="/api/v1")
app.include_router(health.router)