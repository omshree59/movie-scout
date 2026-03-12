from app.core.firebase import get_db
from datetime import datetime
from typing import Optional

def save_rating(user_id: str, movie_id: int, rating: float):
    db = get_db()
    doc_ref = db.collection("ratings").document(f"{user_id}_{movie_id}")
    doc_ref.set({
        "user_id": user_id,
        "movie_id": movie_id,
        "rating": rating,
        "timestamp": datetime.utcnow().isoformat()
    })

def get_user_ratings(user_id: str) -> list:
    db = get_db()
    docs = db.collection("ratings").where("user_id", "==", user_id).stream()
    return [doc.to_dict() for doc in docs]

def add_watch_history(user_id: str, movie_id: int, title: str):
    db = get_db()
    db.collection("watch_history").add({
        "user_id": user_id,
        "movie_id": movie_id,
        "title": title,
        "watched_at": datetime.utcnow().isoformat()
    })

def get_watch_history(user_id: str) -> list:
    db = get_db()
    docs = db.collection("watch_history").where("user_id", "==", user_id).order_by("watched_at", direction="DESCENDING").limit(50).stream()
    return [doc.to_dict() for doc in docs]

def get_user_taste_profile(user_id: str) -> dict:
    """Aggregates user ratings to build a taste vector (genre preferences)."""
    db = get_db()
    docs = db.collection("ratings").where("user_id", "==", user_id).where("rating", ">=", 3.5).stream()
    liked_movies = [doc.to_dict().get("movie_id") for doc in docs]
    return {"user_id": user_id, "liked_movie_ids": liked_movies}
