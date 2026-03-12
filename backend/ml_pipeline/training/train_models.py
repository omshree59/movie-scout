"""
Master training script: trains all ML models and saves artifacts.
Run from backend/: python -m ml_pipeline.training.train_models
"""
import os
import sys
import pickle
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize
import faiss
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "../saved_models")
os.makedirs(MODELS_DIR, exist_ok=True)


def load_data():
    movies_path = os.path.join(DATA_DIR, "movies_processed.csv")
    ratings_path = os.path.join(DATA_DIR, "ratings_processed.csv")
    if not os.path.exists(movies_path):
        print("Data not found. Running preprocessing first...")
        from ml_pipeline.preprocessing.preprocess import preprocess
        movies_df, ratings_df = preprocess()
    else:
        movies_df = pd.read_csv(movies_path)
        ratings_df = pd.read_csv(ratings_path)
    return movies_df, ratings_df


def train_popularity(movies_df):
    print("Training popularity model...")
    pop_scores = movies_df["popularity_score"].fillna(0).tolist()
    with open(os.path.join(MODELS_DIR, "popularity_scores.pkl"), "wb") as f:
        pickle.dump(pop_scores, f)
    print(f"  Popularity scores saved ({len(pop_scores)} movies)")


def train_content_based(movies_df):
    print("Training content-based (TF-IDF) model...")
    movies_df["content_features"] = movies_df["content_features"].fillna("")
    vectorizer = TfidfVectorizer(max_features=10000, ngram_range=(1, 2), stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(movies_df["content_features"])
    with open(os.path.join(MODELS_DIR, "tfidf_vectorizer.pkl"), "wb") as f:
        pickle.dump(vectorizer, f)
    with open(os.path.join(MODELS_DIR, "tfidf_matrix.pkl"), "wb") as f:
        pickle.dump(tfidf_matrix, f)
    print(f"  TF-IDF matrix shape: {tfidf_matrix.shape}")


def train_svd(ratings_df, movies_df):
    print("Training collaborative filtering (SVD)...")
    # Build user-item matrix
    user_ids = ratings_df["userId"].unique()
    movie_ids = movies_df["movieId"].tolist()
    
    user_map = {uid: i for i, uid in enumerate(user_ids)}
    item_map = {mid: i for i, mid in enumerate(movie_ids)}
    
    n_users = len(user_ids)
    n_items = len(movie_ids)
    
    # Sparse matrix via dense (for small dataset)
    R = np.zeros((n_users, n_items), dtype=np.float32)
    for _, row in ratings_df.iterrows():
        u = user_map.get(row["userId"])
        i = item_map.get(row["movieId"])
        if u is not None and i is not None:
            R[u, i] = row["rating"]
    
    # Mean-center
    R_mean = R.mean(axis=1, keepdims=True)
    R_centered = R - R_mean * (R > 0)
    
    # Truncated SVD
    k = min(50, n_users - 1, n_items - 1)
    svd = TruncatedSVD(n_components=k, random_state=42)
    user_factors = svd.fit_transform(R_centered)
    item_factors = svd.components_.T
    
    np.save(os.path.join(MODELS_DIR, "svd_user_factors.npy"), user_factors)
    np.save(os.path.join(MODELS_DIR, "svd_item_factors.npy"), item_factors)
    with open(os.path.join(MODELS_DIR, "svd_item_map.pkl"), "wb") as f:
        pickle.dump(item_map, f)
    with open(os.path.join(MODELS_DIR, "svd_user_map.pkl"), "wb") as f:
        pickle.dump(user_map, f)
    print(f"  SVD factors: users {user_factors.shape}, items {item_factors.shape}")


def train_neural_cf(ratings_df, movies_df, epochs=5, batch_size=512):
    print("Training Neural Collaborative Filtering (NCF)...")
    from ml_pipeline.models.neural_cf import NCF
    
    user_ids = ratings_df["userId"].unique()
    movie_ids = ratings_df["movieId"].unique()
    user_map = {uid: i for i, uid in enumerate(user_ids)}
    item_map = {mid: i for i, mid in enumerate(movie_ids)}
    
    users = torch.tensor([user_map[u] for u in ratings_df["userId"]], dtype=torch.long)
    items = torch.tensor([item_map[m] for m in ratings_df["movieId"]], dtype=torch.long)
    labels = torch.tensor((ratings_df["rating"] >= 4.0).astype(float).values, dtype=torch.float)
    
    dataset = TensorDataset(users, items, labels)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    model = NCF(len(user_ids), len(movie_ids), emb_dim=32)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    loss_fn = nn.BCELoss()
    
    model.train()
    for epoch in range(epochs):
        total_loss = 0.0
        for u, i, l in loader:
            pred = model(u, i)
            loss = loss_fn(pred, l)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        avg_loss = total_loss / len(loader)
        print(f"  Epoch {epoch+1}/{epochs} loss: {avg_loss:.4f}")
    
    torch.save(model.state_dict(), os.path.join(MODELS_DIR, "ncf_model.pt"))
    with open(os.path.join(MODELS_DIR, "ncf_maps.pkl"), "wb") as f:
        pickle.dump({"user_map": user_map, "item_map": item_map}, f)
    print("  NCF model saved.")


def build_faiss_index(movies_df):
    print("Building FAISS semantic index with Sentence Transformers...")
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        texts = (movies_df["title_clean"].fillna("") + " " + movies_df["genres"].str.replace("|", " ").fillna("")).tolist()
        print(f"  Encoding {len(texts)} movies...")
        embeddings = model.encode(texts, batch_size=64, show_progress_bar=True).astype("float32")
        embeddings_norm = normalize(embeddings)
        
        dim = embeddings_norm.shape[1]
        index = faiss.IndexFlatIP(dim)  # Inner product for cosine similarity
        index.add(embeddings_norm)
        
        faiss.write_index(index, os.path.join(MODELS_DIR, "faiss_index.bin"))
        np.save(os.path.join(MODELS_DIR, "embeddings.npy"), embeddings_norm)
        print(f"  FAISS index built with {index.ntotal} vectors (dim={dim})")
    except ImportError:
        print("  sentence_transformers not available. Skipping FAISS index.")


def main():
    print("=" * 60)
    print("MovieScout ML Training Pipeline")
    print("=" * 60)
    movies_df, ratings_df = load_data()
    print(f"\nDataset: {len(movies_df)} movies, {len(ratings_df)} ratings\n")
    
    train_popularity(movies_df)
    train_content_based(movies_df)
    train_svd(ratings_df, movies_df)
    train_neural_cf(ratings_df, movies_df, epochs=5)
    build_faiss_index(movies_df)
    
    print("\n" + "=" * 60)
    print("All models trained and saved to ml_pipeline/saved_models/")


if __name__ == "__main__":
    main()
