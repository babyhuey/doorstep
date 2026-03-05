from typing import Callable

from spotify_client import SpotifyClient
from youtube_client import YouTubeClient


def _build(
    platform: str,
    artist_names: list[str],
    playlist_name: str,
    items_per_artist: int,
    search_fn: Callable[[str, int], list[str]],
    create_fn: Callable[[str, str], str],
    add_fn: Callable[[str, list[str]], None],
    delete_fn: Callable[[str], None],
    url_fn: Callable[[str], str],
    item_label: str,
) -> str | None:
    items: list[str] = []
    found: list[str] = []
    not_found: list[str] = []

    for name in artist_names:
        result = search_fn(name, items_per_artist)
        if result:
            items.extend(result)
            found.append(f"{name} ({len(result)} {item_label})")
        else:
            not_found.append(name)

    if not items:
        print(f"No {item_label} found. {platform} playlist not created.")
        return None

    description = f"Built by doorstep — {len(found)} artist(s)"
    playlist_id = create_fn(playlist_name, description)

    try:
        add_fn(playlist_id, items)
    except Exception as e:
        print(f"[error] Failed to add {item_label} to {platform} playlist: {e}")
        print(f"[error] Cleaning up empty playlist...")
        delete_fn(playlist_id)
        return None

    print(f"\n{platform} playlist summary:")
    for entry in found:
        print(f"  + {entry}")
    if not_found:
        print(f"  Not found on {platform}:")
        for name in not_found:
            print(f"    - {name}")

    return url_fn(playlist_id)


def build_playlist(
    artist_names: list[str],
    playlist_name: str,
    tracks_per_artist: int = 2,
) -> str | None:
    client = SpotifyClient()

    def search(name: str, n: int) -> list[str]:
        artist_id = client.search_artist(name)
        if artist_id is None:
            return []
        return client.get_top_tracks(artist_id, n=n)

    return _build(
        platform="Spotify",
        artist_names=artist_names,
        playlist_name=playlist_name,
        items_per_artist=tracks_per_artist,
        search_fn=search,
        create_fn=client.create_playlist,
        add_fn=client.add_tracks,
        delete_fn=client.delete_playlist,
        url_fn=lambda pid: f"https://open.spotify.com/playlist/{pid}",
        item_label="tracks",
    )


def build_youtube_playlist(
    artist_names: list[str],
    playlist_name: str,
    videos_per_artist: int = 2,
) -> str | None:
    client = YouTubeClient()

    def noop_delete(playlist_id: str) -> None:
        pass  # YouTube playlist deletion requires a separate API call not worth implementing here

    return _build(
        platform="YouTube",
        artist_names=artist_names,
        playlist_name=playlist_name,
        items_per_artist=videos_per_artist,
        search_fn=client.search_videos,
        create_fn=client.create_playlist,
        add_fn=client.add_videos,
        delete_fn=noop_delete,
        url_fn=lambda pid: f"https://www.youtube.com/playlist?list={pid}",
        item_label="videos",
    )
