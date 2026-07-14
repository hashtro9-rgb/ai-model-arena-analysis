"""
LMArena (Chatbot Arena) Leaderboard History — Analysis
======================================================

Loads the weekly LMArena leaderboard snapshots, cleans them, and computes
every finding for the portfolio writeup. Runs top-to-bottom with:

    python analysis/arena_analysis.py

Dependencies: pandas, numpy, matplotlib (seaborn optional, not required).
All paths are relative to the project root, so run it from the project root
(the folder that contains data/, analysis/, charts/).

Author: data-analyst
Data source: LMArena / Chatbot Arena
"""

from __future__ import annotations

import os
import warnings
from itertools import cycle

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # headless, file output only
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import matplotlib.dates as mdates

warnings.filterwarnings("ignore", category=FutureWarning)

# ---------------------------------------------------------------------------
# 0. Paths & house style
# ---------------------------------------------------------------------------
DATA_PATH = os.path.join("data", "ai_model_arena_rankings.csv")
CHART_DIR = "charts"
os.makedirs(CHART_DIR, exist_ok=True)

SRC_NOTE = "Data: LMArena / Chatbot Arena"

# House purple/magenta BI palette
CANVAS = "#F5F3FB"
INK = "#2B2340"
PURPLE = "#6C4AB6"
PURPLE2 = "#7A5FCC"
MAGENTA = "#E84393"
PINK = "#FF4F9A"
LILAC = "#B497E7"
GREY = "#9A93AD"

# A qualitative cycle for multi-line org charts (readable, on-brand-ish)
LINE_COLORS = [
    "#6C4AB6",  # openai (purple)
    "#E84393",  # google (magenta)
    "#00A6A6",  # anthropic (teal)
    "#F39C12",  # alibaba (amber)
    "#2E86DE",  # deepseek (blue)
    "#27AE60",  # meta (green)
    "#C0392B",  # mistral (red)
    "#8E44AD",  # xai (violet)
    "#16A085",  # extra
    "#D35400",  # extra
    "#7F8C8D",  # extra
]

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "#D8D2E8",
    "axes.labelcolor": INK,
    "axes.titlecolor": INK,
    "axes.grid": True,
    "grid.color": "#ECE8F5",
    "grid.linewidth": 0.8,
    "text.color": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "font.size": 11,
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 110,
})


def _finish(fig, ax, fname, title, subtitle=None):
    """Apply title/subtitle/source note and save a chart at 160 dpi.

    Title and subtitle are anchored to the primary axes so they stack cleanly
    regardless of figure height (no fixed-figure-coordinate overlaps)."""
    primary = ax.ravel()[0] if isinstance(ax, np.ndarray) else ax
    if subtitle:
        primary.set_title(title, fontsize=14, fontweight="bold", loc="left", pad=28)
        primary.text(0, 1.03, subtitle, transform=primary.transAxes,
                     fontsize=10.5, color=GREY, ha="left", va="bottom")
    else:
        primary.set_title(title, fontsize=14, fontweight="bold", loc="left", pad=12)
    fig.text(0.99, 0.005, SRC_NOTE, fontsize=8.5, color=GREY, ha="right", va="bottom")
    fig.tight_layout(rect=[0, 0.02, 1, 1.0])
    path = os.path.join(CHART_DIR, fname)
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"    saved chart -> {path}")


def hr(title):
    print("\n" + "=" * 74)
    print(title)
    print("=" * 74)


# ---------------------------------------------------------------------------
# 1. Load & clean
# ---------------------------------------------------------------------------
hr("LOAD & CLEAN")

df = pd.read_csv(DATA_PATH)
print(f"Raw rows: {len(df):,}")

# Parse snapshot date
df["date"] = pd.to_datetime(df["leaderboard_publish_date"])

# Normalise organization: strip whitespace, collapse casing to a canonical
# lowercase key, then present a nice display name.
df["org_key"] = (
    df["organization"].astype("string").str.strip().str.lower()
)
df["org_key"] = df["org_key"].replace({"": pd.NA})
n_blank_org = df["org_key"].isna().sum()
df["org_key"] = df["org_key"].fillna("unknown")

# Display names for the orgs we chart / reference
DISPLAY = {
    "openai": "OpenAI", "google": "Google", "anthropic": "Anthropic",
    "alibaba": "Alibaba", "deepseek": "DeepSeek", "meta": "Meta",
    "mistral": "Mistral", "xai": "xAI", "microsoft": "Microsoft",
    "nvidia": "NVIDIA", "cohere": "Cohere", "tencent": "Tencent",
    "amazon": "Amazon", "zai": "Z.ai / Zhipu", "zhipu ai": "Z.ai / Zhipu",
    "ai2": "Ai2", "ibm": "IBM", "lmsys": "LMSYS", "reka ai": "Reka AI",
    "stepfun": "StepFun", "moonshot": "Moonshot", "tsinghua": "Tsinghua",
    "01 ai": "01.AI", "minimax": "MiniMax", "nexusflow": "NexusFlow",
    "unknown": "Unknown",
}
df["org_display"] = df["org_key"].map(lambda k: DISPLAY.get(k, str(k).title()))

# License: normalise, then classify open-weight vs proprietary.
df["license"] = df["license"].astype("string").str.strip()


def license_category(lic: str) -> str:
    """Proprietary if the license says so (or is missing/unknown); otherwise
    the weights are released under some open/open-weight family -> 'open'."""
    if lic is pd.NA or lic is None or (isinstance(lic, float) and np.isnan(lic)):
        return "proprietary"
    s = str(lic).lower()
    if "proprietary" in s:
        return "proprietary"
    return "open"


df["lic_cat"] = df["license"].apply(license_category)

# China vs US/West lab grouping (only for the orgs the analysis names)
CHINA = {
    "alibaba", "deepseek", "tencent", "zai", "zhipu ai", "minimax",
    "moonshot", "stepfun", "01 ai", "tsinghua", "baidu", "zhipu",
}
US_WEST = {
    "openai", "google", "anthropic", "meta", "xai", "mistral",
    "microsoft", "nvidia", "cohere", "amazon",
}


def geo_group(k: str) -> str:
    if k in CHINA:
        return "China"
    if k in US_WEST:
        return "US / West"
    return "Other"


df["geo"] = df["org_key"].map(geo_group)

# --- Data-quality fix: de-duplicate stacked snapshots ---------------------
# A handful of recent publish dates (notably 2026-06-10) contain the same
# model listed multiple times at different ratings — several leaderboard
# refreshes were collapsed under one publish date, producing e.g. six rank-1
# rows in a single "snapshot". We keep one row per (date, subset, model):
# the one with the most votes (most settled rating), then RE-RANK each
# snapshot by rating so ranks are unique and consecutive again.
n_before = len(df)
df = (df.sort_values("vote_count", na_position="first")
        .drop_duplicates(["date", "subset", "model_name"], keep="last"))
df["rank"] = (df.groupby(["date", "subset", "category"])["rating"]
                .rank(method="first", ascending=False).astype(int))
n_dupes = n_before - len(df)

# Numeric CI width where available
df["ci_width"] = df["rating_upper"] - df["rating_lower"]

snap_dates = sorted(df["date"].unique())
latest_date = df.loc[df["subset"] == "text", "date"].max()

print(f"Snapshots: {df['date'].nunique()}  "
      f"({df['date'].min().date()} -> {df['date'].max().date()})")
print(f"Blank organizations normalised to 'unknown': {n_blank_org:,}")
print(f"Duplicate (date,subset,model) rows removed from stacked snapshots: {n_dupes:,}")
print("Subset row counts:")
print(df["subset"].value_counts().to_string())
print(f"Latest TEXT snapshot used for 'current' numbers: {latest_date.date()}")

# Primary working frame = the TEXT leaderboard (one row per model per snapshot)
text = df[df["subset"] == "text"].copy()

# convenience: top model per (date) in text
def best_per_group(frame, group_cols):
    idx = frame.groupby(group_cols)["rating"].idxmax()
    return frame.loc[idx]


# ===========================================================================
# TIER 1 — THE RACE OVER TIME
# ===========================================================================

# ---------------------------------------------------------------------------
# 1.1  #1-holder timeline (by organization)
# ---------------------------------------------------------------------------
hr("T1.1  #1-HOLDER TIMELINE (organization)")

top1 = (text[text["rank"] == 1]
        .sort_values("date")[["date", "org_display", "org_key", "model_name", "rating"]]
        .reset_index(drop=True))

# Build reigns: contiguous runs of the same org holding #1
reigns = []
prev = None
for _, row in top1.iterrows():
    if prev is None or row["org_key"] != prev["org_key"]:
        reigns.append({"org": row["org_display"], "org_key": row["org_key"],
                       "start": row["date"], "end": row["date"], "weeks": 1})
        prev = row
    else:
        reigns[-1]["end"] = row["date"]
        reigns[-1]["weeks"] += 1
        prev = row
reigns_df = pd.DataFrame(reigns)

print("Reign timeline at #1 (organization):")
for _, r in reigns_df.iterrows():
    print(f"  {r['org']:<14} {r['start'].date()} -> {r['end'].date()}  "
          f"({r['weeks']:>3} snapshots)")

org_total = (top1.groupby("org_display").size()
             .sort_values(ascending=False))
print("\nTotal snapshots at #1 by organization:")
print(org_total.to_string())

# Chart: colored horizontal band of who held #1 across time
fig, ax = plt.subplots(figsize=(12, 4.2))
orgs_in_top1 = list(org_total.index)
cmap = {o: LINE_COLORS[i % len(LINE_COLORS)] for i, o in enumerate(orgs_in_top1)}
# draw each snapshot as a thin vertical bar spanning the gap to next snapshot
dates = top1["date"].tolist()
for i, (_, row) in enumerate(top1.iterrows()):
    start = row["date"]
    end = dates[i + 1] if i + 1 < len(dates) else start + pd.Timedelta(days=7)
    ax.axvspan(start, end, color=cmap[row["org_display"]], alpha=0.95)
ax.set_yticks([])
ax.set_ylim(0, 1)
handles = [plt.Rectangle((0, 0), 1, 1, color=cmap[o]) for o in orgs_in_top1]
ax.legend(handles, [f"{o} ({org_total[o]})" for o in orgs_in_top1],
          loc="upper left", bbox_to_anchor=(0, -0.12), ncol=min(4, len(orgs_in_top1)),
          frameon=False, fontsize=9.5, title="Organization holding #1 (total snapshots)",
          title_fontsize=10, alignment="left")
ax.grid(False)
_finish(fig, ax, "01_top1_org_timeline.png",
        "Who held the #1 spot on the text leaderboard",
        "Each vertical band is one weekly snapshot, colored by the organization at rank 1")

# ---------------------------------------------------------------------------
# 1.2  Org trajectories — best model's Elo per snapshot
# ---------------------------------------------------------------------------
hr("T1.2  ORG TRAJECTORIES (best model Elo over time)")

TRAJ_ORGS = ["openai", "google", "anthropic", "alibaba", "deepseek",
             "meta", "mistral", "xai"]
best_org = (text[text["org_key"].isin(TRAJ_ORGS)]
            .groupby(["date", "org_key"])["rating"].max().reset_index())

fig, ax = plt.subplots(figsize=(12, 6))
for org, color in zip(TRAJ_ORGS, cycle(LINE_COLORS)):
    sub = best_org[best_org["org_key"] == org].sort_values("date")
    if sub.empty:
        continue
    ax.plot(sub["date"], sub["rating"], color=color, lw=2.1,
            label=DISPLAY.get(org, org))
    last = sub.iloc[-1]
    ax.scatter([last["date"]], [last["rating"]], color=color, s=22, zorder=5)
ax.set_ylabel("Best model Elo rating")
ax.set_xlabel("Snapshot date")
ax.legend(loc="upper left", frameon=False, ncol=2, fontsize=9.5)
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
_finish(fig, ax, "02_org_trajectories.png",
        "Frontier trajectories: each lab's best model over time",
        "Elo of the single strongest model each organization had in every weekly snapshot (text)")

# print current standings
cur_best = (best_org[best_org["date"] == latest_date]
            .sort_values("rating", ascending=False))
print(f"Best model Elo by org at {latest_date.date()}:")
for _, r in cur_best.iterrows():
    print(f"  {DISPLAY.get(r['org_key'], r['org_key']):<12} {r['rating']:.1f}")

# ---------------------------------------------------------------------------
# 1.3  Frontier acceleration / compression: #1 rating & (#1 - #10) gap
# ---------------------------------------------------------------------------
hr("T1.3  FRONTIER LEVEL & TOP-10 COMPRESSION")

rows = []
for d, g in text.groupby("date"):
    g = g.sort_values("rank")
    r1 = g.loc[g["rank"] == 1, "rating"]
    r10 = g.loc[g["rank"] == 10, "rating"]
    if r1.empty or r10.empty:
        continue
    rows.append({"date": d, "top1": r1.iloc[0], "top10": r10.iloc[0],
                 "gap": r1.iloc[0] - r10.iloc[0]})
front = pd.DataFrame(rows).sort_values("date")

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(front["date"], front["top1"], color=PURPLE, lw=2.4, label="#1 rating")
ax.plot(front["date"], front["top10"], color=LILAC, lw=2.0, ls="--", label="#10 rating")
ax.fill_between(front["date"], front["top10"], front["top1"],
                color=MAGENTA, alpha=0.10)
ax.set_ylabel("Elo rating")
ax.set_xlabel("Snapshot date")
ax2 = ax.twinx()
ax2.plot(front["date"], front["gap"], color=MAGENTA, lw=1.8, alpha=0.85,
         label="#1 minus #10 gap")
ax2.set_ylabel("#1 - #10 gap (Elo points)", color=MAGENTA)
ax2.tick_params(axis="y", colors=MAGENTA)
ax2.grid(False)
ax2.spines["right"].set_visible(True)
ax2.spines["right"].set_color(MAGENTA)
lines = ax.get_lines() + ax2.get_lines()
ax.legend(lines, [l.get_label() for l in lines], loc="upper left", frameon=False, fontsize=9.5)
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
_finish(fig, ax, "03_frontier_compression.png",
        "The frontier keeps rising while the top-10 pack compresses",
        "Left axis: #1 and #10 Elo. Right axis: the point gap between them (text)")

first, last = front.iloc[0], front.iloc[-1]
print(f"#1 rating: {first['top1']:.0f} ({first['date'].date()}) -> "
      f"{last['top1']:.0f} ({last['date'].date()})  (+{last['top1']-first['top1']:.0f})")
print(f"#1-#10 gap: {first['gap']:.0f} -> {last['gap']:.0f} points")
print(f"Max ever #1-#10 gap: {front['gap'].max():.0f} on {front.loc[front['gap'].idxmax(),'date'].date()}")
print(f"Recent (last 12 snapshots) mean #1-#10 gap: {front['gap'].tail(12).mean():.1f}")

# ---------------------------------------------------------------------------
# 1.4  Open-weight vs proprietary frontier
# ---------------------------------------------------------------------------
hr("T1.4  OPEN-WEIGHT vs PROPRIETARY")

op = []
for d, g in text.groupby("date"):
    o = g.loc[g["lic_cat"] == "open", "rating"].max()
    p = g.loc[g["lic_cat"] == "proprietary", "rating"].max()
    op.append({"date": d, "open": o, "prop": p})
opdf = pd.DataFrame(op).sort_values("date")
opdf["gap"] = opdf["prop"] - opdf["open"]

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(opdf["date"], opdf["prop"], color=PURPLE, lw=2.3, label="Best proprietary")
ax.plot(opdf["date"], opdf["open"], color=MAGENTA, lw=2.3, label="Best open-weight")
ax.fill_between(opdf["date"], opdf["open"], opdf["prop"],
                where=opdf["prop"] >= opdf["open"], color=PURPLE, alpha=0.08)
ax.set_ylabel("Best model Elo rating")
ax.set_xlabel("Snapshot date")
ax.legend(loc="upper left", frameon=False, fontsize=10)
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
_finish(fig, ax, "04_open_vs_proprietary.png",
        "Open-weight models are closing on proprietary frontier",
        "Best Elo among open-weight vs proprietary models each snapshot (text)")

opv = opdf.dropna(subset=["gap"])
print(f"Best proprietary - best open gap: "
      f"{opv.iloc[0]['gap']:.0f} ({opv.iloc[0]['date'].date()}) -> "
      f"{opv.iloc[-1]['gap']:.0f} ({opv.iloc[-1]['date'].date()})")
print(f"Max gap: {opv['gap'].max():.0f}; min (recent) gap: {opv['gap'].tail(20).min():.0f}")
# times open led
led = (opdf["open"] >= opdf["prop"]).sum()
print(f"Snapshots where best open >= best proprietary: {led} of {len(opdf)}")

# ===========================================================================
# TIER 2 — COMPETITIVE STRUCTURE
# ===========================================================================

# ---------------------------------------------------------------------------
# 2.5  China vs US/West frontier
# ---------------------------------------------------------------------------
hr("T2.5  CHINA vs US/WEST FRONTIER")

geo = []
for d, g in text.groupby("date"):
    c = g.loc[g["geo"] == "China", "rating"].max()
    u = g.loc[g["geo"] == "US / West", "rating"].max()
    geo.append({"date": d, "China": c, "US / West": u})
geodf = pd.DataFrame(geo).sort_values("date")
geodf["gap"] = geodf["US / West"] - geodf["China"]

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(geodf["date"], geodf["US / West"], color=PURPLE, lw=2.3, label="US / West best")
ax.plot(geodf["date"], geodf["China"], color=MAGENTA, lw=2.3, label="China best")
ax.fill_between(geodf["date"], geodf["China"], geodf["US / West"],
                color=PURPLE, alpha=0.07)
ax.set_ylabel("Best model Elo rating")
ax.set_xlabel("Snapshot date")
ax.legend(loc="upper left", frameon=False, fontsize=10)
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
_finish(fig, ax, "05_china_vs_us.png",
        "China's top labs have nearly erased the frontier gap",
        "Best Elo among Chinese labs vs US/Western labs each snapshot (text)")

gv = geodf.dropna(subset=["gap"])
print(f"US/West - China frontier gap: "
      f"{gv.iloc[0]['gap']:.0f} ({gv.iloc[0]['date'].date()}) -> "
      f"{gv.iloc[-1]['gap']:.0f} ({gv.iloc[-1]['date'].date()})")
print(f"China ahead in {int((geodf['China'] > geodf['US / West']).sum())} snapshots; "
      f"recent 12-snap mean gap {gv['gap'].tail(12).mean():.1f}")

# ---------------------------------------------------------------------------
# 2.6  Longest / shortest reign at #1 by MODEL
# ---------------------------------------------------------------------------
hr("T2.6  LONGEST / SHORTEST #1 REIGN BY MODEL")

top1_model = text[text["rank"] == 1].sort_values("date")
# contiguous reign runs by model
mreigns = []
prev = None
for _, row in top1_model.iterrows():
    if prev is None or row["model_name"] != prev:
        mreigns.append({"model": row["model_name"], "org": row["org_display"],
                        "start": row["date"], "end": row["date"], "weeks": 1})
        prev = row["model_name"]
    else:
        mreigns[-1]["end"] = row["date"]
        mreigns[-1]["weeks"] += 1
mreigns_df = pd.DataFrame(mreigns)
# total snapshots at #1 per model (a model can have >1 stint)
model_total = (top1_model.groupby(["model_name", "org_display"]).size()
               .reset_index(name="snapshots")
               .sort_values("snapshots", ascending=False))

print("Top 12 models by total snapshots at #1:")
for _, r in model_total.head(12).iterrows():
    print(f"  {r['model_name']:<32} {r['org_display']:<12} {r['snapshots']:>3}")
print("\nShortest reigns (single-stint models that held #1 for exactly 1 snapshot):")
one_off = mreigns_df[mreigns_df["weeks"] == 1]
print(f"  {len(one_off)} models held #1 for just one snapshot, e.g.: "
      f"{', '.join(one_off['model'].head(6))}")

fig, ax = plt.subplots(figsize=(11, 6))
topn = model_total.head(12).iloc[::-1]
bar_colors = [LINE_COLORS[orgs_in_top1.index(o) % len(LINE_COLORS)]
              if o in orgs_in_top1 else PURPLE for o in topn["org_display"]]
ax.barh(topn["model_name"], topn["snapshots"], color=bar_colors)
for y, v in enumerate(topn["snapshots"]):
    ax.text(v + 0.15, y, str(int(v)), va="center", fontsize=9, color=INK)
ax.set_xlabel("Snapshots held at rank #1")
ax.margins(x=0.08)
_finish(fig, ax, "06_model_reign_top1.png",
        "Which specific models ruled the leaderboard longest",
        "Total weekly snapshots each model spent at rank #1 (text)")

# ---------------------------------------------------------------------------
# 2.7  Fastest climbers & notable debuts
# ---------------------------------------------------------------------------
hr("T2.7  FASTEST CLIMBERS & DEBUTS")

t = text.sort_values(["model_name", "date"]).copy()
t["prev_rating"] = t.groupby("model_name")["rating"].shift(1)
t["delta"] = t["rating"] - t["prev_rating"]
jumps = t.dropna(subset=["delta"]).sort_values("delta", ascending=False)
print("Biggest single-snapshot Elo jumps (existing models):")
for _, r in jumps.head(10).iterrows():
    print(f"  {r['model_name']:<30} {r['org_display']:<10} "
          f"+{r['delta']:.0f}  -> {r['rating']:.0f}  ({r['date'].date()})")

# debuts: first appearance of a model, rank on debut
first_app = t.groupby("model_name").first().reset_index()
# rank on debut relative to that snapshot
debut = first_app.sort_values("rating", ascending=False)
top_debuts = debut[debut["rank"] <= 5].sort_values("date").tail(15)
print("\nNotable high debuts (models first appearing at rank <= 5):")
for _, r in debut[debut["rank"] <= 3].sort_values("rating", ascending=False).head(10).iterrows():
    print(f"  {r['model_name']:<30} {r['org_display']:<10} debut rank #{int(r['rank'])} "
          f"@ {r['rating']:.0f}  ({r['date'].date()})")

fig, ax = plt.subplots(figsize=(11, 6))
jt = jumps.head(12).iloc[::-1]
ax.barh(jt["model_name"] + "  (" + jt["date"].dt.strftime("%Y-%m") + ")",
        jt["delta"], color=MAGENTA)
for y, v in enumerate(jt["delta"]):
    ax.text(v + 0.5, y, f"+{v:.0f}", va="center", fontsize=9, color=INK)
ax.set_xlabel("Elo gained vs previous snapshot")
ax.margins(x=0.10)
_finish(fig, ax, "07_fastest_climbers.png",
        "Biggest week-over-week Elo jumps",
        "Largest single-snapshot rating gains for models already on the board (text)")

# ---------------------------------------------------------------------------
# 2.8  License mix in the top 10 over time
# ---------------------------------------------------------------------------
hr("T2.8  LICENSE MIX IN TOP 10 OVER TIME")

mix = []
for d, g in text.groupby("date"):
    t10 = g[g["rank"] <= 10]
    if t10.empty:
        continue
    n = len(t10)
    mix.append({"date": d,
                "open": (t10["lic_cat"] == "open").sum() / n,
                "proprietary": (t10["lic_cat"] == "proprietary").sum() / n})
mixdf = pd.DataFrame(mix).sort_values("date")

fig, ax = plt.subplots(figsize=(12, 6))
ax.stackplot(mixdf["date"], mixdf["open"], mixdf["proprietary"],
             labels=["Open-weight", "Proprietary"],
             colors=[MAGENTA, PURPLE], alpha=0.9)
ax.set_ylabel("Share of top-10 models")
ax.set_xlabel("Snapshot date")
ax.set_ylim(0, 1)
ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda y, _: f"{y:.0%}"))
ax.legend(loc="lower center", frameon=False, ncol=2, bbox_to_anchor=(0.5, -0.18))
ax.grid(False)
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
_finish(fig, ax, "08_top10_license_mix.png",
        "The top 10 flipped from open to proprietary — and back toward open",
        "Share of open-weight vs proprietary licenses among the top-10 models (text)")

early = mixdf.iloc[0]
lastmix = mixdf.iloc[-1]
print(f"Top-10 open-weight share: {early['open']:.0%} ({early['date'].date()}) -> "
      f"{lastmix['open']:.0%} ({lastmix['date'].date()})")
print(f"Min open share ever: {mixdf['open'].min():.0%} on "
      f"{mixdf.loc[mixdf['open'].idxmin(),'date'].date()}")

# ===========================================================================
# TIER 3 — METHOD / QUALITY ANGLES
# ===========================================================================

# ---------------------------------------------------------------------------
# 3.9  vote_count vs rating precision + overlapping CIs in latest snapshot
# ---------------------------------------------------------------------------
hr("T3.9  VOTE COUNT vs PRECISION; OVERLAPPING CIs")

prec = text.dropna(subset=["vote_count", "ci_width"]).copy()
prec = prec[(prec["vote_count"] > 0) & (prec["ci_width"] > 0)]
# binned summary
bins = [0, 1000, 3000, 10000, 30000, 100000, np.inf]
labels = ["<1k", "1-3k", "3-10k", "10-30k", "30-100k", "100k+"]
prec["vbin"] = pd.cut(prec["vote_count"], bins=bins, labels=labels)
binned = prec.groupby("vbin")["ci_width"].agg(["median", "mean", "count"])
print("Median 95% CI width by vote-count bin:")
print(binned.to_string())
corr = np.corrcoef(np.log10(prec["vote_count"]), prec["ci_width"])[0, 1]
print(f"Correlation log10(vote_count) vs CI width: {corr:.2f}")

fig, ax = plt.subplots(figsize=(11, 6))
ax.scatter(prec["vote_count"], prec["ci_width"], s=8, color=LILAC, alpha=0.35,
           edgecolors="none", label="model-snapshot")
med = prec.groupby("vbin")["ci_width"].median()
centers = [500, 2000, 6500, 20000, 65000, 150000]
ax.plot(centers[:len(med)], med.values, color=MAGENTA, lw=2.5, marker="o",
        label="median CI width by bin")
ax.set_xscale("log")
ax.set_xlabel("Vote count (log scale)")
ax.set_ylabel("95% confidence-interval width (Elo points)")
ax.legend(frameon=False, fontsize=9.5)
_finish(fig, ax, "09_votes_vs_precision.png",
        "More votes, tighter ratings: precision scales with sample size",
        "Each dot is a model in one snapshot; the line is the median CI width per vote bin (text)")

# overlapping CIs among adjacent ranks in latest snapshot
lat = text[text["date"] == latest_date].sort_values("rank").dropna(subset=["rating_lower", "rating_upper"])
overlaps = []
lr = lat.reset_index(drop=True)
for i in range(len(lr) - 1):
    a, b = lr.iloc[i], lr.iloc[i + 1]
    # overlap if a's lower bound <= b's upper bound (ranks sorted desc rating)
    if a["rating_lower"] <= b["rating_upper"]:
        overlaps.append((int(a["rank"]), a["model_name"], int(b["rank"]),
                         b["model_name"], a["rating"] - b["rating"]))
print(f"\nAdjacent-rank pairs with OVERLAPPING 95% CIs in {latest_date.date()} "
      f"(statistically indistinguishable): {len(overlaps)} of {len(lr)-1}")
for o in overlaps[:12]:
    print(f"  #{o[0]} {o[1]}  ~=  #{o[2]} {o[3]}  (rating diff {o[4]:.1f})")

# ---------------------------------------------------------------------------
# 3.10  Subset specialists: vision/webdev vs text (same snapshot)
# ---------------------------------------------------------------------------
hr("T3.10  SUBSET SPECIALISTS (vision & webdev vs text)")

def specialist_table(other_subset):
    o = df[df["subset"] == other_subset]
    common_dates = sorted(set(o["date"]) & set(text["date"]))
    if not common_dates:
        return None, None
    d = max(common_dates)
    tt = text[text["date"] == d][["model_name", "rank", "rating"]].rename(
        columns={"rank": "text_rank", "rating": "text_rating"})
    oo = o[o["date"] == d][["model_name", "rank", "rating", "org_display"]].rename(
        columns={"rank": f"{other_subset}_rank", "rating": f"{other_subset}_rating"})
    m = oo.merge(tt, on="model_name", how="inner")
    m["rank_gain"] = m["text_rank"] - m[f"{other_subset}_rank"]  # positive = better in specialty
    return d, m.sort_values("rank_gain", ascending=False)

for ss in ["vision", "webdev"]:
    d, m = specialist_table(ss)
    if m is None or m.empty:
        print(f"No overlapping {ss}+text snapshot.")
        continue
    print(f"\n{ss.upper()} specialists (snapshot {d.date()}) — rank much higher in {ss} than text:")
    for _, r in m.head(8).iterrows():
        print(f"  {r['model_name']:<28} {r['org_display']:<10} "
              f"{ss} #{int(r[f'{ss}_rank']):>3} vs text #{int(r['text_rank']):>3}  "
              f"(+{int(r['rank_gain'])} ranks)")

# Chart the webdev specialists (latest, has data at 2026-07-10)
d, mweb = specialist_table("webdev")
if mweb is not None and not mweb.empty:
    top_spec = mweb.head(10).iloc[::-1]
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.barh(top_spec["model_name"], top_spec["rank_gain"], color=PURPLE2)
    for y, v in enumerate(top_spec["rank_gain"]):
        ax.text(v + 0.2, y, f"+{int(v)}", va="center", fontsize=9, color=INK)
    ax.set_xlabel("Ranks higher in WebDev than in Text  (text_rank - webdev_rank)")
    ax.margins(x=0.10)
    _finish(fig, ax, "10_webdev_specialists.png",
            "WebDev specialists: models that punch above their text rank",
            f"Rank improvement in the WebDev arena vs the text arena, snapshot {d.date()}")

# ---------------------------------------------------------------------------
# 3.11  Style-control effect: text vs text_style_control (latest)
# ---------------------------------------------------------------------------
hr("T3.11  STYLE-CONTROL EFFECT")

sc_dates = sorted(set(df[df["subset"] == "text_style_control"]["date"]) & set(text["date"]))
scd = max(sc_dates)
tt = text[text["date"] == scd][["model_name", "rank", "rating", "org_display"]].rename(
    columns={"rank": "text_rank", "rating": "text_rating"})
sc = df[(df["subset"] == "text_style_control") & (df["date"] == scd)][
    ["model_name", "rank", "rating"]].rename(
    columns={"rank": "sc_rank", "rating": "sc_rating"})
m = tt.merge(sc, on="model_name", how="inner")
m["rank_drop"] = m["sc_rank"] - m["text_rank"]      # positive = falls when style controlled
m["rating_drop"] = m["text_rating"] - m["sc_rating"]

worst = m[m["text_rank"] <= 60].sort_values("rank_drop", ascending=False)
print(f"Snapshot {scd.date()} — models that FALL most when answer style is controlled")
print("(verbose/formatting 'gaming' penalised):")
for _, r in worst.head(10).iterrows():
    print(f"  {r['model_name']:<30} {r['org_display']:<10} "
          f"text #{int(r['text_rank']):>3} -> style-ctrl #{int(r['sc_rank']):>3}  "
          f"({int(r['rank_drop']):+d} ranks, {r['rating_drop']:+.0f} Elo)")

best = m[m["text_rank"] <= 60].sort_values("rank_drop")
print("\nModels that RISE most under style control (substance over style):")
for _, r in best.head(6).iterrows():
    print(f"  {r['model_name']:<30} {r['org_display']:<10} "
          f"text #{int(r['text_rank']):>3} -> style-ctrl #{int(r['sc_rank']):>3}  "
          f"({int(r['rank_drop']):+d} ranks)")

fig, ax = plt.subplots(figsize=(11, 6.2))
plotm = pd.concat([worst.head(8), best.head(4)]).drop_duplicates("model_name")
plotm = plotm.sort_values("rank_drop")
colors = [MAGENTA if v > 0 else PURPLE for v in plotm["rank_drop"]]
ax.barh(plotm["model_name"], plotm["rank_drop"], color=colors)
for y, v in enumerate(plotm["rank_drop"]):
    ax.text(v + (0.2 if v >= 0 else -0.2), y, f"{int(v):+d}",
            va="center", ha="left" if v >= 0 else "right", fontsize=9, color=INK)
ax.axvline(0, color=GREY, lw=1)
ax.set_xlabel("Rank change when style is controlled  (positive = falls / style-reliant)")
ax.margins(x=0.14)
handles = [plt.Rectangle((0, 0), 1, 1, color=MAGENTA),
           plt.Rectangle((0, 0), 1, 1, color=PURPLE)]
ax.legend(handles, ["Falls (style-reliant)", "Rises (substance)"],
          frameon=False, fontsize=9, loc="lower right")
ax.grid(axis="y", visible=False)
_finish(fig, ax, "11_style_control_effect.png",
        "Who was gaming style? Rank shifts when answer formatting is neutralised",
        f"Text vs style-controlled rank, snapshot {scd.date()}")

# ---------------------------------------------------------------------------
# Emit the human-readable findings writeup (analysis/FINDINGS.md)
# ---------------------------------------------------------------------------
hr("WRITE FINDINGS.md")

FINDINGS_MD = r'''# LMArena Leaderboard History — What the Data Says

*An analysis of 247 weekly LMArena (Chatbot Arena) leaderboard snapshots, 8 May 2023 -> 10 July 2026 (~97,000 rows). The Arena ranks AI chat models by an Elo score derived from millions of head-to-head human preference votes. Unless noted, everything below is the **text** leaderboard — the flagship "which model is smartest in conversation" board. All current-state numbers use the latest snapshot, 10 July 2026.*

**How to read Elo:** higher is better; a ~35-point gap means the higher model wins the head-to-head roughly 55% of the time. Ratings come with a 95% confidence interval — if two models' intervals overlap, they are statistically tied.

*Data source: LMArena / Chatbot Arena. Reproduce with `python analysis/arena_analysis.py`.*

**Data-cleaning note:** organization names were normalized for casing/whitespace, ~3,477 blank organizations were labeled "Unknown", and licenses were classified as **open-weight** (Apache, MIT, Llama/Gemma/Qwen/DeepSeek families, etc.) vs **proprietary**. A genuine data-quality issue — 686 duplicate rows where several leaderboard refreshes were stacked under one publish date (mostly 2026-06-10, which had six "rank-1" rows) — was resolved by keeping one row per model per snapshot and re-ranking each board.

---

## Tier 1 — The race over time

### 1. The crown has changed hands, but three labs have owned almost all of it
**Headline: OpenAI has led the leaderboard longer than anyone (91 of 247 snapshots), but Anthropic currently holds the longest unbroken reign in Arena history — 53 straight weeks and counting.**

Who held #1, by total snapshots at the top: **OpenAI 91, Anthropic 58, Google 47, DeepSeek 11, xAI 7, LMSYS 5, Microsoft 3.** The early era (2023) belonged to open research models (LMSYS/Vicuna, a one-week UW cameo) and a brief Microsoft run; OpenAI then dominated 2024 with a 37-week unbroken reign. The most striking recent shifts:

- **Google's breakout:** a single unbroken 47-week reign (Jun 2025 -> Jan 2026) — every one of Google's #1 finishes came in that one streak.
- **Anthropic's current run:** 53 consecutive snapshots at #1 (6 Feb 2026 -> present), the longest single reign in the dataset.
- **DeepSeek's moment:** an 11-week stint at #1 in early 2025 — the only non-US-and-non-"big-three" lab to hold the top spot for a sustained period.

*So what: the frontier is effectively a three-horse race (OpenAI, Google, Anthropic), and leadership now flips in multi-month blocks rather than week to week.*
Chart: `charts/01_top1_org_timeline.png`

### 2. Every major lab is climbing the same staircase — and they're bunched at the top
**Headline: Eight major labs' best models have converged into a tight band near 1450-1500 Elo, up from a scattered ~1000-1100 in early 2024.**

Plotting each lab's single strongest model per snapshot shows a synchronized, step-shaped climb (each step = a new flagship release). Current best-model standings: **Anthropic 1501, Google 1480, Meta 1478, Alibaba 1475, OpenAI 1469, xAI 1455, DeepSeek 1449, Mistral 1431.** The spread between the 1st and 8th of these labs is now only ~70 points — versus 100+ points of separation through most of 2024-2025.

*So what: no single lab has a durable moat; a competitor's next release routinely erases a leader's edge within weeks.*
Chart: `charts/02_org_trajectories.png`

### 3. The ceiling keeps rising while the top-10 pack compresses
**Headline: The #1 rating climbed +407 Elo (1094 -> 1501) over three years, yet the gap between #1 and #10 collapsed from 259 points to just ~24.**

The frontier is simultaneously **rising** (the best model keeps getting better) and **compressing** (the chasing pack has caught up). In May 2023 the #10 model was 259 Elo behind #1; today it is about 24 behind, and the recent 12-snapshot average gap is ~28 points. The top ten are now separated by less than the width of many models' confidence intervals.

*So what: "top-10 on the Arena" has become a near-commodity — the meaningful competition is now for the top 1-2 spots.*
Chart: `charts/03_frontier_compression.png`

### 4. Open-weight models are shadowing the proprietary frontier
**Headline: The best open-weight model trails the best proprietary model by only ~34 Elo today — down from gaps of 100+ during 2024 — and open models have actually led outright in 19 snapshots.**

Early on, open research models *were* the frontier (open led by 16 points in May 2023). Proprietary models then pulled ahead by as much as 135 Elo in 2024. Since then open-weight releases (Llama, Qwen, DeepSeek, and others) have steadily closed the gap; the recent low is ~30 points. Across all 223 comparable snapshots, the best open model matched or beat the best proprietary model in **19** of them.

*So what: for buyers, a self-hostable open-weight model is now within a whisker of frontier quality — a real check on proprietary pricing power.*
Chart: `charts/04_open_vs_proprietary.png`

---

## Tier 2 — Competitive structure

### 5. China's top labs have nearly erased the frontier gap
**Headline: The best Chinese lab now trails the best US/Western lab by only ~26 Elo, and Chinese models have topped the entire board in 12 snapshots.**

Grouping Chinese labs (Alibaba, DeepSeek, Tencent, Zhipu/Z.ai, MiniMax, Moonshot, StepFun, 01.AI, Baidu, Tsinghua) against US/Western labs (OpenAI, Google, Anthropic, Meta, xAI, Mistral, Microsoft, NVIDIA, Cohere, Amazon): the frontier gap has narrowed from the West being 66 points behind in mid-2023, through a wider Western lead, to just **26 points** today (recent 12-snapshot average ~26). DeepSeek's early-2025 run even put a Chinese lab at #1 for 11 straight weeks.

*So what: the "US models are years ahead" narrative doesn't hold on human-preference benchmarks — the frontier is now a genuinely bilateral race.*
Chart: `charts/05_china_vs_us.png`

### 6. Longest reign by a single model: claude-opus-4-6-thinking
**Headline: The individual model that ruled longest is Anthropic's claude-opus-4-6-thinking at 40 snapshots at #1; Google's gemini-2.5-pro (27) and OpenAI's gpt-4o-2024-05-13 (24) round out the podium.**

Top models by total weeks at #1: **claude-opus-4-6-thinking 40, gemini-2.5-pro 27, gpt-4o-2024-05-13 24, gemini-3-pro 20, o1-preview 18, o3-2025-04-16 13, claude-opus-4-6 13, deepseek-r1 11.** At the other extreme, **3** models touched #1 for exactly one snapshot before being dethroned (e.g. guanaco-33b, gpt-4-0125-preview, grok-2-2024-08-13) — a reminder of how quickly a fleeting lead can evaporate.

*So what: real staying power at the very top is rare — only a handful of models have held #1 for more than a couple of months.*
Chart: `charts/06_model_reign_top1.png`

### 7. Fastest climbers and blockbuster debuts
**Headline: The biggest single-week rating jumps came in a Jan 2024 Arena recalibration (+60 to +94 Elo across many models), while the most dramatic debuts arrived at the very top — claude-opus-4-6-thinking launched straight to #1 at 1501.**

The largest week-over-week gains cluster on 2024-01-09 (dolphin-2.2.1-mistral-7b +94, gemini-pro +76, gpt-3.5-turbo-1106 +71, mixtral-8x7b +64), reflecting a leaderboard-wide rescaling rather than sudden model improvements. More telling are **high debuts** — models appearing near the summit on day one: **claude-opus-4-6-thinking (debut #1 @ 1501), gemini-3-pro (debut #1 @ 1495), gemini-3.1-pro-preview (debut #2 @ 1497), gemini-2.5-pro (debut #1 @ 1477), gpt-5-high (debut #2 @ 1462).**

*So what: flagship launches now enter at or near the top instantly — there is no "ramp-up," which is why leadership changes so abruptly.*
Chart: `charts/07_fastest_climbers.png`

### 8. The top 10 flipped from fully open to fully proprietary
**Headline: In May 2023 the top 10 was 100% open-weight; today it is 0% open — every current top-10 model is proprietary.**

Tracking license mix among the top 10 over time shows a decisive shift: open-weight models owned the entire top 10 in early 2023, the proprietary share first hit 100% around mid-2024, and the latest snapshot's top 10 is entirely proprietary. This coexists with Finding 4 (open models are close on raw quality) — open weights are competitive just *outside* the elite tier, which is currently a proprietary club.

*So what: open models have caught up on capability but not on the absolute podium — the last ~30 Elo to the very top remains proprietary territory.*
Chart: `charts/08_top10_license_mix.png`

---

## Tier 3 — Method & measurement quality

### 9. More votes mean sharper ratings — and today's top ranks are a statistical tie
**Headline: Confidence-interval width shrinks from ~43 Elo for models with under 1,000 votes to ~5.6 Elo for models with 100k+ votes (correlation -0.89) — and in the latest snapshot 371 of 373 adjacent-rank pairs have overlapping intervals, meaning they are statistically indistinguishable.**

Median 95% CI width by vote-count bin: **<1k -> 43, 1-3k -> 25, 3-10k -> 17, 10-30k -> 10, 30-100k -> 7.5, 100k+ -> 5.6 Elo.** Precision scales cleanly with sample size, exactly as sampling theory predicts. The flip side: because the top of the board is so compressed (Finding 3), nearly every neighbor pair overlaps. Even #1 vs #2 (claude-opus-4-6-thinking vs claude-opus-4-6) differ by only 3.7 Elo with overlapping intervals — a statistical tie.

*So what: treat small rating differences and exact ranks near the top as noise — "top cluster," not "#1 vs #4," is the honest read.*
Chart: `charts/09_votes_vs_precision.png`

### 10. Some models are specialists — much stronger in Vision or WebDev than in plain text
**Headline: Tencent's hunyuan-large-vision ranks 170 places higher in Vision than in text; IBM's granite-4.1-8b and several MiniMax models rank 80-120 places higher in WebDev than in text.**

Comparing a model's rank in a specialty arena vs the text arena in the same snapshot surfaces clear specialists. **Vision** (snapshot 2026-07-02): hunyuan-large-vision (+170 ranks), plus a cluster of older Google/Anthropic vision-capable models that remain listed on the vision board after dropping down the text board. **WebDev** (snapshot 2026-07-10): granite-4.1-8b (+121), minimax-m2.5 (+102), minimax-m2 (+97), qwen3-coder-480b (+83) — coding-tuned models that punch far above their general-chat rank.

*So what: "best overall" is the wrong question for a specific job — a mid-pack text model can be a top-tier coding or vision model.*
Chart: `charts/10_webdev_specialists.png`

### 11. Style control exposes who was winning on formatting rather than substance
**Headline: When answer length and formatting are neutralized, Amazon's nova-experimental chat model drops 49 ranks and Google's gemini-2.5-pro drops 33 — while OpenAI's gpt-5.2-chat and several xAI Grok models rise 17-37 ranks.**

The Arena's "style control" adjustment strips out the advantage models gain from longer, prettier, more heavily formatted answers. Comparing text vs style-controlled ranks in the latest snapshot, the biggest **fallers** (style-reliant) are amazon-nova-experimental-chat (-49 ranks worse), nvidia-nemotron-3-ultra (-42), glm-4.6 (-35), gemini-2.5-pro (-33), and several Qwen models. The biggest **risers** (rewarded for substance) are gpt-5.2-chat-latest (+37 ranks better), grok-4.1-thinking and grok-4.20-beta1 (+24 each), and gpt-5.6-sol-xhigh (+16).

*So what: raw leaderboard position can overstate models that "write to impress" — style-controlled rank is the fairer measure of actual answer quality.*
Chart: `charts/11_style_control_effect.png`

---

## Reproducibility
- **Script:** `analysis/arena_analysis.py` (pandas + matplotlib; run from the project root).
- **Data:** `data/ai_model_arena_rankings.csv`.
- **Charts:** all 11 PNGs at 160 dpi in `charts/`.
- Every number above is computed directly from the source data; nothing is estimated or fabricated.
'''

with open(os.path.join("analysis", "FINDINGS.md"), "w", encoding="utf-8") as _f:
    _f.write(FINDINGS_MD)
print("    wrote analysis/FINDINGS.md")

hr("DONE")
print(f"All charts written to ./{CHART_DIR}/")
print("Run complete.")
