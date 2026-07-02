"""
Instant Music Recommender - Streamlit app (v2).

Loads the artifacts produced by preprocess.py and lets the user pick a song,
then recommends the most similar songs based on audio features
(danceability, energy, tempo, valence, etc.) using cosine similarity.
"""

import os
import pickle
import urllib.parse
import pandas as pd
import streamlit as st

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
ARTIFACT_DIR = os.path.join(PROJECT_DIR, "artifacts")

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Instant Music Recommender",
    page_icon="🎧",
    layout="centered",
)

# ---------------------------------------------------------------------------
# Styling — lavender theme + green input text
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(160deg, #E6E0F8 0%, #D8CFF2 45%, #C9BCEB 100%);
    }
    h1, h2, h3, h4, p, span, label, div {
        color: #2E2148 !important;
    }
    .stSelectbox > label, .stSlider > label {
        color: #2E2148 !important;
        font-weight: 600 !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #B3A2E0 !important;
        border-radius: 10px !important;
    }
    div[data-baseweb="popover"] * {
        color: #FFFFFF !important;
    }
    div[data-baseweb="popover"] li:hover,
    ul[role="listbox"] li:hover,
    li[role="option"]:hover {
        background-color: rgba(255,255,255,0.15) !important;
    }
    div[data-baseweb="select"] input {
        color: #2E2148 !important;
    }
    .stButton > button {
        background-color: #6C4AB6 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6em 1.4em !important;
        font-weight: 600 !important;
        transition: background-color 0.2s ease-in-out;
    }
    .stButton > button:hover {
        background-color: #5A3A9E !important;
    }
    .song-card {
        padding: 14px 18px;
        margin-bottom: 10px;
        border-radius: 12px;
        background-color: rgba(255,255,255,0.55);
        border: 1px solid rgba(108,74,182,0.25);
        box-shadow: 0 2px 6px rgba(108,74,182,0.12);
    }
    .song-card .title { font-size: 17px; font-weight: 700; color: #2E2148; }
    .song-card .meta { font-size: 13px; opacity: 0.75; margin-top: 4px; color: #4B3B72; }
    hr { border-color: rgba(108,74,182,0.3) !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Big headphone hero illustration (original artwork, not a brand logo)
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div style="display:flex; justify-content:center; margin-bottom: -10px;">
        <svg width="220" height="220" viewBox="0 0 220 220" xmlns="http://www.w3.org/2000/svg">
            <circle cx="110" cy="110" r="105" fill="#6C4AB6" opacity="0.12"/>
            <circle cx="110" cy="110" r="80" fill="#6C4AB6" opacity="0.18"/>
            <path d="M55 118 V100 a55 55 0 0 1 110 0 v18"
                  stroke="#6C4AB6" stroke-width="12" fill="none" stroke-linecap="round"/>
            <rect x="42" y="112" width="26" height="48" rx="13" fill="#6C4AB6"/>
            <rect x="152" y="112" width="26" height="48" rx="13" fill="#6C4AB6"/>
            <rect x="48" y="122" width="14" height="28" rx="7" fill="#FFFFFF" opacity="0.7"/>
            <rect x="158" y="122" width="14" height="28" rx="7" fill="#FFFFFF" opacity="0.7"/>
            <path d="M100 55 q28 4 30 34" stroke="#B3A2E0" stroke-width="5"
                  fill="none" stroke-linecap="round"/>
            <circle cx="132" cy="46" r="9" fill="#6C4AB6"/>
            <path d="M132 46 V22" stroke="#6C4AB6" stroke-width="5" stroke-linecap="round"/>
            <path d="M132 22 q10 -3 11 8" stroke="#6C4AB6" stroke-width="5"
                  fill="none" stroke-linecap="round"/>
        </svg>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div style="text-align:center; margin-bottom: 20px;">
        <div style="font-size: 36px; font-weight: 800; color:#2E2148;">Instant Music Recommender</div>
        <div style="font-size: 15px; opacity: 0.7; margin-top: 2px;">Find your next favorite song 🎧</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Load artifacts (cached so it only runs once per session)
# ---------------------------------------------------------------------------
@st.cache_resource
def load_artifacts():
    songs_path = os.path.join(ARTIFACT_DIR, "songs.pkl")
    sim_path = os.path.join(ARTIFACT_DIR, "similarity.pkl")

    if not os.path.exists(songs_path) or not os.path.exists(sim_path):
        return None, None

    songs = pd.read_pickle(songs_path)
    with open(sim_path, "rb") as f:
        similarity = pickle.load(f)
    return songs, similarity


songs_df, similarity_matrix = load_artifacts()

if songs_df is None:
    st.error(
        "No processed data found. Please run `python3 preprocess.py` from the "
        "`src` folder first, then restart this app with `streamlit run main.py`."
    )
    st.stop()


# ---------------------------------------------------------------------------
# Recommendation logic
# ---------------------------------------------------------------------------
def recommend(song_display_name, top_n=5):
    idx = songs_df.index[songs_df["display_name"] == song_display_name]
    if len(idx) == 0:
        return pd.DataFrame()
    idx = idx[0]

    scores = list(enumerate(similarity_matrix[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)

    top_matches = [s for s in scores if s[0] != idx][:top_n]

    rec_indices = [i for i, _ in top_matches]
    rec_scores = [round(float(score) * 100, 1) for _, score in top_matches]

    result = songs_df.iloc[rec_indices][
        ["song_name", "display_name", "singer", "language", "popularity"]
    ].copy()
    result["match %"] = rec_scores
    return result.reset_index(drop=True)


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
st.markdown("🎵 **Select a song:**")

language_filter = st.selectbox(
    "Filter by language (optional)",
    options=["All"] + sorted(songs_df["language"].dropna().unique().tolist()),
    label_visibility="collapsed",
)

filtered_df = songs_df if language_filter == "All" else songs_df[songs_df["language"] == language_filter]
song_options = sorted(filtered_df["display_name"].tolist())

selected_song = st.selectbox("Pick a song", options=song_options, label_visibility="collapsed")

num_recs = st.slider("Number of recommendations", min_value=3, max_value=15, value=5)

if st.button("🚀 Recommend Similar Songs", use_container_width=False):
    with st.spinner("Finding songs with a similar vibe..."):
        recs = recommend(selected_song, top_n=num_recs)

    if recs.empty:
        st.warning("Sorry, couldn't find that song. Try another one.")
    else:
        st.markdown(f"### Songs similar to **{selected_song}**")
        for _, row in recs.iterrows():
            singer = row["singer"].split("|")[0] if isinstance(row["singer"], str) else "Unknown"
            search_query = urllib.parse.quote(f"{row['song_name']} {singer}")
            spotify_url = f"https://open.spotify.com/search/{search_query}"
            st.markdown(
                f"""
                <div class="song-card">
                    <div class="title">🎧 {row['display_name']}</div>
                    <div class="meta">
                        {singer} &nbsp;•&nbsp; {row['language']} &nbsp;•&nbsp; Match: {row['match %']}%
                    </div>
                    <div style="margin-top: 8px;">
                        <a href="{spotify_url}" target="_blank" style="
                            display: inline-flex;
                            align-items: center;
                            gap: 6px;
                            font-size: 13px;
                            font-weight: 600;
                            color: #1DB954 !important;
                            text-decoration: none;
                        ">🔗 Find on Spotify</a>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

st.markdown("---")
st.caption(f"Dataset: {len(songs_df)} songs across {songs_df['language'].nunique()} language(s).")
