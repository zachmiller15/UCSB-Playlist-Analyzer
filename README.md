Queries searched:
"UCSB",
"UC Santa Barbara",
"University of California, Santa Barbara",
"University of California Santa Barbara",
"Isla Vista",
"Deltopia"

The final playlist text has been manually filtered (cut by ~250-300 playlists).
JSONs were for partial storing of data between requests.
song_info.csv has all relevant data.

---

## Visualizations

Open `graphs/dashboard.html` to view all charts. Run `create_visualizations.py` to regenerate them.

### Top 30 Most Recurring Songs
Horizontal bar chart of the top 30 songs ranked by how many playlists they appear in. Each bar is colored along a green gradient scaled to its count, so the most-played songs read as the brightest. Hover over any bar to see the full song title, artist, and exact playlist count.

### Top 40 Artists by Playlist Presence
Treemap of the top 40 artists sized and colored by their total appearances across all playlists. Artists with the most collective presence occupy the largest tiles. Useful for seeing at a glance which names dominate the dataset and how steeply the drop-off is after the top tier.

### Top 30 Genres
Treemap of the top 30 genre tags across all songs, drawn from up to five genre columns per track. Tile size reflects how frequently each genre appears as a tag. Because songs can carry multiple genre labels, this chart captures the full stylistic range of the dataset rather than just the primary genre.

### Song Duration Distribution
Histogram showing how song lengths are spread across the dataset, bucketed into roughly 10-second intervals. A dashed line marks the average duration. The distribution reveals whether the collection skews toward short radio edits, standard album tracks, or longer DJ-style cuts.

### Explicit vs Clean
Donut chart showing the split between explicit and clean tracks. The center displays the total song count. Gives a quick read on the overall tone of the playlists and how that might reflect the age and context of the audience curating them.

### Top 20 Albums by Playlist Presence
Horizontal bar chart of the top 20 albums ranked by combined playlist appearances across all their tracks. A high-ranking album here means multiple songs from it recur across different playlists, indicating stronger overall album-level affinity rather than a single breakout track.