from spotify_client import SpotifyClient
from youtube_client import YouTubeClient


def build_playlist(
    artist_names: list[str],
    playlist_name: str,
    tracks_per_artist: int = 2,
) -> tuple[str | None, list[str]]:
    client = SpotifyClient()
    track_uris: list[str] = []
    found: list[str] = []
    found_names: set[str] = set()
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
            found_names.add(name.lower())
        else:
            not_found.append(name)

    if not track_uris:
        print("No tracks found. Playlist not created.")
        return None, not_found

    description = f"Built by doorstep — {len(found)} artist(s)"
    existing_id = client.find_playlist(playlist_name)

    if existing_id:
        old_artists = client.get_playlist_artists(existing_id)
        added = found_names - old_artists
        removed = old_artists - found_names

        print(f"Updating existing Spotify playlist: {playlist_name}")
        client.replace_tracks(existing_id, track_uris)
        playlist_id = existing_id

        if added:
            print(f"\n  Added ({len(added)}):")
            for name in sorted(added):
                print(f"    + {name}")
        if removed:
            print(f"\n  Removed ({len(removed)}):")
            for name in sorted(removed):
                print(f"    - {name}")
        if not added and not removed:
            print("  No artist changes.")
    else:
        print(f"Creating new Spotify playlist: {playlist_name}")
        playlist_id = client.create_playlist(playlist_name, description)
        client.add_tracks(playlist_id, track_uris)

        print("\nPlaylist summary:")
        for entry in found:
            print(f"  + {entry}")

    playlist_url = f"https://open.spotify.com/playlist/{playlist_id}"
    return playlist_url, not_found


def build_youtube_playlist(
    artist_names: list[str],
    playlist_name: str,
    videos_per_artist: int = 2,
) -> tuple[str | None, list[str]]:
    client = YouTubeClient()
    video_ids: list[str] = []
    found: list[str] = []
    found_names: set[str] = set()
    not_found: list[str] = []

    for name in artist_names:
        videos = client.search_videos(name, n=videos_per_artist)
        if videos:
            video_ids.extend(videos)
            found.append(f"{name} ({len(videos)} videos)")
            found_names.add(name.lower())
        else:
            not_found.append(name)

    if not video_ids:
        print("No videos found. YouTube playlist not created.")
        return None, not_found

    description = f"Built by doorstep — {len(found)} artist(s)"
    existing_id = client.find_playlist(playlist_name)

    if existing_id:
        old_titles = client.get_playlist_video_titles(existing_id)
        old_artists: set[str] = set()
        for title in old_titles:
            # Video titles are usually "Artist - Song", extract artist portion
            if " - " in title:
                old_artists.add(title.split(" - ")[0].strip().lower())

        added = found_names - old_artists
        removed = old_artists - found_names

        print(f"Updating existing YouTube playlist: {playlist_name}")
        client.clear_playlist(existing_id)
        client.add_videos(existing_id, video_ids)
        playlist_id = existing_id

        if added:
            print(f"\n  Added ({len(added)}):")
            for name in sorted(added):
                print(f"    + {name}")
        if removed:
            print(f"\n  Removed ({len(removed)}):")
            for name in sorted(removed):
                print(f"    - {name}")
        if not added and not removed:
            print("  No artist changes.")
    else:
        print(f"Creating new YouTube playlist: {playlist_name}")
        playlist_id = client.create_playlist(playlist_name, description)
        client.add_videos(playlist_id, video_ids)

        print("\nYouTube playlist summary:")
        for entry in found:
            print(f"  + {entry}")

    return f"https://www.youtube.com/playlist?list={playlist_id}", not_found
