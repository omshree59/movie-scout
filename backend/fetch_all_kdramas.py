"""
Bulk TMDB K-Drama Importer
===========================
Fetches ALL Korean dramas from TMDB from year 2000 to present
and stores them in Firestore `dramas` collection.

This runs ONCE to fully populate the database.
After that, the scheduler keeps it updated every 6 hours.

Usage:
    cd backend
    python fetch_all_kdramas.py

Requirements:
    - TMDB_API_KEY in your .env file
    - Firebase credentials configured
"""
import os
import sys
import time
import logging

# Allow imports from backend root
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

TMDB_BASE       = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

TMDB_GENRE_MAP = {
    10759: "Action & Adventure", 16: "Animation", 35: "Comedy",
    80: "Crime", 99: "Documentary", 18: "Drama", 10751: "Family",
    10762: "Kids", 9648: "Mystery", 10763: "News", 10764: "Reality",
    10765: "Sci-Fi & Fantasy", 10766: "Soap", 10767: "Talk",
    10768: "War & Politics", 37: "Western", 10749: "Romance",
}

# Mood mapping based on genre
GENRE_TO_MOOD = {
    "Drama":            ["drama", "sad"],
    "Romance":          ["romance", "happy"],
    "Comedy":           ["happy", "healing"],
    "Action & Adventure": ["action", "adventure"],
    "Crime":            ["thriller"],
    "Mystery":          ["thriller", "drama"],
    "Sci-Fi & Fantasy": ["adventure", "action"],
    "War & Politics":   ["action", "drama"],
    "Horror":           ["horror"],
}


import requests

def tmdb_get(path: str, params: dict = None) -> dict | None:
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        raise RuntimeError("TMDB_API_KEY is not set in .env!")
    p = params or {}
    p["api_key"] = api_key
    try:
        r = requests.get(f"{TMDB_BASE}{path}", params=p, timeout=15)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        logger.warning(f"TMDB error {path}: {e}")
        return None


def get_cast(tmdb_id: int) -> list[str]:
    data = tmdb_get(f"/tv/{tmdb_id}/credits")
    if not data:
        return []
    return [m["name"] for m in data.get("cast", [])[:6]]


def build_doc(show: dict) -> dict | None:
    tid   = show.get("id")
    title = show.get("name") or show.get("original_name", "")
    if not tid or not title:
        return None

    # Only keep Korean-origin shows
    if "KR" not in show.get("origin_country", []):
        return None

    genre_ids   = show.get("genre_ids", [])
    genre_names = [TMDB_GENRE_MAP[g] for g in genre_ids if g in TMDB_GENRE_MAP]

    # Derive mood tags
    moods: list[str] = []
    for g in genre_names:
        moods.extend(GENRE_TO_MOOD.get(g, []))
    moods = list(dict.fromkeys(moods))  # deduplicate while preserving order
    if not moods:
        moods = ["drama"]

    first_air = show.get("first_air_date", "")
    year      = int(first_air[:4]) if first_air and len(first_air) >= 4 else None

    poster_path = show.get("poster_path", "")
    poster_url  = f"{TMDB_IMAGE_BASE}{poster_path}" if poster_path else ""

    return {
        "tmdb_id":        tid,
        "movie_id":       tid,           # used by frontend
        "title":          title,
        "description":    show.get("overview", ""),
        "genres":         "|".join(genre_names),
        "mood":           moods,
        "year":           year,
        "poster_url":     poster_url,
        "tmdb_popularity": float(show.get("popularity", 0)),
        "vote_average":   float(show.get("vote_average", 0)),
        "vote_count":     int(show.get("vote_count", 0)),
        "source":         "tmdb",
        "cast":           [],            # filled later in batches
    }


def fetch_all_pages(start_year: int = 2000, end_year: int = 2026) -> list[dict]:
    """
    Paginate through POPULAR Korean dramas from TMDB.
    Fetches only the top 2 pages (40 items) per year to keep data quality high.
    """
    all_shows: dict[int, dict] = {}

    for year in range(start_year, end_year + 1):
        logger.info(f"  Fetching popular dramas for {year}…")
        # Only fetch top 2 pages (most popular 40) per year
        for page in range(1, 3):
            data = tmdb_get("/discover/tv", {
                "with_origin_country": "KR",
                "first_air_date.gte": f"{year}-01-01",
                "first_air_date.lte": f"{year}-12-31",
                "sort_by":            "popularity.desc",
                "language":           "en-US",
                "page":               page,
            })
            if not data:
                break

            results = data.get("results", [])
            for show in results:
                # Skip clearly unpopular or incomplete entries
                if show.get("popularity", 0) < 5 or not show.get("poster_path"):
                    continue

                doc = build_doc(show)
                if doc and doc["tmdb_id"] not in all_shows:
                    all_shows[doc["tmdb_id"]] = doc

            time.sleep(0.05)
            if page >= data.get("total_pages", 1):
                break

    logger.info(f"    Total highly popular dramas collected: {len(all_shows)}")
    return list(all_shows.values())


def enrich_with_cast(dramas: list[dict], batch_size: int = 50) -> list[dict]:
    """Fetch cast for each drama (rate-limited)."""
    logger.info(f"Enriching cast for {len(dramas)} dramas (may take a few minutes)…")
    for i, drama in enumerate(dramas):
        try:
            drama["cast"] = get_cast(drama["tmdb_id"])
        except Exception:
            drama["cast"] = []
        if i % batch_size == 0 and i > 0:
            logger.info(f"  Cast enriched: {i}/{len(dramas)}")
        time.sleep(0.05)  # polite rate limiting
    return dramas


def save_to_firestore(dramas: list[dict]) -> int:
    """Upsert all dramas into Firestore `dramas` collection."""
    from app.core.firebase import get_db
    db = get_db()

    total   = len(dramas)
    written = 0
    BATCH_SZ = 400

    for chunk_start in range(0, total, BATCH_SZ):
        chunk = dramas[chunk_start: chunk_start + BATCH_SZ]
        batch = db.batch()
        for drama in chunk:
            ref = db.collection("dramas").document(str(drama["tmdb_id"]))
            batch.set(ref, drama, merge=True)
            written += 1
        batch.commit()
        logger.info(f"  Written {written}/{total} dramas to Firestore…")

    return written


def main():
    logger.info("=" * 60)
    logger.info("MovieScout — Bulk TMDB K-Drama Import")
    logger.info("=" * 60)

    api_key = os.getenv("TMDB_API_KEY")
    if not api_key or api_key == "your_tmdb_api_key_here":
        logger.error("TMDB_API_KEY is not set in .env! Aborting.")
        sys.exit(1)

    logger.info("Step 1: Fetching all Korean dramas from TMDB (2000–2026)…")
    dramas = fetch_all_pages(start_year=2000, end_year=2026)
    logger.info(f"Step 1 complete: {len(dramas)} unique K-dramas found.")

    logger.info("Step 2: Enriching with cast data…")
    dramas = enrich_with_cast(dramas)
    logger.info("Step 2 complete.")

    logger.info("Step 3: Saving to Firestore…")
    count = save_to_firestore(dramas)
    logger.info(f"Step 3 complete: {count} documents written.")

    logger.info("=" * 60)
    logger.info(f"✅ Import done! {count} K-dramas are now in Firestore.")
    logger.info("Restart the backend server — the API will now serve live data.")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
