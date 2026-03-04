from spotify_client import SpotifyClient
from youtube_client import YouTubeClient


def build_playlist(
    artist_names: list[str],
    playlist_name: str,
    tracks_per_artist: int = 2,
) -> str | None:
    client = SpotifyClient()
    track_uris: list[str] = []
    found: list[str] = []
    not_found: list[str] = []

    for name in artist_names:
        artist_id = client.search_artist(name)
        if artist_id is None:
            not_found.append(name)
            continue
        tracks = client.get_top_tracks(artist_id, n=tracks_per_artist)
        if tracks:
            track_uris.extend(tracks)
            found.append(f"{name} ({len(tracks)} tracks)")
        else:
            not_found.append(name)

    if not track_uris:
        print("No tracks found. Playlist not created.")
        return None

    description = f"Built by doorstep — {len(found)} artist(s)"
    playlist_id = client.create_playlist(playlist_name, description)
    client.add_tracks(playlist_id, track_uris)

    print("\nPlaylist summary:")
    for entry in found:
        print(f"  + {entry}")
    if not_found:
        print("  Artists not found:")
        for name in not_found:
            print(f"    - {name}")

    playlist_url = f"https://open.spotify.com/playlist/{playlist_id}"
    return playlist_url


def build_youtube_playlist(
    artist_names: list[str],
    playlist_name: str,
    videos_per_artist: int = 2,
) -> str | None:
    client = YouTubeClient()
    video_ids: list[str] = []
    found: list[str] = []
    not_found: list[str] = []

    for name in artist_names:
        videos = client.search_videos(name, n=videos_per_artist)
        if videos:
            video_ids.extend(videos)
            found.append(f"{name} ({len(videos)} videos)")
        else:
            not_found.append(name)

    if not video_ids:
        print("No videos found. YouTube playlist not created.")
        return None

    description = f"Built by doorstep — {len(found)} artist(s)"
    playlist_id = client.create_playlist(playlist_name, description)
    client.add_videos(playlist_id, video_ids)

    print("\nYouTube playlist summary:")
    for entry in found:
        print(f"  + {entry}")
    if not_found:
        print("  Artists not found:")
        for name in not_found:
            print(f"    - {name}")

    return f"https://www.youtube.com/playlist?list={playlist_id}"
