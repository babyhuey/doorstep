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
