from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import Optional
from app.models.schemas import RatingCreate
from app.services import recommendation as rec_svc
from app.services import firebase_service as fb_svc

router = APIRouter(prefix="/movies", tags=["movies"])


# ── Firestore helpers ─────────────────────────────────────────────────────────

# In-memory RAM Cache to avoid hitting Firebase Free Tier read quotas
_LOCAL_CACHE = {
    "dramas": None,          # list[dict]
    "trending_dramas": None  # list[dict]
}

def _fetch_tmdb_fallback_dramas(limit: int = 20) -> list[dict]:
    """If Firestore is completely offline/quota-exceeded, fetch live TRENDING from TMDB."""
    from app.core.config import settings
    api_key = getattr(settings, "TMDB_API_KEY", None)
    if not api_key or api_key == "your_tmdb_api_key_here":
        return []

    import requests
    try:
        resp = requests.get("https://api.themoviedb.org/3/discover/tv", params={
            "api_key": api_key,
            "with_origin_country": "KR",
            "sort_by": "popularity.desc",
            "language": "en-US",
            "page": 1,
        }, timeout=10)
        resp.raise_for_status()
        results = resp.json().get("results", [])
        
        dramas = []
        for show in results:
            poster_path = show.get("poster_path", "")
            backdrop_path = show.get("backdrop_path", "")
            dramas.append({
                "movie_id": show["id"],
                "tmdb_id": show["id"],
                "title": show.get("name", show.get("original_name", "")),
                "poster_url": f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "",
                "backdrop_url": f"https://image.tmdb.org/t/p/w1280{backdrop_path}" if backdrop_path else "",
                "description": show.get("overview", ""),
                "genres": "Drama",
                "vote_average": float(show.get("vote_average", 0)),
                "tmdb_popularity": float(show.get("popularity", 0)),
            })
        return dramas[:limit]
    except Exception as e:
        print(f"TMDB Fallback (trending) failed: {e}")
        return []


import hashlib
import random
from typing import Optional

def _fetch_tmdb_top_rated(limit: int = 20, seed_string: Optional[str] = None) -> list[dict]:
    """Fetch top-rated (NOT trending) Korean TV shows from TMDB for the 'Top Picks' row."""
    from app.core.config import settings
    api_key = getattr(settings, "TMDB_API_KEY", None)
    if not api_key or api_key == "your_tmdb_api_key_here":
        return []

    import requests
    try:
        page = 1
        if seed_string:
            seed_int = int(hashlib.md5(seed_string.encode()).hexdigest(), 16)
            page = (seed_int % 5) + 1  # Pick a page between 1 and 5 per user

        resp = requests.get("https://api.themoviedb.org/3/discover/tv", params={
            "api_key": api_key,
            "with_origin_country": "KR",
            "sort_by": "vote_average.desc",       # <- Top-rated, different from trending
            "vote_count.gte": 100,                # avoid low-vote shows
            "language": "en-US",
            "page": page,
        }, timeout=10)
        resp.raise_for_status()
        results = resp.json().get("results", [])

        dramas = []
        for show in results:
            poster_path = show.get("poster_path", "")
            backdrop_path = show.get("backdrop_path", "")
            dramas.append({
                "movie_id": show["id"],
                "tmdb_id": show["id"],
                "title": show.get("name", show.get("original_name", "")),
                "poster_url": f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "",
                "backdrop_url": f"https://image.tmdb.org/t/p/w1280{backdrop_path}" if backdrop_path else "",
                "description": show.get("overview", ""),
                "genres": "Drama",
                "vote_average": float(show.get("vote_average", 0)),
                "tmdb_popularity": float(show.get("popularity", 0)),
            })
        return dramas[:limit]
    except Exception as e:
        print(f"TMDB Top-Rated fallback failed: {e}")
        return []



def _get_all_from_firestore(limit: int = 20) -> list[dict]:
    """Stream entire dramas collection (no compound filter needed) with RAM Caching."""
    global _LOCAL_CACHE
    if _LOCAL_CACHE["dramas"] is not None:
        results = _LOCAL_CACHE["dramas"][:]
        results.sort(key=lambda d: d.get("tmdb_popularity", 0), reverse=True)
        return results[:limit]

    try:
        db = fb_svc.get_firestore_client()
        docs = db.collection("dramas").stream()
        results = [d.to_dict() for d in docs]
        if not results:
            results = _fetch_tmdb_fallback_dramas(50)
        
        _LOCAL_CACHE["dramas"] = results
        
        results.sort(key=lambda d: d.get("tmdb_popularity", 0), reverse=True)
        return results[:limit]
    except Exception as e:
        print(f"Firestore dramas read failed (Quota?): {e}")
        fb_dramas = _fetch_tmdb_fallback_dramas(50)
        if fb_dramas:
            _LOCAL_CACHE["dramas"] = fb_dramas
        return fb_dramas[:limit]


def _get_trending_from_firestore(limit: int = 20) -> list[dict]:
    """
    Try trending_dramas collection first (populated by trend_scorer),
    then fall back to popularity-sorted dramas collection.
    """
    global _LOCAL_CACHE
    if _LOCAL_CACHE["trending_dramas"] is not None:
        results = _LOCAL_CACHE["trending_dramas"][:]
        results.sort(key=lambda d: d.get("rank", 999))
        return results[:limit]

    try:
        db = fb_svc.get_firestore_client()
        docs = db.collection("trending_dramas").stream()
        results = [
            d.to_dict() for d in docs
            if d.id != "_meta"
        ]
        if results:
            _LOCAL_CACHE["trending_dramas"] = results
            results.sort(key=lambda d: d.get("rank", 999))
            return results[:limit]
    except Exception as e:
        print(f"Firestore trending read failed: {e}")
        pass
    return _get_all_from_firestore(limit)


def _search_firestore(query: str, limit: int = 10) -> list[dict]:
    """Fetch all dramas and fuzzy-match client-side (avoids Firestore index requirements)."""
    try:
        from rapidfuzz import process, fuzz
        db = fb_svc.get_firestore_client()
        docs = db.collection("dramas").stream()
        dramas = [d.to_dict() for d in docs]
        if not dramas:
            return []
        titles  = [d.get("title", "") for d in dramas]
        matches = process.extract(query, titles, scorer=fuzz.WRatio, limit=limit * 2)
        results = []
        for title, score, idx in matches:
            if score >= 45:
                drama = dict(dramas[idx])
                drama["match_score"] = score
                results.append(drama)
        results.sort(key=lambda d: d["match_score"], reverse=True)
        return results[:limit]
    except Exception as e:
        return []


def _tmdb_search_and_save(query: str) -> list[dict]:
    """
    If TMDB_API_KEY is set, search TMDB for the query and upsert results
    into Firestore so they appear in future searches.
    """
    from app.core.config import settings
    api_key = getattr(settings, "TMDB_API_KEY", None)
    if not api_key or api_key == "your_tmdb_api_key_here":
        return []
    try:
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        from datetime import datetime

        session = requests.Session()
        retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
        session.mount("https://", HTTPAdapter(max_retries=retries))

        TMDB_GENRE_MAP = {
            10759: "Action & Adventure", 16: "Animation", 35: "Comedy",
            80: "Crime", 99: "Documentary", 18: "Drama", 10751: "Family",
            10762: "Kids", 9648: "Mystery", 10763: "News", 10764: "Reality",
            10765: "Sci-Fi & Fantasy", 10766: "Soap", 10767: "Talk",
            10768: "War & Politics", 37: "Western", 10749: "Romance",
        }

        resp = session.get("https://api.themoviedb.org/3/search/tv", params={
            "api_key": api_key,
            "query": query,
            "language": "en-US",
        }, timeout=15)
        resp.raise_for_status()
        results = resp.json().get("results", [])

        db = fb_svc.get_firestore_client()
        found = []
        for show in results[:5]:
            if "KR" not in show.get("origin_country", []):
                continue
            genre_ids   = show.get("genre_ids", [])
            genre_names = [TMDB_GENRE_MAP.get(g, "") for g in genre_ids if g in TMDB_GENRE_MAP]
            first_air   = show.get("first_air_date", "")
            year        = int(first_air[:4]) if first_air and len(first_air) >= 4 else None
            poster_path = show.get("poster_path", "")
            doc = {
                "tmdb_id":        show["id"],
                "movie_id":       show["id"],
                "title":          show.get("name", show.get("original_name", "")),
                "description":    show.get("overview", ""),
                "genres":         "|".join(genre_names),
                "mood":           ["drama"],
                "year":           year,
                "poster_url":     f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "",
                "tmdb_popularity": float(show.get("popularity", 0)),
                "vote_average":   float(show.get("vote_average", 0)),
                "vote_count":     int(show.get("vote_count", 0)),
                "source":         "tmdb_search",
                "cast":           [],
                "fetched_at":     datetime.utcnow().isoformat(),
            }
            ref = db.collection("dramas").document(str(doc["tmdb_id"]))
            ref.set(doc, merge=True)
            found.append(doc)
        return found
    except Exception as e:
        return []


def _track(func, *args):
    try: func(*args)
    except Exception: pass


# ── Static routes (must come before /{movie_id}) ─────────────────────────────

@router.get("/trending")
def get_trending(limit: int = 20):
    """Live trending from Firestore → KDrama mock fallback."""
    live = _get_trending_from_firestore(limit)
    if live:
        return live
    return rec_svc.get_all_kdramas(limit)


@router.get("/search")
def search_movies(
    q: str,
    user_id: Optional[str] = Query(None),
    limit: int = 10,
    background_tasks: BackgroundTasks = None,
):
    """
    Search flow:
    1. Fuzzy-search Firestore dramas collection
    2. If zero results → search TMDB and add to Firestore
    3. If still nothing → rapidfuzz on KDrama mocks
    """
    if background_tasks and user_id:
        background_tasks.add_task(_track, _do_track_search, user_id, q)

    live = _search_firestore(q, limit)
    if live:
        return {"movies": live, "query": q, "source": "firestore"}

    # Not found locally → try TMDB live search + auto-save
    from_tmdb = _tmdb_search_and_save(q)
    if from_tmdb:
        return {"movies": from_tmdb, "query": q, "source": "tmdb_live"}

    # Final fallback to mocks
    mocks = rec_svc.keyword_search(q, limit)
    return {"movies": mocks, "query": q, "source": "mock"}


def _do_track_search(user_id, query):
    from app.services.behavior_tracker import track_search
    track_search(user_id, query)


@router.get("/recommendations")
def get_recommendations(
    user_id: str = Query(...),
    mood: Optional[str] = Query(None),
    limit: int = 15,
):
    """Personalised: liked genres → mood filter → all dramas fallback."""
    try:
        from app.services.behavior_tracker import get_liked_genres
        liked = get_liked_genres(user_id)
        if liked:
            all_d = _get_all_from_firestore(200) # Fast RAM Cache
            matched = [
                d for d in all_d
                if any(g.lower() in d.get("genres", "").lower() for g in liked)
            ]
            if matched:
                matched.sort(key=lambda d: d.get("tmdb_popularity", 0), reverse=True)
                return {"movies": matched[:limit], "model_used": "personalised", "user_id": user_id}
    except Exception:
        pass

    if mood:
        movies = rec_svc.get_kdramas_by_mood(mood, limit)
    else:
        # Use Top-Rated TMDB content so this row is visually distinct from "Trending Now"
        # Pass user_id to randomize content per-user
        top_rated = _fetch_tmdb_top_rated(limit, user_id)
        if top_rated:
            movies = top_rated
        else:
            # Final fallback: use all-from-firestore cache or mocks
            live = _get_all_from_firestore(limit)
            movies = live if live else rec_svc.get_all_kdramas(limit)
    return {"movies": movies, "model_used": "fallback", "user_id": user_id}


@router.post("/rate")
def rate_movie(rating_data: RatingCreate, background_tasks: BackgroundTasks):
    try:
        fb_svc.save_rating(rating_data.user_id, rating_data.movie_id, rating_data.rating)
        background_tasks.add_task(_track, _do_track_rating,
                                  rating_data.user_id, rating_data.movie_id, int(rating_data.rating))
        return {"status": "success", "message": "Rating saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _do_track_rating(user_id, movie_id, stars):
    from app.services.behavior_tracker import track_rating
    drama = rec_svc.get_kdrama_by_id(movie_id)
    genres = drama.get("genres", "") if drama else ""
    track_rating(user_id, movie_id, stars, genres)


@router.get("/mood/{mood}")
def get_mood_recommendations(mood: str, limit: int = 15):
    """Mood-filtered dramas from Firestore → mocks fallback."""
    try:
        db = fb_svc.get_firestore_client()
        docs = db.collection("dramas").stream()
        all_d = [d.to_dict() for d in docs]
        # Filter by mood tag
        matched = [d for d in all_d if mood in d.get("mood", [])]
        if matched:
            matched.sort(key=lambda d: d.get("tmdb_popularity", 0), reverse=True)
            return matched[:limit]
    except Exception:
        pass
    return rec_svc.get_kdramas_by_mood(mood, limit)


# ── Dynamic routes ─────────────────────────────────────────────────────────────

@router.get("/{movie_id}/similar")
def get_similar_movies(movie_id: int, limit: int = 8):
    try:
        similar = rec_svc.get_faiss_similar(movie_id, limit)
        if similar:
            return similar
    except Exception:
        pass
    # Use Firestore — return random popular dramas excluding current
    live = _get_all_from_firestore(limit + 5)
    return [m for m in live if m.get("movie_id") != movie_id][:limit] or rec_svc.get_all_kdramas(limit)


@router.get("/{movie_id}")
def get_movie(
    movie_id: int,
    user_id: Optional[str] = Query(None),
    background_tasks: BackgroundTasks = None,
):
    if background_tasks and user_id:
        background_tasks.add_task(_track, _do_track_click, user_id, movie_id)

    # Fast Path 1: Is it a local mock ID (1-20)?
    try:
        if int(movie_id) <= 20:
            movie = rec_svc.get_kdrama_by_id(movie_id)
            if movie:
                return movie
    except Exception:
        pass

    # Fast Path 2: Check RAM cache before querying slow Firestore
    global _LOCAL_CACHE
    cached_dramas = _LOCAL_CACHE.get("dramas")
    if cached_dramas:
        str_id = str(movie_id)
        for d in cached_dramas:
            if str(d.get("movie_id")) == str_id or str(d.get("tmdb_id")) == str_id:
                return d

    # Try Firestore by tmdb_id (stored as string doc ID)
    try:
        db = fb_svc.get_firestore_client()
        doc = db.collection("dramas").document(str(movie_id)).get(timeout=3)
        if doc.exists:
            return doc.to_dict()
    except Exception:
        pass

    # TMDB Live Fallback (If Firestore quota exceeded but ID is a real TMDB ID)
    from app.core.config import settings
    api_key = getattr(settings, "TMDB_API_KEY", None)
    if api_key and api_key != "your_tmdb_api_key_here":
        import requests
        try:
            resp = requests.get(f"https://api.themoviedb.org/3/tv/{movie_id}", params={
                "api_key": api_key,
                "language": "en-US",
                "append_to_response": "credits"
            }, timeout=5)
            if resp.status_code == 200:
                show = resp.json()
                poster_path = show.get("poster_path", "")
                cast = [c["name"] for c in show.get("credits", {}).get("cast", [])[:5]]
                return {
                    "movie_id": show["id"],
                    "tmdb_id": show["id"],
                    "title": show.get("name", show.get("original_name", "")),
                    "poster_url": f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "",
                    "description": show.get("overview", ""),
                    "genres": "|".join([g["name"] for g in show.get("genres", [])]),
                    "vote_average": float(show.get("vote_average", 0)),
                    "vote_count": int(show.get("vote_count", 0)),
                    "tmdb_popularity": float(show.get("popularity", 0)),
                    "cast": cast
                }
        except Exception as e:
            print(f"Failed to fetch TMDB fallback for ID {movie_id}: {e}")

    # Fallback to mock (IDs 1-15)
    movie = rec_svc.get_kdrama_by_id(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


def _do_track_click(user_id, movie_id):
    from app.services.behavior_tracker import track_click
    track_click(user_id, movie_id)
