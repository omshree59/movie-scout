"""
TMDB K-Drama Ingestion
Fetches trending and popular Korean dramas from TMDB API and stores them in Firestore.
"""
import os
import requests
import logging
from typing import Optional
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
TMDB_GENRE_MAP = {
    10759: "Action & Adventure", 16: "Animation", 35: "Comedy",
    80: "Crime", 99: "Documentary", 18: "Drama",
    10751: "Family", 10762: "Kids", 9648: "Mystery",
    10763: "News", 10764: "Reality", 10765: "Sci-Fi & Fantasy",
    10766: "Soap", 10767: "Talk", 10768: "War & Politics", 37: "Western",
    10749: "Romance",
}


def _get_api_key() -> Optional[str]:
    from app.core.config import settings
    key = getattr(settings, "TMDB_API_KEY", None)
    if not key:
        logger.warning("TMDB_API_KEY not set — TMDB ingestion is disabled.")
    return key


# Create a robust session with retries for TMDB
_session = requests.Session()
_retries = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=["GET"]
)
_session.mount("https://", HTTPAdapter(max_retries=_retries))


def _tmdb_get(path: str, params: dict = None) -> Optional[dict]:
    """Make an authenticated GET request to the TMDB API with retries."""
    api_key = _get_api_key()
    if not api_key:
        return None
    params = params or {}
    params["api_key"] = api_key
    try:
        resp = _session.get(f"{TMDB_BASE}{path}", params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        logger.error(f"TMDB request failed for {path} after retries: {e}")
        return None


def _get_drama_credits(tmdb_id: int) -> list[str]:
    """Fetch top 5 cast members for a drama."""
    data = _tmdb_get(f"/tv/{tmdb_id}/credits")
    if not data:
        return []
    return [m["name"] for m in data.get("cast", [])[:5]]


def _build_drama_doc(show: dict) -> Optional[dict]:
    """Convert a TMDB tv show dict to our Firestore drama document format."""
    tmdb_id = show.get("id")
    if not tmdb_id:
        return None

    # Filter to Korean-origin content
    origin_countries = show.get("origin_country", [])
    if "KR" not in origin_countries:
        return None

    genre_ids = show.get("genre_ids", [])
    genre_names = [TMDB_GENRE_MAP.get(gid, "") for gid in genre_ids if gid in TMDB_GENRE_MAP]

    poster_path = show.get("poster_path")
    poster_url = f"{TMDB_IMAGE_BASE}{poster_path}" if poster_path else ""

    first_air_date = show.get("first_air_date", "")
    year = int(first_air_date[:4]) if first_air_date else None

    return {
        "tmdb_id": tmdb_id,
        "title": show.get("name", show.get("original_name", "Unknown")),
        "description": show.get("overview", ""),
        "genres": "|".join(genre_names),
        "year": year,
        "poster_url": poster_url,
        "tmdb_popularity": float(show.get("popularity", 0)),
        "vote_average": float(show.get("vote_average", 0)),
        "vote_count": int(show.get("vote_count", 0)),
        "source": "tmdb",
        "fetched_at": datetime.utcnow().isoformat(),
    }


def fetch_trending_kdramas(limit: int = 30) -> list[dict]:
    """
    Fetch trending Korean dramas from TMDB.
    Combines results from trending/week and discover endpoints.
    """
    dramas: dict[int, dict] = {}

    # 1. Trending TV this week (all languages, filter to KR later)
    data = _tmdb_get("/trending/tv/week", {"language": "en-US", "page": 1})
    if data:
        for show in data.get("results", []):
            doc = _build_drama_doc(show)
            if doc:
                dramas[doc["tmdb_id"]] = doc

    # 2. Discover Korean dramas sorted by popularity
    for page in range(1, 4):  # pages 1-3 = up to 60 results
        data = _tmdb_get("/discover/tv", {
            "with_origin_country": "KR",
            "sort_by": "popularity.desc",
            "language": "en-US",
            "page": page,
        })
        if not data:
            break
        for show in data.get("results", []):
            tid = show.get("id")
            if tid and tid not in dramas:
                doc = _build_drama_doc(show)
                if doc:
                    dramas[tid] = doc

    # Sort by TMDB popularity and return top N
    sorted_dramas = sorted(dramas.values(), key=lambda d: d["tmdb_popularity"], reverse=True)
    top = sorted_dramas[:limit]

    # Enrich with cast (one API call each — rate-limited gently)
    for drama in top:
        try:
            drama["cast"] = _get_drama_credits(drama["tmdb_id"])
        except Exception:
            drama["cast"] = []

    logger.info(f"TMDB fetched {len(top)} Korean dramas.")
    return top


def upsert_dramas_to_firestore(dramas: list[dict]) -> int:
    """
    Upsert drama documents to Firestore `dramas` collection.
    Uses tmdb_id as document ID for idempotent updates.
    Returns count of documents written.
    """
    try:
        from app.services.firebase_service import get_firestore_client
        db = get_firestore_client()
    except Exception as e:
        logger.error(f"Firestore unavailable: {e}")
        return 0

    batch = db.batch()
    written = 0
    for drama in dramas:
        ref = db.collection("dramas").document(str(drama["tmdb_id"]))
        batch.set(ref, drama, merge=True)
        written += 1
        # Firestore batches max 500 ops
        if written % 400 == 0:
            batch.commit()
            batch = db.batch()

    if written % 400 != 0:
        batch.commit()

    logger.info(f"Upserted {written} dramas to Firestore.")
    return written


def run_ingestion(limit: int = 30) -> list[dict]:
    """Full ingestion run: fetch from TMDB + store to Firestore."""
    dramas = fetch_trending_kdramas(limit)
    upsert_dramas_to_firestore(dramas)
    return dramas
