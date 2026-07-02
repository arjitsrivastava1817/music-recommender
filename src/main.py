"""
Instant Music Recommender - Spotify Live Edition

Instead of a static CSV dataset, this version searches Spotify's real
catalog live using the Spotify Web API (Client Credentials flow).

Note on scope: Spotify deprecated its audio-features and recommendations
endpoints for new apps in late 2024, so true "audio-similarity" recommendations
are no longer possible via the official API. This app instead offers:
  - Live search across Spotify's catalog (biased toward the Indian market)
  - An embedded official Spotify player for each result
  - "More from this artist" / "More from this album" as the recommendation angle

Requires a free Spotify Developer app (Client ID + Client Secret).
See README.md for setup instructions.
"""

import time
import base64
import requests
import streamlit as st
import streamlit.components.v1 as components

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Instant Music Recommender",
    page_icon="🎧",
    layout="centered",
)

# ---------------------------------------------------------------------------
# PWA support — manifest, icons, theme-color (lets phones "Add to Home Screen")
# ---------------------------------------------------------------------------
components.html(
    """
    <script>
    (function() {
        const head = window.parent.document.head;

        function addTag(tagName, attrs) {
            const existing = head.querySelector(
                `${tagName}[rel="${attrs.rel || ''}"][name="${attrs.name || ''}"]`
            );
            if (existing) return;
            const el = document.createElement(tagName);
            Object.entries(attrs).forEach(([k, v]) => el.setAttribute(k, v));
            head.appendChild(el);
        }

        addTag('link', { rel: 'manifest', href: './app/static/manifest.json' });
        addTag('meta', { name: 'theme-color', content: '#6C4AB6' });
        addTag('meta', { name: 'viewport', content: 'width=device-width, initial-scale=1, maximum-scale=1' });
        addTag('link', { rel: 'apple-touch-icon', href: './app/static/icon-192.png' });
        addTag('meta', { name: 'apple-mobile-web-app-capable', content: 'yes' });
        addTag('meta', { name: 'apple-mobile-web-app-title', content: 'MusicRec' });
    })();
    </script>
    """,
    height=0,
)

# ---------------------------------------------------------------------------
# Mobile-responsive tweaks
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @media (max-width: 640px) {
        .stApp { padding: 0.5rem !important; }
        div[data-testid="column"] { min-width: 100% !important; flex: 1 1 100% !important; }
        .song-card .title { font-size: 15px !important; }
        .song-card .meta { font-size: 12px !important; }
        iframe { height: 80px !important; }
    }
    .stButton > button { width: 100%; }
    @media (min-width: 641px) {
        .stButton > button { width: auto; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Styling — lavender theme
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
    .stTextInput > label, .stSelectbox > label {
        color: #2E2148 !important;
        font-weight: 600 !important;
    }
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #B3A2E0 !important;
        border-radius: 10px !important;
    }
    div[data-baseweb="popover"] * {
        color: #FFFFFF !important;
    }
    div[data-baseweb="select"] input, div[data-baseweb="input"] input {
        color: #2E2148 !important;
    }
    .stButton > button {
        background-color: #6C4AB6 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6em 1.4em !important;
        font-weight: 600 !important;
    }
    .stButton > button:hover {
        background-color: #5A3A9E !important;
    }
    .song-card {
        padding: 14px 18px;
        margin-bottom: 12px;
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
        <div style="font-size: 15px; opacity: 0.7; margin-top: 2px;">
            Search Spotify's live Indian music catalog 🎧
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Spotify credentials (never hardcode these in code)
# ---------------------------------------------------------------------------
def get_credentials():
    """Pull Client ID/Secret from Streamlit secrets if present, else sidebar input."""
    client_id = st.secrets.get("SPOTIFY_CLIENT_ID", "") if hasattr(st, "secrets") else ""
    client_secret = st.secrets.get("SPOTIFY_CLIENT_SECRET", "") if hasattr(st, "secrets") else ""

    if not client_id or not client_secret:
        with st.sidebar:
            st.markdown("### 🔑 Spotify API credentials")
            st.caption(
                "Get these free from developer.spotify.com/dashboard. "
                "See README.md for step-by-step instructions."
            )
            client_id = st.text_input("Client ID", value=client_id, type="password")
            client_secret = st.text_input("Client Secret", value=client_secret, type="password")

    return client_id, client_secret


CLIENT_ID, CLIENT_SECRET = get_credentials()

if not CLIENT_ID or not CLIENT_SECRET:
    st.warning(
        "Enter your Spotify Client ID and Client Secret in the sidebar to start searching. "
        "See README.md if you don't have these yet — it only takes a couple of minutes to get them."
    )
    st.stop()


# ---------------------------------------------------------------------------
# Spotify auth (Client Credentials flow — no user login needed, search-only)
# ---------------------------------------------------------------------------
@st.cache_data(ttl=3300, show_spinner=False)  # token lasts 3600s, refresh a bit early
def get_access_token(client_id, client_secret):
    auth_str = f"{client_id}:{client_secret}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()

    resp = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={
            "Authorization": f"Basic {b64_auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={"grant_type": "client_credentials"},
        timeout=10,
    )
    if resp.status_code != 200:
        return None, resp.text
    return resp.json().get("access_token"), None


token, auth_error = get_access_token(CLIENT_ID, CLIENT_SECRET)

if not token:
    st.error(
        "Couldn't authenticate with Spotify. Double-check your Client ID and Client Secret "
        "in the sidebar."
    )
    if auth_error:
        with st.expander("Error details"):
            st.code(auth_error)
    st.stop()


def spotify_get(endpoint, params=None):
    resp = requests.get(
        f"https://api.spotify.com/v1/{endpoint}",
        headers={"Authorization": f"Bearer {token}"},
        params=params or {},
        timeout=10,
    )
    if resp.status_code == 401:
        st.cache_data.clear()  # token expired mid-session, force refresh next run
        st.error("Session expired, please rerun your search.")
        return None
    if resp.status_code != 200:
        st.error(f"Spotify API error ({resp.status_code}). Try again in a moment.")
        return None
    return resp.json()


# ---------------------------------------------------------------------------
# Search UI
# ---------------------------------------------------------------------------
GENRE_HINTS = {
    "All Indian music": "",
    "Bollywood / Hindi": "bollywood hindi",
    "Punjabi": "punjabi",
    "Tamil": "tamil kollywood",
    "Telugu": "telugu tollywood",
    "Marathi": "marathi",
    "Bengali": "bengali",
    "Devotional": "bhakti devotional",
    "Indian Pop": "indian pop",
}

st.markdown("🎵 **Search for a song:**")
col1, col2 = st.columns([2, 1])
with col1:
    query = st.text_input("Song name", placeholder="e.g. Kesariya, Tum Hi Ho, Naatu Naatu...", label_visibility="collapsed")
with col2:
    genre_choice = st.selectbox("Style", options=list(GENRE_HINTS.keys()), label_visibility="collapsed")

search_clicked = st.button("🔍 Search Spotify")

st.caption("Try: " + " · ".join(["Kesariya", "Tum Hi Ho", "Chaiyya Chaiyya", "Naatu Naatu", "Kal Ho Naa Ho"]))


def search_tracks(query_text, genre_hint, limit=10):
    full_query = f"{query_text} {genre_hint}".strip()
    data = spotify_get(
        "search",
        params={"q": full_query, "type": "track", "market": "IN", "limit": limit},
    )
    if not data:
        return []
    return data.get("tracks", {}).get("items", [])


def render_track_card(track, badge=""):
    name = track["name"]
    artists = ", ".join(a["name"] for a in track["artists"])
    album = track["album"]["name"]
    album_art = track["album"]["images"][0]["url"] if track["album"]["images"] else None
    spotify_url = track["external_urls"]["spotify"]
    track_id = track["id"]
    popularity = track.get("popularity", "—")

    cols = st.columns([1, 3])
    with cols[0]:
        if album_art:
            st.image(album_art, use_container_width=True)
    with cols[1]:
        st.markdown(
            f"""
            <div class="song-card">
                <div class="title">🎧 {name} {badge}</div>
                <div class="meta">{artists} &nbsp;•&nbsp; {album} &nbsp;•&nbsp; Popularity: {popularity}</div>
                <div style="margin-top:8px;">
                    <a href="{spotify_url}" target="_blank" style="
                        color:#1DB954 !important; font-weight:600; text-decoration:none; font-size:13px;
                    ">🔗 Open in Spotify</a>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown(
        f"""
        <iframe style="border-radius:12px" src="https://open.spotify.com/embed/track/{track_id}"
            width="100%" height="80" frameborder="0" allowfullscreen=""
            allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
            loading="lazy"></iframe>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)


if search_clicked and query.strip():
    with st.spinner("Searching Spotify..."):
        results = search_tracks(query, GENRE_HINTS[genre_choice])

    if not results:
        st.warning("No results found. Try a different spelling or a broader search term.")
    else:
        st.session_state["last_results"] = results
        st.session_state["last_query"] = query

if "last_results" in st.session_state and st.session_state["last_results"]:
    st.markdown(f"### Results for **{st.session_state['last_query']}**")
    for t in st.session_state["last_results"]:
        render_track_card(t)

    st.markdown("---")
    st.markdown("### 🔁 Discover more")
    pick_names = [f"{t['name']} - {t['artists'][0]['name']}" for t in st.session_state["last_results"]]
    picked = st.selectbox("Pick a track to explore more around it:", options=pick_names)

    if st.button("🚀 Show more like this"):
        picked_track = st.session_state["last_results"][pick_names.index(picked)]
        artist_id = picked_track["artists"][0]["id"]
        album_id = picked_track["album"]["id"]

        with st.spinner("Finding more tracks..."):
            top_tracks_data = spotify_get(f"artists/{artist_id}/top-tracks", params={"market": "IN"})
            album_tracks_data = spotify_get(f"albums/{album_id}/tracks", params={"market": "IN", "limit": 10})

        if top_tracks_data:
            top_tracks = [t for t in top_tracks_data.get("tracks", []) if t["id"] != picked_track["id"]][:5]
            if top_tracks:
                st.markdown(f"**More from {picked_track['artists'][0]['name']}:**")
                for t in top_tracks:
                    render_track_card(t)

        if album_tracks_data:
            album_track_items = album_tracks_data.get("items", [])
            other_album_tracks = [t for t in album_track_items if t["id"] != picked_track["id"]][:5]
            if other_album_tracks:
                st.markdown(f"**Also from the album _{picked_track['album']['name']}_:**")
                for t in other_album_tracks:
                    # album track objects from this endpoint lack 'album'/'popularity' keys — patch them in
                    t["album"] = picked_track["album"]
                    t.setdefault("popularity", "—")
                    render_track_card(t)

st.markdown("---")
st.caption(
    "Powered by the Spotify Web API. Note: Spotify retired its audio-similarity "
    "and recommendations endpoints for new apps in late 2024, so 'more like this' "
    "here is based on the same artist and album rather than audio-feature matching."
)
