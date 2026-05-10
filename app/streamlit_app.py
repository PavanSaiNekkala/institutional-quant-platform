# =========================================================
# FILE: app/streamlit_app.py
# FINAL INSTITUTIONAL QUANT PLATFORM
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

regime = detect_market_regime()

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

    # =====================================================
    # NSE FILTER
    # =====================================================

    stocks = [

        stock for stock in stocks

        if ".NS" in stock
    ]

    # =====================================================
    # REMOVE DUPLICATES
    # =====================================================

    stocks = list(

        dict.fromkeys(stocks)
    )

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
# MAIN ENGINE
# =========================================================

ranking_data = []

progress = st.progress(0)

status = st.empty()

# =========================================================
# STOCK LOOP
# =========================================================

for idx, symbol in enumerate(stocks):

    try:

        status.text(

            f"Analyzing {symbol} "
            f"({idx+1}/{len(stocks)})"
        )

        ticker = yf.Ticker(symbol)

        info = ticker.info

        # =================================================
        # FUNDAMENTALS
        # =================================================

        sector = info.get(

            "sector",

            "Unknown"
        )

        market_cap = info.get(

            "marketCap",

            0
        )

        revenue_growth = info.get(

            "revenueGrowth",

            0
        )

        profit_margin = info.get(

            "profitMargins",

            0
        )

        roe = info.get(

            "returnOnEquity",

            0
        )

        operating_margin = info.get(

            "operatingMargins",

            0
        )

        debt_to_equity = info.get(

            "debtToEquity",

            0
        )

        dividend_yield = info.get(

            "dividendYield",

            0
        )

        # =================================================
        # FILTER LOW QUALITY STOCKS
        # =================================================

        if market_cap < 1_000_000_000:

            continue

        # =================================================
        # PRICE DATA
        # =================================================

        data = yf.download(

            symbol,

            period="6mo",

            progress=False,

            auto_adjust=True
        )

        if data.empty:

            continue

        close = data["Close"].dropna()

        if len(close) < 50:

            continue

        returns = close.pct_change().dropna()

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
        # REGIME ADAPTIVE WEIGHTS
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
        # FACTOR METRICS
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
        # SECTOR ADAPTIVE SCORE
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

        percentile = (

            final_score * 100
        )

        # =================================================
        # APPEND
        # =================================================

        ranking_data.append({

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
        })

    except Exception:
        continue

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
# FOOTER
# =========================================================

st.markdown("---")

st.caption(

    "Institutional Quantamental Intelligence Platform"
)