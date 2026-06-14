"""
FAISS retriever.

Converts a question to a vector, finds the most similar
chunks in the index, returns them with their source metadata.

For processing time queries, fetches live from official sources
since processing times change weekly and cached data goes stale.
"""
import pickle
from pathlib import Path

import httpx
import numpy as np
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

INDEX_DIR = Path("data/faiss_index")

PROCESSING_TIME_KEYWORDS = [
    "processing time",
    "processing date",
    "current processing",
    "how long",
    "waiting time",
    "wait time",
    "weeks to process",
    "when will",
    "how long does it take",
    "how long will it take",
    "irp renewal",
    "renew my irp",
    "employment permit processing",
    "visa decision",
]

LIVE_SOURCES = [
    {
        "url": (
            "https://enterprise.gov.ie/en/what-we-do/workplace-and-skills/"
            "employment-permits/current-application-processing-dates/"
        ),
        "title": "Current employment permit processing dates — DETE",
        "category": "processing_times",
        "keywords": [
            "employment permit", "critical skills", "general permit", "work permit",
        ],
    },
    {
        "url": "https://www.irishimmigration.ie/visa-decisions/",
        "title": "Visa decisions — Irish Immigration Service",
        "category": "processing_times",
        "keywords": ["visa", "visa decision", "visa processing"],
    },
    {
        "url": (
            "https://www.irishimmigration.ie/registering-your-immigration-permission/"
            "how-to-renew-your-current-permission/"
            "renewing-your-registration-permission-if-you-live-in-the-republic-of-ireland/"
            "#processing"
        ),
        "title": "IRP renewal processing times — Irish Immigration Service",
        "category": "processing_times",
        "keywords": ["irp", "irp renewal", "registration renewal", "stamp renewal"],
    },
]


def is_processing_time_query(query: str) -> bool:
    """Detect if the question is about processing times."""
    query_lower = query.lower()
    return any(kw in query_lower for kw in PROCESSING_TIME_KEYWORDS)


def detect_processing_source(query: str) -> list[dict]:
    """Return the most relevant live sources for a processing time query."""
    query_lower = query.lower()
    matched = []

    for source in LIVE_SOURCES:
        if any(kw in query_lower for kw in source["keywords"]):
            matched.append(source)

    if not matched:
        matched = LIVE_SOURCES

    return matched


async def fetch_live_processing_times(query: str) -> list[dict]:
    """
    Fetch current processing times live from official sources.

    Different questions need different sources:
    - Employment permits → enterprise.gov.ie
    - Visa decisions → irishimmigration.ie/visa-decisions
    - IRP renewal → irishimmigration.ie IRP renewal page

    Processing times change weekly — static cached data goes stale.
    """
    sources_to_fetch = detect_processing_source(query)
    results = []

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; IrishPathNavigator/1.0; "
            "educational research tool)"
        )
    }

    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        for source in sources_to_fetch:
            try:
                response = await client.get(source["url"], headers=headers)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "lxml")
                for tag in soup(
                    ["nav", "header", "footer", "script", "style", "aside"]
                ):
                    tag.decompose()

                main = (
                    soup.find("main")
                    or soup.find("article")
                    or soup.find(id="content")
                    or soup.find("body")
                )
                text = main.get_text(separator=" ", strip=True) if main else ""
                lines = [line.strip() for line in text.splitlines() if line.strip()]
                clean_text = " ".join(lines)

                if clean_text:
                    results.append({
                        "url": source["url"],
                        "title": source["title"],
                        "category": source["category"],
                        "text": clean_text[:4000],
                        "relevance_score": 0.95,
                    })
                    logger.info(
                        "live_source_fetched",
                        url=source["url"],
                        text_length=len(clean_text),
                    )

            except Exception as e:
                logger.warning(
                    "live_fetch_failed",
                    url=source["url"],
                    error=str(e),
                )

    return results


class ImmigrationRetriever:
    def __init__(self) -> None:
        self._index = None
        self._metadata: list[dict] = []
        self._model: SentenceTransformer | None = None

    def load(self) -> bool:
        """Load index from disk. Returns True if successful."""
        try:
            import faiss

            index_path = INDEX_DIR / "index.faiss"
            metadata_path = INDEX_DIR / "metadata.pkl"

            if not index_path.exists() or not metadata_path.exists():
                logger.warning("index_not_found", path=str(INDEX_DIR))
                return False

            self._index = faiss.read_index(str(index_path))
            with open(metadata_path, "rb") as f:
                self._metadata = pickle.load(f)

            self._model = SentenceTransformer(settings.embedding_model)

            logger.info(
                "index_loaded",
                total_chunks=len(self._metadata),
            )
            return True

        except Exception as e:
            logger.error("index_load_failed", error=str(e))
            return False

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Search the FAISS index for chunks relevant to the query.
        Returns top_k chunks with source metadata and relevance scores.
        """
        if self._index is None or self._model is None:
            logger.warning("retriever_not_loaded")
            return []

        try:
            query_embedding = self._model.encode([query])
            query_embedding = np.array(query_embedding, dtype="float32")

            distances, indices = self._index.search(query_embedding, top_k)

            results = []
            for idx, distance in zip(indices[0], distances[0], strict=False):
                if idx == -1:
                    continue
                chunk = self._metadata[idx].copy()
                chunk["relevance_score"] = float(1 / (1 + distance))
                results.append(chunk)

            logger.info(
                "retrieval_complete",
                query=query[:50],
                num_results=len(results),
            )
            return results

        except Exception as e:
            logger.error("retrieval_failed", error=str(e))
            return []

    async def search_async(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Async search with live fetch for processing time queries.

        Processing time questions get live official data first,
        then static index results for supporting context.
        All other questions use the static FAISS index only.
        """
        if is_processing_time_query(query):
            logger.info(
                "processing_time_query_detected",
                query=query[:60],
            )
            live_results = await fetch_live_processing_times(query)
            if live_results:
                static_results = self.search(query, top_k=3)
                return live_results + static_results

        return self.search(query, top_k=top_k)


retriever = ImmigrationRetriever()