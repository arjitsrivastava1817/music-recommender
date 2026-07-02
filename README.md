# Instant Music Recommender — Spotify Live Edition

Searches Spotify's real, live catalog for Indian songs (Bollywood, Punjabi,
Tamil, Telugu, Marathi, Bengali, devotional, Indian pop) instead of a static
CSV file. Shows album art, an embedded Spotify player, and "more from this
artist / album" as the discovery angle.

**Why not audio-similarity like before?** Spotify shut down its
`audio-features` and `recommendations` API endpoints for new developer apps
in late 2024. There is currently no official way for a new app to pull
danceability/energy/tempo-style data or true "similar songs" from Spotify.
This app instead uses what's still available: search, artist top-tracks, and
album tracks.

## 1. Get free Spotify API credentials (one-time setup, ~2 minutes)

1. Go to **https://developer.spotify.com/dashboard**
2. Log in with any Spotify account (free account is fine)
3. Click **Create app**
   - App name: anything, e.g. "My Music Recommender"
   - App description: anything, e.g. "Personal project"
   - Redirect URI: `http://localhost:8501` (required field, but this app doesn't use it)
   - Check the box agreeing to the terms
4. Click **Save**
5. On your new app's page, click **Settings**
6. Copy your **Client ID**
7. Click **View client secret** and copy your **Client Secret**

Keep these private — don't share them or commit them to GitHub.

## 2. Run locally

```bash
pip3 install -r requirements.txt
cd src
streamlit run main.py
```

When the app opens in your browser, paste your Client ID and Client Secret
into the sidebar fields. That's it — no preprocessing step needed this time,
since there's no offline dataset to build.

## 3. (Optional) Avoid re-entering credentials every time

Create a real secrets file locally:
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```
Then edit `.streamlit/secrets.toml` and fill in your real Client ID/Secret.
The app will pick these up automatically and skip the sidebar prompt.

**Important:** `.streamlit/secrets.toml` should never be committed to GitHub.
Add it to `.gitignore` (already included in this project).

## 4. Deploying to Streamlit Cloud

1. Push this project to GitHub as before (the `.streamlit/secrets.toml` file
   itself should NOT be pushed — only the `.example` version)
2. On share.streamlit.io, after creating the app, go to
   **Manage app → Settings → Secrets**
3. Paste in:
   ```
   SPOTIFY_CLIENT_ID = "your-client-id-here"
   SPOTIFY_CLIENT_SECRET = "your-client-secret-here"
   ```
4. Save — the deployed app will now authenticate automatically without
   showing the sidebar prompt to visitors.

## 5. Install as an app on your phone (PWA)

Once deployed (or even running locally on the same network), you can add this
app to your phone's home screen so it opens full-screen like a native app:

**On iPhone (Safari):**
1. Open your deployed app URL in Safari
2. Tap the **Share** icon (square with an arrow)
3. Scroll down and tap **"Add to Home Screen"**
4. Tap **Add**

**On Android (Chrome):**
1. Open your deployed app URL in Chrome
2. Tap the **⋮** menu (top right)
3. Tap **"Add to Home screen"** or **"Install app"**
4. Confirm

The app icon, name, and theme color are already configured via
`static/manifest.json`. No app store submission needed for this — it installs
directly from the browser.

**Note:** this works best once the app is deployed to a real URL (e.g.
Streamlit Cloud), since phones need to reach it over the internet. It won't
work with `localhost` on your own machine unless your phone is on the same
network and you use your computer's local IP address instead of `localhost`.


- Results are biased toward the Indian Spotify market (`market=IN`) and a
  genre/style dropdown to narrow results (Bollywood, Punjabi, Tamil, etc.)
- The embedded player is Spotify's own official widget — playback requires
  the listener to have (or log into) a Spotify account, per Spotify's rules.
- If you see "Spotify API error", it's usually a temporary rate limit —
  wait a few seconds and search again.
