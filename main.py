from playlist_builder import build_playlist


def main():
    print("=== doorstep — Venue Playlist Builder ===\n")

    artist_names: list[str] = []
    print("Enter artist names one at a time. Type 'done' when finished.\n")
    while True:
        name = input("Enter artist name (or 'done' to finish): ").strip()
        if name.lower() == "done":
            break
        if name:
            artist_names.append(name)

    if not artist_names:
        print("No artists entered. Exiting.")
        return

    playlist_name = input("\nEnter playlist name: ").strip()
    if not playlist_name:
        playlist_name = "Doorstep Playlist"

    print("\nBuilding playlist...\n")
    url = build_playlist(artist_names, playlist_name)

    if url:
        print(f"\nPlaylist ready: {url}")


if __name__ == "__main__":
    main()
