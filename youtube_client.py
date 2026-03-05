import os
import stat
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Minimal scope: HTTPS-enforced playlist read/write; does not grant full account management
_SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
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

            # Write token with owner-only permissions (0600)
            token_json = credentials.to_json()
            fd = os.open(str(_TOKEN_FILE), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            try:
                os.write(fd, token_json.encode())
            finally:
                os.close(fd)

        self.youtube = build("youtube", "v3", credentials=credentials)

    def search_videos(self, artist: str, n: int = 2) -> list[str]:
        try:
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
        except HttpError as e:
            print(f"  [warning] YouTube search failed for {artist!r}: {e}")
            return []

    def create_playlist(self, name: str, description: str = "") -> str:
        response = (
            self.youtube.playlists()
            .insert(
                part="snippet,status",
                body={
                    # YouTube enforces a 150-char title limit
                    "snippet": {"title": name[:150], "description": description},
                    "status": {"privacyStatus": "private"},
                },
            )
            .execute()
        )
        return response["id"]

    def add_videos(self, playlist_id: str, video_ids: list[str]) -> None:
        failed = 0
        for video_id in video_ids:
            try:
                self.youtube.playlistItems().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "playlistId": playlist_id,
                            "resourceId": {
                                "kind": "youtube#video",
                                "videoId": video_id,
                            },
                        }
                    },
                ).execute()
            except HttpError as e:
                failed += 1
                print(f"  [warning] Could not add video {video_id}: {e}")
        if failed:
            print(
                f"  [warning] {failed} video(s) could not be added (region-locked or removed)."
            )
