from pydantic import BaseModel
from typing import Optional, List, Any

class Movie(BaseModel):
    movie_id: int
    title: str
    genres: str
    year: Optional[int] = None
    poster_url: Optional[str] = None
    overview: Optional[str] = None
    description: Optional[str] = None
    suitable_for: Optional[str] = None
    cast: Optional[List[str]] = []
    rating: Optional[float] = None
    vote_count: Optional[int] = None
    score: Optional[float] = None

class RatingCreate(BaseModel):
    user_id: str
    movie_id: int
    rating: float  # 0.5 to 5.0

class SearchQuery(BaseModel):
    query: str
    mode: str = "semantic"  # "semantic" or "keyword"
    limit: int = 20

class RecommendationRequest(BaseModel):
    user_id: str
    mood: Optional[str] = None  # e.g., "happy", "sad", "action", "romance"
    limit: int = 20
    model: str = "hybrid"  # "popularity", "content", "collaborative", "neural", "hybrid"

class RecommendationResponse(BaseModel):
    movies: List[Movie]
    model_used: str
    user_id: Optional[str] = None

class UserHistoryItem(BaseModel):
    movie_id: int
    title: str
    rating: Optional[float] = None
    watched_at: Optional[str] = None

class MovieDetails(Movie):
    similar_movies: Optional[List[Movie]] = []
    tags: Optional[List[str]] = []
