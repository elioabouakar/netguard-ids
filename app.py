import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
import pickle
import os

# ═══════════════════════════════════════════════════════════════════════
# PAGE CONFIG  (must be the FIRST streamlit call)
# ═══════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="NetGuard IDS",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════
# GLOBAL CSS
# ═══════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Exo+2:wght@300;400;600;800&display=swap');

/* ── Base ─────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
    background: #080c14 !important;
    font-family: 'Exo 2', sans-serif;
}
[data-testid="stSidebar"] {
    background: #0b1020 !important;
    border-right: 1px solid rgba(0,255,200,0.12);
}

/* ── Header card ──────────────────────────────────── */
.header-card {
    background: linear-gradient(135deg, #0d1f3c 0%, #091428 100%);
    border: 1px solid rgba(0,220,180,0.25);
    border-radius: 18px;
    padding: 28px 36px;
    margin-bottom: 28px;
    box-shadow: 0 0 40px rgba(0,200,160,0.06);
    position: relative;
    overflow: hidden;
}
.header-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #00e5c8, transparent);
}
.header-title {
    font-size: 2rem;
    font-weight: 800;
    color: #e8f4f0;
    margin: 0 0 6px 0;
    letter-spacing: -0.5px;
}
.header-sub {
    color: rgba(160,210,200,0.65);
    font-size: 0.95rem;
    margin: 0;
    font-weight: 300;
}

/* ── Metric cards ─────────────────────────────────── */
.metric-card {
    background: linear-gradient(145deg, #111827, #0f1a2e);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 22px 18px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.metric-card.red   { border-color: rgba(255,80,80,0.35);  box-shadow: 0 0 20px rgba(255,60,60,0.08); }
.metric-card.green { border-color: rgba(0,230,130,0.30);  box-shadow: 0 0 20px rgba(0,200,120,0.08); }
.metric-card.blue  { border-color: rgba(80,160,255,0.30); box-shadow: 0 0 20px rgba(60,130,240,0.08); }
.metric-card.amber { border-color: rgba(255,180,50,0.30); box-shadow: 0 0 20px rgba(240,160,30,0.08); }
.metric-value {
    font-family: 'Share Tech Mono', monospace;
    font-size: 2.6rem;
    font-weight: 400;
    line-height: 1;
    margin: 0;
}
.metric-value.red   { color: #ff5c5c; }
.metric-value.green { color: #00e68a; }
.metric-value.blue  { color: #5aabff; }
.metric-value.amber { color: #ffb833; }
.metric-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: rgba(180,200,220,0.5);
    margin-top: 8px;
}

/* ── Section titles ───────────────────────────────── */
.section-title {
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 3px;
    color: rgba(0,220,180,0.7);
    margin: 24px 0 12px 0;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(0,220,180,0.15);
}

/* ── Alert banners ────────────────────────────────── */
.alert-critical {
    background: linear-gradient(90deg, rgba(220,30,30,0.25), rgba(180,0,0,0.15));
    border: 1px solid rgba(255,80,80,0.5);
    border-radius: 12px;
    padding: 18px 24px;
    text-align: center;
    font-size: 1.05rem;
    font-weight: 700;
    color: #ff8080;
    animation: threat-pulse 2s ease-in-out infinite;
    margin: 16px 0;
}
.alert-warning {
    background: linear-gradient(90deg, rgba(200,130,0,0.22), rgba(160,100,0,0.14));
    border: 1px solid rgba(255,180,50,0.45);
    border-radius: 12px;
    padding: 18px 24px;
    text-align: center;
    font-size: 1.05rem;
    font-weight: 700;
    color: #ffcc66;
    margin: 16px 0;
}
.alert-safe {
    background: linear-gradient(90deg, rgba(0,180,100,0.18), rgba(0,130,80,0.10));
    border: 1px solid rgba(0,220,130,0.40);
    border-radius: 12px;
    padding: 18px 24px;
    text-align: center;
    font-size: 1.05rem;
    font-weight: 700;
    color: #66ffbb;
    margin: 16px 0;
}
@keyframes threat-pulse {
    0%, 100% { box-shadow: 0 0 0 rgba(255,60,60,0); }
    50%       { box-shadow: 0 0 24px rgba(255,60,60,0.30); }
}

/* ── Upload zone ──────────────────────────────────── */
[data-testid="stFileUploader"] {
    background: rgba(10,20,40,0.6) !important;
    border: 2px dashed rgba(0,200,170,0.25) !important;
    border-radius: 16px !important;
}

/* ── Buttons ──────────────────────────────────────── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #005c4b, #007a63) !important;
    border: 1px solid rgba(0,220,180,0.4) !important;
    color: #e0fff8 !important;
    font-family: 'Exo 2', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    border-radius: 10px !important;
    font-size: 1rem !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #007a63, #009e80) !important;
    box-shadow: 0 0 20px rgba(0,200,160,0.3) !important;
}

/* ── Sidebar styles ───────────────────────────────── */
.sidebar-team-name {
    font-family: 'Share Tech Mono', monospace;
    color: #00e5c8;
    font-size: 0.9rem;
    padding: 4px 0;
}

/* ── Landing info cards ───────────────────────────── */
.info-card {
    background: rgba(10,20,36,0.8);
    border: 1px solid rgba(0,200,170,0.15);
    border-radius: 14px;
    padding: 20px;
    text-align: center;
    height: 100%;
}
.info-icon { font-size: 2rem; margin-bottom: 10px; }
.info-title { color: #00e5c8; font-weight: 700; margin-bottom: 6px; font-size: 1rem; }
.info-desc { color: rgba(180,200,220,0.65); font-size: 0.88rem; line-height: 1.5; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════
ATTACK_SEVERITY = {
    'BENIGN': 0,
    'PortScan': 1,
    'Bot': 2,
    'DoS slowloris': 3, 'DoS Slowhttptest': 3,
    'Web Attack \x96 XSS': 3, 'Web Attack - XSS': 3,
    'Web Attack \x96 Brute Force': 3, 'Web Attack - Brute Force': 3,
    'FTP-Patator': 3, 'SSH-Patator': 3,
    'DoS GoldenEye': 4, 'DoS Hulk': 4,
    'DDoS': 4,
    'Web Attack \x96 Sql Injection': 5, 'Web Attack - Sql Injection': 5,
    'Heartbleed': 5, 'Infiltration': 5,
}
SEV_BADGE = {0: '', 1: '●', 2: '◆', 3: '▲', 4: '★', 5: '☠'}
SEV_COLOR = {0: '#00e68a', 1: '#5aabff', 2: '#a0c8ff', 3: '#ffb833', 4: '#ff6e40', 5: '#ff3c3c'}

DEMO_CLASSES = ['BENIGN'] * 16 + [
    'DDoS', 'DoS Hulk', 'PortScan', 'Web Attack - Brute Force',
    'Bot', 'SSH-Patator', 'DoS GoldenEye', 'FTP-Patator'
]
DEMO_WEIGHTS_RAW = [0.78] + [0.22 / 8] * 8
# normalise to sum to 1 (16 BENIGN + 8 attack types = 24 classes in DEMO_CLASSES)
_w = [0.78 / 16] * 16 + [0.22 / 8] * 8
DEMO_W = [x / sum(_w) for x in _w]

# ═══════════════════════════════════════════════════════════════════════
# MODEL LOADING
# ═══════════════════════════════════════════════════════════════════════
@st.cache_resource
def load_models():
    candidates = [
        ('models/rf_model.pkl', 'models/scaler.pkl', 'models/label_encoder.pkl'),
        ('rf_model.pkl', 'scaler.pkl', 'label_encoder.pkl'),
    ]
    for mpath, spath, lpath in candidates:
        if all(os.path.exists(p) for p in [mpath, spath, lpath]):
            try:
                m  = pickle.load(open(mpath, 'rb'))
                sc = pickle.load(open(spath, 'rb'))
                le = pickle.load(open(lpath, 'rb'))
                return m, sc, le, True
            except Exception:
                pass
    return None, None, None, False

model, scaler, label_enc, MODEL_LOADED = load_models()

# ═══════════════════════════════════════════════════════════════════════
# PREDICTION HELPERS
# ═══════════════════════════════════════════════════════════════════════
def demo_predict(n: int):
    rng = np.random.default_rng(42)
    preds = rng.choice(DEMO_CLASSES, size=n, p=DEMO_W)
    proba = np.where(
        preds == 'BENIGN',
        rng.uniform(0.87, 0.99, n),
        rng.uniform(0.74, 0.97, n),
    )
    return preds, proba

def run_prediction(df: pd.DataFrame):
    if MODEL_LOADED:
        try:
            feat = df.drop(columns=['Label'], errors='ignore')
            X    = scaler.transform(feat.values)
            idx  = model.predict(X)
            preds = label_enc.inverse_transform(idx)
            proba = model.predict_proba(X).max(axis=1)
            return preds, proba
        except Exception as e:
            st.warning(f"Model prediction failed ({e}). Falling back to demo mode.")
    return demo_predict(len(df))

# ═══════════════════════════════════════════════════════════════════════
# CHART BUILDERS
# ═══════════════════════════════════════════════════════════════════════
_CHART_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#a0c8c0', family='Exo 2, sans-serif'),
    margin=dict(t=48, b=16, l=16, r=16),
    title_font=dict(size=14, color='#c0e0d8'),
)

def chart_pie(df: pd.DataFrame) -> go.Figure:
    counts = df['Prediction'].value_counts().reset_index()
    counts.columns = ['Class', 'Count']
    colors = ['#ff4b4b' if c != 'BENIGN' else '#00e68a' for c in counts['Class']]
    fig = px.pie(
        counts, values='Count', names='Class',
        color_discrete_sequence=colors, hole=0.5,
        title='Traffic Composition',
    )
    fig.update_traces(
        textposition='inside', textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>',
        marker=dict(line=dict(color='#080c14', width=2)),
    )
    fig.update_layout(**_CHART_LAYOUT, legend=dict(orientation='v', x=1.02, font_size=11))
    return fig

def chart_timeline(df: pd.DataFrame) -> go.Figure:
    df2 = df.copy()
    df2['idx'] = range(len(df2))
    df2['is_atk'] = df2['Prediction'] != 'BENIGN'
    df2['cum']    = df2['is_atk'].cumsum()
    attacks = df2[df2['is_atk']]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df2['idx'], y=df2['cum'],
        fill='tozeroy', mode='lines',
        line=dict(color='#ff4b4b', width=2),
        fillcolor='rgba(255,75,75,0.10)',
        name='Cumulative Attacks',
        hovertemplate='Packet %{x}: %{y} total attacks<extra></extra>',
    ))
    if len(attacks):
        fig.add_trace(go.Scatter(
            x=attacks['idx'], y=attacks['cum'],
            mode='markers',
            marker=dict(color='#ff1744', size=7, symbol='x-thin', line=dict(width=2)),
            name='Attack Event',
            text=attacks['Prediction'],
            hovertemplate='<b>%{text}</b><br>Packet %{x}<extra></extra>',
        ))

    fig.update_layout(
        **_CHART_LAYOUT,
        title='Attack Timeline',
        xaxis=dict(title='Packet #', gridcolor='rgba(255,255,255,0.05)', zeroline=False),
        yaxis=dict(title='Cumulative Attacks', gridcolor='rgba(255,255,255,0.05)', zeroline=False),
        legend=dict(orientation='h', y=-0.2, font_size=11),
        hovermode='x unified',
    )
    return fig

def chart_gauge(attack_pct: float) -> go.Figure:
    if attack_pct < 0.10:
        bar_color = '#00e68a'
    elif attack_pct < 0.30:
        bar_color = '#ffb833'
    else:
        bar_color = '#ff4b4b'

    fig = go.Figure(go.Indicator(
        mode='gauge+number',
        value=round(attack_pct * 100, 1),
        number=dict(suffix='%', font=dict(size=32, color='white', family='Share Tech Mono')),
        title=dict(text='Threat Level', font=dict(size=14, color='#a0c8c0')),
        gauge=dict(
            axis=dict(range=[0, 100], tickcolor='rgba(255,255,255,0.3)',
                      tickfont=dict(color='rgba(255,255,255,0.4)', size=10)),
            bar=dict(color=bar_color, thickness=0.28),
            bgcolor='rgba(10,20,36,1)',
            borderwidth=0,
            steps=[
                dict(range=[0, 10],  color='rgba(0,230,130,0.08)'),
                dict(range=[10, 30], color='rgba(255,180,50,0.08)'),
                dict(range=[30, 100],color='rgba(255,75,75,0.08)'),
            ],
        ),
    ))
    fig.update_layout(**_CHART_LAYOUT, height=230)
    return fig

def chart_confidence(df: pd.DataFrame) -> go.Figure:
    fig = px.histogram(
        df, x='Conf_val', color='Status',
        nbins=25, barmode='overlay', opacity=0.75,
        color_discrete_map={'🔴 ATTACK': '#ff4b4b', '🟢 SAFE': '#00e68a'},
        title='Prediction Confidence Distribution',
        labels={'Conf_val': 'Confidence Score', 'count': 'Packets'},
    )
    fig.update_layout(
        **_CHART_LAYOUT,
        xaxis=dict(tickformat='.0%', gridcolor='rgba(255,255,255,0.05)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
        legend=dict(orientation='h', y=-0.2, font_size=11),
        bargap=0.05,
    )
    return fig

# ═══════════════════════════════════════════════════════════════════════
# DATAFRAME STYLING
# ═══════════════════════════════════════════════════════════════════════
def style_df(df: pd.DataFrame):
    display = df.drop(columns=['Conf_val', 'Prediction'], errors='ignore')
    def row_color(row):
        if 'ATTACK' in str(row.get('Status', '')):
            return [
                'background-color: rgba(255,70,70,0.14); color: #ff9090'
            ] * len(row)
        return [
            'background-color: rgba(0,220,110,0.08); color: #80ffbb'
        ] * len(row)
    return display.style.apply(row_color, axis=1)

# ═══════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🛡️ NetGuard IDS")
    st.markdown("*Faculty of Engineering & Technology*  \n*Antonine University*")
    st.divider()

    if MODEL_LOADED:
        st.success("✅ Real Model Active")
        st.caption("Random Forest trained on CIC-IDS 2017")
    else:
        st.warning("⚠️ Demo Mode")
        st.caption("Place `rf_model.pkl`, `scaler.pkl`, `label_encoder.pkl` in a `models/` folder to use your real model.")

    st.divider()
    st.markdown("**⚙️ Processing Speed**")
    speed = st.select_slider(
        " ", label_visibility="collapsed",
        options=["Slow — dramatic", "Medium", "Fast", "Instant"],
        value="Medium",
    )
    DELAY      = {"Slow — dramatic": 0.10, "Medium": 0.03, "Fast": 0.008, "Instant": 0.0}[speed]
    BATCH_SIZE = {"Slow — dramatic": 1,    "Medium": 3,    "Fast": 8,     "Instant": 99999}[speed]

    st.divider()
    st.markdown("**👥 Team**")
    st.markdown('<p class="sidebar-team-name">› Elio Abou Akar</p>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-team-name">› Charbel Mrad</p>', unsafe_allow_html=True)
    st.caption("AI Project 2025–2026")

# ═══════════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="header-card">
  <p class="header-title">🛡️ Network Intrusion Detection System</p>
  <p class="header-sub">
      Real-time network traffic classification &nbsp;·&nbsp;
      Random Forest &nbsp;·&nbsp; CIC-IDS 2017 &nbsp;·&nbsp;
      15 attack types detected
  </p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# UPLOAD
# ═══════════════════════════════════════════════════════════════════════
col_up, col_hint = st.columns([3, 2])

with col_up:
    uploaded = st.file_uploader(
        "📂 Upload Network Traffic CSV",
        type=["csv"],
        help="CSV with CIC-IDS 2017 feature columns. Label column is optional — it won't be used for prediction.",
    )

with col_hint:
    with st.expander("📋 How to export test data from Colab"):
        st.code("""
# ── Run this in your Colab notebook ──

import pickle, pandas as pd, numpy as np

# 1. Save the trained models
os.makedirs('models', exist_ok=True)
pickle.dump(rf_model, open('models/rf_model.pkl',     'wb'))
pickle.dump(scaler,   open('models/scaler.pkl',        'wb'))
pickle.dump(le,       open('models/label_encoder.pkl', 'wb'))

# 2. Export a mixed test CSV (benign + attacks)
benign_idx = np.where(y_test == le.transform(['BENIGN'])[0])[0][:150]
attack_idx = np.where(y_test != le.transform(['BENIGN'])[0])[0][:80]
idx = np.concatenate([benign_idx, attack_idx])
np.random.shuffle(idx)

pd.DataFrame(X_test[idx], columns=feature_cols).to_csv(
    'test_traffic.csv', index=False
)

# 3. Download from Colab
from google.colab import files
files.download('test_traffic.csv')
        """, language="python")

# ═══════════════════════════════════════════════════════════════════════
# LANDING STATE  (no file uploaded)
# ═══════════════════════════════════════════════════════════════════════
if uploaded is None:
    st.markdown('<p class="section-title">How it works</p>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    cards = [
        ("📂", "Upload CSV", "Drop any CIC-IDS 2017 formatted traffic capture file"),
        ("⚡", "Live Analysis", "Watch each packet get classified row by row in real time"),
        ("📊", "Visual Dashboard", "Pie chart, attack timeline, threat gauge & confidence scores"),
        ("🔴 / 🟢", "Instant Verdict", "Red rows = attack detected · Green rows = safe traffic"),
    ]
    for col, (icon, title, desc) in zip([c1, c2, c3, c4], cards):
        col.markdown(f"""
        <div class="info-card">
          <div class="info-icon">{icon}</div>
          <div class="info-title">{title}</div>
          <div class="info-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
    st.stop()

# ═══════════════════════════════════════════════════════════════════════
# FILE LOADED — preview + analyse button
# ═══════════════════════════════════════════════════════════════════════
df_raw = pd.read_csv(uploaded)
st.success(f"✅ **{len(df_raw):,} rows** loaded · {df_raw.shape[1]} columns")

with st.expander("👁️ Preview raw data (first 5 rows)"):
    st.dataframe(df_raw.head(), use_container_width=True)

if not st.button("🚀 START ANALYSIS", type="primary", use_container_width=True):
    st.stop()

# ═══════════════════════════════════════════════════════════════════════
# RUN PREDICTIONS  (all at once — we animate display only)
# ═══════════════════════════════════════════════════════════════════════
preds, proba = run_prediction(df_raw)
total = len(preds)

# Pre-build the full results list so we can index into it
all_results = []
for i in range(total):
    label    = preds[i]
    is_atk   = label != 'BENIGN'
    sev      = ATTACK_SEVERITY.get(label, 0)
    all_results.append({
        'Status'     : '🔴 ATTACK' if is_atk else '🟢 SAFE',
        'Type'       : label,
        'Severity'   : SEV_BADGE.get(sev, ''),
        'Confidence' : f"{proba[i]:.1%}",
        'Conf_val'   : proba[i],
        'Prediction' : label,
    })

# ═══════════════════════════════════════════════════════════════════════
# LAYOUT PLACEHOLDERS
# ═══════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-title">Live Analysis Feed</p>', unsafe_allow_html=True)
prog_bar     = st.progress(0)
status_text  = st.empty()
table_ph     = st.empty()

st.markdown('<p class="section-title">Dashboard</p>', unsafe_allow_html=True)
mcol1, mcol2, mcol3, mcol4 = st.columns(4)
m_total   = mcol1.empty()
m_attacks = mcol2.empty()
m_benign  = mcol3.empty()
m_rate    = mcol4.empty()

alert_ph   = st.empty()
ccol1, ccol2 = st.columns([1.3, 1])
pie_ph     = ccol1.empty()
gauge_ph   = ccol2.empty()
timeline_ph = st.empty()
conf_ph    = st.empty()

# ═══════════════════════════════════════════════════════════════════════
# ANIMATION LOOP
# ═══════════════════════════════════════════════════════════════════════
done_results = []

for start in range(0, total, BATCH_SIZE):
    end = min(start + BATCH_SIZE, total)
    done_results.extend(all_results[start:end])
    n_done = len(done_results)

    res_df   = pd.DataFrame(done_results)
    n_atk    = (res_df['Status'] == '🔴 ATTACK').sum()
    n_ben    = n_done - n_atk
    atk_pct  = n_atk / n_done

    # ── Progress ──────────────────────────────────────────────────────
    prog_bar.progress(n_done / total)
    status_text.markdown(
        f"*Scanning packet **{n_done:,}** of **{total:,}** — "
        f"**{n_atk}** threat{'s' if n_atk != 1 else ''} detected so far*"
    )

    # ── Live table (last 20 rows) ──────────────────────────────────────
    display_tail = res_df.tail(20)
    table_ph.dataframe(style_df(display_tail), use_container_width=True, height=380)

    # ── Metric cards ───────────────────────────────────────────────────
    m_total.markdown(f"""
    <div class="metric-card blue">
      <p class="metric-value blue">{n_done:,}</p>
      <p class="metric-label">Packets Scanned</p>
    </div>""", unsafe_allow_html=True)

    m_attacks.markdown(f"""
    <div class="metric-card red">
      <p class="metric-value red">{n_atk:,}</p>
      <p class="metric-label">Attacks Detected</p>
    </div>""", unsafe_allow_html=True)

    m_benign.markdown(f"""
    <div class="metric-card green">
      <p class="metric-value green">{n_ben:,}</p>
      <p class="metric-label">Safe Packets</p>
    </div>""", unsafe_allow_html=True)

    m_rate.markdown(f"""
    <div class="metric-card {'red' if atk_pct > 0.3 else 'amber' if atk_pct > 0.1 else 'green'}">
      <p class="metric-value {'red' if atk_pct > 0.3 else 'amber' if atk_pct > 0.1 else 'green'}">{atk_pct:.1%}</p>
      <p class="metric-label">Threat Rate</p>
    </div>""", unsafe_allow_html=True)

    # ── Charts (refresh every ~10 packets for performance) ─────────────
    if n_done % 10 == 0 or n_done == total:
        pie_ph.plotly_chart(chart_pie(res_df),      use_container_width=True, key=f"pie_{n_done}")
        gauge_ph.plotly_chart(chart_gauge(atk_pct), use_container_width=True, key=f"gauge_{n_done}")
        timeline_ph.plotly_chart(chart_timeline(res_df), use_container_width=True, key=f"tl_{n_done}")

    if DELAY > 0:
        time.sleep(DELAY)

# ═══════════════════════════════════════════════════════════════════════
# FINAL STATE
# ═══════════════════════════════════════════════════════════════════════
prog_bar.progress(1.0)
status_text.markdown(f"✅ **Analysis complete!** All **{total:,}** packets processed.")

# Full table
table_ph.dataframe(style_df(res_df), use_container_width=True, height=420)

# Confidence chart
st.markdown('<p class="section-title">Confidence Analysis</p>', unsafe_allow_html=True)
st.plotly_chart(chart_confidence(res_df), use_container_width=True)

# Alert banner
if atk_pct > 0.30:
    alert_ph.markdown(
        f'<div class="alert-critical">🚨 CRITICAL THREAT LEVEL — '
        f'{n_atk:,} attacks detected ({atk_pct:.1%} of all traffic)</div>',
        unsafe_allow_html=True
    )
elif atk_pct > 0.05:
    alert_ph.markdown(
        f'<div class="alert-warning">⚠️ ELEVATED THREAT — '
        f'{n_atk:,} suspicious flows detected ({atk_pct:.1%})</div>',
        unsafe_allow_html=True
    )
else:
    alert_ph.markdown(
        f'<div class="alert-safe">✅ LOW THREAT — '
        f'Network traffic appears mostly normal ({atk_pct:.1%} anomalies)</div>',
        unsafe_allow_html=True
    )

# ── Attack breakdown table ─────────────────────────────────────────────
st.markdown('<p class="section-title">Attack Breakdown</p>', unsafe_allow_html=True)
attack_rows = res_df[res_df['Type'] != 'BENIGN']
if len(attack_rows):
    breakdown = (
        attack_rows['Type']
        .value_counts()
        .reset_index()
        .rename(columns={'Type': 'Attack Type', 'count': 'Count'})
    )
    breakdown['% of Traffic'] = (breakdown['Count'] / total * 100).round(2).astype(str) + '%'
    breakdown['Avg Confidence'] = (
        attack_rows.groupby('Type')['Conf_val'].mean()
        .reindex(breakdown['Attack Type'])
        .values
    )
    breakdown['Avg Confidence'] = breakdown['Avg Confidence'].apply(lambda x: f"{x:.1%}")
    st.dataframe(breakdown, use_container_width=True, hide_index=True)
else:
    st.info("No attacks detected in this capture.")

# ── Download button ────────────────────────────────────────────────────
st.markdown('<p class="section-title">Export</p>', unsafe_allow_html=True)
export_df = res_df.drop(columns=['Conf_val', 'Prediction'], errors='ignore')
st.download_button(
    label="⬇️ Download Full Results as CSV",
    data=export_df.to_csv(index=False),
    file_name="netguard_ids_results.csv",
    mime="text/csv",
    use_container_width=True,
)
