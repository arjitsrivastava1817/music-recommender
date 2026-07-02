"""
Preprocessing script for Instant Music Recommender.

Reads the raw Old_songs.csv and Hindi_songs.csv files, cleans them,
combines them into a single dataset, engineers audio-feature vectors,
and saves everything needed by the Streamlit app (main.py) as pickle files.

Run this once (or whenever the raw CSVs change) before starting the app:
    python3 preprocess.py
"""

import os
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import pickle

# ---------------------------------------------------------------------------
# Paths (work no matter which directory you run this script from)
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")
ARTIFACT_DIR = os.path.join(PROJECT_DIR, "artifacts")
os.makedirs(ARTIFACT_DIR, exist_ok=True)

OLD_SONGS_PATH = os.path.join(DATA_DIR, "Old_songs.csv")
HINDI_SONGS_PATH = os.path.join(DATA_DIR, "Hindi_songs.csv")

FEATURE_COLS = [
    "danceability",
    "acousticness",
    "energy",
    "liveness",
    "loudness",
    "speechiness",
    "tempo",
    "mode",
    "key",
    "Valence",
    "time_signature",
    "popularity",
]


def load_and_clean(path, default_language=None):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Could not find dataset: {path}")

    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]

    if default_language and "language" in df.columns:
        df["language"] = df["language"].fillna(default_language)

    required = ["song_name"] + FEATURE_COLS
    df = df.dropna(subset=[c for c in required if c in df.columns])

    for col in FEATURE_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=FEATURE_COLS)

    return df


def build_dataset():
    old_df = load_and_clean(OLD_SONGS_PATH, default_language="Old")
    hindi_df = load_and_clean(HINDI_SONGS_PATH, default_language="Hindi")

    combined = pd.concat([old_df, hindi_df], ignore_index=True)

    combined["dedup_key"] = (
        combined["song_name"].str.lower().str.strip()
        + " || "
        + combined["singer"].fillna("").str.lower().str.strip()
    )
    combined = combined.drop_duplicates(subset="dedup_key").reset_index(drop=True)
    combined = combined.drop(columns=["dedup_key"])

    combined["display_name"] = combined["song_name"].str.strip()
    has_singer = combined["singer"].notna() & (combined["singer"].str.strip() != "")
    combined.loc[has_singer, "display_name"] = (
        combined.loc[has_singer, "song_name"].str.strip()
        + " - "
        + combined.loc[has_singer, "singer"].str.split("|").str[0].str.strip()
    )

    dup_mask = combined["display_name"].duplicated(keep=False)
    combined.loc[dup_mask, "display_name"] = (
        combined.loc[dup_mask, "display_name"] + " (" + combined.loc[dup_mask, "language"] + ")"
    )

    return combined.reset_index(drop=True)


def main():
    print("Loading and cleaning raw CSVs...")
    df = build_dataset()
    print(f"Combined dataset: {len(df)} songs")

    print("Scaling audio features...")
    scaler = StandardScaler()
    feature_matrix = scaler.fit_transform(df[FEATURE_COLS])

    print("Computing cosine similarity matrix...")
    similarity_matrix = cosine_similarity(feature_matrix)

    print("Saving artifacts...")
    df.to_pickle(os.path.join(ARTIFACT_DIR, "songs.pkl"))
    with open(os.path.join(ARTIFACT_DIR, "similarity.pkl"), "wb") as f:
        pickle.dump(similarity_matrix, f)
    with open(os.path.join(ARTIFACT_DIR, "scaler.pkl"), "wb") as f:
        pickle.dump(scaler, f)

    print("Done! Artifacts saved to:", ARTIFACT_DIR)


if __name__ == "__main__":
    main()
