import os

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()


class SpotifyClient:
    def __init__(self):
        client_id = os.environ.get("SPOTIFY_CLIENT_ID")
        client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
        if not client_id or not client_secret:
            raise RuntimeError(
                "SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set in your .env file."
            )

        self.sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=os.getenv(
                    "SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback"
                ),
                scope="playlist-modify-public playlist-modify-private",
            )
        )
        try:
            self.user_id = self.sp.current_user()["id"]
        except Exception as e:
            raise RuntimeError(f"Could not authenticate with Spotify: {e}")

    def search_artist(self, name: str) -> str | None:
        try:
            results = self.sp.search(q=f"artist:{name}", type="artist", limit=1)
            items = results.get("artists", {}).get("items", [])
            return items[0]["id"] if items else None
        except spotipy.SpotifyException as e:
            print(f"  [warning] Spotify search failed for {name!r}: {e}")
            return None

    def get_top_tracks(self, artist_id: str, n: int = 2) -> list[str]:
        try:
            results = self.sp.artist_top_tracks(artist_id, country="US")
            tracks = results.get("tracks", [])[:n]
            return [t["uri"] for t in tracks]
        except spotipy.SpotifyException as e:
            print(f"  [warning] Could not fetch top tracks: {e}")
            return []

    def find_playlist(self, name: str) -> str | None:
        """Find an existing playlist by exact name. Returns playlist ID or None."""
        offset = 0
        while True:
            results = self.sp.current_user_playlists(limit=50, offset=offset)
            for item in results["items"]:
                if item["name"] == name and item["owner"]["id"] == self.user_id:
                    return item["id"]
            if results["next"] is None:
                return None
            offset += 50

    def create_playlist(self, name: str, description: str = "") -> str:
        # Spotify enforces a 100-char title limit
        playlist = self.sp.user_playlist_create(
            self.user_id, name[:100], public=False, description=description
        )
        return playlist["id"]

    def get_playlist_artists(self, playlist_id: str) -> set[str]:
        """Return the set of artist names currently in a playlist (lowercased)."""
        artists: set[str] = set()
        offset = 0
        while True:
            results = self.sp.playlist_items(
                playlist_id,
                fields="items.track.artists.name,next",
                limit=100,
                offset=offset,
            )
            for item in results.get("items", []):
                track = item.get("track")
                if track:
                    for artist in track.get("artists", []):
                        artists.add(artist["name"].lower())
            if results.get("next") is None:
                break
            offset += 100
        return artists

    def replace_tracks(self, playlist_id: str, track_uris: list[str]) -> None:
        """Replace all tracks in a playlist."""
        # First batch via replace (clears existing), rest via add
        self.sp.playlist_replace_items(playlist_id, track_uris[:100])
        for i in range(100, len(track_uris), 100):
            self.sp.playlist_add_items(playlist_id, track_uris[i : i + 100])

    def delete_playlist(self, playlist_id: str) -> None:
        try:
            self.sp.current_user_unfollow_playlist(playlist_id)
        except spotipy.SpotifyException:
            pass

    def add_tracks(self, playlist_id: str, track_uris: list[str]) -> None:
        for i in range(0, len(track_uris), 100):
            self.sp.playlist_add_items(playlist_id, track_uris[i : i + 100])
