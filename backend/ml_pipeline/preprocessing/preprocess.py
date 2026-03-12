"""
MovieLens Data Preprocessing Pipeline.
Downloads and preprocesses the MovieLens dataset.
Run: python -m ml_pipeline.preprocessing.preprocess
"""
import os
import re
import zipfile
import requests
import pandas as pd
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")
MOVIELENS_URL = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"


def download_movielens():
    os.makedirs(DATA_DIR, exist_ok=True)
    zip_path = os.path.join(DATA_DIR, "ml-latest-small.zip")
    
    if not os.path.exists(zip_path):
        print("Downloading MovieLens dataset...")
        r = requests.get(MOVIELENS_URL, stream=True)
        with open(zip_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Download complete.")
    
    extract_dir = os.path.join(DATA_DIR, "ml-latest-small")
    if not os.path.exists(extract_dir):
        print("Extracting...")
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(DATA_DIR)
        print("Extraction complete.")
    return extract_dir


def extract_year(title: str):
    match = re.search(r"\((\d{4})\)", title)
    return int(match.group(1)) if match else None


def preprocess():
    raw_dir = download_movielens()
    
    movies = pd.read_csv(os.path.join(raw_dir, "movies.csv"))
    ratings = pd.read_csv(os.path.join(raw_dir, "ratings.csv"))
    tags = pd.read_csv(os.path.join(raw_dir, "tags.csv"))
    
    # Extract year from title
    movies["year"] = movies["title"].apply(extract_year)
    movies["title_clean"] = movies["title"].str.replace(r"\s*\(\d{4}\)", "", regex=True)
    
    # Aggregate ratings
    agg = ratings.groupby("movieId").agg(
        avg_rating=("rating", "mean"),
        num_ratings=("rating", "count")
    ).reset_index()
    
    # Aggregate tags
    tag_agg = tags.groupby("movieId")["tag"].apply(lambda ts: " ".join(ts.astype(str))).reset_index()
    tag_agg.columns = ["movieId", "tags"]
    
    # Merge all data
    df = movies.merge(agg, on="movieId", how="left")
    df = df.merge(tag_agg, on="movieId", how="left")
    df["num_ratings"] = df["num_ratings"].fillna(0).astype(int)
    df["avg_rating"] = df["avg_rating"].fillna(0.0).round(2)
    df["tags"] = df["tags"].fillna("")
    
    # Weighted popularity score (IMDB formula variant)
    C = df["avg_rating"].mean()
    m = df["num_ratings"].quantile(0.70)
    df["popularity_score"] = (
        (df["num_ratings"] / (df["num_ratings"] + m)) * df["avg_rating"] +
        (m / (df["num_ratings"] + m)) * C
    )
    
    # Content features for TF-IDF
    df["content_features"] = (
        df["genres"].str.replace("|", " ") + " " +
        df["title_clean"] + " " +
        df["tags"]
    )
    
    out_path = os.path.join(DATA_DIR, "movies_processed.csv")
    ratings_path = os.path.join(DATA_DIR, "ratings_processed.csv")
    df.to_csv(out_path, index=False)
    ratings.to_csv(ratings_path, index=False)
    print(f"Processed {len(df)} movies. Saved to {out_path}")
    return df, ratings


if __name__ == "__main__":
    preprocess()
