# =========================================================
# FILE: app/streamlit_app.py
# FINAL SPEED-OPTIMIZED INSTITUTIONAL QUANT PLATFORM
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
# LIVE MARKET REGIME
# =========================================================

@st.cache_data(ttl=1800)
def cached_regime():

    return detect_market_regime()


regime = cached_regime()

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
# LOAD DYNAMIC UNIVERSE
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

    stocks = [

        stock for stock in stocks

        if ".NS" in stock
    ]

    stocks = list(

        dict.fromkeys(stocks)
    )

    # =====================================================
    # LIMIT UNIVERSE FOR SPEED
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
# STOCK ANALYZER
# =========================================================

def analyze_stock(symbol, regime):

    try:

        ticker = yf.Ticker(symbol)

        # =================================================
        # FAST INFO
        # =================================================

        info = ticker.fast_info

        market_cap = info.get(

            "market_cap",

            0
        )

        if market_cap < 1_000_000_000:

            return None

        # =================================================
        # BASIC INFO
        # =================================================

        try:

            detailed = ticker.info

            sector = detailed.get(

                "sector",

                "Unknown"
            )

            revenue_growth = detailed.get(

                "revenueGrowth",

                0
            )

            profit_margin = detailed.get(

                "profitMargins",

                0
            )

            roe = detailed.get(

                "returnOnEquity",

                0
            )

            operating_margin = detailed.get(

                "operatingMargins",

                0
            )

            debt_to_equity = detailed.get(

                "debtToEquity",

                0
            )

            dividend_yield = detailed.get(

                "dividendYield",

                0
            )

        except Exception:

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

            period="3mo",

            progress=False,

            auto_adjust=True
        )

        if data.empty:

            return None

        close = data["Close"].dropna()

        if len(close) < 50:

            return None

        returns = close.pct_change().dropna()

        if returns.empty:

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

        trend_strength = (

            sma20 / sma50

        ) if sma50 != 0 else 0

        # =================================================
        # REGIME ADAPTATION
        # =================================================

        if "BULLISH" in regime:

            momentum *= 1.20
            sharpe *= 1.10

        elif "BEARISH" in regime:

            volatility *= 1.30
            dividend_yield *= 1.20

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

        percentile = final_score * 100

        return {

            "Symbol":
                symbol,

            "Sector":
                sector,

            "Market Cap":
                market_cap,

            "Revenue Growth":
                round(revenue_growth, 4),

            "Profit Margin":
                round(profit_margin, 4),

            "ROE":
                round(roe, 4),

            "Operating Margin":
                round(operating_margin, 4),

            "Momentum":
                round(momentum, 4),

            "Volatility":
                round(volatility, 4),

            "Sharpe":
                round(sharpe, 4),

            "Trend Strength":
                round(trend_strength, 4),

            "Dividend Yield":
                round(dividend_yield, 4),

            "Debt To Equity":
                round(debt_to_equity, 4),

            "Final Score":
                round(final_score, 4),

            "Percentile":
                round(percentile, 2),

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

with ThreadPoolExecutor(max_workers=10) as executor:

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

        if result:

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
# DATAFRAME
# =========================================================

results = pd.DataFrame(

    ranking_data
)

if results.empty:

    st.error(

        "No valid stocks ranked"
    )

    st.stop()

results = results.sort_values(

    by="Final Score",

    ascending=False
)

results = results.head(top_n)

# =========================================================
# DASHBOARD METRICS
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

        round(

            results["Final Score"].max(),

            4
        )
    )

# =========================================================
# RANKINGS TABLE
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

factor_fig = px.scatter(

    results,

    x="Momentum",

    y="Sharpe",

    size="Final Score",

    color="Sector",

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
# DOWNLOAD
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
