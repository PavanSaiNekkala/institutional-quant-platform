# =========================================================
# FILE: app/streamlit_app.py
# ULTRA MODERN INSTITUTIONAL QUANT DASHBOARD
# =========================================================

import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go

from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed
)

from core.live_regime import (
    detect_market_regime
)

from core.sector_models import (
    detect_sector,
    sector_factor_score
)

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Institutional Quant Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# PREMIUM CSS
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background: linear-gradient(
            180deg,
            #020617 0%,
            #071028 100%
        );
        color: white;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #081120 0%,
            #0B1629 100%
        );
        border-right: 1px solid #1E293B;
        width: 320px !important;
    }

    section[data-testid="stSidebar"] > div {
        width: 320px !important;
    }

    h1, h2, h3, h4 {
        color: white !important;
        font-weight: 700 !important;
    }

    .hero-title {
        font-size: 58px;
        font-weight: 800;
        line-height: 1.1;
        color: white;
    }

    .hero-subtitle {
        font-size: 22px;
        color: #94A3B8;
        margin-top: -10px;
    }

    .metric-card {
        background: linear-gradient(
            135deg,
            rgba(17,24,39,0.95),
            rgba(15,23,42,0.95)
        );

        border: 1px solid rgba(148,163,184,0.15);

        border-radius: 22px;

        padding: 1.5rem;

        backdrop-filter: blur(10px);

        box-shadow:
            0 4px 30px rgba(0,0,0,0.3);

        transition: 0.3s;
    }

    .metric-card:hover {
        transform: translateY(-4px);
        border: 1px solid #38BDF8;
    }

    .metric-label {
        color: #94A3B8;
        font-size: 16px;
        margin-bottom: 8px;
    }

    .metric-value {
        color: white;
        font-size: 42px;
        font-weight: 800;
    }

    .market-card {
        background: linear-gradient(
            135deg,
            rgba(30,41,59,0.95),
            rgba(15,23,42,0.95)
        );

        border-radius: 20px;
        padding: 1.3rem;
        border: 1px solid rgba(148,163,184,0.12);
    }

    .processing-card {
        background: linear-gradient(
            135deg,
            rgba(10,25,47,0.95),
            rgba(3,15,35,0.95)
        );

        border-radius: 20px;

        padding: 1.5rem;

        border: 1px solid rgba(56,189,248,0.15);
    }

    .stDataFrame {
        border-radius: 20px;
        overflow: hidden;
        border: 1px solid rgba(148,163,184,0.12);
    }

    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }

    div[data-baseweb="select"] > div {
        background-color: #0F172A !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
    }

    div[data-baseweb="base-input"] > div {
        background-color: #0F172A !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# HERO SECTION
# =========================================================

st.markdown(
    """
    <div class="hero-title">
        📈 Institutional Quant Platform
    </div>

    <div class="hero-subtitle">
        AI-Powered Institutional Quantitative Analytics Engine
    </div>
    """,
    unsafe_allow_html=True
)

st.caption(
    f"Last Updated: {pd.Timestamp.now().strftime('%d-%m-%Y %H:%M:%S IST')}"
)

st.markdown("<br>", unsafe_allow_html=True)

# =========================================================
# MARKET REGIME
# =========================================================

@st.cache_data(ttl=1800)
def cached_regime():
    return detect_market_regime()

regime = cached_regime()

# =========================================================
# LOAD STOCKS
# =========================================================

universe_path = (
    ROOT_DIR
    / "data"
    / "valid_stocks.xlsx"
)

universe_df = pd.read_excel(universe_path)

stocks = (
    universe_df.iloc[:, 0]
    .dropna()
    .astype(str)
    .str.upper()
    .unique()
    .tolist()
)

stocks = [
    s for s in stocks
    if s.endswith(".NS")
]

stocks = list(dict.fromkeys(stocks))

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## ⚙️ Institutional Controls")

    st.markdown("---")

    top_n = st.slider(
        "Live Analysis Universe",
        min_value=100,
        max_value=len(stocks),
        value=300,
        step=50
    )

    signal_filter = st.selectbox(
        "Trade Signal",
        [
            "All",
            "STRONG_BUY",
            "BUY",
            "WATCH",
            "AVOID"
        ]
    )

    min_score = st.slider(
        "Minimum Institutional Score",
        min_value=0,
        max_value=100,
        value=60
    )

    search_stock = st.text_input(
        "Search Stock"
    )

    st.markdown("---")

    st.success("📊 AI Quant Engine Enabled")
    st.info("📈 Live Regime Detection Enabled")
    st.info("🧠 Smart Sector Rotation Enabled")
    st.info("⚡ Backtesting Engine Enabled")

# =========================================================
# SAFE ROUND
# =========================================================

def safe_round(value, digits=2):

    try:

        if value is None:
            return 0

        if pd.isna(value):
            return 0

        if np.isinf(value):
            return 0

        return round(float(value), digits)

    except:
        return 0

# =========================================================
# ANALYZE STOCK
# =========================================================

def analyze_stock(symbol, regime):

    try:

        ticker = yf.Ticker(symbol)

        data = yf.download(
            symbol,
            period="3mo",
            interval="1d",
            auto_adjust=True,
            progress=False,
            threads=False
        )

        if data.empty:
            return None

        close = data["Close"]

        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]

        close = close.dropna()

        if len(close) < 40:
            return None

        returns = close.pct_change().dropna()

        momentum = (
            close.iloc[-1]
            / close.iloc[-20]
        ) - 1

        volatility = (
            returns.std()
            * np.sqrt(252)
        )

        sharpe = (
            returns.mean()
            / max(returns.std(), 0.0001)
        ) * np.sqrt(252)

        total_return = (
            close.iloc[-1]
            / close.iloc[0]
        ) - 1

        sma20 = (
            close.rolling(20)
            .mean()
            .iloc[-1]
        )

        sma50 = (
            close.rolling(40)
            .mean()
            .iloc[-1]
        )

        trend_strength = (
            sma20 / sma50
        )

        cmp = close.iloc[-1]

        recent_volatility = (
            close.pct_change()
            .rolling(14)
            .std()
            .iloc[-1]
        )

        if pd.isna(recent_volatility):
            recent_volatility = 0.02

        stop_loss = cmp * (
            1 - recent_volatility * 2
        )

        target_price = cmp * (
            1 + recent_volatility * 4
        )

        risk_reward = (
            (target_price - cmp)
            / max(
                cmp - stop_loss,
                0.0001
            )
        )

        sector = detect_sector(symbol)

        final_score = sector_factor_score(
            sector=sector,
            momentum=momentum,
            sharpe=sharpe,
            trend_strength=trend_strength,
            total_return=total_return,
            volatility=volatility,
            risk_reward=risk_reward,
            regime=regime
        )

        if final_score >= 1.20:
            classification = "STRONG_BUY"

        elif final_score >= 0.80:
            classification = "BUY"

        elif final_score >= 0.50:
            classification = "WATCH"

        else:
            classification = "AVOID"

        return {

            "Symbol": symbol,
            "Sector": sector,
            "CMP": safe_round(cmp),
            "Momentum": safe_round(momentum * 100),
            "Volatility": safe_round(volatility),
            "Sharpe": safe_round(sharpe),
            "Final Score": safe_round(final_score),
            "Risk Reward": safe_round(risk_reward),
            "Classification": classification
        }

    except:
        return None

# =========================================================
# PROCESS ENGINE
# =========================================================

ranking_data = []

progress_bar = st.progress(0)

status_box = st.empty()

start_time = time.time()

processed = 0
success = 0
failed = 0

with ThreadPoolExecutor(max_workers=6) as executor:

    futures = {

        executor.submit(
            analyze_stock,
            symbol,
            regime
        ): symbol

        for symbol in stocks[:top_n]
    }

    for future in as_completed(futures):

        processed += 1

        symbol = futures[future]

        try:

            result = future.result()

            if result:

                ranking_data.append(result)

                success += 1

            else:

                failed += 1

        except:

            failed += 1

        progress_bar.progress(
            processed / top_n
        )

        remaining = (
            (
                time.time()
                - start_time
            ) / max(processed, 1)
        ) * (
            top_n - processed
        )

        status_box.markdown(
            f"""
            <div class="processing-card">

            🔄 <b>Processing:</b> {symbol}<br><br>

            ✅ Success: {success}<br><br>

            ❌ Failed: {failed}<br><br>

            ⏳ Remaining: {int(remaining)} sec

            </div>
            """,
            unsafe_allow_html=True
        )

# =========================================================
# RESULTS
# =========================================================

results = pd.DataFrame(ranking_data)

if results.empty:

    st.error("No valid stocks analyzed.")

    st.stop()

results["Percentile"] = (
    results["Final Score"] * 100
)

results = results[
    results["Percentile"]
    >= min_score
]

if signal_filter != "All":

    results = results[
        results["Classification"]
        == signal_filter
    ]

if search_stock:

    results = results[
        results["Symbol"]
        .str.contains(
            search_stock.upper(),
            na=False
        )
    ]

results = results.sort_values(
    by="Final Score",
    ascending=False
)

# =========================================================
# MARKET INFO CARDS
# =========================================================

m1, m2, m3 = st.columns(3)

with m1:

    st.markdown(
        f"""
        <div class="market-card">
        🔴 <b>NSE Market Regime</b><br><br>
        <span style="font-size:28px;">
        {regime}
        </span>
        </div>
        """,
        unsafe_allow_html=True
    )

with m2:

    st.markdown(
        f"""
        <div class="market-card">
        ⚡ <b>Universe Size</b><br><br>
        <span style="font-size:28px;">
        {len(results)}
        </span>
        </div>
        """,
        unsafe_allow_html=True
    )

with m3:

    st.markdown(
        f"""
        <div class="market-card">
        🏆 <b>Strong Buys</b><br><br>
        <span style="font-size:28px;">
        {
            len(
                results[
                    results["Classification"]
                    == "STRONG_BUY"
                ]
            )
        }
        </span>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# =========================================================
# KPI CARDS
# =========================================================

c1, c2, c3, c4 = st.columns(4)

with c1:

    st.markdown(
        f"""
        <div class="metric-card">
        <div class="metric-label">
        Live Stocks
        </div>

        <div class="metric-value">
        {len(results)}
        </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c2:

    st.markdown(
        f"""
        <div class="metric-card">
        <div class="metric-label">
        Institutional Score
        </div>

        <div class="metric-value">
        {safe_round(results["Final Score"].mean()*100)}
        </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c3:

    st.markdown(
        f"""
        <div class="metric-card">
        <div class="metric-label">
        Avg Risk Reward
        </div>

        <div class="metric-value">
        {safe_round(results["Risk Reward"].mean())}
        </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c4:

    st.markdown(
        f"""
        <div class="metric-card">
        <div class="metric-label">
        Confidence
        </div>

        <div class="metric-value">
        {safe_round(results["Percentile"].mean())}
        </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# TABLE
# =========================================================

st.markdown("## 🏦 Institutional Rankings")

st.dataframe(
    results,
    use_container_width=True,
    height=650
)

# =========================================================
# SCORE CHART
# =========================================================

top_chart = results.head(25)

fig = px.bar(
    top_chart,
    x="Symbol",
    y="Final Score",
    color="Classification",
    title="Institutional Alpha Rankings",
    template="plotly_dark"
)

fig.update_layout(
    height=650,
    paper_bgcolor="#050816",
    plot_bgcolor="#050816",
    font=dict(color="white")
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =========================================================
# RISK REWARD MATRIX
# =========================================================

scatter = px.scatter(
    results.head(100),
    x="Risk Reward",
    y="Final Score",
    color="Classification",
    size="Momentum",
    hover_name="Symbol",
    title="Institutional Risk Reward Matrix",
    template="plotly_dark"
)

scatter.update_layout(
    height=700,
    paper_bgcolor="#050816",
    plot_bgcolor="#050816",
    font=dict(color="white")
)

st.plotly_chart(
    scatter,
    use_container_width=True
)

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    """
    Institutional Quantamental Intelligence Platform •
    AI Powered • Institutional Grade • Smart Sector Rotation
    """
)
