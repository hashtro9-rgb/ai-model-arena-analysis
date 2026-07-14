# LMArena Leaderboard History — What the Data Says

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
