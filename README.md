# Instant Music Recommender (v2)

A content-based music recommender built with Streamlit. Recommends similar
songs using audio features (danceability, energy, tempo, valence, acousticness,
etc.) from your Old Songs and Hindi Songs datasets, compared with cosine similarity.

## Setup

```
pip3 install -r requirements.txt
cd src
python3 preprocess.py
streamlit run main.py
```

Then open the URL shown in the terminal (usually http://localhost:8501).

## What's new in v2
- Big headphone hero illustration at the top of the page
- Lavender background theme throughout
- Green text in the song dropdown/search box for visibility
- More robust file paths (works no matter which folder you run commands from)

## How it works
- `data/Old_songs.csv` and `data/Hindi_songs.csv` — raw song datasets
- `src/preprocess.py` — cleans + merges both datasets, scales audio features,
  and precomputes a cosine-similarity matrix. Saves results to `artifacts/`.
- `src/main.py` — the Streamlit app. Pick a song (optionally filtered by
  language), then see the top N most similar songs with a match %.

## Notes
- Re-run `preprocess.py` any time you update the CSVs.
- On Mac, use `python3` / `pip3` (not `python` / `pip`).
