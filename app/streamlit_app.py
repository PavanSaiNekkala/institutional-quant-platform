# =========================================================
# FILE: app/streamlit_app.py
# FINAL OPTIMIZED INSTITUTIONAL QUANT PLATFORM
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

    page_icon="🏦",

    layout="wide"
)

# =========================================================
# TITLE
# =========================================================

st.title(

    "🏦 Institutional Quant Research Platform"
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

    st.success(

        f"📈 Live Market Regime: {regime}"
    )

elif "BEARISH" in regime:

    st.error(

        f"📉 Live Market Regime: {regime}"
    )

else:

    st.warning(

        f"📊 Live Market Regime: {regime}"
    )

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header(

    "Institutional Controls"
)

top_n = st.sidebar.slider(

    "Top Ranked Stocks",

    min_value=10,

    max_value=100,

    value=50,

    step=10
)

# =========================================================
# LOAD FULL UNIVERSE
# =========================================================

universe_path = (

    ROOT_DIR
    / "data"
    / "valid_stocks.xlsx"
)

try:

    universe_df = pd.read_excel(

        universe_path
    )

    stocks = (

        universe_df.iloc[:, 0]

        .dropna()

        .astype(str)

        .str.strip()

        .str.upper()

        .unique()

        .tolist()
    )

    # =====================================================
    # FILTER NSE STOCKS
    # =====================================================

    stocks = [

        stock

        for stock in stocks

        if stock.endswith(".NS")
    ]

    # =====================================================
    # REMOVE DUPLICATES
    # =====================================================

    stocks = list(dict.fromkeys(stocks))

except Exception as e:

    st.error(

        f"Universe loading failed: {e}"
    )

    st.stop()

# =========================================================
# SIDEBAR METRIC
# =========================================================

st.sidebar.metric(

    "Universe Loaded",

    f"{len(stocks):,}"
)

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

        return round(

            float(value),

            digits
        )

    except Exception:

        return 0

# =========================================================
# STOCK ANALYZER
# =========================================================

def analyze_stock(symbol, regime):

    # =====================================================
    # SMALL THROTTLE
    # =====================================================

    time.sleep(0.02)

    try:

        ticker = yf.Ticker(symbol)

        # =================================================
        # FAST INFO
        # =================================================

        try:

            fast_info = ticker.fast_info

        except Exception:

            fast_info = {}

        market_cap = fast_info.get(

            "market_cap",

            0
        )

        if market_cap is None:

            market_cap = 0

        # =================================================
        # SECTOR
        # =================================================

        sector = detect_sector(symbol)

        # =================================================
        # FAST DOWNLOAD
        # =================================================

        data = yf.download(

            symbol,

            period="3mo",

            interval="1d",

            auto_adjust=True,

            progress=False,

            threads=False,

            timeout=8
        )

        if data.empty:

            return None

        close = data["Close"]

        if isinstance(close, pd.DataFrame):

            close = close.iloc[:, 0]

        close = close.dropna()

        if len(close) < 40:

            return None

        # =================================================
        # RETURNS
        # =================================================

        returns = close.pct_change().dropna()

        if len(returns) < 20:

            return None

        # =================================================
        # FACTORS
        # =================================================

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

        # =================================================
        # CURRENT PRICE
        # =================================================

        cmp = close.iloc[-1]

        # =================================================
        # RISK MODEL
        # =================================================

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

        # =================================================
        # FINAL SCORE
        # =================================================

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

        # =================================================
        # CLASSIFICATION
        # =================================================

        if final_score >= 1.20:

            classification = "STRONG_BUY"

        elif final_score >= 0.80:

            classification = "BUY"

        elif final_score >= 0.50:

            classification = "WATCH"

        else:

            classification = "AVOID"

        percentile = (

            final_score * 100
        )

        return {

            "Symbol":
                symbol,

            "Sector":
                sector,

            "Market Cap":
                safe_round(market_cap, 0),

            "Current Price":
                safe_round(cmp, 2),

            "Stop Loss":
                safe_round(stop_loss, 2),

            "Target":
                safe_round(target_price, 2),

            "Risk Reward":
                safe_round(risk_reward, 2),

            "Momentum":
                safe_round(momentum),

            "Volatility":
                safe_round(volatility),

            "Sharpe":
                safe_round(sharpe),

            "Trend Strength":
                safe_round(trend_strength),

            "Total Return":
                safe_round(total_return),

            "Final Score":
                safe_round(final_score),

            "Percentile":
                safe_round(percentile, 2),

            "Classification":
                classification
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

# =========================================================
# PROCESSING ENGINE
# =========================================================

with st.spinner(

    "Running Institutional Quant Engine..."
):

    with ThreadPoolExecutor(max_workers=12) as executor:

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

            except Exception:

                failed_count += 1

            # =================================================
            # PROGRESS
            # =================================================

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

results = pd.DataFrame(

    ranking_data
)

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

# =========================================================
# NORMALIZED SCORE
# =========================================================

results["Normalized Score"] = (

    results["Final Score"]

    / results.groupby("Sector")["Final Score"]

    .transform("max")
)

# =========================================================
# SORT RESULTS
# =========================================================

results = results.sort_values(

    by=[

        "Normalized Score",
        "Final Score"
    ],

    ascending=False
)

# =========================================================
# DISPLAY ONLY TOP N
# =========================================================

display_results = results.head(top_n)

# =========================================================
# METRICS
# =========================================================

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(

        "Market Regime",

        regime
    )

with col2:

    st.metric(

        "Stocks Ranked",

        len(results)
    )

with col3:

    st.metric(

        "Average Score",

        safe_round(

            display_results["Final Score"].mean()
        )
    )

with col4:

    st.metric(

        "Average RR",

        safe_round(

            display_results["Risk Reward"].mean()
        )
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

    display_results,

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

    sector_leaders,

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

    top_picks,

    use_container_width=True
)

# =========================================================
# DOWNLOAD CSV
# =========================================================

csv = results.to_csv(

    index=False
)

st.download_button(

    label="Download Rankings CSV",

    data=csv,

    file_name="institutional_rankings.csv",

    mime="text/csv"
)

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(

    "Institutional Quantamental Intelligence Platform"
)
