"""
User Behaviour Tracker
Writes user interaction events to Firestore for personalised recommendations.

Tracked events:
  - search queries
  - movie detail page clicks
  - ratings submitted
  - favorites added/removed

Firestore schema per user (users/{uid}):
  search_history : [{query, timestamp}]   (capped at 100 entries)
  watch_history  : [{movie_id, title, timestamp}]
  ratings        : {movie_id_str: stars}
  liked_genres   : [genre_strings]        (derived from rated dramas)
  favorites      : [movie_id_ints]
"""
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

_ANON = "anonymous"


def _now() -> str:
    return datetime.utcnow().isoformat()


def _db():
    from app.services.firebase_service import get_firestore_client
    return get_firestore_client()


def _user_ref(user_id: str):
    return _db().collection("users").document(user_id)


# ── Public tracking functions ─────────────────────────────────────────────────

def track_search(user_id: Optional[str], query: str):
    """Append a search query to the user's search_history."""
    uid = user_id or _ANON
    if not query or not query.strip():
        return
    try:
        from google.cloud.firestore_v1 import ArrayUnion
        _user_ref(uid).set(
            {"search_history": ArrayUnion([{"query": query.strip(), "timestamp": _now()}])},
            merge=True,
        )
    except Exception as e:
        logger.debug(f"track_search failed ({uid}): {e}")


def track_click(user_id: Optional[str], movie_id: int, title: str = ""):
    """Append a clicked drama to the user's watch_history."""
    uid = user_id or _ANON
    try:
        from google.cloud.firestore_v1 import ArrayUnion
        _user_ref(uid).set(
            {"watch_history": ArrayUnion([{"movie_id": movie_id, "title": title, "timestamp": _now()}])},
            merge=True,
        )
    except Exception as e:
        logger.debug(f"track_click failed ({uid}): {e}")


def track_rating(user_id: Optional[str], movie_id: int, stars: int, genres: str = ""):
    """
    Store the user's rating and update liked_genres accordingly.
    Ratings >= 4 stars contribute to liked_genres.
    """
    uid = user_id or _ANON
    if not 1 <= stars <= 5:
        return
    try:
        update: dict = {f"ratings.{movie_id}": stars}

        if stars >= 4 and genres:
            from google.cloud.firestore_v1 import ArrayUnion
            genre_list = [g.strip() for g in genres.split("|") if g.strip()]
            update["liked_genres"] = ArrayUnion(genre_list)

        _user_ref(uid).set(update, merge=True)
    except Exception as e:
        logger.debug(f"track_rating failed ({uid}): {e}")


def track_favorite(user_id: Optional[str], movie_id: int, added: bool = True):
    """Add or remove a movie from the user's favorites list."""
    uid = user_id or _ANON
    try:
        from google.cloud.firestore_v1 import ArrayUnion, ArrayRemove
        op = ArrayUnion([movie_id]) if added else ArrayRemove([movie_id])
        _user_ref(uid).set({"favorites": op}, merge=True)
    except Exception as e:
        logger.debug(f"track_favorite failed ({uid}): {e}")


def get_user_profile(user_id: str) -> dict:
    """Fetch a user's full behaviour profile from Firestore."""
    try:
        snap = _user_ref(user_id).get()
        return snap.to_dict() or {}
    except Exception as e:
        logger.debug(f"get_user_profile failed ({user_id}): {e}")
        return {}


def get_liked_genres(user_id: str) -> list[str]:
    """Return the list of genres the user has positively engaged with."""
    profile = get_user_profile(user_id)
    return profile.get("liked_genres", [])
