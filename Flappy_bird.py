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
canvas#nc {{ display: block; width: 100%; border-radius: 6px; }}
.net-lbl {{ font-size: 9px; color: #3a4a6a; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px; }}
#statusBar {{ font-size: 10px; color: #3a4a6a; text-align: center; margin-top: 4px; font-family: 'Space Mono', monospace; }}
.bar-bg {{ height: 4px; background: #1a2540; border-radius: 2px; overflow: hidden; margin-top: 6px; }}
.bar-fill {{ height: 100%; background: #f9c74f; border-radius: 2px; transition: width 0.3s; }}
</style>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
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
      <div class="net-lbl">Neural Net — Best Bird</div>
      <canvas id="nc" width="186" height="140"></canvas>
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
const nc = document.getElementById('nc');
const nc2 = nc.getContext('2d');
const fc = document.getElementById('fc');
const fc2 = fc.getContext('2d');

function rw() {{ return (Math.random()*2-1); }}
class NNet {{
  constructor(w) {{
    this.w = w ? [...w] : Array.from({{length:24}}, rw);
  }}
  forward(inp) {{
    let h = [0,0,0,0];
    for (let j=0;j<4;j++) {{
      for (let i=0;i<5;i++) h[j] += inp[i]*this.w[j*5+i];
      h[j] = Math.tanh(h[j]);
    }}
    let o = 0;
    for (let j=0;j<4;j++) o += h[j]*this.w[20+j];
    this.hidden=[...h]; this.out=Math.tanh(o); return this.out;
  }}
  mutate(r) {{
    return new NNet(this.w.map(w => Math.random()<r ? w+(Math.random()*2-1)*0.4 : w));
  }}
}}

const GRAV=0.38, JUMP=-7, BR=11, PIPE_W=52, PIPE_SPEED=2.4;
function mkBird(net) {{
  return {{x:80,y:H/2,vy:0,alive:true,score:0,fitness:0,net:net||new NNet(),hidden:[0,0,0,0],out:0}};
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

let bestBird=null;
function step() {{
  frameN++;
  if (frameN%82===0) addPipe();
  for (let p of pipes) p.x -= PIPE_SPEED;
  pipes = pipes.filter(p=>p.x>-PIPE_W-10);
  for (let p of pipes) {{
    if (!p.passed && p.x < (birds[0]?.x||80)-BR) {{ p.passed=true; score++; }}
  }}
  let np = pipes.find(p=>p.x+PIPE_W>(birds[0]?.x||80)-BR) || pipes[0];
  for (let b of birds) {{
    if (!b.alive) continue;
    b.score=score; b.fitness=frameN+score*60;
    let dist = np ? (np.x-b.x)/W : 1;
    let topY = np ? np.top/H : 0.5;
    let botY = np ? np.bot/H : 0.5;
    let out = b.net.forward([b.y/H, b.vy/15, dist, topY, botY]);
    b.hidden=[...b.net.hidden]; b.out=out;
    if (out>0) b.vy=JUMP;
    b.vy+=GRAV; b.y+=b.vy;
    if (b.y<BR||b.y>H-BR) {{ b.alive=false; continue; }}
    if (np) {{
      if (b.x+BR>np.x && b.x-BR<np.x+PIPE_W) {{
        if (b.y-BR<np.top||b.y+BR>np.bot) b.alive=false;
      }}
    }}
  }}
  let alive = birds.filter(b=>b.alive);
  bestBird = (alive.length>0?alive:birds).sort((a,b)=>b.fitness-a.fitness)[0];
  if (alive.length===0) evolve();
  let aliveCount = birds.filter(b=>b.alive).length;
  document.getElementById('genVal').textContent=generation;
  document.getElementById('bestVal').textContent=bestScore;
  document.getElementById('aliveVal').textContent=aliveCount+' / '+POP_SIZE;
  document.getElementById('scoreVal').textContent='score: '+score;
  document.getElementById('aliveBar').style.width=Math.round(aliveCount/POP_SIZE*100)+'%';
  document.getElementById('statusBar').textContent='gen '+generation+' · '+aliveCount+' alive · pipes cleared: '+score;
}}

// Stars background
let stars = Array.from({{length:60}},()=>([Math.random()*W,Math.random()*H,Math.random()*1.5+0.3]));

function drawGame() {{
  ctx.fillStyle='#0a0f1a'; ctx.fillRect(0,0,W,H);
  // stars
  for (let [sx,sy,sr] of stars) {{
    ctx.beginPath(); ctx.arc(sx,sy,sr,0,Math.PI*2);
    ctx.fillStyle='rgba(200,220,255,0.4)'; ctx.fill();
  }}
  // ground
  ctx.fillStyle='#0d2a1a'; ctx.fillRect(0,H-22,W,22);
  ctx.fillStyle='#1a5c2a'; ctx.fillRect(0,H-24,W,4);
  // pipes
  for (let p of pipes) {{
    let grad = ctx.createLinearGradient(p.x,0,p.x+PIPE_W,0);
    grad.addColorStop(0,'#1a5c2a'); grad.addColorStop(0.4,'#2a8c3a'); grad.addColorStop(1,'#1a5c2a');
    ctx.fillStyle=grad;
    ctx.beginPath(); ctx.roundRect(p.x,0,PIPE_W,p.top,4); ctx.fill();
    ctx.beginPath(); ctx.roundRect(p.x,p.bot,PIPE_W,H-p.bot-22,4); ctx.fill();
    // caps
    ctx.fillStyle='#1a7030';
    ctx.beginPath(); ctx.roundRect(p.x-5,p.top-16,PIPE_W+10,16,3); ctx.fill();
    ctx.beginPath(); ctx.roundRect(p.x-5,p.bot,PIPE_W+10,16,3); ctx.fill();
  }}
  // dead birds
  for (let b of birds) {{
    if (!b.alive) {{
      ctx.beginPath(); ctx.arc(b.x,b.y,BR,0,Math.PI*2);
      ctx.fillStyle='rgba(100,100,120,0.15)'; ctx.fill();
    }}
  }}
  // alive birds
  for (let b of birds.filter(b=>b.alive)) {{
    ctx.save();
    ctx.translate(b.x,b.y);
    let ang=Math.max(-0.5,Math.min(0.5,b.vy*0.05));
    ctx.rotate(ang);
    let isBest=(b===bestBird);
    // body
    ctx.beginPath(); ctx.arc(0,0,BR,0,Math.PI*2);
    ctx.fillStyle=isBest?'#f9c74f':'#f4d03f';
    ctx.fill();
    if (isBest) {{ ctx.strokeStyle='#ff9f00'; ctx.lineWidth=2; ctx.stroke(); }}
    // wing
    ctx.fillStyle=isBest?'#e67e00':'#d4a800';
    ctx.beginPath(); ctx.ellipse(-3,4,7,4,0.3,0,Math.PI*2); ctx.fill();
    // eye
    ctx.fillStyle='#fff'; ctx.beginPath(); ctx.arc(5,-3,3.5,0,Math.PI*2); ctx.fill();
    ctx.fillStyle='#111'; ctx.beginPath(); ctx.arc(6,-2.5,1.8,0,Math.PI*2); ctx.fill();
    ctx.fillStyle='#fff'; ctx.beginPath(); ctx.arc(6.5,-3.2,0.7,0,Math.PI*2); ctx.fill();
    ctx.restore();
  }}
  // score overlay
  ctx.font='bold 32px Space Mono, monospace';
  ctx.textAlign='center';
  ctx.fillStyle='rgba(0,0,0,0.5)';
  ctx.fillText(score,W/2+1,45);
  ctx.fillStyle='#f9c74f';
  ctx.fillText(score,W/2,44);
  // gen label
  ctx.font='11px Space Mono, monospace';
  ctx.fillStyle='rgba(255,255,255,0.2)';
  ctx.textAlign='left';
  ctx.fillText('GEN '+generation, 12, H-30);
}}

function drawNet() {{
  nc2.clearRect(0,0,186,140);
  if (!bestBird||!bestBird.net.hidden) return;
  const b=bestBird;
  const lx=[22,93,164];
  const ly=[[18,36,54,72,90],[28,50,72,94],[61]];
  // connections i->h
  for (let j=0;j<4;j++) for (let i=0;i<5;i++) {{
    let w=b.net.w[j*5+i], a=Math.min(0.6,Math.abs(w)*0.4);
    nc2.strokeStyle=`rgba(88,130,200,${{a}})`;
    nc2.lineWidth=0.8;
    nc2.beginPath(); nc2.moveTo(lx[0],ly[0][i]); nc2.lineTo(lx[1],ly[1][j]); nc2.stroke();
  }}
  // connections h->o
  for (let j=0;j<4;j++) {{
    let w=b.net.w[20+j], a=Math.min(0.6,Math.abs(w)*0.4);
    nc2.strokeStyle=`rgba(249,199,79,${{a}})`;
    nc2.lineWidth=0.8;
    nc2.beginPath(); nc2.moveTo(lx[1],ly[1][j]); nc2.lineTo(lx[2],ly[2][0]); nc2.stroke();
  }}
  // input nodes
  const iLabels=['y','vy','Δx','pt','pb'];
  for (let i=0;i<5;i++) {{
    nc2.beginPath(); nc2.arc(lx[0],ly[0][i],6,0,Math.PI*2);
    nc2.fillStyle='#185fa5'; nc2.fill();
    nc2.fillStyle='#8abaef'; nc2.font='8px Space Mono,monospace'; nc2.textAlign='right';
    nc2.fillText(iLabels[i],lx[0]-9,ly[0][i]+3);
  }}
  // hidden
  for (let j=0;j<4;j++) {{
    let act=b.net.hidden[j];
    let r=Math.round((act+1)/2*180), bl=Math.round((1-(act+1)/2)*180);
    nc2.beginPath(); nc2.arc(lx[1],ly[1][j],6,0,Math.PI*2);
    nc2.fillStyle=`rgb(${{r}},80,${{bl}})`; nc2.fill();
  }}
  // output
  let jumping=b.net.out>0;
  nc2.beginPath(); nc2.arc(lx[2],ly[2][0],8,0,Math.PI*2);
  nc2.fillStyle=jumping?'#f9c74f':'#1a2e4a'; nc2.fill();
  nc2.strokeStyle=jumping?'#ff9f00':'#2a4a7a'; nc2.lineWidth=1.5; nc2.stroke();
  nc2.fillStyle='#5a6a8a'; nc2.font='8px Space Mono,monospace'; nc2.textAlign='left';
  nc2.fillText(jumping?'JUMP':'HOLD',lx[2]+12,ly[2][0]+3);
  nc2.textAlign='left'; nc2.fillStyle='#2a3a5a'; nc2.font='8px Space Mono,monospace';
  nc2.fillText('in',4,9); nc2.fillText('hidden',75,9); nc2.fillText('out',154,9);
}}

function drawFitness() {{
  fc2.clearRect(0,0,186,60);
  if (fitnessHistory.length<2) return;
  let max=Math.max(...fitnessHistory,1);
  fc2.strokeStyle='#f9c74f'; fc2.lineWidth=1.5;
  fc2.beginPath();
  for (let i=0;i<fitnessHistory.length;i++) {{
    let x=4+(i/(fitnessHistory.length-1))*178;
    let y=56-(fitnessHistory[i]/max)*52;
    i===0?fc2.moveTo(x,y):fc2.lineTo(x,y);
  }}
  fc2.stroke();
  // fill
  fc2.lineTo(4+(fitnessHistory.length-1)/(fitnessHistory.length-1)*178,56);
  fc2.lineTo(4,56);
  fc2.closePath();
  fc2.fillStyle='rgba(249,199,79,0.08)'; fc2.fill();
  // axes
  fc2.fillStyle='#2a3a5a'; fc2.font='8px Space Mono,monospace';
  fc2.textAlign='left'; fc2.fillText('fitness',2,10);
  fc2.textAlign='right'; fc2.fillText(Math.round(max),184,10);
}}

initPop(POP_SIZE);

function loop() {{
  for (let i=0;i<SIM_SPEED;i++) step();
  drawGame(); drawNet(); drawFitness();
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

st.caption("Adjust controls in the sidebar and click **Rerun** (or press R) to apply new settings. The neural net visualizer shows the best bird's activations in real time.")
