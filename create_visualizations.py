import os
import pandas as pd
import plotly.graph_objects as go
import warnings
warnings.filterwarnings("ignore")

# ── Palette ──────────────────────────────────────────────────────────────────
BG       = "#121212"
CARD_BG  = "#181818"
SURFACE  = "#282828"
TEXT     = "#FFFFFF"
MUTED    = "#B3B3B3"
GREEN    = "#1DB954"
GREEN_D  = "#158a3e"
GREEN_L  = "#1ed760"
PINK     = "#FF6B9D"
PURPLE   = "#A855F7"
TEAL     = "#00C9A7"
CYAN     = "#00D2FF"

COLORSCALE = [[0, GREEN_D], [0.5, GREEN], [1, GREEN_L]]

LAYOUT_BASE = dict(
    paper_bgcolor=BG,
    plot_bgcolor=CARD_BG,
    font=dict(family="'Helvetica Neue', Arial, sans-serif", color=TEXT, size=13),
    title_font=dict(size=22, color=TEXT),
    margin=dict(l=60, r=40, t=80, b=60),
    hoverlabel=dict(bgcolor=SURFACE, font_color=TEXT, font_size=13,
                    bordercolor=GREEN),
)

os.makedirs("graphs", exist_ok=True)

df = pd.read_csv("song_info.csv")
df["duration_min"] = df["duration_ms"] / 60_000

num_playlists = sum(1 for line in open("playlist_ids.txt") if line.strip())


# ── 1. TOP 25 ARTISTS ────────────────────────────────────────────────────────
artist_counts = (
    df.groupby("artist_1")["count"]
    .sum()
    .sort_values(ascending=False)
    .head(25)
    .reset_index()
)
artist_counts.columns = ["Artist", "Total Appearances"]
artist_counts = artist_counts.sort_values("Total Appearances")

fig1 = go.Figure(go.Bar(
    x=artist_counts["Total Appearances"],
    y=artist_counts["Artist"],
    orientation="h",
    marker=dict(
        color=list(range(len(artist_counts))),
        colorscale=COLORSCALE,
        showscale=False,
        line=dict(width=0),
    ),
    text=artist_counts["Total Appearances"],
    textposition="outside",
    textfont=dict(color=MUTED, size=11),
    hovertemplate="<b>%{y}</b><br>Appearances: %{x}<extra></extra>",
))
fig1.update_layout(
    **LAYOUT_BASE,
    title="Top Artists",
    xaxis=dict(showgrid=True, gridcolor=SURFACE,
               title="Total Playlist Appearances", color=MUTED,
               range=[0, artist_counts["Total Appearances"].max() * 1.18]),
    yaxis=dict(showgrid=False, color=TEXT, tickfont=dict(size=12),
               ticksuffix="  "),
    height=700,
    bargap=0.25,
)
fig1.write_html("graphs/01_top_artists.html")
print("✓ 01_top_artists.html")


# ── 2. TOP 30 SONGS ──────────────────────────────────────────────────────────
top_songs = (
    df[["name", "artist_1", "count"]]
    .sort_values("count", ascending=False)
    .head(30)
    .reset_index(drop=True)
)
top_songs["Label"] = top_songs["name"] + "  —  " + top_songs["artist_1"]
top_songs = top_songs.sort_values("count")

fig2 = go.Figure(go.Bar(
    x=top_songs["count"],
    y=top_songs["Label"],
    orientation="h",
    marker=dict(
        color=top_songs["count"],
        colorscale=COLORSCALE,
        showscale=True,
        colorbar=dict(
            title=dict(text="Playlists", font=dict(color=MUTED)),
            tickfont=dict(color=MUTED),
        ),
        line=dict(width=0),
    ),
    text=top_songs["count"],
    textposition="outside",
    textfont=dict(color=MUTED, size=11),
    hovertemplate="<b>%{y}</b><br>Appears in %{x} playlists<extra></extra>",
))
fig2.update_layout(
    **LAYOUT_BASE,
    title="Top 30 Most Recurring Songs",
    xaxis=dict(showgrid=True, gridcolor=SURFACE,
               title="Playlist Appearances", color=MUTED,
               range=[0, top_songs["count"].max() * 1.18]),
    yaxis=dict(showgrid=False, color=TEXT, tickfont=dict(size=10),
               ticksuffix="  "),
    height=900,
    bargap=0.2,
)
fig2.write_html("graphs/02_top_songs.html")
print("✓ 02_top_songs.html")


# ── 3. GENRE TREEMAP ─────────────────────────────────────────────────────────
all_genres = pd.concat(
    [df[c] for c in ["genre_1", "genre_2", "genre_3", "genre_4", "genre_5"]]
).dropna()

genre_counts = all_genres.value_counts().head(40).reset_index()
genre_counts.columns = ["Genre", "Count"]

top_genres = genre_counts.head(30).copy()

fig4 = go.Figure(go.Treemap(
    labels=top_genres["Genre"],
    parents=[""] * len(top_genres),
    values=top_genres["Count"],
    marker=dict(
        colors=top_genres["Count"],
        colorscale=COLORSCALE,
        showscale=False,
        line=dict(width=2, color=BG),
    ),
    textfont=dict(size=14, color=TEXT),
    hovertemplate="<b>%{label}</b><br>Count: %{value}<extra></extra>",
    texttemplate="<b>%{label}</b><br>%{value}",
))
fig4.update_layout(
    **LAYOUT_BASE,
    title="Top 30 Genres",
    height=600,
)
fig4.write_html("graphs/03_genre_treemap.html")
print("✓ 03_genre_treemap.html")


# ── 5. SONG DURATION DISTRIBUTION ────────────────────────────────────────────
fig5 = go.Figure()

fig5.add_trace(go.Histogram(
    x=df["duration_min"],
    nbinsx=60,
    marker=dict(
        color=GREEN,
        opacity=0.85,
        line=dict(width=0.5, color=BG),
    ),
    hovertemplate="Duration: %{x:.2f} min<br>Songs: %{y}<extra></extra>",
    name="Songs",
))

mean_dur = df["duration_min"].mean()
fig5.add_vline(
    x=mean_dur, line_dash="dash", line_color=TEXT, line_width=2,
    annotation_text=f"  avg {mean_dur:.2f} min",
    annotation_font_color=TEXT,
)

fig5.update_layout(
    **LAYOUT_BASE,
    title="Song Duration Distribution",
    xaxis=dict(title="Duration (minutes)", color=MUTED, showgrid=True,
               gridcolor=SURFACE, range=[0, 10]),
    yaxis=dict(title="Number of Songs", color=MUTED, showgrid=True,
               gridcolor=SURFACE),
    height=500,
    showlegend=False,
)
fig5.write_html("graphs/04_duration_distribution.html")
print("✓ 04_duration_distribution.html")


# ── 6. EXPLICIT VS CLEAN DONUT ───────────────────────────────────────────────
exp_counts = df["explicit"].value_counts()
labels = ["Clean", "Explicit"]
values = [exp_counts.get(False, 0), exp_counts.get(True, 0)]

fig6 = go.Figure(go.Pie(
    labels=labels,
    values=values,
    hole=0.6,
    marker=dict(colors=[GREEN, PURPLE], line=dict(color=BG, width=3)),
    textinfo="label+percent",
    textfont=dict(size=14, color=TEXT),
    hovertemplate="<b>%{label}</b><br>Songs: %{value}<br>%{percent}<extra></extra>",
    pull=[0, 0.04],
))
fig6.add_annotation(
    text=f"<b>{len(df):,}</b><br>songs",
    x=0.5, y=0.5, font=dict(size=18, color=TEXT),
    showarrow=False,
)
fig6.update_layout(
    **LAYOUT_BASE,
    title="Explicit vs Clean",
    height=500,
    legend=dict(font=dict(color=TEXT), bgcolor=CARD_BG),
)
fig6.write_html("graphs/05_explicit_donut.html")
print("✓ 05_explicit_donut.html")


# ── 6. ARTIST TREEMAP ────────────────────────────────────────────────────────
top_artists_tm = (
    df.groupby("artist_1")["count"]
    .sum()
    .sort_values(ascending=False)
    .head(40)
    .reset_index()
)
top_artists_tm.columns = ["Artist", "Total"]

fig8 = go.Figure(go.Treemap(
    labels=top_artists_tm["Artist"],
    parents=[""] * len(top_artists_tm),
    values=top_artists_tm["Total"],
    marker=dict(
        colors=top_artists_tm["Total"],
        colorscale=COLORSCALE,
        showscale=False,
        line=dict(width=2, color=BG),
    ),
    textfont=dict(size=13, color=TEXT),
    hovertemplate="<b>%{label}</b><br>Total appearances: %{value}<extra></extra>",
    texttemplate="<b>%{label}</b><br>%{value}",
))
fig8.update_layout(
    **LAYOUT_BASE,
    title="Top 40 Artists by Playlist Presence",
    height=650,
)
fig8.write_html("graphs/06_artist_treemap.html")
print("✓ 06_artist_treemap.html")


# ── 9. TOP ALBUMS BAR ────────────────────────────────────────────────────────
top_albums = (
    df.groupby(["album", "artist_1"])["count"]
    .sum()
    .sort_values(ascending=False)
    .head(20)
    .reset_index()
)
top_albums["Label"] = top_albums["album"] + "  ·  " + top_albums["artist_1"]
top_albums = top_albums.sort_values("count")

fig9 = go.Figure(go.Bar(
    x=top_albums["count"],
    y=top_albums["Label"],
    orientation="h",
    marker=dict(
        color=list(range(len(top_albums))),
        colorscale=COLORSCALE,
        showscale=False,
        line=dict(width=0),
    ),
    text=top_albums["count"],
    textposition="outside",
    textfont=dict(color=MUTED, size=11),
    hovertemplate="<b>%{y}</b><br>Total appearances: %{x}<extra></extra>",
))
fig9.update_layout(
    **LAYOUT_BASE,
    title="Top 20 Albums by Playlist Presence",
    xaxis=dict(showgrid=True, gridcolor=SURFACE,
               title="Total Playlist Appearances", color=MUTED,
               range=[0, top_albums["count"].max() * 1.18]),
    yaxis=dict(showgrid=False, color=TEXT, tickfont=dict(size=10),
               ticksuffix="  "),
    height=680,
    bargap=0.25,
)
fig9.write_html("graphs/07_top_albums.html")
print("✓ 07_top_albums.html")


# ── 10. DASHBOARD ────────────────────────────────────────────────────────────
most_played_name = df.loc[df["count"].idxmax(), "name"]
most_played_display = most_played_name[:16] + ("..." if len(most_played_name) > 16 else "")

dashboard_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>UCSB Playlist Wrapped</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&display=swap');
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: {BG};
      font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
      color: {TEXT};
      min-height: 100vh;
    }}
    header {{
      background: linear-gradient(135deg, #0a3d20 0%, {GREEN_D} 40%, {GREEN} 75%, {TEAL} 100%);
      padding: 60px 40px 44px;
      text-align: center;
    }}
    header h1 {{
      font-size: clamp(2rem, 6vw, 4rem);
      font-weight: 900;
      letter-spacing: -1px;
      text-shadow: 0 2px 20px rgba(0,0,0,0.5);
    }}
    header p {{
      margin-top: 12px;
      font-size: 1.1rem;
      opacity: 0.8;
    }}
    .stats-bar {{
      display: flex;
      justify-content: center;
      gap: 48px;
      flex-wrap: wrap;
      padding: 32px 40px;
      background: {CARD_BG};
      border-bottom: 1px solid {SURFACE};
    }}
    .stat {{ text-align: center; }}
    .stat-num {{
      font-size: 2rem;
      font-weight: 800;
      color: {GREEN};
    }}
    .stat-label {{
      font-size: 0.75rem;
      color: {MUTED};
      text-transform: uppercase;
      letter-spacing: 1.5px;
      margin-top: 6px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(min(100%, 700px), 1fr));
      gap: 24px;
      padding: 32px 24px;
      max-width: 1600px;
      margin: 0 auto;
    }}
    .card {{
      background: {CARD_BG};
      border-radius: 16px;
      overflow: hidden;
      border: 1px solid {SURFACE};
      box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    }}
    .card.full-width {{ grid-column: 1 / -1; }}
    iframe {{ width: 100%; border: none; display: block; }}
    footer {{
      text-align: center;
      padding: 40px;
      color: {MUTED};
      font-size: 0.85rem;
      border-top: 1px solid {SURFACE};
    }}
    footer span {{ color: {GREEN}; }}
  </style>
</head>
<body>
  <header>
    <h1>UCSB Playlist Wrapped</h1>
    <p>Your collective music taste, visualized</p>
  </header>

  <div class="stats-bar">
    <div class="stat">
      <div class="stat-num">{num_playlists}</div>
      <div class="stat-label">Playlists Analyzed</div>
    </div>
    <div class="stat">
      <div class="stat-num">{len(df):,}</div>
      <div class="stat-label">Unique Songs</div>
    </div>
    <div class="stat">
      <div class="stat-num">{df['artist_1'].nunique():,}</div>
      <div class="stat-label">Artists</div>
    </div>
    <div class="stat">
      <div class="stat-num">{int(df['duration_min'].sum() / 60):,}h</div>
      <div class="stat-label">Total Music</div>
    </div>
    <div class="stat">
      <div class="stat-num">{int(df['explicit'].mean()*100)}%</div>
      <div class="stat-label">Explicit</div>
    </div>
    <div class="stat">
      <div class="stat-num" style="font-size:1.2rem">{most_played_display}</div>
      <div class="stat-label">Most Played</div>
    </div>
  </div>

  <div class="grid">
    <div class="card full-width">
      <iframe src="02_top_songs.html" height="920"></iframe>
    </div>
    <div class="card full-width">
      <iframe src="06_artist_treemap.html" height="680"></iframe>
    </div>
    <div class="card">
      <iframe src="03_genre_treemap.html" height="630"></iframe>
    </div>
    <div class="card">
      <iframe src="04_duration_distribution.html" height="530"></iframe>
    </div>
    <div class="card">
      <iframe src="05_explicit_donut.html" height="530"></iframe>
    </div>
    <div class="card full-width">
      <iframe src="07_top_albums.html" height="710"></iframe>
    </div>
  </div>

  <footer>Built with Plotly &mdash; <span>UCSB Playlist Analyzer</span></footer>
</body>
</html>"""

with open("graphs/dashboard.html", "w") as f:
    f.write(dashboard_html)

print("✓ dashboard.html")
print(f"\nAll done. Open graphs/dashboard.html in your browser.")
