"""
Build the self-contained interactive dashboard (index.html) for GitHub Pages.
==============================================================================

Reads analysis/dashboard_data.json (produced by arena_analysis.py) and writes
index.html at the repo root with ALL data, CSS and JS inlined. The only
external resource the shipped page loads is the pinned Chart.js CDN bundle.

Run (from the project root) after arena_analysis.py:

    python analysis/build_dashboard.py
"""

import json
import os

DATA_PATH = os.path.join("analysis", "dashboard_data.json")
OUT_PATH = "index.html"
CHARTJS = "https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    data_json = f.read()

# Compact validation so we fail loudly if the pipeline drifts.
d = json.loads(data_json)
for key in ("meta", "kpis", "dates", "trajectories", "frontier", "openprop",
            "chinaus", "licensemix", "reign", "scatter", "ci_bars"):
    assert key in d, f"dashboard_data.json missing '{key}'"

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The AI Model Race &middot; 2023&ndash;2026</title>
<script src="__CHARTJS__"></script>
<style>
  :root{
    --canvas:#F5F3FB; --ink:#2B2340; --muted:#8B84A0;
    --purple:#6C4AB6; --purple2:#7A5FCC; --magenta:#E84393; --pink:#FF4F9A;
    --lilac:#B497E7; --card:#FFFFFF; --line:#ECE8F5;
    --shadow:0 8px 24px rgba(108,74,182,.12);
  }
  *{box-sizing:border-box;}
  html,body{height:100%;margin:0;overflow:hidden;}
  body{
    font-family:"Segoe UI",-apple-system,BlinkMacSystemFont,Roboto,Helvetica,Arial,sans-serif;
    background:var(--canvas); color:var(--ink);
    display:grid; grid-template-columns:236px 1fr; height:100vh;
  }
  /* ---------- Nav rail ---------- */
  .rail{
    background:linear-gradient(170deg,#6C4AB6 0%,#7A5FCC 42%,#E84393 100%);
    color:#fff; display:flex; flex-direction:column; padding:22px 18px;
    position:relative;
  }
  .logo{font-weight:700; letter-spacing:.5px; line-height:1.15; font-size:18px;}
  .logo .dot{display:inline-block;width:10px;height:10px;border-radius:50%;
    background:#FF4F9A;margin-right:7px;box-shadow:0 0 0 4px rgba(255,79,154,.25);}
  .logo small{display:block;font-weight:400;font-size:11px;opacity:.8;margin-top:4px;letter-spacing:2px;}
  .menu{margin-top:34px;display:flex;flex-direction:column;gap:8px;}
  .menu button{
    all:unset; cursor:pointer; display:flex; align-items:center; gap:11px;
    padding:11px 13px; border-radius:11px; font-size:14px; color:rgba(255,255,255,.82);
    transition:background .15s,color .15s;
  }
  .menu button .ic{width:9px;height:9px;border-radius:2px;background:rgba(255,255,255,.55);}
  .menu button:hover{background:rgba(255,255,255,.10);color:#fff;}
  .menu button.active{background:rgba(255,255,255,.18);color:#fff;font-weight:600;}
  .menu button.active .ic{background:#fff;}
  .rail-foot{margin-top:auto;text-align:center;}
  .rail-foot .ring{position:relative;width:118px;height:118px;margin:0 auto 6px;}
  .rail-foot .ring .val{position:absolute;inset:0;display:flex;flex-direction:column;
    align-items:center;justify-content:center;}
  .rail-foot .ring .val b{font-size:24px;line-height:1;}
  .rail-foot .ring .val span{font-size:9.5px;opacity:.85;margin-top:3px;letter-spacing:.3px;}
  .rail-foot p{font-size:11px;opacity:.85;margin:8px 4px 0;line-height:1.35;}
  /* ---------- Main ---------- */
  .main{display:grid;grid-template-rows:auto auto 1fr;min-width:0;padding:18px 22px 14px;gap:14px;}
  .header{display:flex;align-items:baseline;gap:16px;flex-wrap:wrap;}
  .header h1{margin:0;font-size:23px;font-weight:700;
    background:linear-gradient(90deg,#6C4AB6,#E84393);-webkit-background-clip:text;
    background-clip:text;color:transparent;}
  .pills{display:flex;gap:8px;flex-wrap:wrap;}
  .pill{background:#fff;border:1px solid var(--line);border-radius:999px;
    padding:5px 12px;font-size:11.5px;color:var(--muted);box-shadow:var(--shadow);}
  /* ---------- KPI tiles ---------- */
  .kpis{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;}
  .kpi{border-radius:15px;padding:13px 15px;color:#fff;box-shadow:var(--shadow);position:relative;overflow:hidden;}
  .kpi h3{margin:0;font-size:11px;font-weight:600;opacity:.9;letter-spacing:.3px;text-transform:uppercase;}
  .kpi .big{font-size:27px;font-weight:700;margin-top:6px;line-height:1;}
  .kpi .sub{font-size:11px;opacity:.9;margin-top:5px;}
  .k1{background:linear-gradient(135deg,#6C4AB6,#7A5FCC);}
  .k2{background:linear-gradient(135deg,#7A5FCC,#B497E7);}
  .k3{background:linear-gradient(135deg,#9B59B6,#E84393);}
  .k4{background:linear-gradient(135deg,#E84393,#FF4F9A);}
  .k5{background:linear-gradient(135deg,#C0399B,#FF4F9A);}
  /* ---------- Tab panels ---------- */
  .stage{position:relative;min-height:0;}
  .panel{position:absolute;inset:0;display:none;grid-template-columns:1fr 1fr;
    grid-template-rows:1fr 1fr;gap:14px;}
  .panel.active{display:grid;}
  .card{background:var(--card);border-radius:16px;box-shadow:var(--shadow);
    padding:12px 14px 10px;display:flex;flex-direction:column;min-height:0;min-width:0;}
  .card .ct{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;}
  .card h2{margin:0;font-size:13.5px;font-weight:700;}
  .card .cs{font-size:10.5px;color:var(--muted);}
  .card .cv{position:relative;flex:1;min-height:0;}
  .card canvas{width:100%!important;height:100%!important;}
  .tall{grid-row:span 2;}
  select{font:inherit;font-size:11.5px;color:var(--ink);background:#fff;
    border:1px solid var(--line);border-radius:8px;padding:4px 8px;cursor:pointer;}
  .src{position:absolute;right:10px;bottom:2px;font-size:9px;color:#B7B0C6;}
  @media (max-width:1200px){
    body{grid-template-columns:200px 1fr;}
    .kpis{grid-template-columns:repeat(5,1fr);}
    .kpi .big{font-size:22px;}
  }
</style>
</head>
<body>
<script id="arena-data" type="application/json">__DATA__</script>

<!-- ===================== NAV RAIL ===================== -->
<aside class="rail">
  <div class="logo"><span class="dot"></span>AI MODEL ARENA
    <small>LEADERBOARD INTEL</small>
  </div>
  <nav class="menu" id="menu">
    <button class="active" data-tab="race"><span class="ic"></span>The Race</button>
    <button data-tab="structure"><span class="ic"></span>Competitive Structure</button>
    <button data-tab="quality"><span class="ic"></span>Rating Quality</button>
  </nav>
  <div class="rail-foot">
    <div class="ring">
      <canvas id="ringChart"></canvas>
      <div class="val"><b id="ringPct">91%</b><span>top-10 gap<br>compressed</span></div>
    </div>
    <p><b id="railSnaps">247</b> weekly snapshots analysed,<br>May 2023 &ndash; Jul 2026.</p>
  </div>
</aside>

<!-- ===================== MAIN ===================== -->
<main class="main">
  <div class="header">
    <h1>The AI Model Race &middot; 2023&ndash;2026</h1>
    <div class="pills">
      <span class="pill" id="pillSnaps">247 snapshots</span>
      <span class="pill" id="pillRows">~97k leaderboard rows</span>
      <span class="pill">May 2023 &ndash; Jul 2026</span>
      <span class="pill">Data: LMArena / Chatbot Arena</span>
    </div>
  </div>

  <div class="kpis" id="kpis"></div>

  <div class="stage">
    <!-- ---------- TAB 1: THE RACE ---------- -->
    <section class="panel active" id="tab-race">
      <div class="card tall">
        <div class="ct">
          <h2>Frontier trajectories &mdash; each lab's best model</h2>
          <select id="trajFilter" title="Filter which labs are shown">
            <option value="all">All labs</option>
            <option value="us">US / West labs</option>
            <option value="china">China labs</option>
          </select>
        </div>
        <div class="cv"><canvas id="trajChart"></canvas></div>
        <div class="cs">Click a legend item to toggle a lab. Best Elo per snapshot (text).</div>
      </div>
      <div class="card">
        <div class="ct"><h2>Frontier rises, top-10 pack compresses</h2></div>
        <div class="cv"><canvas id="frontChart"></canvas></div>
        <div class="cs">#1 &amp; #10 Elo (left) vs the #1&minus;#10 gap (right).</div>
      </div>
      <div class="card">
        <div class="ct"><h2>Open-weight vs proprietary frontier</h2></div>
        <div class="cv"><canvas id="openChart"></canvas></div>
        <div class="cs">Best Elo among open-weight vs proprietary models.</div>
      </div>
    </section>

    <!-- ---------- TAB 2: COMPETITIVE STRUCTURE ---------- -->
    <section class="panel" id="tab-structure">
      <div class="card tall">
        <div class="ct"><h2>China vs US / West frontier</h2></div>
        <div class="cv"><canvas id="geoChart"></canvas></div>
        <div class="cs">Best-model Elo per group each snapshot (text).</div>
      </div>
      <div class="card">
        <div class="ct"><h2>Top-10 license mix over time</h2></div>
        <div class="cv"><canvas id="mixChart"></canvas></div>
        <div class="cs">Share of open-weight vs proprietary among the top 10.</div>
      </div>
      <div class="card">
        <div class="ct"><h2>Longest reigns at #1 (by model)</h2></div>
        <div class="cv"><canvas id="reignChart"></canvas></div>
        <div class="cs">Total snapshots each model held rank #1.</div>
      </div>
    </section>

    <!-- ---------- TAB 3: RATING QUALITY ---------- -->
    <section class="panel" id="tab-quality">
      <div class="card tall">
        <div class="ct"><h2>More votes &rarr; tighter ratings</h2></div>
        <div class="cv"><canvas id="scatterChart"></canvas></div>
        <div class="cs">Each dot: a model in one snapshot. Line: median CI width per vote bin.</div>
      </div>
      <div class="card tall">
        <div class="ct"><h2>Latest top-15: confidence intervals overlap</h2></div>
        <div class="cv"><canvas id="ciChart"></canvas></div>
        <div class="cs" id="ciCaption">95% CI per model &mdash; overlapping bars are statistical ties.</div>
      </div>
    </section>
  </div>
</main>

<script>
const DATA = JSON.parse(document.getElementById('arena-data').textContent);
const C = {purple:'#6C4AB6', purple2:'#7A5FCC', magenta:'#E84393', pink:'#FF4F9A',
           lilac:'#B497E7', teal:'#00A6A6', amber:'#F39C12', blue:'#2E86DE',
           green:'#27AE60', red:'#C0392B', violet:'#8E44AD', ink:'#2B2340'};
Chart.defaults.font.family = '"Segoe UI",system-ui,sans-serif';
Chart.defaults.color = '#6f6885';
Chart.defaults.font.size = 11;

/* ---- KPI tiles ---- */
const k = DATA.kpis;
document.getElementById('kpis').innerHTML = [
  ['k1','Current #1', k.top_rating, k.top_org+' &middot; '+k.top_model],
  ['k2','Longest reign', k.longest_reign_weeks+' wks', 'Anthropic, ongoing'],
  ['k3','#1 &harr; #10 gap', k.gap_1_10, 'Elo (was 259 in 2023)'],
  ['k4','Open vs prop. gap', k.open_gap, 'Elo behind frontier'],
  ['k5','China vs US gap', k.china_gap, 'Elo behind frontier'],
].map(t=>`<div class="kpi ${t[0]}"><h3>${t[1]}</h3><div class="big">${t[2]}</div><div class="sub">${t[3]}</div></div>`).join('');

/* ---- header / rail meta ---- */
document.getElementById('pillSnaps').textContent = DATA.meta.snapshots+' snapshots';
document.getElementById('pillRows').textContent = '~'+Math.round(DATA.meta.rows/1000)+'k leaderboard rows';
document.getElementById('railSnaps').textContent = DATA.meta.snapshots;
document.getElementById('ringPct').textContent = k.top10_compression_pct+'%';

/* ---- helpers ---- */
const labels = DATA.dates;
// show a tick only at the first snapshot of each calendar year
function yearTicks(scaleOpts){
  scaleOpts.ticks = {maxRotation:0, autoSkip:false, callback:(v,i)=>{
    const y = labels[i].slice(0,4);
    const prev = i>0 ? labels[i-1].slice(0,4) : '';
    return y!==prev ? y : '';
  }};
}
const baseLine = {responsive:true, maintainAspectRatio:false, interaction:{mode:'index',intersect:false},
  elements:{point:{radius:0, hitRadius:8, hoverRadius:4}, line:{tension:.25, borderWidth:2}},
  plugins:{legend:{position:'top', labels:{boxWidth:12, boxHeight:12, usePointStyle:true, padding:10}},
           tooltip:{callbacks:{title:(it)=>labels[it[0].dataIndex]}}},
  scales:{x:{grid:{display:false}}, y:{grid:{color:'#F0ECF8'}}}};
function clone(o){return JSON.parse(JSON.stringify(o));}
function gradient(ctx, c1, c2){
  const g = ctx.createLinearGradient(0,0,0,ctx.canvas.height||260);
  g.addColorStop(0,c1); g.addColorStop(1,c2); return g;
}

/* ================= TAB 1 ================= */
const trajColors = {OpenAI:C.purple, Google:C.magenta, Anthropic:C.teal, Alibaba:C.amber,
  DeepSeek:C.blue, Meta:C.green, Mistral:C.red, xAI:C.violet};
const US = new Set(['OpenAI','Google','Anthropic','Meta','Mistral','xAI']);
const CHINA = new Set(['Alibaba','DeepSeek']);
const trajOpts = clone(baseLine); yearTicks(trajOpts.scales.x);
trajOpts.scales.y.title = {display:true, text:'Best model Elo'};
const trajChart = new Chart(document.getElementById('trajChart'), {
  type:'line',
  data:{labels, datasets:Object.keys(DATA.trajectories).map(org=>({
    label:org, data:DATA.trajectories[org], borderColor:trajColors[org],
    backgroundColor:trajColors[org], spanGaps:true}))},
  options:trajOpts
});
document.getElementById('trajFilter').addEventListener('change', e=>{
  const v = e.target.value;
  trajChart.data.datasets.forEach((ds,i)=>{
    const show = v==='all' || (v==='us'&&US.has(ds.label)) || (v==='china'&&CHINA.has(ds.label));
    trajChart.setDatasetVisibility(i, show);
  });
  trajChart.update();
});

const frontOpts = clone(baseLine); yearTicks(frontOpts.scales.x);
frontOpts.scales.y.title = {display:true, text:'Elo'};
frontOpts.scales.y1 = {position:'right', grid:{display:false},
  title:{display:true, text:'#1 - #10 gap'}};
new Chart(document.getElementById('frontChart'), {
  type:'line',
  data:{labels, datasets:[
    {label:'#1 rating', data:DATA.frontier.top1, borderColor:C.purple, backgroundColor:C.purple, spanGaps:true},
    {label:'#10 rating', data:DATA.frontier.top10, borderColor:C.lilac, backgroundColor:C.lilac, borderDash:[5,4], spanGaps:true},
    {label:'#1-#10 gap', data:DATA.frontier.gap, borderColor:C.magenta, backgroundColor:C.magenta, yAxisID:'y1', spanGaps:true}
  ]},
  options:frontOpts
});

const openOpts = clone(baseLine); yearTicks(openOpts.scales.x);
openOpts.scales.y.title = {display:true, text:'Best Elo'};
new Chart(document.getElementById('openChart'), {
  type:'line',
  data:{labels, datasets:[
    {label:'Best proprietary', data:DATA.openprop.prop, borderColor:C.purple, backgroundColor:C.purple, spanGaps:true},
    {label:'Best open-weight', data:DATA.openprop.open, borderColor:C.magenta, backgroundColor:C.magenta, spanGaps:true}
  ]},
  options:openOpts
});

/* ================= TAB 2 ================= */
const geoOpts = clone(baseLine); yearTicks(geoOpts.scales.x);
geoOpts.scales.y.title = {display:true, text:'Best Elo'};
new Chart(document.getElementById('geoChart'), {
  type:'line',
  data:{labels, datasets:[
    {label:'US / West best', data:DATA.chinaus.us, borderColor:C.purple, backgroundColor:C.purple, spanGaps:true},
    {label:'China best', data:DATA.chinaus.china, borderColor:C.magenta, backgroundColor:C.magenta, spanGaps:true}
  ]},
  options:geoOpts
});

const mixOpts = clone(baseLine); yearTicks(mixOpts.scales.x);
mixOpts.scales.y = {min:0, max:100, stacked:true, grid:{color:'#F0ECF8'},
  ticks:{callback:v=>v+'%'}, title:{display:true, text:'Share of top 10'}};
mixOpts.scales.x.stacked = true;
mixOpts.elements = {point:{radius:0}, line:{tension:.2}};
new Chart(document.getElementById('mixChart'), {
  type:'line',
  data:{labels, datasets:[
    {label:'Open-weight', data:DATA.licensemix.open, borderColor:C.magenta, backgroundColor:'rgba(232,67,147,.55)', fill:true, spanGaps:true},
    {label:'Proprietary', data:DATA.licensemix.prop, borderColor:C.purple, backgroundColor:'rgba(108,74,182,.55)', fill:true, spanGaps:true}
  ]},
  options:mixOpts
});

const reign = DATA.reign;
const reignOpts = clone(baseLine);
reignOpts.indexAxis = 'y';
reignOpts.plugins.legend.display = false;
reignOpts.scales = {x:{grid:{color:'#F0ECF8'}, title:{display:true, text:'Snapshots at #1'}},
  y:{grid:{display:false}}};
reignOpts.plugins.tooltip = {callbacks:{title:it=>reign[it[0].dataIndex].model,
  label:it=>reign[it.dataIndex].org+': '+reign[it.dataIndex].snapshots+' snapshots'}};
new Chart(document.getElementById('reignChart'), {
  type:'bar',
  data:{labels:reign.map(r=>r.model), datasets:[{
    data:reign.map(r=>r.snapshots),
    backgroundColor:reign.map((r,i)=>i%2?C.purple2:C.magenta),
    borderRadius:5, barThickness:'flex', maxBarThickness:16}]},
  options:reignOpts
});

/* ================= TAB 3 ================= */
new Chart(document.getElementById('scatterChart'), {
  data:{datasets:[
    {type:'scatter', label:'model-snapshot', data:DATA.scatter.map(p=>({x:p[0], y:p[1]})),
     pointRadius:2.4, pointBackgroundColor:'rgba(180,151,231,.45)', pointBorderWidth:0},
    {type:'line', label:'median CI width by vote bin',
     data:DATA.scatter_median.map(p=>({x:p[0], y:p[1]})),
     borderColor:C.magenta, backgroundColor:C.magenta, borderWidth:2.5,
     pointRadius:4, pointBackgroundColor:C.magenta, tension:.25}
  ]},
  options:{responsive:true, maintainAspectRatio:false,
    plugins:{legend:{position:'top', labels:{usePointStyle:true, boxWidth:10}},
      tooltip:{callbacks:{label:it=>'votes '+Math.round(it.parsed.x).toLocaleString()+', CI '+it.parsed.y+' Elo'}}},
    scales:{
      x:{type:'logarithmic', title:{display:true, text:'Vote count (log scale)'}, grid:{color:'#F0ECF8'}},
      y:{title:{display:true, text:'95% CI width (Elo)'}, grid:{color:'#F0ECF8'}}}}
});

const ci = DATA.ci_bars;
document.getElementById('ciCaption').textContent =
  k.overlap_pairs+' of '+k.overlap_total+' adjacent-rank pairs overlap in the latest snapshot.';
const ciOpts = clone(baseLine);
ciOpts.indexAxis = 'y';
ciOpts.plugins.legend.display = false;
ciOpts.plugins.tooltip = {callbacks:{
  title:it=>ci[it[0].dataIndex].model,
  label:it=>{const c=ci[it.dataIndex]; return c.org+': '+c.rating+' Elo ['+c.low+' &ndash; '+c.high+']';}}};
ciOpts.scales = {x:{min:Math.floor(Math.min(...ci.map(c=>c.low))-5),
  max:Math.ceil(Math.max(...ci.map(c=>c.high))+2),
  grid:{color:'#F0ECF8'}, title:{display:true, text:'Elo (95% confidence interval)'}},
  y:{grid:{display:false}, ticks:{font:{size:9.5}}}};
new Chart(document.getElementById('ciChart'), {
  type:'bar',
  data:{labels:ci.map((c,i)=>'#'+(i+1)+' '+c.model), datasets:[{
    data:ci.map(c=>[c.low, c.high]),
    backgroundColor:ci.map((c,i)=>i<3?C.magenta:C.purple2),
    borderRadius:4, barThickness:'flex', maxBarThickness:13}]},
  options:ciOpts
});

/* ---- progress ring in the rail ---- */
new Chart(document.getElementById('ringChart'), {
  type:'doughnut',
  data:{datasets:[{data:[k.top10_compression_pct, 100-k.top10_compression_pct],
    backgroundColor:['#FF4F9A','rgba(255,255,255,.22)'], borderWidth:0}]},
  options:{cutout:'78%', responsive:true, maintainAspectRatio:true,
    plugins:{legend:{display:false}, tooltip:{enabled:false}}, animation:{animateRotate:true}}
});

/* ================= TABS ================= */
const menu = document.getElementById('menu');
menu.addEventListener('click', e=>{
  const btn = e.target.closest('button'); if(!btn) return;
  menu.querySelectorAll('button').forEach(b=>b.classList.toggle('active', b===btn));
  document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));
  document.getElementById('tab-'+btn.dataset.tab).classList.add('active');
});
</script>
</body>
</html>
"""

html = (HTML
        .replace("__CHARTJS__", CHARTJS)
        .replace("__DATA__", data_json))

with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Wrote {OUT_PATH} ({len(html):,} bytes; data {len(data_json):,} bytes inlined).")
print(f"Chart.js pinned: {CHARTJS}")
