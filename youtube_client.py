import json
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

_SCOPES = ["https://www.googleapis.com/auth/youtube"]
_TOKEN_FILE = Path(__file__).parent / ".youtube_token.json"
_SECRETS_FILE = Path(__file__).parent / "client_secrets.json"


class YouTubeClient:
    def __init__(self):
        if not _SECRETS_FILE.exists():
            raise FileNotFoundError(
                f"YouTube credentials not found at {_SECRETS_FILE}.\n"
                "Download client_secrets.json from Google Cloud Console:\n"
                "  APIs & Services → Credentials → OAuth 2.0 Client ID → Desktop app\n"
                "Make sure YouTube Data API v3 is enabled in your project."
            )

        credentials = None

        if _TOKEN_FILE.exists():
            credentials = Credentials.from_authorized_user_file(
                str(_TOKEN_FILE), _SCOPES
            )

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(_SECRETS_FILE), _SCOPES
                )
                credentials = flow.run_local_server(port=0)
            _TOKEN_FILE.write_text(credentials.to_json())

        self.youtube = build("youtube", "v3", credentials=credentials)

    def search_videos(self, artist: str, n: int = 3) -> list[str]:
        response = (
            self.youtube.search()
            .list(
                part="id",
                q=f"{artist} official audio",
                type="video",
                maxResults=n,
            )
            .execute()
        )
        return [item["id"]["videoId"] for item in response.get("items", [])]

    def find_playlist(self, name: str) -> str | None:
        """Find an existing playlist by exact title. Returns playlist ID or None."""
        page_token = None
        while True:
            response = (
                self.youtube.playlists()
                .list(part="snippet", mine=True, maxResults=50, pageToken=page_token)
                .execute()
            )
            for item in response.get("items", []):
                if item["snippet"]["title"] == name:
                    return item["id"]
            page_token = response.get("nextPageToken")
            if not page_token:
                return None

    def get_playlist_video_titles(self, playlist_id: str) -> list[str]:
        """Return the list of video titles currently in a playlist."""
        titles: list[str] = []
        page_token = None
        while True:
            response = (
                self.youtube.playlistItems()
                .list(
                    part="snippet",
                    playlistId=playlist_id,
                    maxResults=50,
                    pageToken=page_token,
                )
                .execute()
            )
            for item in response.get("items", []):
                titles.append(item["snippet"]["title"])
            page_token = response.get("nextPageToken")
            if not page_token:
                break
        return titles

    def clear_playlist(self, playlist_id: str) -> None:
        """Remove all items from a playlist."""
        while True:
            response = (
                self.youtube.playlistItems()
                .list(part="id", playlistId=playlist_id, maxResults=50)
                .execute()
            )
            items = response.get("items", [])
            if not items:
                break
            for item in items:
                self.youtube.playlistItems().delete(id=item["id"]).execute()

    def create_playlist(self, name: str, description: str = "") -> str:
        response = (
            self.youtube.playlists()
            .insert(
                part="snippet,status",
                body={
                    "snippet": {"title": name, "description": description},
                    "status": {"privacyStatus": "public"},
                },
            )
            .execute()
        )
        return response["id"]

    def add_videos(self, playlist_id: str, video_ids: list[str]) -> None:
        for video_id in video_ids:
            self.youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {"kind": "youtube#video", "videoId": video_id},
                    }
                },
            ).execute()
