import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv
import pylast
import csv
import json
import time

SPOTIFY_CACHE_FILE = "spotify_track_cache.json"
LASTFM_CACHE_FILE = "lastfm_tag_cache.json"
MAX_NEW_SPOTIFY_CALLS = 500

load_dotenv()

auth_manager = SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
)

sp = spotipy.Spotify(auth_manager=auth_manager)

network = pylast.LastFMNetwork(api_key=os.getenv("LAST_FM_API_KEY"))

def load_json_cache(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)

    return {}

def save_json_cache(filename, cache):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(cache, file, ensure_ascii=False, indent=2)

spotify_cache = load_json_cache(SPOTIFY_CACHE_FILE)
lastfm_cache = load_json_cache(LASTFM_CACHE_FILE)

new_spotify_calls = 0
def get_spotify_track_cached(track_id):
    global new_spotify_calls

    if track_id in spotify_cache:
        return spotify_cache[track_id]

    if new_spotify_calls >= MAX_NEW_SPOTIFY_CALLS:
        return "STOP_LIMIT"

    while True:
        try:
            track = sp.track(track_id, market="US")
            spotify_cache[track_id] = track
            save_json_cache(SPOTIFY_CACHE_FILE, spotify_cache)
            new_spotify_calls += 1
            time.sleep(2)
            return track

        except Exception as e:
            error_message = str(e).lower()

            if "rate limit" in error_message or "429" in error_message:
                print("Spotify rate limit hit. Waiting 60 seconds...")
                time.sleep(60)
            else:
                print(f"Spotify failed for {track_id}: {e}")
                return None

def get_lastfm_genres_cached(artist_name, song_name):
    key = f"{artist_name.lower().strip()}|||{song_name.lower().strip()}"

    if key in lastfm_cache:
        return lastfm_cache[key]

    try:
        tags = network.get_track(artist_name, song_name).get_top_tags(limit=10)
        genres = [tag.item.name for tag in tags][:5]

    except Exception as e:
        print(f"No known genre for song {song_name} by primary artist {artist_name}")
        genres = []

    while len(genres) < 5:
        genres.append("")

    lastfm_cache[key] = genres
    save_json_cache(LASTFM_CACHE_FILE, lastfm_cache)

    return genres

with open("track_ids.txt", "r") as f:
    track_ids = [x[:-1] for x in f.readlines()] # remove new lines

track_counts = {}

for track_id in track_ids:
    if track_id in track_counts:
        track_counts[track_id] += 1
    else:
        track_counts[track_id] = 1

headers = [
    "track_id",
    "name",
    "count",
    "album",
    "artist_1",
    "artist_2",
    "artist_3",
    "duration_ms",
    "explicit",
    "genre_1",
    "genre_2",
    "genre_3",
    "genre_4",
    "genre_5"
]

unique_track_ids = list(track_counts.keys())

print(f"Total track appearances: {len(track_ids)}")
print(f"Unique tracks: {len(unique_track_ids)}")
quit()

track_data = {}

with open("song_info.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(headers)

    num_songs = 0

    for track_id in unique_track_ids:
        track = get_spotify_track_cached(track_id)

        if track == "STOP_LIMIT":
            print("Reached safe Spotify call limit for this run. Stop here and resume later.")
            break

        if track is None:
            continue

        num_songs += 1

        name = track.get("name", "")
        album = track.get("album", {}).get("name", "")
        artists = [artist["name"] for artist in track.get("artists", [])]
        duration_ms = track.get("duration_ms", "")
        explicit = track.get("explicit", "")

        while len(artists) < 3:
            artists.append("")

        genres = get_lastfm_genres_cached(artists[0], name)

        writer.writerow([
            track_id,
            name,
            track_counts[track_id],
            album,
            artists[0],
            artists[1],
            artists[2],
            duration_ms,
            explicit,
            genres[0],
            genres[1],
            genres[2],
            genres[3],
            genres[4]
        ])

        print(f"Inserted song {num_songs}: {name}")

print("Done")
