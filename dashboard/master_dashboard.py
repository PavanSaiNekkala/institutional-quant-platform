import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf

from signals.live_signals import (
    generate_live_signal
)

from portfolio.live_monitor import (
    live_portfolio_report
)

from monitoring.alerts import (
    AlertManager
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

    "Institutional Quantitative Intelligence Platform"
)

# =========================================================
# LOAD & RANK STOCK UNIVERSE
# =========================================================

@st.cache_data(ttl=3600)
def load_ranked_universe():

    ranked_file = Path(

        "ranked_universe.xlsx"
    )

    # =====================================================
    # LOAD PRECOMPUTED RANKINGS
    # =====================================================

    if ranked_file.exists():

        try:

            ranking_df = pd.read_excel(

                ranked_file
            )

            return ranking_df

        except Exception:

            pass

    # =====================================================
    # GENERATE NEW RANKINGS
    # =====================================================

    try:

        universe = pd.read_excel(

            "valid_stocks.xlsx"
        )

        symbols = (

            universe.iloc[:, 0]

            .dropna()

            .astype(str)

            .unique()

            .tolist()
        )

        ranking_data = []

        progress = st.progress(0)

        status = st.empty()

        total_symbols = len(symbols)

        for idx, symbol in enumerate(symbols):

            try:

                status.text(

                    f"Ranking {symbol} ({idx+1}/{total_symbols})"
                )

                data = yf.download(

                    symbol,

                    period="3mo",

                    progress=False,

                    auto_adjust=True,

                    threads=True
                )

                if data.empty:

                    continue

                close = data["Close"]

                if isinstance(close, pd.DataFrame):

                    close = close.iloc[:, 0]

                close = close.dropna()

                if len(close) < 40:

                    continue

                returns = close.pct_change().dropna()

                if returns.empty:

                    continue

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

                sharpe = (

                    returns.mean()

                    / returns.std()

                ) * np.sqrt(252)

                total_return = (

                    close.iloc[-1]

                    / close.iloc[0]

                ) - 1

                avg_volume = (

                    data["Volume"]

                    .tail(20)

                    .mean()
                )

                # =================================================
                # INSTITUTIONAL SCORE
                # =================================================

                score = (

                    momentum * 0.30

                    + sharpe * 0.30

                    + total_return * 0.20

                    - volatility * 0.10

                    + np.log1p(avg_volume) * 0.10
                )

                ranking_data.append({

                    "Symbol":

                        symbol,

                    "Momentum":

                        round(momentum, 4),

                    "Volatility":

                        round(volatility, 4),

                    "Sharpe":

                        round(sharpe, 4),

                    "Total Return":

                        round(total_return, 4),

                    "Avg Volume":

                        round(avg_volume, 0),

                    "Institutional Score":

                        round(score, 4)
                })

            except Exception:

                continue

            progress.progress(

                (idx + 1) / total_symbols
            )

        status.text(

            "Institutional ranking completed"
        )

        ranking_df = pd.DataFrame(

            ranking_data
        )

        if ranking_df.empty:

            return pd.DataFrame()

        ranking_df = ranking_df.sort_values(

            by="Institutional Score",

            ascending=False
        )

        ranking_df = ranking_df.reset_index(

            drop=True
        )

        # =====================================================
        # SAVE RANKINGS
        # =====================================================

        ranking_df.to_excel(

            "ranked_universe.xlsx",

            index=False
        )

        return ranking_df

    except Exception as e:

        st.error(

            f"Universe ranking failed: {e}"
        )

        return pd.DataFrame()

# =========================================================
# LOAD RANKINGS
# =========================================================

ranking_df = load_ranked_universe()

# =========================================================
# DEBUG OUTPUT
# =========================================================

st.write(

    f"Ranked Stocks Loaded: {len(ranking_df)}"
)

# =========================================================
# RANKING ENGINE DISPLAY
# =========================================================

st.subheader(

    "Institutional Ranking Engine"
)

if not ranking_df.empty:

    st.dataframe(

        ranking_df.head(100),

        use_container_width=True,

        height=500
    )

# =========================================================
# TOP 1000 WATCHLIST
# =========================================================

all_symbols = (

    ranking_df["Symbol"]

    .head(1000)

    .tolist()

    if not ranking_df.empty

    else [

        "RELIANCE.NS",
        "TCS.NS",
        "INFY.NS",
        "HDFCBANK.NS"
    ]
)

# =========================================================
# EMPTY PROTECTION
# =========================================================

if len(all_symbols) == 0:

    st.error(

        "No ranked stocks available"
    )

    st.stop()

# =========================================================
# SIDEBAR CONTROLS
# =========================================================

st.sidebar.header(

    "Institutional Controls"
)

# =========================================================
# SAFE WATCHLIST
# =========================================================

max_watchlist = max(

    1,

    min(300, len(all_symbols))
)

default_watchlist = min(

    100,

    max_watchlist
)

min_watchlist = 1

watchlist_size = st.sidebar.slider(

    "Live Signal Watchlist",

    min_value=min_watchlist,

    max_value=max_watchlist,

    value=default_watchlist,

    step=1
)

# =========================================================
# SAFE OFFSET
# =========================================================

max_offset = max(

    0,

    len(all_symbols) - watchlist_size
)

offset = st.sidebar.number_input(

    "Universe Offset",

    min_value=0,

    max_value=max_offset,

    value=0,

    step=1
)

symbols = all_symbols[
    offset : offset + watchlist_size
]

# =========================================================
# EQUAL WEIGHTS
# =========================================================

weights = np.array(

    [1 / len(symbols)]

    * len(symbols)
)

# =========================================================
# SIGNAL CACHE
# =========================================================

@st.cache_data(ttl=3600)
def cached_signal(symbol):

    return generate_live_signal(symbol)

# =========================================================
# LIVE SIGNALS
# =========================================================

st.subheader(

    "Live AI Signals"
)

signal_reports = []

signal_progress = st.progress(0)

signal_status = st.empty()

# =========================================================
# LIMIT LIVE SIGNALS FOR STABILITY
# =========================================================

live_signal_symbols = symbols[:100]

for idx, symbol in enumerate(live_signal_symbols):

    try:

        signal_status.text(

            f"Generating signal for {symbol} ({idx+1}/{len(live_signal_symbols)})"
        )

        report = cached_signal(symbol)

        signal_reports.append(report)

    except Exception as e:

        st.warning(

            f"Signal error for {symbol}: {e}"
        )

    signal_progress.progress(

        (idx + 1) / len(live_signal_symbols)
    )

signal_status.text(

    "Signal generation completed"
)

signal_df = pd.DataFrame(

    signal_reports
)

# =========================================================
# SIGNAL TABLE
# =========================================================

if not signal_df.empty:

    st.dataframe(

        signal_df,

        use_container_width=True,

        height=600
    )

else:

    st.warning(

        "No signals generated"
    )

# =========================================================
# SIGNAL VISUALIZATION
# =========================================================

st.subheader(

    "Signal Score Distribution"
)

if not signal_df.empty:

    fig = go.Figure()

    fig.add_trace(

        go.Bar(

            x=signal_df["Symbol"],

            y=signal_df["Signal Score"]
        )
    )

    fig.update_layout(

        xaxis_title="Symbol",

        yaxis_title="Signal Score",

        height=600
    )

    st.plotly_chart(

        fig,

        use_container_width=True
    )

# =========================================================
# TOP SIGNALS
# =========================================================

st.subheader(

    "Top Institutional Signals"
)

if not signal_df.empty:

    top_signals = signal_df.sort_values(

        by="Signal Score",

        ascending=False
    ).head(25)

    st.dataframe(

        top_signals,

        use_container_width=True
    )

# =========================================================
# PORTFOLIO MONITOR
# =========================================================

st.subheader(

    "Live Portfolio Analytics"
)

try:

    portfolio = live_portfolio_report(

        symbols,

        weights
    )

    portfolio_df = pd.DataFrame({

        "Metric":

            portfolio.keys(),

        "Value":

            portfolio.values()
    })

    st.dataframe(

        portfolio_df,

        use_container_width=True
    )

except Exception as e:

    st.error(

        f"Portfolio monitor failed: {e}"
    )

# =========================================================
# ALERTS
# =========================================================

st.subheader(

    "Institutional Alerts"
)

alerts = AlertManager()

alerts.risk_alert(

    drawdown=-0.12
)

alerts.volatility_alert(

    volatility=0.35
)

alerts.signal_alert(

    symbol="RELIANCE.NS",

    decision="BUY"
)

alert_df = pd.DataFrame(

    alerts.get_alerts()
)

st.dataframe(

    alert_df,

    use_container_width=True
)

# =========================================================
# DASHBOARD METRICS
# =========================================================

st.subheader(

    "Platform Statistics"
)

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(

        "Ranked Universe",

        len(all_symbols)
    )

with col2:

    st.metric(

        "Watchlist",

        len(symbols)
    )

with col3:

    st.metric(

        "Signals Generated",

        len(signal_df)
    )

with col4:

    st.metric(

        "Top Signal",

        round(

            signal_df["Signal Score"].max(),

            4
        ) if not signal_df.empty else 0
    )

# =========================================================
# SYSTEM HEALTH
# =========================================================

st.success(

    "Institutional Quant Platform Operational"
)