from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from app.models.schemas import (
    RatingCreate, SearchQuery, RecommendationRequest,
    RecommendationResponse, Movie, MovieDetails
)
from app.services import recommendation as rec_svc
from app.services import firebase_service as fb_svc

router = APIRouter(prefix="/movies", tags=["movies"])


# ── Static routes MUST come before /{movie_id} to avoid int-parse errors ──

@router.get("/trending")
def get_trending(limit: int = 15):
    """All KDramas cycled for trending row."""
    movies = rec_svc.get_all_kdramas(limit)
    return movies


@router.get("/search")
def search_movies(
    q: str,
    mode: str = "semantic",
    limit: int = 10
):
    """Semantic or keyword-based movie search."""
    if mode == "semantic":
        movies = rec_svc.get_semantic_search(q, limit)
    else:
        movies = rec_svc.keyword_search(q, limit)
    return {"movies": movies, "query": q}


@router.get("/recommendations")
def get_recommendations(
    user_id: str = Query(...),
    mood: Optional[str] = Query(None),
    model: str = Query("hybrid"),
    limit: int = 15
):
    """Recommendations based on mood or all dramas."""
    if mood:
        movies = rec_svc.get_kdramas_by_mood(mood, limit)
    else:
        movies = rec_svc.get_all_kdramas(limit)
    return {"movies": movies, "model_used": model, "user_id": user_id}


@router.post("/rate")
def rate_movie(rating_data: RatingCreate):
    """Save user rating to Firebase Firestore."""
    try:
        fb_svc.save_rating(rating_data.user_id, rating_data.movie_id, rating_data.rating)
        return {"status": "success", "message": "Rating saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mood/{mood}")
def get_mood_recommendations(mood: str, limit: int = 15):
    """Mood-aware KDrama recommendations."""
    movies = rec_svc.get_kdramas_by_mood(mood, limit)
    return movies


# ── Dynamic /{movie_id} routes come LAST ──

@router.get("/{movie_id}/similar")
def get_similar_movies(movie_id: int, limit: int = 8):
    """Similar movies — returns all KDramas except the current one."""
    all_dramas = rec_svc.get_all_kdramas(15)
    similar = [m for m in all_dramas if m["movie_id"] != movie_id]
    return similar[:limit]


@router.get("/{movie_id}")
def get_movie(movie_id: int):
    """Get a single KDrama by its stable ID (1–15)."""
    movie = rec_svc.get_kdrama_by_id(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie
