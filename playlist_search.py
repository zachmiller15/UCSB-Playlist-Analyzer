import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

QUERIES = [
    "UCSB",
    "UC Santa Barbara",
    "University of California, Santa Barbara",
    "University of California Santa Barbara",
    "Isla Vista",
    "Deltopia"
]

auth_manager = SpotifyClientCredentials(
    client_id="068d3dfa31d0431391104cddbc252aed",
    client_secret="10a2355c48f34fc2934d17e45aa5a20b"
)
sp = spotipy.Spotify(auth_manager=auth_manager)

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