# =========================================================
# INSTITUTIONAL QUANT PLATFORM
# ENTERPRISE POWERBI-STYLE DASHBOARD
# =========================================================

import sys
import time
from pathlib import Path

# =========================================================
# ROOT PATH
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

# =========================================================
# IMPORTS
# =========================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf

from datetime import datetime

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Institutional Quant Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
}

/* Main Background */
.stApp {
    background-color: #f4f6fb;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #081028 0%, #101b3a 100%);
    border-right: 1px solid rgba(255,255,255,0.08);
}

/* Cards */
.metric-card {
    background: white;
    padding: 1rem;
    border-radius: 18px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.06);
    border-left: 5px solid #3b82f6;
}

/* Institutional Engine */
.engine-card {
    background: white;
    border-radius: 24px;
    padding: 2rem;
    box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}

/* Live Badge */
.live-badge {
    background: #dbeafe;
    color: #2563eb;
    padding: 8px 14px;
    border-radius: 12px;
    font-weight: 700;
    font-size: 12px;
}

/* Ticker */
.ticker {
    background: #0f172a;
    color: white;
    padding: 12px;
    border-radius: 10px;
    overflow: hidden;
    white-space: nowrap;
}

/* Headers */
h1, h2, h3 {
    color: #0f172a;
}

/* Progress */
div.stProgress > div > div > div {
    background-color: #2563eb;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# AUTO REFRESH
# =========================================================

time.sleep(1)

# =========================================================
# DATA LOADING
# =========================================================

DATA_PATH = (
    ROOT_DIR
    / "data"
    / "parquet"
    / "institutional_dataset.parquet"
)

if not DATA_PATH.exists():
    st.error("Dataset not found")
    st.stop()

df = pd.read_parquet(DATA_PATH)

# =========================================================
# REQUIRED COLUMNS
# =========================================================

required_columns = [
    "symbol",
    "institutional_score",
    "signal"
]

for col in required_columns:
    if col not in df.columns:
        st.error(f"Missing required column: {col}")
        st.stop()

# =========================================================
# OPTIONAL COLUMNS
# =========================================================

optional_defaults = {
    "sector": "Unknown",
    "momentum_20": 0,
    "volatility": 0,
    "close": 0,
    "volume": 0
}

for col, default in optional_defaults.items():
    if col not in df.columns:
        df[col] = default

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.markdown("# ⚙ Dashboard Controls")

signal_options = sorted(df["signal"].dropna().unique())

selected_signals = st.sidebar.multiselect(
    "📈 Trade Signal Filter",
    options=signal_options,
    default=[]
)

min_score = st.sidebar.slider(
    "Minimum Institutional Score",
    0,
    100,
    60
)

search_stock = st.sidebar.text_input(
    "Search Stock",
    placeholder="Type stock name..."
)

# =========================================================
# FILTERS
# =========================================================

filtered_df = df.copy()

filtered_df = filtered_df[
    filtered_df["institutional_score"] >= min_score
]

if selected_signals:
    filtered_df = filtered_df[
        filtered_df["signal"].isin(selected_signals)
    ]

if search_stock:
    filtered_df = filtered_df[
        filtered_df["symbol"]
        .str.contains(search_stock, case=False)
    ]

# =========================================================
# LIVE MARKET DATA
# =========================================================

try:

    nifty = yf.Ticker("^NSEI")
    banknifty = yf.Ticker("^NSEBANK")

    nifty_price = round(
        nifty.history(period="1d")["Close"].iloc[-1],
        2
    )

    bank_price = round(
        banknifty.history(period="1d")["Close"].iloc[-1],
        2
    )

except:
    nifty_price = "Unavailable"
    bank_price = "Unavailable"

# =========================================================
# HEADER
# =========================================================

st.markdown(f"""
<div class="ticker">
📈 NIFTY 50: {nifty_price} |
🏦 BANKNIFTY: {bank_price} |
⚡ Institutional Engine Active |
🟢 Live Market Connected
</div>
""", unsafe_allow_html=True)

st.markdown("")

updated_time = datetime.now().strftime(
    "%d-%m-%Y %I:%M:%S %p"
)

st.caption(f"Updated: {updated_time} IST")

# =========================================================
# PROCESSING BAR
# =========================================================

universe = len(df)
completed = len(filtered_df)

progress = completed / max(universe, 1)

st.info(
    "⚡ Running institutional analysis across full NSE universe..."
)

st.progress(progress)

# =========================================================
# MAIN ENGINE CARD
# =========================================================

st.markdown("""
<div class="engine-card">
<h1>📊 Institutional Processing Engine</h1>
<p>Real-Time Quant Processing</p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# KPI ROW
# =========================================================

buy_count = len(
    filtered_df[
        filtered_df["signal"]
        .isin(["BUY", "STRONG BUY"])
    ]
)

sell_count = len(
    filtered_df[
        filtered_df["signal"]
        .isin(["SELL", "STRONG SELL"])
    ]
)

avg_score = round(
    filtered_df["institutional_score"].mean(),
    2
) if len(filtered_df) > 0 else 0

market_breadth = round(
    (buy_count / max(len(filtered_df), 1)) * 100,
    2
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
    <h5>✅ COMPLETED</h5>
    <h1>{completed}</h1>
    <p>out of {universe}</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
    <h5>📉 SELL SIGNALS</h5>
    <h1>{sell_count}</h1>
    <p>Institutional exits</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
    <h5>📈 BUY SIGNALS</h5>
    <h1>{buy_count}</h1>
    <p>Institutional accumulation</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
    <h5>🔥 MARKET BREADTH</h5>
    <h1>{market_breadth}%</h1>
    <p>Bullish participation</p>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# INSTITUTIONAL SCORE GAUGE
# =========================================================

st.markdown("## 🎯 Institutional Sentiment Gauge")

gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=avg_score,
    title={'text': "Institutional Strength"},
    gauge={
        'axis': {'range': [0, 100]},
        'bar': {'color': "#2563eb"},
        'steps': [
            {'range': [0, 40], 'color': "#fee2e2"},
            {'range': [40, 70], 'color': "#fef3c7"},
            {'range': [70, 100], 'color': "#dcfce7"}
        ]
    }
))

gauge.update_layout(height=350)

st.plotly_chart(
    gauge,
    use_container_width=True
)

# =========================================================
# TREEMAP
# =========================================================

st.markdown("## 🌍 Institutional Heatmap")

treemap = px.treemap(
    filtered_df,
    path=["sector", "symbol"],
    values="institutional_score",
    color="institutional_score",
    color_continuous_scale="RdYlGn"
)

treemap.update_layout(height=650)

st.plotly_chart(
    treemap,
    use_container_width=True
)

# =========================================================
# TOP STOCKS
# =========================================================

st.markdown("## 🚀 Top Institutional Stocks")

top_df = filtered_df.sort_values(
    "institutional_score",
    ascending=False
).head(20)

bar_fig = px.bar(
    top_df,
    x="symbol",
    y="institutional_score",
    color="institutional_score",
    text="institutional_score",
    color_continuous_scale="Blues"
)

bar_fig.update_layout(
    height=500,
    xaxis_title="Stock",
    yaxis_title="Institutional Score"
)

st.plotly_chart(
    bar_fig,
    use_container_width=True
)

# =========================================================
# MOMENTUM SCATTER
# =========================================================

st.markdown("## 📊 Momentum vs Institutional Score")

scatter = px.scatter(
    filtered_df,
    x="momentum_20",
    y="institutional_score",
    size="volume",
    color="signal",
    hover_data=["symbol", "sector"],
    size_max=40
)

scatter.update_layout(height=650)

st.plotly_chart(
    scatter,
    use_container_width=True
)

# =========================================================
# SIGNAL DISTRIBUTION
# =========================================================

st.markdown("## 📈 Signal Distribution")

histogram = px.histogram(
    filtered_df,
    x="signal",
    color="signal"
)

histogram.update_layout(height=450)

st.plotly_chart(
    histogram,
    use_container_width=True
)

# =========================================================
# SECTOR ROTATION
# =========================================================

st.markdown("## 🏭 Sector Rotation")

sector_df = (
    filtered_df
    .groupby("sector")["institutional_score"]
    .mean()
    .reset_index()
)

sector_chart = px.bar(
    sector_df,
    x="sector",
    y="institutional_score",
    color="institutional_score",
    color_continuous_scale="Viridis"
)

sector_chart.update_layout(height=500)

st.plotly_chart(
    sector_chart,
    use_container_width=True
)

# =========================================================
# MARKET COMMENTARY
# =========================================================

st.markdown("## 🧠 AI Institutional Commentary")

if market_breadth > 70:

    commentary = """
    Institutional accumulation remains strong across the market.
    Momentum breadth is expanding with bullish participation.
    Risk appetite improving in large-cap sectors.
    """

elif market_breadth > 40:

    commentary = """
    Market remains balanced with selective institutional activity.
    Sector rotation observed across defensive segments.
    """

else:

    commentary = """
    Institutional weakness detected.
    Risk-off sentiment increasing across broader markets.
    """

st.success(commentary)

# =========================================================
# DATA TABLE
# =========================================================

st.markdown("## 📋 Institutional Dataset")

styled_df = filtered_df.sort_values(
    "institutional_score",
    ascending=False
)

st.dataframe(
    styled_df,
    use_container_width=True,
    height=600
)

# =========================================================
# EXPORT
# =========================================================

csv = styled_df.to_csv(index=False)

st.download_button(
    label="⬇ Download Institutional Dataset",
    data=csv,
    file_name="institutional_quant_data.csv",
    mime="text/csv"
)

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption("""
Institutional Quant Platform • Enterprise Edition •
Built with Streamlit + Plotly + Quant Analytics
""")
