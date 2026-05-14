# =========================================================
# FILE: app/streamlit_app.py
# EXECUTIVE POWERBI STYLE INSTITUTIONAL DASHBOARD
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

from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed
)

from core.live_regime import detect_market_regime
from core.sector_models import (
    detect_sector,
    sector_factor_score
)

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
# POWERBI EXECUTIVE CSS
# =========================================================

st.markdown("""
<style>

/* =====================================================
GLOBAL APP
===================================================== */

.stApp {

    background-color: #F3F4F6;

    color: #111827;

    font-family: "Segoe UI", sans-serif;
}

/* =====================================================
REMOVE STREAMLIT HEADER SPACE
===================================================== */

.block-container {

    padding-top: 1rem;

    padding-bottom: 2rem;

    max-width: 96%;
}

/* =====================================================
SIDEBAR
===================================================== */

section[data-testid="stSidebar"] {

    background: #111827;

    border-right: 1px solid #1F2937;

    width: 320px !important;
}

section[data-testid="stSidebar"] > div {

    width: 320px !important;

    padding-top: 1rem;
}

/* =====================================================
SIDEBAR TEXT
===================================================== */

section[data-testid="stSidebar"] * {

    color: #F9FAFB !important;
}

/* =====================================================
LABELS
===================================================== */

label {

    color: #E5E7EB !important;

    font-size: 15px !important;

    font-weight: 600 !important;
}

/* =====================================================
SELECT BOX
===================================================== */

div[data-baseweb="select"] > div {

    background-color: #1F2937 !important;

    border: 1px solid #374151 !important;

    border-radius: 10px !important;

    min-height: 48px !important;

    color: white !important;
}

/* =====================================================
INPUT BOX
===================================================== */

div[data-baseweb="base-input"] > div {

    background-color: #1F2937 !important;

    border: 1px solid #374151 !important;

    border-radius: 10px !important;

    min-height: 48px !important;

    color: white !important;
}

/* =====================================================
SLIDER
===================================================== */

.stSlider {

    padding-top: 10px;
}

/* =====================================================
MAIN TITLE
===================================================== */

.main-title {

    font-size: 48px;

    font-weight: 800;

    color: #111827;

    margin-bottom: -10px;
}

.subtitle {

    font-size: 18px;

    color: #6B7280;
}

/* =====================================================
KPI CARDS
===================================================== */

.kpi-card {

    background: white;

    border-radius: 18px;

    padding: 1.5rem;

    border-left: 6px solid #2563EB;

    box-shadow:
        0 2px 12px rgba(0,0,0,0.08);

    transition: 0.2s;
}

.kpi-card:hover {

    transform: translateY(-3px);
}

.kpi-title {

    font-size: 15px;

    color: #6B7280;

    margin-bottom: 10px;
}

.kpi-value {

    font-size: 40px;

    font-weight: 800;

    color: #111827;
}

/* =====================================================
STATUS CARD
===================================================== */

.status-card {

    background: white;

    border-radius: 18px;

    padding: 1.5rem;

    border-left: 6px solid #10B981;

    box-shadow:
        0 2px 12px rgba(0,0,0,0.08);
}

/* =====================================================
TABLE
===================================================== */

.stDataFrame {

    border-radius: 18px;

    overflow: hidden;

    border: 1px solid #E5E7EB;

    background: white;
}

/* =====================================================
CHART CONTAINER
===================================================== */

.element-container:has(.js-plotly-plot) {

    background: white;

    border-radius: 18px;

    padding: 1rem;

    box-shadow:
        0 2px 12px rgba(0,0,0,0.08);

    margin-bottom: 1rem;
}

/* =====================================================
BUTTONS
===================================================== */

.stButton button {

    border-radius: 10px;

    background: #2563EB;

    color: white;

    border: none;

    height: 45px;

    font-weight: 600;
}

/* =====================================================
DOWNLOAD BUTTON
===================================================== */

.stDownloadButton button {

    border-radius: 10px;

    background: #10B981;

    color: white;

    border: none;

    height: 45px;

    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div class="main-title">
📊 Institutional Quant Platform
</div>

<div class="subtitle">
Executive Institutional Analytics Dashboard
</div>
""", unsafe_allow_html=True)

st.caption(
    f"Updated: {pd.Timestamp.now().strftime('%d-%m-%Y %H:%M:%S IST')}"
)

st.markdown("---")

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

    st.markdown("## ⚙️ Dashboard Controls")

    st.markdown("---")

    top_n = st.slider(
        "Stocks To Analyze",
        min_value=100,
        max_value=min(len(stocks), 3000),
        value=300,
        step=25
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

    st.success("AI Quant Engine Enabled")
    st.info("Live Regime Detection Enabled")
    st.info("Sector Rotation Enabled")

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

        trend_strength = sma20 / sma50

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

processed = 0
success = 0
failed = 0

start_time = time.time()

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
            <div class="status-card">

            <b>Processing:</b> {symbol}<br><br>

            ✅ Success: {success}<br>

            ❌ Failed: {failed}<br>

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
# KPI SECTION
# =========================================================

k1, k2, k3, k4 = st.columns(4)

with k1:

    st.markdown(
        f"""
        <div class="kpi-card">
        <div class="kpi-title">
        Universe Size
        </div>

        <div class="kpi-value">
        {len(results)}
        </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with k2:

    avg_score = safe_round(
        results["Final Score"].mean() * 100
    )

    st.markdown(
        f"""
        <div class="kpi-card">
        <div class="kpi-title">
        Avg Institutional Score
        </div>

        <div class="kpi-value">
        {avg_score}
        </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with k3:

    strong_buys = len(
        results[
            results["Classification"]
            == "STRONG_BUY"
        ]
    )

    st.markdown(
        f"""
        <div class="kpi-card">
        <div class="kpi-title">
        Strong Buy Opportunities
        </div>

        <div class="kpi-value">
        {strong_buys}
        </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with k4:

    st.markdown(
        f"""
        <div class="kpi-card">
        <div class="kpi-title">
        Market Regime
        </div>

        <div class="kpi-value" style="font-size:24px;">
        {regime}
        </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# =========================================================
# CHARTS ROW
# =========================================================

chart1, chart2 = st.columns(2)

# =========================================================
# SIGNAL DISTRIBUTION
# =========================================================

with chart1:

    signal_counts = (
        results["Classification"]
        .value_counts()
        .reset_index()
    )

    signal_counts.columns = [
        "Signal",
        "Count"
    ]

    pie_fig = px.pie(

        signal_counts,

        names="Signal",

        values="Count",

        hole=0.55,

        title="Signal Distribution",

        template="plotly_white"
    )

    pie_fig.update_layout(

        paper_bgcolor="white",

        plot_bgcolor="white",

        font=dict(color="#111827"),

        height=450
    )

    st.plotly_chart(
        pie_fig,
        use_container_width=True
    )

# =========================================================
# SECTOR PERFORMANCE
# =========================================================

with chart2:

    sector_perf = (
        results
        .groupby("Sector")["Final Score"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )

    sector_fig = px.bar(

        sector_perf.head(10),

        x="Sector",

        y="Final Score",

        color="Final Score",

        title="Top Sector Performance",

        template="plotly_white",

        color_continuous_scale="Viridis"
    )

    sector_fig.update_layout(

        paper_bgcolor="white",

        plot_bgcolor="white",

        font=dict(color="#111827"),

        height=450
    )

    st.plotly_chart(
        sector_fig,
        use_container_width=True
    )

# =========================================================
# TABLE
# =========================================================

st.markdown("## 🏦 Top Institutional Rankings")

st.dataframe(
    results.head(100),
    use_container_width=True,
    height=650
)

# =========================================================
# RISK REWARD MATRIX
# =========================================================

st.markdown("## 📈 Risk Reward Opportunity Matrix")

scatter_df = results.head(100).copy()

scatter_df["Bubble Size"] = (
    scatter_df["Momentum"]
    .abs()
    .fillna(0)
)

scatter_df["Bubble Size"] = (
    scatter_df["Bubble Size"] * 2
) + 10

scatter = px.scatter(

    scatter_df,

    x="Risk Reward",

    y="Final Score",

    color="Classification",

    size="Bubble Size",

    hover_name="Symbol",

    hover_data=[
        "Sector",
        "Momentum",
        "Sharpe"
    ],

    template="plotly_white"
)

scatter.update_layout(

    paper_bgcolor="white",

    plot_bgcolor="white",

    font=dict(color="#111827"),

    height=700
)

st.plotly_chart(
    scatter,
    use_container_width=True
)

# =========================================================
# TOP STOCKS BAR CHART
# =========================================================

st.markdown("## 🚀 Top Stocks By Institutional Score")

top_stocks = results.head(15)

top_fig = px.bar(

    top_stocks,

    x="Symbol",

    y="Final Score",

    color="Final Score",

    template="plotly_white",

    color_continuous_scale="Turbo"
)

top_fig.update_layout(

    paper_bgcolor="white",

    plot_bgcolor="white",

    font=dict(color="#111827"),

    height=550
)

st.plotly_chart(
    top_fig,
    use_container_width=True
)

# =========================================================
# DOWNLOAD CSV
# =========================================================

csv = results.to_csv(index=False)

st.download_button(
    label="📥 Download Rankings CSV",
    data=csv,
    file_name="institutional_rankings.csv",
    mime="text/csv"
)

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    """
    Institutional Quantamental Intelligence Platform •
    Executive Analytics Dashboard • Institutional Research Engine
    """
)
