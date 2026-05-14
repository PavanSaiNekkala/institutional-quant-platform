# =========================================================
# FILE: app/streamlit_app.py
# FINAL UPDATED INSTITUTIONAL QUANT PLATFORM
# =========================================================

import sys
from pathlib import Path
from datetime import datetime
import pytz
import time

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px

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
# CSS
# =========================================================

st.markdown("""
<style>

.stApp {
    background-color: #F3F4F6;
    color: #111827;
    font-family: "Segoe UI", sans-serif;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
    max-width: 96%;
}

section[data-testid="stSidebar"] {
    background: #111827;
    border-right: 1px solid #1F2937;
    width: 320px !important;
}

section[data-testid="stSidebar"] > div {
    width: 320px !important;
    padding-top: 1rem;
}

section[data-testid="stSidebar"] * {
    color: #F9FAFB !important;
}

label {
    color: #E5E7EB !important;
    font-size: 15px !important;
    font-weight: 600 !important;
}

div[data-baseweb="select"] > div {
    background-color: #1F2937 !important;
    border: 1px solid #374151 !important;
    border-radius: 10px !important;
    min-height: 48px !important;
    color: white !important;
}

div[data-baseweb="base-input"] > div {
    background-color: #FFFFFF !important;
    border: 2px solid #2563EB !important;
    border-radius: 12px !important;
    min-height: 50px !important;
}

input[type="text"] {
    color: #111827 !important;
    -webkit-text-fill-color: #111827 !important;
    font-weight: 700 !important;
    font-size: 16px !important;
    background-color: white !important;
}

input[type="text"]::placeholder {
    color: #6B7280 !important;
}

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

.element-container:has(.js-plotly-plot) {
    background: white;
    border-radius: 18px;
    padding: 1rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    margin-bottom: 1rem;
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

india_tz = pytz.timezone("Asia/Kolkata")

current_time = datetime.now(india_tz)

st.caption(
    f"Updated: {current_time.strftime('%d-%m-%Y %I:%M:%S %p IST')}"
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
# COLORS
# =========================================================

signal_colors = {
    "STRONG_BUY": "#006400",
    "BUY": "#32CD32",
    "WATCH": "#FF8C00",
    "AVOID": "#DC2626"
}

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
        "Search Stock",
        placeholder="Type stock name..."
    )

    if search_stock:

        matching_stocks = [
            s for s in stocks
            if search_stock.upper() in s.upper()
        ][:15]

        if matching_stocks:

            st.markdown("### 🔍 Matching Stocks")

            for stock in matching_stocks:

                st.markdown(
                    f"""
                    <div style="
                        background:#1F2937;
                        padding:10px;
                        border-radius:10px;
                        margin-bottom:8px;
                        color:white;
                        font-weight:600;
                        border-left:4px solid #32CD32;
                    ">
                    {stock}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    st.markdown("---")

    st.success(
        f"✅ NSE Universe Loaded: {len(stocks)}"
    )

    st.info("📈 Live Regime Detection Enabled")

    st.info("🧠 Sector Rotation Enabled")

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

def analyze_stock(symbol, close_data, regime):

    try:

        if symbol not in close_data.columns:
            return None

        close = close_data[symbol].dropna()

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
# ANALYSIS ENGINE
# =========================================================

@st.cache_data(show_spinner=False, ttl=3600)
def run_analysis(stock_list, regime):

    ranking_data = []

    failed_stocks = []

    progress_bar = st.progress(0)

    status_box = st.empty()

    total = len(stock_list)

    start_time = datetime.now(india_tz)

    batch_size = 75

    completed = 0

    for batch_start in range(0, total, batch_size):

        batch = stock_list[
            batch_start: batch_start + batch_size
        ]

        try:

            data = yf.download(
                tickers=batch,
                period="3mo",
                interval="1d",
                auto_adjust=True,
                progress=False,
                threads=False,
                group_by="ticker"
            )

        except:

            failed_stocks.extend(batch)

            continue

        close_data = pd.DataFrame()

        for symbol in batch:

            try:

                if symbol in data.columns.levels[0]:

                    close_data[symbol] = data[symbol]["Close"]

                else:

                    failed_stocks.append(symbol)

            except:

                failed_stocks.append(symbol)

        for symbol in batch:

            completed += 1

            try:

                result = analyze_stock(
                    symbol,
                    close_data,
                    regime
                )

                if result:

                    ranking_data.append(result)

                else:

                    failed_stocks.append(symbol)

            except:

                failed_stocks.append(symbol)

            progress_bar.progress(
                completed / total
            )

            elapsed_minutes = round(
                (
                    datetime.now(india_tz)
                    - start_time
                ).total_seconds() / 60,
                1
            )

            estimated_total = round(
                (
                    elapsed_minutes
                    / max(completed, 1)
                ) * total,
                1
            )

            remaining_minutes = round(
                max(
                    estimated_total
                    - elapsed_minutes,
                    0
                ),
                1
            )

            if completed % 10 == 0:

                status_box.markdown(
                    f"""
                    <div style="
                        background:white;
                        border-radius:18px;
                        padding:18px;
                        border-left:6px solid #10B981;
                        box-shadow:0 2px 12px rgba(0,0,0,0.08);
                        height:260px;
                        overflow:hidden;
                    ">

                    <h3 style="
                        margin-top:0;
                        margin-bottom:12px;
                        color:#111827;
                    ">
                    📊 Institutional Processing Engine
                    </h3>

                    <hr style="margin:8px 0 14px 0;">

                    <div style="
                        display:grid;
                        grid-template-columns:1fr 1fr;
                        gap:14px;
                        font-size:17px;
                        font-weight:600;
                        color:#374151;
                    ">

                        <div>
                        ✅ Completed<br>
                        <span style="
                            font-size:26px;
                            color:#10B981;
                            font-weight:800;
                        ">
                        {completed}/{total}
                        </span>
                        </div>

                        <div>
                        ❌ Failed<br>
                        <span style="
                            font-size:26px;
                            color:#DC2626;
                            font-weight:800;
                        ">
                        {len(set(failed_stocks))}
                        </span>
                        </div>

                        <div>
                        🌐 Universe<br>
                        <span style="
                            font-size:24px;
                            color:#2563EB;
                            font-weight:800;
                        ">
                        {total}
                        </span>
                        </div>

                        <div>
                        ⏳ Remaining<br>
                        <span style="
                            font-size:24px;
                            color:#F59E0B;
                            font-weight:800;
                        ">
                        {remaining_minutes}m
                        </span>
                        </div>

                    </div>

                    <div style="
                        margin-top:16px;
                        padding:12px;
                        border-radius:12px;
                        background:#F3F4F6;
                        font-size:15px;
                        font-weight:600;
                        color:#111827;
                    ">
                    🔍 Current Stock:
                    {symbol}
                    </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

        time.sleep(1)

    progress_bar.empty()

    status_box.empty()

    failed_stocks = list(set(failed_stocks))

    return pd.DataFrame(ranking_data), failed_stocks

# =========================================================
# RUN ANALYSIS
# =========================================================

raw_results, failed_stocks = run_analysis(
    stocks,
    regime
)

if raw_results.empty:

    st.error("No valid stocks analyzed.")

    st.stop()

results = raw_results.copy()

results["Percentile"] = (
    results["Final Score"] * 100
)

results = results[
    results["Percentile"] >= min_score
]

if signal_filter != "All":

    results = results[
        results["Classification"] == signal_filter
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
# FAILED STOCKS
# =========================================================

if failed_stocks:

    with st.expander(
        f"⚠️ Failed Stocks ({len(failed_stocks)})"
    ):

        failed_df = pd.DataFrame({
            "Failed Stocks": failed_stocks
        })

        st.dataframe(
            failed_df,
            use_container_width=True,
            height=300
        )

# =========================================================
# KPIs
# =========================================================

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric("Universe Size", len(results))

with k2:
    st.metric(
        "Avg Institutional Score",
        safe_round(
            results["Final Score"].mean() * 100
        )
    )

with k3:
    st.metric(
        "Strong Buy Opportunities",
        len(
            results[
                results["Classification"]
                == "STRONG_BUY"
            ]
        )
    )

with k4:
    st.metric(
        "Market Regime",
        regime
    )

st.markdown("<br>", unsafe_allow_html=True)

# =========================================================
# CHARTS
# =========================================================

chart1, chart2 = st.columns(2)

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
        template="plotly_white",
        color="Signal",
        color_discrete_map=signal_colors
    )

    pie_fig.update_layout(height=450)

    st.plotly_chart(
        pie_fig,
        use_container_width=True
    )

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
        color_continuous_scale=[
            "#FF8C00",
            "#32CD32",
            "#006400"
        ]
    )

    sector_fig.update_layout(height=450)

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
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    """
    Institutional Quantamental Intelligence Platform •
    Executive Analytics Dashboard • Institutional Research Engine
    """
)
