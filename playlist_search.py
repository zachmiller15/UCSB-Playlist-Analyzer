import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv

QUERIES = [
    "UCSB",
    "UC Santa Barbara",
    "University of California, Santa Barbara",
    "University of California Santa Barbara",
    "Isla Vista",
    "Deltopia"
]

load_dotenv()

auth_manager = SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
)
sp = spotipy.Spotify(auth_manager=auth_manager)

#Returns a list of all playlist IDs that match a search query
def get_playlists(query: str) -> list[str]:
    playlists = set()

    for i in range(0, 1001, 10):
        response = sp.search(
            q = query,
            type = "playlist",
            limit = 10,
            offset=i
        )

        if response["playlists"]["next"] is None:
            break

        for item in response["playlists"]["items"]:
            if item is None:
                break
            
            playlists.add(item["id"])
    
    return playlists

if __name__ == "__main__":
    all_playlists = set()

    for query in QUERIES:
        all_playlists = all_playlists.union(get_playlists(query))

    with open("playlist_ids.txt", "w") as f:
        for playlist_id in all_playlists:
            f.write(playlist_id+'\n')