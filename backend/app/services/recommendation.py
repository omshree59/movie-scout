"""
Inference pipeline: loads all saved ML artifacts and provides unified recommendation interface.
"""
import os
import pickle
import numpy as np
import pandas as pd
import faiss
from typing import List, Optional

MODELS_DIR = os.path.join(os.path.dirname(__file__), "../../ml_pipeline/saved_models")
DATA_DIR = os.path.join(os.path.dirname(__file__), "../../ml_pipeline/data")

# Lazy-loaded globals
_movies_df = None
_tfidf_matrix = None
_tfidf_vectorizer = None
_svd_model = None
_svd_user_factors = None
_svd_item_factors = None
_faiss_index = None
_embeddings = None
_popularity_scores = None


def _load_movies():
    global _movies_df
    if _movies_df is None:
        path = os.path.join(DATA_DIR, "movies_processed.csv")
        if os.path.exists(path):
            _movies_df = pd.read_csv(path)
        else:
            # Fallback mock data
            _movies_df = pd.DataFrame({
                "movieId": range(1, 101),
                "title": [f"Movie {i}" for i in range(1, 101)],
                "genres": ["Action|Drama"] * 100,
                "year": [2020] * 100,
                "avg_rating": np.random.uniform(2.5, 5.0, 100),
                "num_ratings": np.random.randint(50, 10000, 100),
            })
    return _movies_df


def _load_tfidf():
    global _tfidf_matrix, _tfidf_vectorizer
    vect_path = os.path.join(MODELS_DIR, "tfidf_vectorizer.pkl")
    mat_path = os.path.join(MODELS_DIR, "tfidf_matrix.pkl")
    if _tfidf_vectorizer is None and os.path.exists(vect_path):
        with open(vect_path, "rb") as f:
            _tfidf_vectorizer = pickle.load(f)
        with open(mat_path, "rb") as f:
            _tfidf_matrix = pickle.load(f)


def _load_svd():
    global _svd_user_factors, _svd_item_factors
    u_path = os.path.join(MODELS_DIR, "svd_user_factors.npy")
    v_path = os.path.join(MODELS_DIR, "svd_item_factors.npy")
    if _svd_user_factors is None and os.path.exists(u_path):
        _svd_user_factors = np.load(u_path)
        _svd_item_factors = np.load(v_path)


def _load_faiss():
    global _faiss_index, _embeddings
    idx_path = os.path.join(MODELS_DIR, "faiss_index.bin")
    emb_path = os.path.join(MODELS_DIR, "embeddings.npy")
    if _faiss_index is None and os.path.exists(idx_path):
        _faiss_index = faiss.read_index(idx_path)
        _embeddings = np.load(emb_path)


def _load_popularity():
    global _popularity_scores
    path = os.path.join(MODELS_DIR, "popularity_scores.pkl")
    if _popularity_scores is None and os.path.exists(path):
        with open(path, "rb") as f:
            _popularity_scores = pickle.load(f)


# User Configuration for Github Raw CDN 
# Example URL structure: https://raw.githubusercontent.com/username/movie-assets/main/posters
GITHUB_CDN_BASE = "https://raw.githubusercontent.com/omshree59/movie-assets/main/posters"

KDRAMA_MOCKS = [
    {"id": 1, "title": "Crash Landing on You", "poster": f"{GITHUB_CDN_BASE}/cloy.jpg", "genres": "Romance|Comedy|Drama",
     "mood": ["romance", "happy", "adventure"],
     "desc": "A South Korean heiress paraglides into North Korea and into the life of an army officer, who decides he will help her hide.",
     "suitable": "Perfect for fans of sweeping, epic romances and heart-warming comedies. If you like star-crossed lovers and emotional rollercoasters, this is for you!",
     "cast": ["Hyun Bin", "Son Ye-jin", "Seo Ji-hye", "Kim Jung-hyun"]},

    {"id": 2, "title": "Goblin", "poster": f"{GITHUB_CDN_BASE}/goblin.jpg", "genres": "Fantasy|Romance|Drama",
     "mood": ["romance", "sad", "adventure"],
     "desc": "An immortal goblin goes looking for his human bride to remove an invisible sword from his chest and end his life.",
     "suitable": "Ideal for those who enjoy beautiful cinematography, bittersweet romances, hilarious bromances, and heavy fantasy elements.",
     "cast": ["Gong Yoo", "Kim Go-eun", "Lee Dong-wook", "Yoo In-na"]},

    {"id": 3, "title": "Squid Game", "poster": f"{GITHUB_CDN_BASE}/squid.jpg", "genres": "Thriller|Drama|Action",
     "mood": ["action", "thriller"],
     "desc": "Hundreds of cash-strapped players accept a strange invitation to compete in children's games. Inside, a tempting prize awaits with deadly high stakes.",
     "suitable": "Perfect for thrill-seekers, horror fans, and viewers who enjoy psychological games, social commentary, and edge-of-your-seat suspense.",
     "cast": ["Lee Jung-jae", "Park Hae-soo", "Jung Ho-yeon", "Wi Ha-joon"]},

    {"id": 4, "title": "Descendants of the Sun", "poster": f"{GITHUB_CDN_BASE}/dots.jpg", "genres": "Romance|Action|Drama",
     "mood": ["romance", "action", "adventure"],
     "desc": "A love story develops between a surgeon and a special forces officer. Together they face danger in a war-torn country.",
     "suitable": "Great for fans of action-packed romance, medical dramas, and beautiful scenery. Features a strong, confident power couple.",
     "cast": ["Song Joong-ki", "Song Hye-kyo", "Jin Goo", "Kim Ji-won"]},

    {"id": 5, "title": "It's Okay to Not Be Okay", "poster": f"{GITHUB_CDN_BASE}/iotnbo.jpg", "genres": "Romance|Drama",
     "mood": ["romance", "sad", "healing"],
     "desc": "An extraordinary road to emotional healing opens up for an antisocial children's book author and an empathetic psychiatric ward caretaker.",
     "suitable": "Highly recommended for those who appreciate mental health representation, dark fairytales, deep character growth, and stunning fashion.",
     "cast": ["Kim Soo-hyun", "Seo Yea-ji", "Oh Jung-se", "Park Gyu-young"]},

    {"id": 6, "title": "Itaewon Class", "poster": f"{GITHUB_CDN_BASE}/itaewon.jpg", "genres": "Drama|Romance",
     "mood": ["action", "happy", "romance"],
     "desc": "An ex-con and his friends fight to make their ambitious dreams for their street bar a reality, taking on a powerful foe.",
     "suitable": "A must-watch for underdog story fans. It's inspiring, empowering, and deals heavily with revenge, loyalty, and business ambition.",
     "cast": ["Park Seo-joon", "Kim Da-mi", "Yoo Jae-myung", "Kwon Nara"]},

    {"id": 7, "title": "Vincenzo", "poster": f"{GITHUB_CDN_BASE}/vincenzo.jpg", "genres": "Comedy|Crime|Drama",
     "mood": ["action", "happy", "thriller"],
     "desc": "During a visit to his motherland, a Korean-Italian mafia lawyer gives an unrivaled conglomerate a taste of its own medicine with a side of justice.",
     "suitable": "For viewers who love dark comedy, anti-heroes, clever legal battles, and satisfying revenge plots with incredible action sequences.",
     "cast": ["Song Joong-ki", "Jeon Yeo-been", "Ok Taec-yeon", "Kim Yeo-jin"]},

    {"id": 8, "title": "Reply 1988", "poster": f"{GITHUB_CDN_BASE}/reply.jpg", "genres": "Comedy|Family|Romance",
     "mood": ["happy", "romance", "healing", "sad"],
     "desc": "Follows the lives of five friends and their families living in the same neighborhood of Ssangmundong, Seoul, in the year 1988.",
     "suitable": "The ultimate slice-of-life drama. If you want a comforting, nostalgic show about deep friendships, family bonds, and first loves, look no further.",
     "cast": ["Lee Hye-ri", "Park Bo-gum", "Go Kyung-pyo", "Ryu Jun-yeol"]},

    {"id": 9, "title": "Hospital Playlist", "poster": f"{GITHUB_CDN_BASE}/hospital.jpg", "genres": "Drama|Comedy|Medical",
     "mood": ["happy", "healing", "sad"],
     "desc": "Every day is extraordinary for five doctors and their patients inside a hospital, where birth, death and everything in between coexist.",
     "suitable": "Perfect for medical drama lovers who want less medical politics and more heartwarming friendships, great music, and wholesome patient stories.",
     "cast": ["Jo Jung-suk", "Yoo Yeon-seok", "Jung Kyung-ho", "Kim Dae-myung", "Jeon Mi-do"]},

    {"id": 10, "title": "My Mister", "poster": f"{GITHUB_CDN_BASE}/mister.jpg", "genres": "Drama|Family",
     "mood": ["sad", "healing"],
     "desc": "A struggling young woman and a weary middle-aged man find comfort and healing in one another as they endure the hardships of life.",
     "suitable": "A masterpiece for those seeking a mature, realistic, emotionally profound drama. It's highly emotional and explores human empathy deeply.",
     "cast": ["Lee Sun-kyun", "IU", "Go Doo-shim", "Park Ho-san"]},

    {"id": 11, "title": "Signal", "poster": f"{GITHUB_CDN_BASE}/signal.jpg", "genres": "Crime|Thriller|Sci-Fi",
     "mood": ["action", "thriller", "adventure"],
     "desc": "Detectives from the present and a detective from the past communicate via walkie-talkie to solve a long-unsolved case.",
     "suitable": "A brilliant watch for mystery, true-crime, and thriller enthusiasts. Fast-paced, mind-bending, and features incredibly tense investigations.",
     "cast": ["Lee Je-hoon", "Kim Hye-soo", "Cho Jin-woong"]},

    {"id": 12, "title": "Mr. Sunshine", "poster": f"{GITHUB_CDN_BASE}/sunshine.jpg", "genres": "Historical|Romance|Drama",
     "mood": ["romance", "sad", "adventure"],
     "desc": "A young boy who ends up in the U.S. after the 1871 Shinmiyangyo incident returns to Korea at a historical turning point and falls for a noblewoman.",
     "suitable": "For lovers of historical epics, breathtaking cinematography, phenomenal acting, and heartbreakingly beautiful, slow-burn romances.",
     "cast": ["Lee Byung-hun", "Kim Tae-ri", "Yoo Yeon-seok", "Kim Min-jung"]},

    {"id": 13, "title": "Kingdom", "poster": f"{GITHUB_CDN_BASE}/kingdom.jpg", "genres": "Horror|Thriller|Historical",
     "mood": ["action", "thriller", "adventure"],
     "desc": "While strange rumors about their ill King grip a kingdom, the crown prince becomes their only hope against a mysterious plague overtaking the land.",
     "suitable": "Zombie fans and historical drama fans alike. It perfectly blends high-stakes political royal tension with terrifying zombie action.",
     "cast": ["Ju Ji-hoon", "Ryu Seung-ryong", "Bae Doona", "Kim Sung-kyu"]},

    {"id": 14, "title": "The Glory", "poster": f"{GITHUB_CDN_BASE}/glory.jpg", "genres": "Thriller|Drama",
     "mood": ["sad", "thriller"],
     "desc": "Years after surviving horrific abuse in high school, a woman puts an elaborate revenge scheme in motion to make the perpetrators pay.",
     "suitable": "For fans of chilling psychological thrillers, meticulous long-term revenge plots, and dark storytelling that keeps you hooked.",
     "cast": ["Song Hye-kyo", "Lee Do-hyun", "Lim Ji-yeon", "Yeom Hye-ran"]},

    {"id": 15, "title": "Sweet Home", "poster": f"{GITHUB_CDN_BASE}/sweet.jpg", "genres": "Horror|Action|Sci-Fi",
     "mood": ["action", "thriller", "adventure"],
     "desc": "As humans turn into savage monsters and wreak terror, one troubled teenager and his apartment neighbors fight to survive.",
     "suitable": "Perfect for monster-horror fans, apocalyptic survival stories, and intense, bloody, CGI-heavy action sequences.",
     "cast": ["Song Kang", "Lee Jin-wook", "Lee Si-young", "Lee Do-hyun"]}
]

# Stable lookup by ID
_KDRAMA_BY_ID = {d["id"]: d for d in KDRAMA_MOCKS}

def _drama_to_dict(drama: dict) -> dict:
    """Convert a KDrama mock entry to API response dict."""
    return {
        "movie_id": drama["id"],
        "title": drama["title"],
        "genres": drama["genres"],
        "year": 2020,
        "poster_url": drama["poster"],
        "description": drama["desc"],
        "suitable_for": drama["suitable"],
        "cast": drama.get("cast", []),
        # No static rating — user ratings are stored in Firebase
    }


def get_kdrama_by_id(movie_id: int) -> Optional[dict]:
    """Look up a single KDrama by its stable numeric ID."""
    drama = _KDRAMA_BY_ID.get(movie_id)
    return _drama_to_dict(drama) if drama else None


def get_all_kdramas(limit: int = 15) -> List[dict]:
    return [_drama_to_dict(d) for d in KDRAMA_MOCKS[:limit]]


def get_kdramas_by_mood(mood: str, limit: int = 15) -> List[dict]:
    """Return KDramas matching a mood tag."""
    mood = mood.lower()
    matched = [d for d in KDRAMA_MOCKS if mood in d.get("mood", [])]
    # Fallback: return all if nothing matched
    if not matched:
        matched = KDRAMA_MOCKS
    return [_drama_to_dict(d) for d in matched[:limit]]


def _df_to_dicts(df: pd.DataFrame, limit: int = 20) -> List[dict]:
    """Cycle through KDramas for trending/popular rows using stable IDs."""
    results = []
    dramas = KDRAMA_MOCKS
    for i, (_, row) in enumerate(df.head(limit).iterrows()):
        drama = dramas[i % len(dramas)]
        results.append({
            "movie_id": drama["id"],
            "title": drama["title"],
            "genres": drama["genres"],
            "year": int(row["year"]) if "year" in row and pd.notna(row.get("year")) else 2020,
            "poster_url": drama["poster"],
            "description": drama["desc"],
            "suitable_for": drama["suitable"],
            "cast": drama["cast"],
            "rating": float(row["avg_rating"]) if "avg_rating" in row and pd.notna(row.get("avg_rating")) else 4.8,
            "vote_count": int(row["num_ratings"]) if "num_ratings" in row and pd.notna(row.get("num_ratings")) else 1500,
        })
    return results


def get_popular_movies(limit: int = 20) -> List[dict]:
    _load_popularity()
    df = _load_movies()
    if _popularity_scores is not None:
        df = df.copy()
        df["pop_score"] = _popularity_scores
        df = df.sort_values("pop_score", ascending=False)
    else:
        df = df.sort_values(["num_ratings", "avg_rating"], ascending=False)
    return _df_to_dicts(df, limit)


def get_content_based(movie_id: int, limit: int = 10) -> List[dict]:
    from sklearn.metrics.pairwise import cosine_similarity
    _load_tfidf()
    df = _load_movies()
    if _tfidf_matrix is None:
        return get_popular_movies(limit)
    movie_ids = df["movieId"].tolist()
    if movie_id not in movie_ids:
        return get_popular_movies(limit)
    idx = movie_ids.index(movie_id)
    sim_scores = cosine_similarity(_tfidf_matrix[idx], _tfidf_matrix).flatten()
    sim_indices = sim_scores.argsort()[::-1][1:limit+1]
    return _df_to_dicts(df.iloc[sim_indices], limit)


def get_collaborative(user_id: str, liked_movie_ids: List[int], limit: int = 20) -> List[dict]:
    _load_svd()
    df = _load_movies()
    if _svd_item_factors is None or not liked_movie_ids:
        return get_popular_movies(limit)
    # Average the item vectors of liked movies to estimate user preference
    movie_ids = df["movieId"].tolist()
    indices = [movie_ids.index(mid) for mid in liked_movie_ids if mid in movie_ids]
    if not indices:
        return get_popular_movies(limit)
    user_vec = _svd_item_factors[indices].mean(axis=0)
    scores = _svd_item_factors.dot(user_vec)
    top_indices = np.argsort(scores)[::-1]
    # Filter already liked
    top_indices = [i for i in top_indices if movie_ids[i] not in liked_movie_ids][:limit]
    return _df_to_dicts(df.iloc[top_indices], limit)


def _search_kdramas(query: str, limit: int = 20) -> List[dict]:
    results = []
    q = query.lower()

    try:
        from rapidfuzz import fuzz
        use_fuzz = True
    except ImportError:
        use_fuzz = False

    scored_dramas = []
    for i, drama in enumerate(KDRAMA_MOCKS):
        title = drama['title']
        title_lower = title.lower()
        searchable_text = f"{title} {drama['genres']} {' '.join(drama.get('cast', []))}".lower()
        
        score = 0
        if title_lower.startswith(q) or q in title_lower:
            score = 100
        elif use_fuzz:
            score = max(
                fuzz.partial_ratio(q, title_lower),
                fuzz.token_set_ratio(q, searchable_text) * 0.8
            )
        else:
            if q in searchable_text:
                score = 80
                
        if score > 50:
            scored_dramas.append((score, i, drama))
            
    # Sort by descending score
    scored_dramas.sort(key=lambda x: x[0], reverse=True)
    
    for score, i, drama in scored_dramas[:limit]:
        results.append({
            "movie_id": i + 15, # Offset strictly for mock modulo mapping
            "title": drama["title"],
            "genres": drama["genres"],
            "year": 2020,
            "poster_url": drama["poster"],
            "description": drama["desc"],
            "suitable_for": drama["suitable"],
            "cast": drama.get("cast", []),
            "rating": 4.9,
            "vote_count": 5000,
            "score": int(score)
        })
    return results

def get_semantic_search(query: str, limit: int = 20) -> List[dict]:
    results = _search_kdramas(query, limit)
    return results if results else get_popular_movies(limit)

def keyword_search(query: str, limit: int = 20) -> List[dict]:
    results = _search_kdramas(query, limit)
    return results if results else get_popular_movies(limit)
