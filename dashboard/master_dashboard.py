# =========================================================
# INSTITUTIONAL QUANT RESEARCH PLATFORM
# OPTIMIZED STREAMLIT VERSION
# =========================================================

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf

from signals.live_signals import generate_live_signal
from portfolio.live_monitor import live_portfolio_report
from monitoring.alerts import AlertManager

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Institutional Quant Research Platform",
    layout="wide"
)

# =========================================================
# TITLE
# =========================================================

st.title("🏛 Institutional Quant Research Platform")

# =========================================================
# LOAD RANKED UNIVERSE
# =========================================================

@st.cache_data(ttl=86400)
def load_ranked_universe():

    ranked_file = Path("ranked_universe.xlsx")

    # =====================================================
    # LOAD PRECOMPUTED RANKINGS
    # =====================================================

    if ranked_file.exists():

        try:

            ranking_df = pd.read_excel(ranked_file)

            ranking_df = ranking_df.sort_values(
                by="Institutional Score",
                ascending=False
            )

            ranking_df = ranking_df.reset_index(drop=True)

            return ranking_df

        except Exception as e:

            st.warning(f"Cached ranking load failed: {e}")

    # =====================================================
    # GENERATE NEW RANKINGS
    # =====================================================

    try:

        universe = pd.read_excel("valid_stocks.xlsx")

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

        # =====================================================
        # LIMIT FOR CLOUD STABILITY
        # =====================================================

        symbols = symbols[:500]

        for idx, symbol in enumerate(symbols):

            try:

                status.text(
                    f"Ranking {symbol} ({idx+1}/{len(symbols)})"
                )

                data = yf.download(
                    symbol,
                    period="6mo",
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
                    close.iloc[-1] / close.iloc[-20]
                ) - 1

                volatility = (
                    returns.std() * np.sqrt(252)
                )

                sharpe = (
                    returns.mean() / returns.std()
                ) * np.sqrt(252)

                total_return = (
                    close.iloc[-1] / close.iloc[0]
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
                (idx + 1) / len(symbols)
            )

        status.text("Ranking Completed")

        ranking_df = pd.DataFrame(ranking_data)

        if ranking_df.empty:
            return pd.DataFrame()

        ranking_df = ranking_df.sort_values(
            by="Institutional Score",
            ascending=False
        )

        ranking_df = ranking_df.reset_index(drop=True)

        # =====================================================
        # SAVE CACHE
        # =====================================================

        ranking_df.to_excel(
            "ranked_universe.xlsx",
            index=False
        )

        return ranking_df

    except Exception as e:

        st.error(f"Universe ranking failed: {e}")

        return pd.DataFrame()

# =========================================================
# LOAD DATA
# =========================================================

ranking_df = load_ranked_universe()

# =========================================================
# DEBUG INFO
# =========================================================

st.write(f"Total Ranked Stocks: {len(ranking_df)}")

# =========================================================
# SIDEBAR CONTROLS
# =========================================================

st.sidebar.header("Institutional Controls")

# =========================================================
# TOP STOCK DISPLAY
# =========================================================

top_n = st.sidebar.selectbox(
    "Top Stocks",
    [10, 25, 50, 100, 250, 500],
    index=3
)

# =========================================================
# WATCHLIST SIZE
# =========================================================

watchlist_size = st.sidebar.selectbox(
    "Live Signal Watchlist",
    [10, 25, 50, 75, 100],
    index=2
)

# =========================================================
# OFFSET
# =========================================================

max_offset = max(
    0,
    len(ranking_df) - watchlist_size
)

offset = st.sidebar.number_input(
    "Universe Offset",
    min_value=0,
    max_value=max_offset,
    value=0,
    step=1
)

# =========================================================
# DISPLAY RANKINGS
# =========================================================

st.subheader("Institutional Alpha Rankings")

if not ranking_df.empty:

    display_df = ranking_df.head(top_n)

    st.dataframe(
        display_df,
        width="stretch",
        height=700
    )

else:

    st.warning("No rankings available")

# =========================================================
# SYMBOL UNIVERSE
# =========================================================

all_symbols = (
    ranking_df["Symbol"]
    .tolist()
    if not ranking_df.empty
    else [
        "RELIANCE.NS",
        "TCS.NS",
        "INFY.NS",
        "HDFCBANK.NS"
    ]
)

symbols = all_symbols[
    offset : offset + watchlist_size
]

# =========================================================
# EMPTY PROTECTION
# =========================================================

if len(symbols) == 0:

    st.error("No symbols available")

    st.stop()

# =========================================================
# EQUAL WEIGHTS
# =========================================================

weights = np.array(
    [1 / len(symbols)] * len(symbols)
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

st.subheader("Live AI Signals")

signal_reports = []

signal_progress = st.progress(0)

signal_status = st.empty()

# =========================================================
# STABILITY LIMIT
# =========================================================

live_signal_symbols = symbols[:50]

for idx, symbol in enumerate(live_signal_symbols):

    try:

        signal_status.text(
            f"Generating Signal: {symbol}"
        )

        report = cached_signal(symbol)

        signal_reports.append(report)

    except Exception as e:

        st.warning(f"Signal Error {symbol}: {e}")

    signal_progress.progress(
        (idx + 1) / len(live_signal_symbols)
    )

signal_status.text("Signal Generation Completed")

signal_df = pd.DataFrame(signal_reports)

# =========================================================
# SIGNAL TABLE
# =========================================================

if not signal_df.empty:

    st.dataframe(
        signal_df,
        width="stretch",
        height=600
    )

else:

    st.warning("No signals generated")

# =========================================================
# SIGNAL VISUALIZATION
# =========================================================

st.subheader("Signal Score Distribution")

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
        width="stretch"
    )

# =========================================================
# TOP SIGNALS
# =========================================================

st.subheader("Top Institutional Signals")

if not signal_df.empty:

    top_signals = signal_df.sort_values(
        by="Signal Score",
        ascending=False
    ).head(25)

    st.dataframe(
        top_signals,
        width="stretch"
    )

# =========================================================
# PORTFOLIO ANALYTICS
# =========================================================

st.subheader("Live Portfolio Analytics")

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
        width="stretch"
    )

except Exception as e:

    st.error(f"Portfolio Monitor Failed: {e}")

# =========================================================
# ALERTS
# =========================================================

st.subheader("Institutional Alerts")

alerts = AlertManager()

alerts.risk_alert(drawdown=-0.12)

alerts.volatility_alert(volatility=0.35)

alerts.signal_alert(
    symbol="RELIANCE.NS",
    decision="BUY"
)

alert_df = pd.DataFrame(
    alerts.get_alerts()
)

st.dataframe(
    alert_df,
    width="stretch"
)

# =========================================================
# DASHBOARD METRICS
# =========================================================

st.subheader("Platform Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Ranked Universe",
        len(ranking_df)
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
# SYSTEM STATUS
# =========================================================

st.success(
    "Institutional Quant Platform Operational"
)
