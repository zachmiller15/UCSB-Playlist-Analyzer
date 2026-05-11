import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


PLAYLIST_FILE = "playlist_ids.txt"
OUTPUT_FILE = "spotify_track_ids.txt"

RECOMMENDED_SONG_COUNT = 10
STABLE_SCROLL_LIMIT = 2
STEP_SIZE = 350
MAX_SCROLLS = 2000


def get_playlist_id(line):
    line = line.strip()

    if line == "":
        return None

    match = re.search(r"/playlist/([A-Za-z0-9]+)", line)

    if match:
        return match.group(1)

    return line


def load_playlist_ids(filename):
    playlist_ids = []

    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            playlist_id = get_playlist_id(line)

            if playlist_id is not None:
                playlist_ids.append(playlist_id)

    return playlist_ids


def extract_track_ids(driver):
    hrefs = driver.execute_script(
        """
        return Array.from(document.querySelectorAll('a[href*="/track/"]'))
            .map(link => link.href);
        """
    )

    track_ids = []

    for href in hrefs:
        if href is None:
            continue

        match = re.search(r"/track/([A-Za-z0-9]+)", href)

        if match:
            track_ids.append(match.group(1))

    return track_ids


def get_best_scroll_container(driver):
    script = """
    const candidates = [document.scrollingElement, ...document.querySelectorAll('*')];

    let best = document.scrollingElement;
    let bestScrollableDistance = 0;

    for (const element of candidates) {
        if (!element) {
            continue;
        }

        const scrollableDistance = element.scrollHeight - element.clientHeight;

        if (scrollableDistance > bestScrollableDistance) {
            bestScrollableDistance = scrollableDistance;
            best = element;
        }
    }

    return best;
    """

    return driver.execute_script(script)


def get_scroll_top(driver, container):
    return driver.execute_script(
        "return arguments[0].scrollTop;",
        container
    )


def scroll_to_position(driver, container, position):
    driver.execute_script(
        "arguments[0].scrollTop = arguments[1];",
        container,
        position
    )


def scrape_playlist(driver, playlist_id):
    playlist_url = f"https://open.spotify.com/playlist/{playlist_id}"

    driver.get(playlist_url)
    time.sleep(4)

    container = get_best_scroll_container(driver)

    all_track_ids = []
    seen = set()

    last_count = 0
    stable_rounds = 0

    for scroll_number in range(MAX_SCROLLS):
        current_ids = extract_track_ids(driver)

        for track_id in current_ids:
            if track_id not in seen:
                seen.add(track_id)
                all_track_ids.append(track_id)

        print(f"Playlist {playlist_id}, scroll {scroll_number}: found {len(all_track_ids)} unique track IDs")

        if len(all_track_ids) == last_count:
            stable_rounds += 1
        else:
            stable_rounds = 0

        last_count = len(all_track_ids)

        if stable_rounds >= STABLE_SCROLL_LIMIT:
            print(f"No new track IDs after {STABLE_SCROLL_LIMIT} scrolls. Stopping this playlist.")
            break

        scroll_top = get_scroll_top(driver, container)
        new_position = scroll_top + STEP_SIZE
        scroll_to_position(driver, container, new_position)

        time.sleep(1)

    if len(all_track_ids) > RECOMMENDED_SONG_COUNT:
        playlist_track_ids = all_track_ids[:-RECOMMENDED_SONG_COUNT]
    else:
        playlist_track_ids = all_track_ids

    return playlist_track_ids


def append_tracks_to_file(filename, playlist_id, track_ids):
    with open(filename, "a", encoding="utf-8") as file:
        file.write(f"PLAYLIST {playlist_id}\n")

        for track_id in track_ids:
            file.write(track_id + "\n")

        file.write("\n")


def main():
    playlist_ids = load_playlist_ids(PLAYLIST_FILE)

    print(f"Loaded {len(playlist_ids)} playlists from {PLAYLIST_FILE}")

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument(
        r"--user-data-dir=C:\Users\bigdi\OneDrive\Desktop\Spotify Tracker\chrome_profile"
    )

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get("https://open.spotify.com/")
        time.sleep(2)

        for index, playlist_id in enumerate(playlist_ids, start=1):
            print()
            print(f"Starting playlist {index} of {len(playlist_ids)}: {playlist_id}")

            try:
                track_ids = scrape_playlist(driver, playlist_id)
                append_tracks_to_file(OUTPUT_FILE, playlist_id, track_ids)

                print(f"Appended {len(track_ids)} track IDs for playlist {playlist_id}")

            except Exception as error:
                print(f"Failed on playlist {playlist_id}")
                print(error)

    finally:
        driver.quit()


if __name__ == "__main__":
    main()