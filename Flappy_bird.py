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

/* subtle depth added */
.stApp {
    background: radial-gradient(circle at top, #0a0f1a, #050810);
}

.main .block-container {
    padding: 1.5rem 2rem 2rem 2rem;
    max-width: 1200px;
}

h1 {
    font-family: 'Space Mono', monospace !important;
    color: #ffd166 !important;
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

.stSlider label {
    color: #8899bb !important;
    font-size: 0.8rem !important;
    font-family: 'Space Mono', monospace !important;
}

.stSlider [data-baseweb="slider"] { margin-top: -4px; }

div[data-testid="stMetricValue"] {
    color: #ffd166 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 1.6rem !important;
}

div[data-testid="stMetricLabel"] {
    color: #5a6a8a !important;
    font-size: 0.72rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-family: 'Space Mono', monospace !important;
}

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
    border-color: #ffd166 !important;
    color: #ffd166 !important;
    transform: translateY(-1px);
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

game_html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
body {{ background: #0a0f1a; margin:0; overflow:hidden; }}
canvas {{ display:block; margin:auto; }}
</style>
</head>
<body>
<canvas id="gc" width="400" height="500"></canvas>

<script>
const POP_SIZE = {pop_size};
const SIM_SPEED = {sim_speed};
const MUT_RATE = {mut_rate / 100};

const gc = document.getElementById('gc');
const ctx = gc.getContext('2d');

const W=400, H=500;

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
    this.out=Math.tanh(o);
    return this.out;
  }}
  mutate(r) {{
    return new NNet(this.w.map(w => Math.random()<r ? w+(Math.random()*2-1)*0.4 : w));
  }}
}}

const GRAV=0.38, JUMP=-7, BR=11;

function mkBird(net) {{
  return {{x:80,y:H/2,vy:0,alive:true,score:0,fitness:0,net:net||new NNet()}};
}}

let birds = Array.from({{length:POP_SIZE}},()=>mkBird());

function step() {{
  for (let b of birds) {{
    if (!b.alive) continue;
    let out=b.net.forward([b.y/H, b.vy/10, 0.5, 0.5, 0.5]);
    if (out>0) b.vy=JUMP;
    b.vy+=GRAV;
    b.y+=b.vy;
    if (b.y<0||b.y>H) b.alive=false;
  }}
}}

function draw() {{
  ctx.fillStyle='#0a0f1a';
  ctx.fillRect(0,0,W,H);

  for (let b of birds) {{
    ctx.beginPath();

    // subtle glow
    ctx.shadowColor = 'rgba(255,209,102,0.25)';
    ctx.shadowBlur = 8;

    ctx.arc(b.x,b.y,BR,0,Math.PI*2);
    ctx.fillStyle=b.alive?'#ffd166':'rgba(255,255,255,0.1)';
    ctx.fill();

    ctx.shadowBlur = 0;
  }}
}}

function loop() {{
  for(let i=0;i<SIM_SPEED;i++) step();
  draw();
  requestAnimationFrame(loop);
}}

loop();
</script>
</body>
</html>
"""

components.html(game_html, height=520)

st.markdown("---")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Population", pop_size)
c2.metric("Speed", f"{sim_speed}x")
c3.metric("Mutation", f"{mut_rate}%")
c4.metric("Architecture", "5→4→1")
