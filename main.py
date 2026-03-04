import sys
from datetime import date

from playlist_builder import build_playlist, build_youtube_playlist


def _next_month(d: date) -> date:
    if d.month == 12:
        return d.replace(year=d.year + 1, month=1, day=1)
    return d.replace(month=d.month + 1, day=1)


def _pick_month() -> date:
    today = date.today()
    nxt = _next_month(today)
    print("\nWhich month?")
    print(f"  1. This month ({today.strftime('%B %Y')}) (default)")
    print(f"  2. Next month ({nxt.strftime('%B %Y')})")
    choice = input("\nChoice [1/2]: ").strip()
    return nxt if choice == "2" else today


def _manual_mode() -> tuple[str, list[str], date]:
    month = _pick_month()
    artist_names: list[str] = []
    print("\nEnter artist names one at a time. Type 'done' when finished.\n")
    while True:
        name = input("Enter artist name (or 'done' to finish): ").strip()
        if name.lower() == "done":
            break
        if name:
            artist_names.append(name)
    return "", artist_names, month


def _url_mode(url: str = "") -> tuple[str, list[str], date]:
    from venue_parser import fetch_artists_from_url

    if not url:
        url = input("Venue event page URL: ").strip()
    if not url:
        print("No URL entered.")
        return "", [], date.today()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    month = _pick_month()
    print(f"\nFetching and parsing page (filtering to {month.strftime('%B %Y')})...")
    try:
        venue_name, artists = fetch_artists_from_url(url, month=month)
    except Exception as e:
        print(f"Error parsing page: {e}")
        return "", [], month

    if not artists:
        print("No artists found on that page.")
        return "", [], month

    print(f"\nFound {len(artists)} artist(s) at {venue_name}:")
    for a in artists:
        print(f"  - {a}")

    return venue_name, artists, month


def _select_platforms() -> set[str]:
    print("\nWhich platform(s)?")
    print("  1. Spotify (default)")
    print("  2. YouTube")
    print("  3. Both")
    choice = input("\nChoice [1/2/3]: ").strip()
    if choice == "2":
        return {"youtube"}
    if choice == "3":
        return {"spotify", "youtube"}
    return {"spotify"}


def main():
    cli_url = sys.argv[1] if len(sys.argv) > 1 else ""

    print("=== doorstep — Venue Playlist Builder ===\n")

    if cli_url:
        venue_name, artist_names, selected_month = _url_mode(url=cli_url)
    else:
        print("How do you want to add artists?")
        print("  1. Enter names manually")
        print("  2. Parse a venue webpage")
        choice = input("\nChoice [1/2]: ").strip()

        if choice == "2":
            venue_name, artist_names, selected_month = _url_mode()
        else:
            venue_name, artist_names, selected_month = _manual_mode()

    if not artist_names:
        print("No artists entered. Exiting.")
        return

    platforms = _select_platforms()

    if venue_name:
        playlist_name = f"{venue_name} — {selected_month.strftime('%B %Y')}"
        print(f"\nPlaylist name: {playlist_name}")
    else:
        playlist_name = input("\nEnter playlist name: ").strip() or "Doorstep Playlist"

    print("\nBuilding playlist(s)...\n")
    urls: dict[str, str] = {}

    if "spotify" in platforms:
        url = build_playlist(artist_names, playlist_name)
        if url:
            urls["Spotify"] = url

    if "youtube" in platforms:
        url = build_youtube_playlist(artist_names, playlist_name)
        if url:
            urls["YouTube"] = url

    if urls:
        print("\nPlaylists ready:")
        for platform, url in urls.items():
            print(f"  {platform}: {url}")


if __name__ == "__main__":
    main()
