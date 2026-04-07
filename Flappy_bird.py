import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="RL Flappy Bird",
    page_icon="🐦",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
.stApp {
    background: #0a0f1a;
}
.main .block-container {
    padding: 1.5rem 2rem 2rem 2rem;
    max-width: 1200px;
}
h1 {
    font-family: 'Space Mono', monospace !important;
    color: #f9c74f !important;
    font-size: 1.6rem !important;
    letter-spacing: -0.02em;
    margin-bottom: 0 !important;
}
.subtitle {
    color: #5a6a8a;
    font-size: 0.85rem;
    margin-top: 2px;
    margin-bottom: 1.2rem;
    font-family: 'Space Mono', monospace;
}
hr { border-color: #1a2540 !important; }
.stSlider label { color: #8899bb !important; font-size: 0.8rem !important; font-family: 'Space Mono', monospace !important; }
.stSlider [data-baseweb="slider"] { margin-top: -4px; }
div[data-testid="stMetricValue"] { color: #f9c74f !important; font-family: 'Space Mono', monospace !important; font-size: 1.6rem !important; }
div[data-testid="stMetricLabel"] { color: #5a6a8a !important; font-size: 0.72rem !important; text-transform: uppercase; letter-spacing: 0.08em; font-family: 'Space Mono', monospace !important; }
.stButton button {
    background: transparent !important;
    border: 1px solid #1e2d4a !important;
    color: #8899bb !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.78rem !important;
    width: 100%;
    transition: all 0.2s;
}
.stButton button:hover {
    border-color: #f9c74f !important;
    color: #f9c74f !important;
}
section[data-testid="stSidebar"] {
    background: #060b14 !important;
    border-right: 1px solid #1a2540 !important;
}
section[data-testid="stSidebar"] .stMarkdown p {
    color: #8899bb;
    font-size: 0.8rem;
    font-family: 'Space Mono', monospace;
}
</style>
""", unsafe_allow_html=True)

st.markdown("# 🐦 RL Flappy Bird")
st.markdown('<p class="subtitle">neuroevolution · genetic algorithm · real-time learning</p>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ⚙️ Config")
    pop_size = st.slider("Population size", 10, 200, 50, 10)
    sim_speed = st.slider("Simulation speed", 1, 20, 1, 1)
    mut_rate = st.slider("Mutation rate (%)", 1, 50, 10, 1)
    st.markdown("---")
    st.markdown("**How it works**")
    st.markdown("""
Each bird has a tiny neural net:
- **5 inputs**: y position, velocity, pipe distance, gap top, gap bottom
- **4 hidden** neurons (tanh)
- **1 output**: jump or hold

After all birds die, the top 5 survivors breed the next generation via weight mutation.
    """)
    st.markdown("---")
    st.markdown("**Tips**")
    st.markdown("""
- Crank speed to **10–20x** to skip early chaos
- Lower mutation after gen 10 to **exploit**
- Bigger populations find solutions faster
    """)

game_html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ background: #0a0f1a; font-family: 'Space Mono', monospace; overflow: hidden; }}
#app {{ display: flex; gap: 16px; padding: 12px; height: 100vh; align-items: flex-start; }}
#canvasWrap {{ flex: 1; }}
canvas#gc {{ display: block; width: 100%; border-radius: 10px; border: 1px solid #1a2540; }}
#panel {{ width: 210px; display: flex; flex-direction: column; gap: 10px; }}
.card {{ background: #0d1525; border: 1px solid #1a2540; border-radius: 10px; padding: 10px 12px; }}
.lbl {{ font-size: 10px; color: #5a6a8a; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 3px; }}
.val {{ font-size: 22px; font-weight: 700; color: #f9c74f; font-family: 'Space Mono', monospace; }}
.sub {{ font-size: 11px; color: #5a6a8a; margin-top: 2px; }}
.row {{ display: flex; gap: 10px; }}
.row .card {{ flex: 1; }}
#statusBar {{ font-size: 10px; color: #3a4a6a; text-align: center; margin-top: 4px; font-family: 'Space Mono', monospace; }}
.bar-bg {{ height: 4px; background: #1a2540; border-radius: 2px; overflow: hidden; margin-top: 6px; }}
.bar-fill {{ height: 100%; background: #f9c74f; border-radius: 2px; transition: width 0.3s; }}
</style>
</head>
<body>
<div id="app">
  <div id="canvasWrap">
    <canvas id="gc" width="400" height="500"></canvas>
    <div id="statusBar">initializing...</div>
  </div>
  <div id="panel">
    <div class="row">
      <div class="card"><div class="lbl">Gen</div><div class="val" id="genVal">1</div></div>
      <div class="card"><div class="lbl">Best</div><div class="val" id="bestVal">0</div></div>
    </div>
    <div class="card">
      <div class="lbl">Alive</div>
      <div class="val" id="aliveVal">{pop_size}</div>
      <div class="sub" id="scoreVal">score: 0</div>
      <div class="bar-bg"><div class="bar-fill" id="aliveBar" style="width:100%"></div></div>
    </div>
    <div class="card">
      <div class="lbl">Fitness trend</div>
      <canvas id="fc" width="186" height="60"></canvas>
    </div>
  </div>
</div>

<script>
const POP_SIZE = {pop_size};
const SIM_SPEED = {sim_speed};
const MUT_RATE = {mut_rate / 100};

const gc = document.getElementById('gc');
const ctx = gc.getContext('2d');
const W = 400, H = 500;
const fc = document.getElementById('fc');
const fc2 = fc.getContext('2d');

function rw() {{ return (Math.random()*2-1); }}

class NNet {{
  constructor(w) {{
    this.w = w ? [...w] : Array.from({{length:24}}, rw);
  }}
  forward(inp) {{
    let h=[0,0,0,0];
    for (let j=0;j<4;j++) {{
      for (let i=0;i<5;i++) h[j]+=inp[i]*this.w[j*5+i];
      h[j]=Math.tanh(h[j]);
    }}
    let o=0;
    for (let j=0;j<4;j++) o+=h[j]*this.w[20+j];
    return Math.tanh(o);
  }}
  mutate(r) {{
    return new NNet(this.w.map(w => Math.random()<r ? w+(Math.random()*2-1)*0.4 : w));
  }}
}}

const GRAV=0.38, JUMP=-7, BR=11, PIPE_W=52, PIPE_SPEED=2.4;

function mkBird(net) {{
  return {{x:80,y:H/2,vy:0,alive:true,fitness:0,net:net||new NNet()}};
}}

let birds=[], pipes=[], frameN=0, score=0, generation=1, bestScore=0;
let fitnessHistory=[];

function addPipe() {{
  let top = 85 + Math.random()*(H-145-80);
  pipes.push({{x:W+20,top,bot:top+145,passed:false}});
}}

function initPop(size) {{
  birds = Array.from({{length:size}},()=>mkBird());
  pipes=[]; frameN=0; score=0; addPipe();
}}

function evolve() {{
  let sorted = [...birds].sort((a,b)=>b.fitness-a.fitness);
  let best = sorted[0];
  if (best.fitness>bestScore) bestScore=Math.round(best.fitness);
  fitnessHistory.push(Math.round(best.fitness));
  if (fitnessHistory.length>30) fitnessHistory.shift();
  generation++;
  let top5 = sorted.slice(0,5);
  let nb = [mkBird(best.net)];
  while(nb.length<POP_SIZE) {{
    let p = top5[Math.floor(Math.random()*top5.length)];
    nb.push(mkBird(p.net.mutate(MUT_RATE)));
  }}
  birds=nb; pipes=[]; frameN=0; score=0; addPipe();
}}

function step() {{
  frameN++;
  if (frameN%82===0) addPipe();
  for (let p of pipes) p.x -= PIPE_SPEED;
  pipes = pipes.filter(p=>p.x>-PIPE_W-10);

  let np = pipes[0];

  for (let b of birds) {{
    if (!b.alive) continue;
    b.fitness=frameN;
    let out = b.net.forward([b.y/H, b.vy/15, 0.5, 0.5, 0.5]);
    if (out>0) b.vy=JUMP;
    b.vy+=GRAV; b.y+=b.vy;
    if (b.y<BR||b.y>H-BR) b.alive=false;
  }}

  let alive = birds.filter(b=>b.alive);
  if (alive.length===0) evolve();

  let aliveCount = birds.filter(b=>b.alive).length;

  document.getElementById('genVal').textContent=generation;
  document.getElementById('bestVal').textContent=bestScore;
  document.getElementById('aliveVal').textContent=aliveCount+' / '+POP_SIZE;
  document.getElementById('aliveBar').style.width=Math.round(aliveCount/POP_SIZE*100)+'%';
  document.getElementById('statusBar').textContent='gen '+generation+' · '+aliveCount+' alive';
}}

function drawGame() {{
  ctx.fillStyle='#0a0f1a'; ctx.fillRect(0,0,W,H);

  for (let b of birds) {{
    ctx.beginPath();
    ctx.arc(b.x,b.y,BR,0,Math.PI*2);
    ctx.fillStyle=b.alive?'#f9c74f':'rgba(100,100,120,0.15)';
    ctx.fill();
  }}
}}

function drawFitness() {{
  fc2.clearRect(0,0,186,60);
  if (fitnessHistory.length<2) return;
  let max=Math.max(...fitnessHistory,1);
  fc2.strokeStyle='#f9c74f';
  fc2.beginPath();
  for (let i=0;i<fitnessHistory.length;i++) {{
    let x=4+(i/(fitnessHistory.length-1))*178;
    let y=56-(fitnessHistory[i]/max)*52;
    i===0?fc2.moveTo(x,y):fc2.lineTo(x,y);
  }}
  fc2.stroke();
}}

initPop(POP_SIZE);

function loop() {{
  for (let i=0;i<SIM_SPEED;i++) step();
  drawGame(); drawFitness();
  requestAnimationFrame(loop);
}}
requestAnimationFrame(loop);
</script>
</body>
</html>
"""

components.html(game_html, height=560, scrolling=False)

st.markdown("---")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Population", pop_size)
c2.metric("Speed", f"{sim_speed}x")
c3.metric("Mutation", f"{mut_rate}%")
c4.metric("Architecture", "5→4→1")

st.caption("Adjust controls in the sidebar and click **Rerun** (or press R) to apply new settings.")
