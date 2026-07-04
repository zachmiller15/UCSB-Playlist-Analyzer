import os
from copy import deepcopy
import pandas as pd
import plotly.graph_objects as go
import warnings
warnings.filterwarnings("ignore")

# ── Palette ──────────────────────────────────────────────────────────────────
BG       = "#080808"
CARD_BG  = "#0b0b0b"
SURFACE  = "#202020"
TEXT     = "#d8d8d8"
MUTED    = "#8f8f8f"
GREEN    = "#2fbf6f"
GREEN_D  = "#153d27"
GREEN_L  = "#67d696"
PINK     = "#d7d7d7"
PURPLE   = "#7f7f7f"
TEAL     = "#87ffd2"
CYAN     = "#b8b8b8"

COLORSCALE = [[0, "#173820"], [0.55, "#237a48"], [1, GREEN]]
TREEMAP_COLORSCALE = [[0, "#0f2418"], [0.55, "#1b5635"], [1, "#268a51"]]
BW_BG = "#FFFFFF"
BW_SURFACE = "#E5E5E5"
BW_TEXT = "#111111"
BW_MUTED = "#555555"
BW_TILE = "#F2F2F2"
FONT_FAMILY = "'Source Serif 4', Georgia, serif"
TITLE_FONT_FAMILY = "'Space Grotesk', Avenir, 'Helvetica Neue', Arial, sans-serif"
FONT_IMPORT = "@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,300;0,8..60,400;1,8..60,300;1,8..60,400&family=Space+Grotesk:wght@400;500&display=swap');"

LAYOUT_BASE = dict(
    paper_bgcolor=BG,
    plot_bgcolor=BG,
    font=dict(family=FONT_FAMILY, color=TEXT, size=12),
    title_x=0,
    title_xanchor="left",
    title_font=dict(size=21, color=TEXT, family=TITLE_FONT_FAMILY, weight=500),
    margin=dict(l=60, r=32, t=70, b=48),
    hoverlabel=dict(bgcolor="#101010", font_color=TEXT, font_size=12,
                    bordercolor=GREEN),
)


def chart_title(text):
    return dict(
        text=text,
        x=0,
        xanchor="left",
        font=dict(
            family=TITLE_FONT_FAMILY,
            color=TEXT,
            size=21,
            weight=500,
        ),
    )


def format_duration(seconds):
    minutes, secs = divmod(int(round(seconds)), 60)
    return f"{minutes}:{secs:02d}"


def write_graph(fig, path, page_bg=BG, mobile_min_width=720):
    html = fig.to_html(
        full_html=True,
        include_plotlyjs=True,
        config={"displayModeBar": False, "responsive": True, "staticPlot": True},
    )
    html = html.replace(
        "<head>",
        f"""<head><style>
{FONT_IMPORT}
html, body {{
  background: {page_bg};
  margin: 0;
  overflow: hidden;
}}
.plotly-graph-div {{
  background: {page_bg} !important;
}}
.main-svg {{
  shape-rendering: geometricPrecision;
}}
.plotly-graph-div,
.main-svg,
.plotly .cursor-pointer,
.plotly .nsewdrag {{
  cursor: default !important;
}}
.gtitle {{
  font-family: {TITLE_FONT_FAMILY} !important;
  font-weight: 500 !important;
}}
.treemaplayer .trace.treemap > .slice:first-child > .surface {{
  fill: {page_bg} !important;
  stroke: {page_bg} !important;
  fill-opacity: 1 !important;
  stroke-opacity: 1 !important;
}}
.treemaplayer .trace.treemap > .slice:first-child > .slicetext {{
  display: none !important;
}}
.treemaplayer .trace.treemap > .slice > .surface {{
  stroke: {page_bg} !important;
}}
@media (max-width: 600px) {{
  html, body {{
    overflow-x: auto;
  }}
  .plotly-graph-div {{
    min-width: {mobile_min_width}px;
  }}
}}
</style>""",
        1,
    )
    with open(path, "w") as f:
        f.write(html)


def apply_bw_theme(fig):
    bw_fig = deepcopy(fig)
    bw_fig.update_layout(
        paper_bgcolor=BW_BG,
        plot_bgcolor=BW_BG,
        template="none",
        font=dict(family=FONT_FAMILY, color=BW_TEXT, size=13),
        title_font=dict(size=22, color=BW_TEXT),
        hoverlabel=dict(bgcolor=BW_BG, font_color=BW_TEXT, font_size=13,
                        bordercolor=BW_TEXT),
    )
    bw_fig.update_xaxes(color=BW_MUTED, gridcolor=BW_SURFACE, zerolinecolor=BW_SURFACE)
    bw_fig.update_yaxes(color=BW_TEXT, gridcolor=BW_SURFACE, zerolinecolor=BW_SURFACE)

    for trace in bw_fig.data:
        if hasattr(trace, "marker") and trace.marker is not None:
            if trace.type == "pie":
                trace.marker.colors = [BW_BG, "#D9D9D9"]
                trace.marker.line.color = BW_TEXT
            else:
                if trace.type == "treemap":
                    trace.marker.colors = [BW_TILE] * len(trace.labels)
                    trace.marker.colorscale = None
                    trace.marker.line.color = BW_TEXT
                elif getattr(trace.marker, "colorscale", None):
                    trace.marker.color = "#111111"
                    trace.marker.colorscale = None
                else:
                    trace.marker.color = "#111111"
                if getattr(trace.marker, "line", None) and trace.type != "treemap":
                    trace.marker.line.color = BW_BG if trace.type == "bar" else BW_TEXT

        if hasattr(trace, "textfont") and trace.textfont is not None:
            trace.textfont.color = BW_TEXT

    for shape in bw_fig.layout.shapes or []:
        if getattr(shape, "line", None):
            shape.line.color = BW_TEXT

    for annotation in bw_fig.layout.annotations or []:
        annotation.font.color = BW_TEXT

    if bw_fig.layout.legend:
        bw_fig.layout.legend.font = dict(color=BW_TEXT)
        bw_fig.layout.legend.bgcolor = BW_BG

    return bw_fig


def write_bw_graph(fig, filename, mobile_min_width=720):
    write_graph(
        apply_bw_theme(fig),
        os.path.join("BW_graphs", filename),
        page_bg=BW_BG,
        mobile_min_width=mobile_min_width,
    )


os.makedirs("graphs", exist_ok=True)
os.makedirs("BW_graphs", exist_ok=True)

df = pd.read_csv("song_info.csv")
df["duration_min"] = df["duration_ms"] / 60_000
df["duration_sec"] = df["duration_ms"] / 1_000

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
    title=chart_title("Top artists"),
    xaxis=dict(showgrid=True, gridcolor=SURFACE,
               title="Total playlist appearances", color=MUTED,
               range=[0, artist_counts["Total Appearances"].max() * 1.18]),
    yaxis=dict(showgrid=False, color=TEXT, tickfont=dict(size=12),
               showline=False,
               ticksuffix="  "),
    height=700,
    bargap=0.25,
)
fig1.add_shape(
    type="line", x0=0, x1=0, y0=0, y1=1,
    xref="x", yref="paper", layer="above",
    line=dict(color=TEXT, width=2),
)
write_graph(fig1, "graphs/01_top_artists.html")
write_bw_graph(fig1, "01_top_artists.html")
print("✓ 01_top_artists.html")


# ── 2. TOP 30 SONGS ──────────────────────────────────────────────────────────
top_songs = (
    df[["name", "artist_1", "count"]]
    .sort_values("count", ascending=False)
    .head(20)
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
        showscale=False,
        line=dict(width=0),
    ),
    text=top_songs["count"],
    textposition="outside",
    textfont=dict(color=MUTED, size=11),
    hovertemplate="<b>%{y}</b><br>Appears in %{x} playlists<extra></extra>",
))
fig2.update_layout(
    **LAYOUT_BASE,
    title=chart_title("Top 20 most recurring songs (excluding features)"),
    xaxis=dict(showgrid=True, gridcolor=SURFACE,
               title="Playlist appearances", color=MUTED,
               range=[0, top_songs["count"].max() * 1.18]),
    yaxis=dict(showgrid=False, color=TEXT, tickfont=dict(size=10),
               showline=False,
               ticksuffix="  ", automargin=True),
    height=900,
    bargap=0.2,
)
fig2.update_layout(margin=dict(l=360, r=40, t=80, b=60))
fig2.add_shape(
    type="line", x0=0, x1=0, y0=0, y1=1,
    xref="x", yref="paper", layer="above",
    line=dict(color=TEXT, width=2),
)
write_graph(fig2, "graphs/02_top_songs.html", mobile_min_width=780)
write_bw_graph(fig2, "02_top_songs.html", mobile_min_width=780)
print("✓ 02_top_songs.html")


# ── 3. GENRE TREEMAP ─────────────────────────────────────────────────────────
all_genres = pd.concat(
    [df[c] for c in ["genre_1", "genre_2", "genre_3", "genre_4", "genre_5"]]
).dropna()
all_genres = all_genres.str.strip().str.lower().str.title().str.replace(r'(\d)S\b', r'\1s', regex=True)
all_genres = all_genres.str.replace(r"\bHip\s+Hop\b", "Hip-Hop", regex=True)
all_genres = all_genres.str.replace("Rnb", "R&B", case=False, regex=False)
all_genres = all_genres[all_genres != ""]

genre_counts = all_genres.value_counts().head(40).reset_index()
genre_counts.columns = ["Genre", "Count"]

top_genres = genre_counts.head(25).copy()

fig4 = go.Figure(go.Treemap(
    labels=top_genres["Genre"],
    parents=[""] * len(top_genres),
    values=top_genres["Count"],
    root_color=BG,
    marker=dict(
        colors=top_genres["Count"],
        colorscale=TREEMAP_COLORSCALE,
        showscale=False,
        line=dict(width=0),
    ),
    pathbar=dict(visible=False),
    tiling=dict(pad=4),
    textfont=dict(size=14, color="#f2f2f2"),
    hovertemplate="<b>%{label}</b><br>Count: %{value}<extra></extra>",
    texttemplate="<b>%{label}</b><br>%{value}",
))
fig4.update_layout(
    **LAYOUT_BASE,
    title=chart_title("Top 25 genres"),
    height=600,
)
write_graph(fig4, "graphs/03_genre_treemap.html")
write_bw_graph(fig4, "03_genre_treemap.html")
print("✓ 03_genre_treemap.html")


# ── 5. SONG DURATION DISTRIBUTION ────────────────────────────────────────────
fig5 = go.Figure()

duration_bins = pd.interval_range(start=0, end=600, freq=10, closed="left")
duration_counts = pd.cut(df["duration_sec"], bins=duration_bins).value_counts().sort_index()
duration_centers = [interval.left + 5 for interval in duration_counts.index]
duration_labels = [
    f"{format_duration(interval.left)}-{format_duration(interval.right)}"
    for interval in duration_counts.index
]

fig5.add_trace(go.Bar(
    x=duration_centers,
    y=duration_counts.values,
    customdata=duration_labels,
    marker=dict(
        color=GREEN,
        opacity=0.85,
        line=dict(width=0.5, color=BG),
    ),
    hovertemplate="Duration: %{customdata}<br>Songs: %{y}<extra></extra>",
    name="Songs",
))

mean_dur = df["duration_sec"].mean()
fig5.add_vline(
    x=mean_dur, line_dash="dash", line_color=TEXT, line_width=2,
    annotation_text=f"  avg {format_duration(mean_dur)}",
    annotation_font_color=TEXT,
)

fig5.update_layout(
    **LAYOUT_BASE,
    title=chart_title("Song duration distribution"),
    xaxis=dict(title="Duration", color=MUTED, showgrid=True,
               gridcolor=SURFACE, range=[0, 600],
               tickvals=list(range(0, 601, 60)),
               ticktext=[format_duration(x) for x in range(0, 601, 60)]),
    yaxis=dict(title="Number of songs", color=MUTED, showgrid=True,
               gridcolor=SURFACE),
    height=500,
    showlegend=False,
    bargap=0.03,
)
write_graph(fig5, "graphs/04_duration_distribution.html")
write_bw_graph(fig5, "04_duration_distribution.html")
print("✓ 04_duration_distribution.html")


# ── 6. EXPLICIT VS CLEAN DONUT ───────────────────────────────────────────────
exp_counts = df["explicit"].value_counts()
labels = ["Clean", "Explicit"]
values = [exp_counts.get(False, 0), exp_counts.get(True, 0)]

fig6 = go.Figure(go.Pie(
    labels=labels,
    values=values,
    hole=0.6,
    marker=dict(colors=["#9a9a9a", "#35c978"], line=dict(color=BG, width=3)),
    textinfo="label+percent",
    texttemplate="%{label}<br>%{percent:.0%}",
    textfont=dict(size=14, color="#070707"),
    textposition="inside",
    insidetextorientation="horizontal",
    hovertemplate="<b>%{label}</b><br>Songs: %{value}<br>%{percent:.0%}<extra></extra>",
    pull=[0, 0.04],
))
fig6.add_annotation(
    text=f"<b>{len(df):,}</b><br>songs",
    x=0.5, y=0.5, font=dict(size=18, color=TEXT),
    showarrow=False,
)
fig6.update_layout(
    **LAYOUT_BASE,
    title=chart_title("How explicit is the music?"),
    height=500,
    legend=dict(font=dict(color=TEXT), bgcolor=CARD_BG),
)
write_graph(fig6, "graphs/05_explicit_donut.html", mobile_min_width=420)
write_bw_graph(fig6, "05_explicit_donut.html", mobile_min_width=420)
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
    root_color=BG,
    marker=dict(
        colors=top_artists_tm["Total"],
        colorscale=TREEMAP_COLORSCALE,
        showscale=False,
        line=dict(width=0),
    ),
    pathbar=dict(visible=False),
    tiling=dict(pad=4),
    textfont=dict(size=13, color="#f2f2f2"),
    hovertemplate="<b>%{label}</b><br>Total appearances: %{value}<extra></extra>",
    texttemplate="<b>%{label}</b><br>%{value}",
))
fig8.update_layout(
    **LAYOUT_BASE,
    title=chart_title("Top 40 artists by playlist presence"),
    height=650,
)
write_graph(fig8, "graphs/06_artist_treemap.html")
write_bw_graph(fig8, "06_artist_treemap.html")
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
    title=chart_title("Top 20 albums by playlist presence"),
    xaxis=dict(showgrid=True, gridcolor=SURFACE,
               title="Total playlist appearances", color=MUTED,
               range=[0, top_albums["count"].max() * 1.18]),
    yaxis=dict(showgrid=False, color=TEXT, tickfont=dict(size=10),
               showline=False,
               ticksuffix="  ", automargin=True),
    height=680,
    bargap=0.25,
)
fig9.update_layout(margin=dict(l=320, r=40, t=80, b=60))
fig9.add_shape(
    type="line", x0=0, x1=0, y0=0, y1=1,
    xref="x", yref="paper", layer="above",
    line=dict(color=TEXT, width=2),
)
write_graph(fig9, "graphs/07_top_albums.html")
write_bw_graph(fig9, "07_top_albums.html")
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
    {FONT_IMPORT}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: {BG};
      font-family: {FONT_FAMILY};
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
    .chart-scroll {{ overflow-x: auto; -webkit-overflow-scrolling: touch; }}
    @media (max-width: 600px) {{
      html, body {{ overflow-x: hidden; width: 100%; }}
      .chart-scroll iframe {{ min-width: 720px; }}
      .chart-scroll.explicit-chart iframe {{ min-width: 420px; }}
    }}
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
      <div class="stat-label">Playlists analyzed</div>
    </div>
    <div class="stat">
      <div class="stat-num">{len(df):,}</div>
      <div class="stat-label">Unique songs</div>
    </div>
    <div class="stat">
      <div class="stat-num">{df['artist_1'].nunique():,}</div>
      <div class="stat-label">Artists</div>
    </div>
    <div class="stat">
      <div class="stat-num">{all_genres.nunique():,}</div>
      <div class="stat-label">Genres</div>
    </div>
    <div class="stat">
      <div class="stat-num">{int(df['duration_min'].sum() / 60):,}h</div>
      <div class="stat-label">Total music</div>
    </div>
    <div class="stat">
      <div class="stat-num">{int(df['explicit'].mean()*100)}%</div>
      <div class="stat-label">Explicit</div>
    </div>
    <div class="stat">
      <div class="stat-num" style="font-size:1.2rem">{most_played_display}</div>
      <div class="stat-label">Most played</div>
    </div>
  </div>

  <div class="grid">
    <div class="card full-width chart-scroll">
      <iframe src="02_top_songs.html" height="920"></iframe>
    </div>
    <div class="card full-width chart-scroll">
      <iframe src="06_artist_treemap.html" height="680"></iframe>
    </div>
    <div class="card chart-scroll">
      <iframe src="03_genre_treemap.html" height="630"></iframe>
    </div>
    <div class="card chart-scroll">
      <iframe src="04_duration_distribution.html" height="530"></iframe>
    </div>
    <div class="card chart-scroll explicit-chart">
      <iframe src="05_explicit_donut.html" height="530"></iframe>
    </div>
    <div class="card full-width chart-scroll">
      <iframe src="07_top_albums.html" height="710"></iframe>
    </div>
  </div>

  <footer>Built with Plotly &mdash; <span>UCSB Playlist Analyzer</span></footer>
</body>
</html>"""

with open("graphs/dashboard.html", "w") as f:
    f.write(dashboard_html)

bw_dashboard_html = dashboard_html.replace(
    "linear-gradient(135deg, #0a3d20 0%, #158a3e 40%, #1DB954 75%, #00C9A7 100%)",
    "#FFFFFF",
)
for old, new in [
    (TEXT, BW_TEXT),
    (BG, BW_BG),
    (CARD_BG, BW_BG),
    (SURFACE, BW_SURFACE),
    (MUTED, BW_MUTED),
    (GREEN, BW_TEXT),
    (GREEN_D, BW_MUTED),
    (TEAL, BW_SURFACE),
    ("#0a3d20", BW_TEXT),
]:
    bw_dashboard_html = bw_dashboard_html.replace(old, new)

bw_dashboard_html = bw_dashboard_html.replace(
    "header {\n      background: #111111;",
    "header {\n      background: #FFFFFF;",
)
bw_dashboard_html = bw_dashboard_html.replace(
    "      text-shadow: 0 2px 20px rgba(0,0,0,0.5);\n",
    "",
)

with open("BW_graphs/dashboard.html", "w") as f:
    f.write(bw_dashboard_html)

print("✓ dashboard.html")
print(f"\nAll done. Open graphs/dashboard.html in your browser.")
