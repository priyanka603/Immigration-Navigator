"""
FAISS retriever.

Converts a question to a vector, finds the most similar
chunks in the index, returns them with their source metadata.
"""
import pickle
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

INDEX_DIR = Path("data/faiss_index")


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
        Search the index for chunks relevant to the query.

        Returns top_k chunks with their source metadata.
        Each result includes the text, source URL, title, and category.
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


retriever = ImmigrationRetriever()