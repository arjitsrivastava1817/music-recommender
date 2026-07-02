# Instant Music Recommender (CSV version)

A content-based music recommender built with Streamlit. Recommends similar
songs using audio features (danceability, energy, tempo, valence, acousticness,
etc.) from your Old Songs and Hindi Songs datasets, compared with cosine similarity.

Fully self-contained: no external API, no login, no usage caps. Works for
anyone who opens the link.

## Setup

```
pip3 install -r requirements.txt
cd src
python3 preprocess.py
streamlit run main.py
```

Then open the URL shown in the terminal (usually http://localhost:8501).

## How it works
- `data/Old_songs.csv` and `data/Hindi_songs.csv` — raw song datasets
- `src/preprocess.py` — cleans + merges both datasets, scales audio features,
  and precomputes a cosine-similarity matrix. Saves results to `artifacts/`.
- `src/main.py` — the Streamlit app. Pick a song (optionally filtered by
  language), then see the top N most similar songs with a match %.

## Notes
- Re-run `preprocess.py` any time you update the CSVs.
- On Mac, use `python3` / `pip3` (not `python` / `pip`).
- Big headphone hero illustration + lavender theme included.
- Spotify search links are included per recommended song (external links only,
  no API key required for these).
