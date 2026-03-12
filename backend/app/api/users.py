from fastapi import APIRouter, HTTPException, Query
from app.services import firebase_service as fb_svc
from app.models.schemas import UserHistoryItem
from typing import List

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}/history", response_model=List[UserHistoryItem])
def get_history(user_id: str):
    """Retrieve user's watch and rating history."""
    try:
        history = fb_svc.get_watch_history(user_id)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/ratings")
def get_ratings(user_id: str):
    """All ratings given by the user."""
    try:
        ratings = fb_svc.get_user_ratings(user_id)
        return {"user_id": user_id, "ratings": ratings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{user_id}/history")
def add_to_history(user_id: str, movie_id: int = Query(...), title: str = Query(...)):
    """Record a movie watch event for the user."""
    try:
        fb_svc.add_watch_history(user_id, movie_id, title)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/taste-profile")
def get_taste(user_id: str):
    """Get user's computed taste profile based on ratings."""
    try:
        taste = fb_svc.get_user_taste_profile(user_id)
        return taste
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
