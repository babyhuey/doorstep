# doorstep

Paste a venue's event page URL and doorstep automatically builds you a playlist — on Spotify, YouTube, or both — from that month's performing artists.

## How it works

1. You give it a venue URL (or type artist names manually)
2. A headless browser renders the page so JavaScript-loaded content is visible
3. Claude reads the page and extracts artist names + show dates
4. Shows are filtered to the month you choose (this month or next)
5. Top tracks are pulled for each artist and added to a playlist (or an existing one is updated)

## Features

- **Venue page parsing** — works on any site, including JS-heavy ones, via Playwright
- **Smart date filtering** — pick this month or next month; duplicate artists are removed automatically
- **Multi-artist splitting** — entries like `Artist A / Artist B` are split into individual artists
- **Playlist updates** — re-running with the same venue/month updates the existing playlist and shows what changed (added/removed artists)
- **Not-found report** — artists that couldn't be found on any platform are listed at the end
- **Multi-platform** — create playlists on Spotify, YouTube, or both at once
- **Auto-named playlists** — named from the page title and month, e.g. `Motorco Music Hall — March 2026`
- **CLI shortcut** — pass a URL directly: `python main.py motorcomusic.com`
- **Manual mode** — type artist names yourself if you don't have a URL

## Setup

### 1. Install dependencies

```bash
pip install poetry
poetry install
```

### 2. Configure environment variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

**Spotify** — create an app at [developer.spotify.com](https://developer.spotify.com/dashboard):
```
SPOTIFY_CLIENT_ID=...
SPOTIFY_CLIENT_SECRET=...
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
```

**Anthropic** — get a key at [console.anthropic.com](https://console.anthropic.com):
```
ANTHROPIC_API_KEY=...
```

**YouTube** *(optional)* — create an OAuth 2.0 Client ID (Desktop app) in [Google Cloud Console](https://console.cloud.google.com) with the YouTube Data API v3 enabled, then download `client_secrets.json` into the project folder.

### 3. Install pre-commit hooks

```bash
poetry run pre-commit install
```

## Usage

```bash
# Interactive
poetry run python main.py

# Pass a URL directly
poetry run python main.py motorcomusic.com
```

### Example session

```
=== doorstep — Venue Playlist Builder ===

How do you want to add artists?
  1. Enter names manually
  2. Parse a venue webpage

Choice [1/2]: 2
Venue event page URL: motorcomusic.com

Which month?
  1. This month (March 2026) (default)
  2. Next month (April 2026)

Choice [1/2]: 1

Fetching and parsing page (filtering to March 2026)...

Found 8 artist(s) at Motorco Music Hall:
  - Wednesday
  - Waxahatchee
  - Indigo De Souza
  ...

Which platform(s)?
  1. Spotify (default)
  2. YouTube
  3. Both

Choice [1/2/3]: 3

Playlist name: Motorco Music Hall — March 2026

Playlists ready:
  Spotify: https://open.spotify.com/playlist/...
  YouTube: https://www.youtube.com/playlist?list=...
```

## CI

Every push runs a [Black](https://github.com/psf/black) formatting check via GitHub Actions. Dependency vulnerability scanning is handled by [Dependabot](https://docs.github.com/en/code-security/dependabot), which opens PRs automatically for outdated or vulnerable packages.

Black also runs locally on every `git commit` via pre-commit.
