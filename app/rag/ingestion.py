"""
RAG ingestion pipeline — reads from locally saved HTML files.

Flow:
  1. Read each HTML file from data/raw_html/
  2. Parse and clean the HTML
  3. Split into overlapping chunks
  4. Embed each chunk using sentence-transformers
  5. Store in FAISS index

Run this once to build the knowledge base:
  python scripts/ingest.py
"""
import pickle
from pathlib import Path

from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer

from app.core.config import get_settings
from app.core.logging import get_logger
from app.rag.sources import IMMIGRATION_SOURCES, RAW_HTML_DIR

logger = get_logger(__name__)
settings = get_settings()

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
INDEX_DIR = Path("data/faiss_index")


def parse_html_file(filepath: Path) -> str:
    """Parse a saved HTML file and return cleaned text."""
    try:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            html = f.read()

        soup = BeautifulSoup(html, "lxml")

        # Remove noise elements
        for tag in soup(["nav", "header", "footer", "script",
                         "style", "aside", "noscript"]):
            tag.decompose()

        # Prefer main content area
        main = (
            soup.find("main")
            or soup.find("article")
            or soup.find(id="content")
            or soup.find(class_="content")
            or soup.find("body")
        )
        if main is None:
            return ""

        text = main.get_text(separator=" ", strip=True)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return " ".join(lines)

    except Exception as e:
        logger.warning("parse_failed", filepath=str(filepath), error=str(e))
        return ""


def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """
    Split text into overlapping chunks.

    Overlap ensures context is not lost at chunk boundaries.
    A sentence spanning two chunks appears in both.
    """
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i : i + chunk_size])
        if chunk:
            chunks.append(chunk)
        i += chunk_size - overlap
    return chunks


def build_index() -> None:
    """
    Build the FAISS index from all local HTML sources.
    Saves index and metadata to data/faiss_index/.
    """
    try:
        import faiss
        import numpy as np
    except ImportError:
        logger.error("faiss_not_installed")
        return

    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("ingestion_started", num_sources=len(IMMIGRATION_SOURCES))

    model = SentenceTransformer(settings.embedding_model)
    # sentence_transformers provides get_sentence_embedding_dimension()
    # older/other APIs might use get_embedding_dimension(); handle both
    embedding_dim = None
    if hasattr(model, "get_sentence_embedding_dimension"):
        embedding_dim = model.get_sentence_embedding_dimension()
    elif hasattr(model, "get_embedding_dimension"):
        embedding_dim = model.get_embedding_dimension()

    if embedding_dim is None:
        logger.error("unknown_embedding_dimension")
        return

    embedding_dim = int(embedding_dim)

    index = faiss.IndexFlatL2(embedding_dim)
    metadata = []
    skipped = 0

    for source in IMMIGRATION_SOURCES:
        filepath = RAW_HTML_DIR / source["filename"]

        if not filepath.exists():
            logger.warning(
                "file_not_found",
                filename=source["filename"],
                title=source["title"],
            )
            skipped += 1
            continue

        logger.info(
            "processing_source",
            filename=source["filename"],
            title=source["title"],
        )

        text = parse_html_file(filepath)
        if not text:
            logger.warning("empty_file", filename=source["filename"])
            skipped += 1
            continue

        chunks = chunk_text(text)
        logger.info(
            "source_chunked",
            filename=source["filename"],
            num_chunks=len(chunks),
            text_length=len(text),
        )

        embeddings = model.encode(chunks, show_progress_bar=False)
        embeddings = np.array(embeddings, dtype="float32")

        index.add(embeddings)

        for chunk in chunks:
            metadata.append({
                "url": source["url"],
                "title": source["title"],
                "category": source["category"],
                "text": chunk,
            })

    faiss.write_index(index, str(INDEX_DIR / "index.faiss"))

    with open(INDEX_DIR / "metadata.pkl", "wb") as f:
        pickle.dump(metadata, f)

    logger.info(
        "ingestion_complete",
        total_chunks=len(metadata),
        index_size=index.ntotal,
        sources_processed=len(IMMIGRATION_SOURCES) - skipped,
        sources_skipped=skipped,
    )


if __name__ == "__main__":
    from app.core.logging import configure_logging
    configure_logging()
    build_index()