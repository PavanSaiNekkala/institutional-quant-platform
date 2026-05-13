# =========================================================
# FILE: app/streamlit_app.py
# FINAL INSTITUTIONAL QUANT PLATFORM
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
# ADVANCED DARK CSS
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #050816;
        color: white;
    }

    section[data-testid="stSidebar"] {
        background-color: #0B1220;
        width: 320px !important;
    }

    section[data-testid="stSidebar"] > div {
        width: 320px !important;
    }

    h1, h2, h3, h4 {
        color: white !important;
        font-weight: 700 !important;
    }

    .metric-card {
        background: linear-gradient(
            135deg,
            #132238,
            #0E1B2E
        );

        padding: 1.2rem;
        border-radius: 18px;
        border: 1px solid #1E2B40;
        margin-bottom: 1rem;
    }

    .regime-bull {
        background: rgba(0,255,100,0.12);
        padding: 1rem;
        border-radius: 14px;
        border-left: 5px solid #00C853;
        font-size: 18px;
    }

    .regime-bear {
        background: rgba(255,0,0,0.12);
        padding: 1rem;
        border-radius: 14px;
        border-left: 5px solid #FF5252;
        font-size: 18px;
    }

    .regime-sideways {
        background: rgba(255,165,0,0.12);
        padding: 1rem;
        border-radius: 14px;
        border-left: 5px solid #FFD54F;
        font-size: 18px;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    div[data-baseweb="slider"] {
        padding-top: 0rem;
        padding-bottom: 0rem;
    }

    .stDataFrame {
        border-radius: 15px;
        overflow: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# TITLE
# =========================================================

st.markdown(
    """
    # 📈 Institutional Quant Platform

    ### AI-Powered Institutional Quantitative Analytics Platform
    """
)

st.caption(
    f"Last Updated: {pd.Timestamp.now().strftime('%d-%m-%Y %H:%M:%S IST')}"
)

st.markdown("---")

# =========================================================
# LIVE MARKET REGIME
# =========================================================

@st.cache_data(ttl=1800)
def cached_regime():

    return detect_market_regime()

regime = cached_regime()

# =========================================================
# REGIME DISPLAY
# =========================================================

if "BULLISH" in regime:

    st.markdown(
        f"""
        <div class="regime-bull">
        📈 <b>Market Regime:</b> {regime}
        </div>
        """,
        unsafe_allow_html=True
    )

elif "BEARISH" in regime:

    st.markdown(
        f"""
        <div class="regime-bear">
        📉 <b>Market Regime:</b> {regime}
        </div>
        """,
        unsafe_allow_html=True
    )

else:

    st.markdown(
        f"""
        <div class="regime-sideways">
        📊 <b>Market Regime:</b> {regime}
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# LOAD UNIVERSE
# =========================================================

universe_path = (
    ROOT_DIR
    / "data"
    / "valid_stocks.xlsx"
)

try:

    universe_df = pd.read_excel(universe_path)

    stocks = (
        universe_df.iloc[:, 0]
        .dropna()
        .astype(str)
        .str.strip()
        .str.upper()
        .unique()
        .tolist()
    )

    stocks = [
        stock
        for stock in stocks
        if stock.endswith(".NS")
    ]

    stocks = list(dict.fromkeys(stocks))

except Exception as e:

    st.error(f"Universe loading failed: {e}")

    st.stop()

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

    sector_filter = st.selectbox(
        "Sector",
        ["All"]
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
    st.info("🧠 Sector Rotation Enabled")
    st.info("⚡ Backtesting Engine Enabled")

# =========================================================
# SAFE ROUND
# =========================================================

def safe_round(value, digits=4):

    try:

        if value is None:
            return 0

        if pd.isna(value):
            return 0

        if np.isinf(value):
            return 0

        return round(float(value), digits)

    except Exception:

        return 0

# =========================================================
# STOCK ANALYZER
# =========================================================

def analyze_stock(symbol, regime):

    try:

        ticker = yf.Ticker(symbol)

        try:
            fast_info = ticker.fast_info
        except Exception:
            fast_info = {}

        market_cap = fast_info.get("market_cap", 0)

        if market_cap is None:
            market_cap = 0

        sector = detect_sector(symbol)

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

        if len(returns) < 20:
            return None

        momentum = (
            close.iloc[-1]
            / close.iloc[-20]
        ) - 1

        volatility = (
            returns.std()
            * np.sqrt(252)
        )

        if returns.std() == 0:
            sharpe = 0
        else:
            sharpe = (
                returns.mean()
                / returns.std()
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
        ) if sma50 != 0 else 0

        cmp = close.iloc[-1]

        recent_volatility = (
            close.pct_change()
            .rolling(14)
            .std()
            .iloc[-1]
        )

        if pd.isna(recent_volatility):
            recent_volatility = 0.02

        stop_loss = (
            cmp
            * (
                1 - recent_volatility * 2
            )
        )

        target_price = (
            cmp
            * (
                1 + recent_volatility * 4
            )
        )

        risk_reward = (
            (target_price - cmp)
            / max(
                cmp - stop_loss,
                0.0001
            )
        )

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

        percentile = final_score * 100

        return {

            "Symbol": symbol,
            "Sector": sector,
            "Market Cap": safe_round(market_cap, 0),
            "Current Price": safe_round(cmp, 2),
            "Stop Loss": safe_round(stop_loss, 2),
            "Target": safe_round(target_price, 2),
            "Risk Reward": safe_round(risk_reward, 2),
            "Momentum": safe_round(momentum),
            "Volatility": safe_round(volatility),
            "Sharpe": safe_round(sharpe),
            "Trend Strength": safe_round(trend_strength),
            "Total Return": safe_round(total_return),
            "Final Score": safe_round(final_score),
            "Percentile": safe_round(percentile, 2),
            "Classification": classification
        }

    except Exception:

        return None

# =========================================================
# MAIN ENGINE
# =========================================================

ranking_data = []

progress_bar = st.progress(0)

status_text = st.empty()

metric_placeholder = st.empty()

start_time = time.time()

processed_count = 0
success_count = 0
failed_count = 0

failed_stocks = []

with st.spinner(
    "Running Institutional Quant Engine..."
):

    with ThreadPoolExecutor(max_workers=6) as executor:

        futures = {

            executor.submit(
                analyze_stock,
                symbol,
                regime
            ): symbol

            for symbol in stocks
        }

        for idx, future in enumerate(
            as_completed(futures)
        ):

            processed_count += 1

            symbol = futures[future]

            try:

                result = future.result()

                if result is not None:

                    ranking_data.append(result)

                    success_count += 1

                else:

                    failed_count += 1

                    failed_stocks.append(symbol)

            except Exception:

                failed_count += 1

                failed_stocks.append(symbol)

            progress = (
                processed_count
                / len(stocks)
            )

            progress_bar.progress(progress)

            elapsed = (
                time.time()
                - start_time
            )

            avg_time = (
                elapsed
                / max(processed_count, 1)
            )

            remaining = (
                avg_time
                * (
                    len(stocks)
                    - processed_count
                )
            )

            status_text.info(
                f"""
                🔄 Processing: {symbol}

                ✅ Success: {success_count}

                ❌ Failed: {failed_count}

                ⏳ Remaining: {int(remaining)} sec
                """
            )

            metric_placeholder.metric(
                "Processing Progress",
                f"{processed_count}/{len(stocks)}"
            )

# =========================================================
# RESULTS
# =========================================================

results = pd.DataFrame(ranking_data)

if results.empty:

    st.error(
        """
        No valid stocks ranked.

        Possible reasons:
        - Yahoo Finance rate limit
        - Invalid symbols
        - Network/API issue
        """
    )

    st.stop()

# =========================================================
# SECTOR RANK
# =========================================================

results["Sector Rank"] = (
    results
    .groupby("Sector")["Final Score"]
    .rank(
        ascending=False,
        method="dense"
    )
)

results["Normalized Score"] = (
    results["Final Score"]
    / results.groupby("Sector")["Final Score"]
    .transform("max")
)

results = results.sort_values(
    by=[
        "Normalized Score",
        "Final Score"
    ],
    ascending=False
)

# =========================================================
# FILTERS
# =========================================================

results = results[
    results["Percentile"] >= min_score
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

display_results = results.head(top_n)

# =========================================================
# KPI METRICS
# =========================================================

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.markdown(
        f"""
        <div class="metric-card">
        <h4>📊 Universe Size</h4>
        <h2>{len(display_results)}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:

    st.markdown(
        f"""
        <div class="metric-card">
        <h4>🏆 Avg Institutional Score</h4>
        <h2>{safe_round(display_results["Final Score"].mean()*100,2)}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:

    strong_buy_count = len(
        display_results[
            display_results["Classification"]
            == "STRONG_BUY"
        ]
    )

    st.markdown(
        f"""
        <div class="metric-card">
        <h4>🚀 Strong Buys</h4>
        <h2>{strong_buy_count}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:

    st.markdown(
        f"""
        <div class="metric-card">
        <h4>🎯 Confidence</h4>
        <h2>{safe_round(display_results["Percentile"].mean(),2)}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# COLOR MAP
# =========================================================

color_map = {

    "STRONG_BUY": "#00C853",
    "BUY": "#64DD17",
    "WATCH": "#FFD600",
    "AVOID": "#D50000"
}

# =========================================================
# MAIN TABLE
# =========================================================

st.subheader(
    "🏦 Institutional Rankings"
)

st.dataframe(
    display_results.style.background_gradient(
        cmap="RdYlGn",
        subset=["Final Score"]
    ),
    use_container_width=True,
    height=700
)

# =========================================================
# SECTOR LEADERS
# =========================================================

st.subheader(
    "📈 Sector Leaders"
)

sector_leaders = (
    display_results
    .groupby("Sector")
    .head(5)
)

st.dataframe(
    sector_leaders.style.background_gradient(
        cmap="RdYlGn",
        subset=["Final Score"]
    ),
    use_container_width=True,
    height=500
)

# =========================================================
# SCORE CHART
# =========================================================

fig = px.bar(
    display_results,
    x="Symbol",
    y="Final Score",
    color="Classification",
    color_discrete_map=color_map,
    title="Institutional Alpha Scores"
)

fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="#050816",
    plot_bgcolor="#050816",
    font=dict(color="white"),
    height=600
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =========================================================
# RISK REWARD MATRIX
# =========================================================

scatter_data = display_results.copy()

scatter_data["Bubble"] = (
    scatter_data["Momentum"]
    .abs()
    .fillna(0)
    .replace([np.inf, -np.inf], 0)
    + 0.05
)

rr_fig = px.scatter(
    scatter_data,
    x="Risk Reward",
    y="Final Score",
    size="Bubble",
    color="Classification",
    hover_name="Symbol",
    color_discrete_map=color_map,
    title="Institutional Risk Reward Matrix"
)

rr_fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="#050816",
    plot_bgcolor="#050816",
    font=dict(color="white"),
    height=650
)

st.plotly_chart(
    rr_fig,
    use_container_width=True
)

# =========================================================
# TOP PICKS
# =========================================================

st.subheader(
    "🚀 Institutional Buy Candidates"
)

top_picks = display_results[
    display_results["Classification"]
    .isin([
        "STRONG_BUY",
        "BUY"
    ])
]

st.dataframe(
    top_picks.style.background_gradient(
        cmap="RdYlGn",
        subset=["Final Score"]
    ),
    use_container_width=True
)

# =========================================================
# DOWNLOAD CSV
# =========================================================

csv = results.to_csv(index=False)

st.download_button(
    label="Download Rankings CSV",
    data=csv,
    file_name="institutional_rankings.csv",
    mime="text/csv"
)

# =========================================================
# FAILED STOCKS
# =========================================================

st.markdown("---")

st.subheader(
    "❌ Failed Stock Downloads"
)

if len(failed_stocks) == 0:

    st.success(
        "No failed stock downloads."
    )

else:

    failed_df = pd.DataFrame({
        "Failed Symbols": failed_stocks
    })

    st.dataframe(
        failed_df,
        use_container_width=True,
        height=400
    )

    st.warning(
        f"{len(failed_stocks)} stocks failed during processing."
    )

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    """
    Institutional Quantamental Intelligence Platform •
    AI Driven • Sector Rotation • Institutional Alpha Engine
    """
)
