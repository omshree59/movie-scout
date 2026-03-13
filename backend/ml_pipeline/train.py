"""
ML Training Pipeline
Builds a FAISS vector index from the current drama corpus stored in Firestore
(or falls back to the static KDRAMA_MOCKS if Firestore is empty).

Run manually:   python ml_pipeline/train.py
Called by:      schedulers/scheduler.py every 24 hours
"""
import os
import sys
import pickle
import logging
import numpy as np

# Allow imports from the backend root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

MODELS_DIR = os.path.join(os.path.dirname(__file__), "saved_models")
os.makedirs(MODELS_DIR, exist_ok=True)

FAISS_INDEX_PATH = os.path.join(MODELS_DIR, "faiss_index.bin")
META_PATH        = os.path.join(MODELS_DIR, "drama_meta.pkl")


def load_corpus() -> list[dict]:
    """
    Load drama corpus:
    1. Try Firestore `dramas` collection (populated by tmdb_ingestion)
    2. Fall back to KDRAMA_MOCKS from recommendation.py
    """
    try:
        from app.services.firebase_service import get_firestore_client
        db = get_firestore_client()
        docs = db.collection("dramas").stream()
        corpus = [doc.to_dict() for doc in docs]
        if corpus:
            logger.info(f"Loaded {len(corpus)} dramas from Firestore.")
            return corpus
    except Exception as e:
        logger.warning(f"Firestore unavailable: {e}. Falling back to KDRAMA_MOCKS.")

    # Static fallback
    from app.services.recommendation import KDRAMA_MOCKS
    corpus = [
        {
            "tmdb_id": d["id"],
            "title": d["title"],
            "description": d.get("desc", ""),
            "genres": d.get("genres", ""),
            "cast": d.get("cast", []),
        }
        for d in KDRAMA_MOCKS
    ]
    logger.info(f"Loaded {len(corpus)} dramas from KDRAMA_MOCKS fallback.")
    return corpus


def build_text_corpus(dramas: list[dict]) -> list[str]:
    """Combine title + genres + description into a single string per drama for embedding."""
    texts = []
    for d in dramas:
        title  = d.get("title", "")
        genres = d.get("genres", "").replace("|", " ")
        desc   = d.get("description", d.get("desc", ""))
        cast   = " ".join(d.get("cast", []))
        texts.append(f"{title} {genres} {desc} {cast}".strip())
    return texts


def generate_embeddings(texts: list[str]) -> np.ndarray:
    """Generate sentence embeddings using all-MiniLM-L6-v2 (fast + accurate)."""
    logger.info("Loading sentence-transformers model…")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")
    logger.info(f"Encoding {len(texts)} drama texts…")
    embeddings = model.encode(texts, batch_size=32, show_progress_bar=True, normalize_embeddings=True)
    return embeddings.astype(np.float32)


def build_faiss_index(embeddings: np.ndarray):
    """Build a FAISS inner-product index (cosine similarity with normalised vectors)."""
    import faiss
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    logger.info(f"FAISS index built: {index.ntotal} vectors, dim={dim}.")
    return index


def save_artifacts(index, meta: list[dict]):
    """Save FAISS index + metadata pickle to disk."""
    import faiss
    faiss.write_index(index, FAISS_INDEX_PATH)
    with open(META_PATH, "wb") as f:
        pickle.dump(meta, f)
    logger.info(f"Saved FAISS index → {FAISS_INDEX_PATH}")
    logger.info(f"Saved drama meta  → {META_PATH}")


def run_training():
    """Full training pipeline: load → embed → index → save."""
    corpus = load_corpus()
    if not corpus:
        logger.error("No drama data available — aborting training.")
        return

    texts  = build_text_corpus(corpus)
    embeds = generate_embeddings(texts)
    index  = build_faiss_index(embeds)
    save_artifacts(index, corpus)
    logger.info("Training pipeline complete ✓")


if __name__ == "__main__":
    run_training()
