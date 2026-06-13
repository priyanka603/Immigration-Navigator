"""
Run this script to build the FAISS knowledge base.

Usage:
    python scripts/ingest.py

This fetches all government sources, chunks them,
embeds them, and saves the FAISS index to data/faiss_index/.

Run this once before starting the app, then periodically
to keep the knowledge base fresh.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.logging import configure_logging
from app.rag.ingestion import build_index

if __name__ == "__main__":
    configure_logging()
    build_index()