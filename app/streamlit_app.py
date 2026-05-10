# =========================================================
# FILE: app/streamlit_app.py
# FINAL STABLE + FAST INSTITUTIONAL QUANT PLATFORM
# =========================================================

import sys
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
    sector_score
)

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(

    page_title="Institutional Quant Platform",

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
# CACHE REGIME
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

    "Top Stocks",

    25,

    500,

    100
)

max_universe = st.sidebar.slider(

    "Universe Limit",

    100,

    2000,

    500,

    step=100
)

# =========================================================
# LOAD STOCK UNIVERSE
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

        .unique()

        .tolist()
    )

    # =====================================================
    # NSE FILTER
    # =====================================================

    stocks = [

        stock.strip().upper()

        for stock in stocks

        if ".NS" in stock
    ]

    # =====================================================
    # REMOVE DUPLICATES
    # =====================================================

    stocks = list(

        dict.fromkeys(stocks)
    )

    # =====================================================
    # LIMIT UNIVERSE
    # =====================================================

    stocks = stocks[:max_universe]

except Exception as e:

    st.error(

        f"Universe load failed: {e}"
    )

    st.stop()

# =========================================================
# SIDEBAR METRICS
# =========================================================

st.sidebar.metric(

    "Universe Size",

    len(stocks)
)

# =========================================================
# SAFE ROUND
# =========================================================

def safe_round(value, digits=4):

    try:

        if value is None:
            return 0

        if np.isnan(value):
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

        # =================================================
        # FAST INFO ONLY
        # =================================================

        ticker = yf.Ticker(symbol)

        try:

            fast_info = ticker.fast_info

        except Exception:

            return None

        # =================================================
        # MARKET CAP
        # =================================================

        market_cap = fast_info.get(

            "market_cap",

            0
        )

        if market_cap is None:

            market_cap = 0

        if market_cap < 1_000_000_000:

            return None

        # =================================================
        # DEFAULT FUNDAMENTALS
        # =================================================

        sector = "Unknown"

        revenue_growth = 0
        profit_margin = 0
        roe = 0
        operating_margin = 0
        debt_to_equity = 0
        dividend_yield = 0

        # =================================================
        # PRICE DATA
        # =================================================

        data = yf.download(

            symbol,

            period="6mo",

            interval="1d",

            progress=False,

            auto_adjust=True,

            threads=False
        )

        if data.empty:

            return None

        close = data["Close"]

        # =================================================
        # MULTIINDEX FIX
        # =====================================================

        if isinstance(close, pd.DataFrame):

            close = close.iloc[:, 0]

        close = close.dropna()

        if len(close) < 50:

            return None

        returns = close.pct_change().dropna()

        if len(returns) < 20:

            return None

        # =================================================
        # TECHNICALS
        # =================================================

        momentum = (

            close.iloc[-1]
            / close.iloc[-20]
        ) - 1

        volatility = (

            returns.std()
            * np.sqrt(252)
        )

        # =================================================
        # SHARPE
        # =================================================

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

            close.rolling(50)
            .mean()
            .iloc[-1]
        )

        if sma50 == 0:

            trend_strength = 0

        else:

            trend_strength = (

                sma20 / sma50
            )

        # =================================================
        # REGIME ADAPTATION
        # =================================================

        if "BULLISH" in regime:

            momentum *= 1.20
            sharpe *= 1.10

        elif "BEARISH" in regime:

            volatility *= 1.30

        elif "SIDEWAYS" in regime:

            sharpe *= 1.10
            trend_strength *= 0.80

        # =================================================
        # METRICS
        # =================================================

        metrics = {

            "revenue_growth":
                revenue_growth,

            "profit_margin":
                profit_margin,

            "roe":
                roe,

            "operating_margin":
                operating_margin,

            "momentum":
                momentum,

            "volatility":
                volatility,

            "sharpe":
                sharpe,

            "total_return":
                total_return,

            "trend_strength":
                trend_strength,

            "dividend_yield":
                dividend_yield,

            "debt_to_equity":
                debt_to_equity
        }

        # =================================================
        # SECTOR SCORE
        # =================================================

        final_score = sector_score(

            sector,

            metrics
        )

        if np.isnan(final_score):

            return None

        # =================================================
        # CLASSIFICATION
        # =================================================

        if final_score >= 1.0:

            classification = (

                "INSTITUTIONAL_LONG"
            )

        elif final_score >= 0.7:

            classification = (

                "HIGH_CONVICTION"
            )

        elif final_score >= 0.4:

            classification = (

                "WATCHLIST"
            )

        else:

            classification = "AVOID"

        percentile = (

            final_score * 100
        )

        # =================================================
        # FINAL OUTPUT
        # =================================================

        return {

            "Symbol":
                symbol,

            "Sector":
                sector,

            "Market Cap":
                safe_round(market_cap, 0),

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

progress = st.progress(0)

status = st.empty()

# =========================================================
# PARALLEL EXECUTION
# =========================================================

with ThreadPoolExecutor(max_workers=5) as executor:

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

        result = future.result()

        if result is not None:

            ranking_data.append(result)

        status.text(

            f"Processed "
            f"{idx+1}/{len(stocks)} stocks"
        )

        progress.progress(

            (idx + 1)
            / len(stocks)
        )

status.text(

    "Institutional Ranking Completed"
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
        - Invalid symbols
        - Yahoo rate limiting
        - Empty Excel file
        - Network issue
        """
    )

    st.stop()

# =========================================================
# SORT
# =========================================================

results = results.sort_values(

    by="Final Score",

    ascending=False
)

results = results.head(top_n)

# =========================================================
# METRICS
# =========================================================

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(

        "Live Regime",

        regime
    )

with col2:

    st.metric(

        "Stocks Ranked",

        len(results)
    )

with col3:

    st.metric(

        "Top Alpha Score",

        safe_round(

            results["Final Score"].max()
        )
    )

# =========================================================
# TABLE
# =========================================================

st.subheader(

    "Institutional Alpha Rankings"
)

st.dataframe(

    results,

    use_container_width=True,

    height=700
)

# =========================================================
# BAR CHART
# =========================================================

fig = px.bar(

    results,

    x="Symbol",

    y="Final Score",

    color="Classification",

    title="Institutional Alpha Scores"
)

st.plotly_chart(

    fig,

    use_container_width=True
)

# =========================================================
# FACTOR MAP
# =========================================================

plot_results = results.copy()

plot_results["Bubble Size"] = (

    plot_results["Final Score"]

    .abs()

    + 0.05
)

factor_fig = px.scatter(

    plot_results,

    x="Momentum",

    y="Sharpe",

    size="Bubble Size",

    color="Classification",

    hover_name="Symbol",

    title="Institutional Factor Intelligence"
)

st.plotly_chart(

    factor_fig,

    use_container_width=True
)

# =========================================================
# DISTRIBUTION
# =========================================================

hist_fig = px.histogram(

    results,

    x="Percentile",

    nbins=20,

    title="Alpha Percentile Distribution"
)

st.plotly_chart(

    hist_fig,

    use_container_width=True
)

# =========================================================
# TOP PICKS
# =========================================================

st.subheader(

    "Institutional Long Candidates"
)

top_picks = results[

    results["Classification"]

    == "INSTITUTIONAL_LONG"
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
