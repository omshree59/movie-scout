"""
Trend Scorer
Calculates composite trend scores for K-dramas using TMDB popularity data.
Stores ranked trending list to Firestore `trending_dramas` collection.
"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def compute_trend_scores(dramas: list[dict]) -> list[dict]:
    """
    Compute a normalised trend score for each drama.

    Score formula (all normalised 0-1):
      trend_score = 0.7 * tmdb_popularity_norm
                  + 0.2 * vote_score_norm
                  + 0.1 * recency_bonus

    Returns dramas list sorted by trend_score descending, with score added.
    """
    if not dramas:
        return []

    # Normalise TMDB popularity
    pops = [d.get("tmdb_popularity", 0) for d in dramas]
    max_pop = max(pops) or 1

    # Normalise vote average (0-10 scale → 0-1)
    votes = [d.get("vote_average", 0) for d in dramas]
    max_vote = max(votes) or 1

    current_year = datetime.utcnow().year

    for drama in dramas:
        pop_norm  = drama.get("tmdb_popularity", 0) / max_pop
        vote_norm = drama.get("vote_average", 0) / 10.0

        year = drama.get("year") or (current_year - 5)
        recency = max(0, 1 - (current_year - year) / 10)  # dramas >10 yrs old → 0

        drama["trend_score"] = round(
            0.7 * pop_norm + 0.2 * vote_norm + 0.1 * recency,
            4,
        )

    return sorted(dramas, key=lambda d: d["trend_score"], reverse=True)


def update_trending_firestore(ranked_dramas: list[dict], limit: int = 20):
    """
    Write top `limit` dramas to Firestore `trending_dramas` collection.
    Each document uses rank as its ID (rank_01, rank_02 …) for easy ordered fetching.
    Also writes a `trending_meta` document with the refresh timestamp.
    """
    try:
        from app.services.firebase_service import get_firestore_client
        db = get_firestore_client()
    except Exception as e:
        logger.error(f"Firestore unavailable: {e}")
        return

    top = ranked_dramas[:limit]
    batch = db.batch()

    for i, drama in enumerate(top, start=1):
        doc_id = f"rank_{i:02d}"
        ref = db.collection("trending_dramas").document(doc_id)
        batch.set(ref, {**drama, "rank": i}, merge=False)

    # Meta document tracks last update time
    meta_ref = db.collection("trending_dramas").document("_meta")
    batch.set(meta_ref, {
        "updated_at": datetime.utcnow().isoformat(),
        "count": len(top),
    })

    batch.commit()
    logger.info(f"Updated trending_dramas with {len(top)} entries.")


def run_trend_scoring(dramas: list[dict], limit: int = 20) -> list[dict]:
    """Full trend scoring run: score dramas + write to Firestore."""
    ranked = compute_trend_scores(dramas)
    update_trending_firestore(ranked, limit)
    return ranked
