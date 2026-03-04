import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()


class SpotifyClient:
    def __init__(self):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback"),
            scope="playlist-modify-public playlist-modify-private",
        ))
        self.user_id = self.sp.current_user()["id"]

    def search_artist(self, name: str) -> str | None:
        results = self.sp.search(q=f"artist:{name}", type="artist", limit=1)
        items = results["artists"]["items"]
        if not items:
            return None
        return items[0]["id"]

    def get_top_tracks(self, artist_id: str, n: int = 3) -> list[str]:
        results = self.sp.artist_top_tracks(artist_id, country="US")
        tracks = results["tracks"][:n]
        return [t["uri"] for t in tracks]

    def create_playlist(self, name: str, description: str = "") -> str:
        playlist = self.sp.user_playlist_create(
            self.user_id, name, public=True, description=description
        )
        return playlist["id"]

    def add_tracks(self, playlist_id: str, track_uris: list[str]) -> None:
        # Spotify API accepts max 100 tracks per request
        for i in range(0, len(track_uris), 100):
            self.sp.playlist_add_items(playlist_id, track_uris[i:i + 100])
