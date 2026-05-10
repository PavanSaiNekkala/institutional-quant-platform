# =========================================================
# INSTITUTIONAL QUANT RESEARCH PLATFORM
# FUNDAMENTAL + TECHNICAL + SECTOR RANKING ENGINE
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

st.title("🏛 Institutional Quant Research Platform")

# =========================================================
# CONFIG
# =========================================================

TOP_TOTAL_STOCKS = 500
CACHE_FILE = "ranked_universe.xlsx"

# =========================================================
# SAFE VALUE
# =========================================================

def safe(value, default=0):

    try:

        if value is None:
            return default

        if pd.isna(value):
            return default

        return value

    except Exception:

        return default

# =========================================================
# LOAD RANKED UNIVERSE
# =========================================================

@st.cache_data(ttl=86400)
def load_ranked_universe():

    ranked_file = Path(CACHE_FILE)

    # =====================================================
    # LOAD CACHE
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
    # LOAD STOCK UNIVERSE
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

        # =====================================================
        # LIMIT FOR CLOUD STABILITY
        # =====================================================

        symbols = symbols[:2000]

        ranking_data = []

        progress = st.progress(0)

        status = st.empty()

        total_symbols = len(symbols)

        # =====================================================
        # LOOP THROUGH STOCKS
        # =====================================================

        for idx, symbol in enumerate(symbols):

            try:

                status.text(
                    f"Analyzing {symbol} ({idx+1}/{total_symbols})"
                )

                ticker = yf.Ticker(symbol)

                info = ticker.info

                sector = safe(
                    info.get("sector"),
                    "Unknown"
                )

                market_cap = safe(
                    info.get("marketCap")
                )

                pe_ratio = safe(
                    info.get("trailingPE")
                )

                pb_ratio = safe(
                    info.get("priceToBook")
                )

                roe = safe(
                    info.get("returnOnEquity")
                )

                profit_margin = safe(
                    info.get("profitMargins")
                )

                revenue_growth = safe(
                    info.get("revenueGrowth")
                )

                debt_to_equity = safe(
                    info.get("debtToEquity")
                )

                current_ratio = safe(
                    info.get("currentRatio")
                )

                operating_margin = safe(
                    info.get("operatingMargins")
                )

                dividend_yield = safe(
                    info.get("dividendYield")
                )

                beta = safe(
                    info.get("beta")
                )

                avg_volume = safe(
                    info.get("averageVolume")
                )

                # =================================================
                # PRICE DATA
                # =================================================

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
                # TECHNICAL FACTORS
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

                sma_20 = close.rolling(20).mean().iloc[-1]

                sma_50 = close.rolling(50).mean().iloc[-1]

                trend_strength = (
                    sma_20 / sma_50
                ) if sma_50 != 0 else 0

                # =================================================
                # INSTITUTIONAL SCORE
                # =================================================

                score = (

                    # Fundamental Growth
                    revenue_growth * 0.15

                    +

                    # Profitability
                    profit_margin * 0.15

                    +

                    # ROE
                    roe * 0.15

                    +

                    # Operating Margin
                    operating_margin * 0.10

                    +

                    # Momentum
                    momentum * 0.10

                    +

                    # Sharpe Ratio
                    sharpe * 0.10

                    +

                    # Trend Strength
                    trend_strength * 0.05

                    +

                    # Total Return
                    total_return * 0.05

                    +

                    # Liquidity
                    np.log1p(avg_volume) * 0.05

                    +

                    # Dividend Yield
                    dividend_yield * 0.05

                    -

                    # Volatility Penalty
                    volatility * 0.03

                    -

                    # Debt Penalty
                    debt_to_equity * 0.015

                    -

                    # Beta Penalty
                    beta * 0.015
                )

                # =================================================
                # CLASSIFICATION
                # =================================================

                if score >= 1.0:

                    classification = "INSTITUTIONAL_LONG"

                elif score >= 0.7:

                    classification = "HIGH_CONVICTION"

                elif score >= 0.4:

                    classification = "WATCHLIST"

                else:

                    classification = "AVOID"

                ranking_data.append({

                    "Symbol":
                        symbol,

                    "Sector":
                        sector,

                    "Market Cap":
                        market_cap,

                    "PE Ratio":
                        round(pe_ratio, 2),

                    "PB Ratio":
                        round(pb_ratio, 2),

                    "ROE":
                        round(roe, 4),

                    "Profit Margin":
                        round(profit_margin, 4),

                    "Revenue Growth":
                        round(revenue_growth, 4),

                    "Debt To Equity":
                        round(debt_to_equity, 2),

                    "Current Ratio":
                        round(current_ratio, 2),

                    "Operating Margin":
                        round(operating_margin, 4),

                    "Dividend Yield":
                        round(dividend_yield, 4),

                    "Momentum":
                        round(momentum, 4),

                    "Volatility":
                        round(volatility, 4),

                    "Sharpe":
                        round(sharpe, 4),

                    "Trend Strength":
                        round(trend_strength, 4),

                    "Total Return":
                        round(total_return, 4),

                    "Institutional Score":
                        round(score, 4),

                    "Classification":
                        classification
                })

            except Exception:
                continue

            progress.progress(
                (idx + 1) / total_symbols
            )

        status.text("Institutional Ranking Completed")

        ranking_df = pd.DataFrame(ranking_data)

        if ranking_df.empty:

            return pd.DataFrame()

        # =====================================================
        # FILTER LOW QUALITY STOCKS
        # =====================================================

        ranking_df = ranking_df[
            ranking_df["Market Cap"] > 1_000_000_000
        ]

        # =====================================================
        # SECTOR BALANCING
        # =====================================================

        sectors = ranking_df["Sector"].unique()

        sector_selected = []

        stocks_per_sector = max(
            5,
            TOP_TOTAL_STOCKS // max(1, len(sectors))
        )

        for sector in sectors:

            sector_df = ranking_df[
                ranking_df["Sector"] == sector
            ]

            sector_df = sector_df.sort_values(
                by="Institutional Score",
                ascending=False
            )

            top_sector = sector_df.head(
                stocks_per_sector
            )

            sector_selected.append(top_sector)

        final_df = pd.concat(
            sector_selected,
            ignore_index=True
        )

        # =====================================================
        # FINAL TOP 500
        # =====================================================

        final_df = final_df.sort_values(
            by="Institutional Score",
            ascending=False
        )

        final_df = final_df.head(
            TOP_TOTAL_STOCKS
        )

        final_df = final_df.reset_index(drop=True)

        # =====================================================
        # SAVE CACHE
        # =====================================================

        final_df.to_excel(
            CACHE_FILE,
            index=False
        )

        return final_df

    except Exception as e:

        st.error(f"Universe ranking failed: {e}")

        return pd.DataFrame()

# =========================================================
# LOAD DATA
# =========================================================

ranking_df = load_ranked_universe()

# =========================================================
# SIDEBAR CONTROLS
# =========================================================

st.sidebar.header("Institutional Controls")

top_n = st.sidebar.selectbox(
    "Display Stocks",
    [25, 50, 100, 250, 500],
    index=2
)

watchlist_size = st.sidebar.selectbox(
    "Live Signal Watchlist",
    [10, 25, 50, 75, 100],
    index=2
)

selected_sector = st.sidebar.selectbox(
    "Sector Filter",
    ["ALL"] + sorted(
        ranking_df["Sector"]
        .dropna()
        .unique()
        .tolist()
    ) if not ranking_df.empty else ["ALL"]
)

# =========================================================
# FILTER DISPLAY
# =========================================================

display_df = ranking_df.copy()

if selected_sector != "ALL":

    display_df = display_df[
        display_df["Sector"] == selected_sector
    ]

display_df = display_df.head(top_n)

# =========================================================
# METRICS
# =========================================================

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Ranked Universe",
        len(ranking_df)
    )

with col2:

    st.metric(
        "Sectors",
        ranking_df["Sector"].nunique()
        if not ranking_df.empty else 0
    )

with col3:

    st.metric(
        "Displayed Stocks",
        len(display_df)
    )

with col4:

    st.metric(
        "Top Score",
        round(
            ranking_df["Institutional Score"].max(),
            4
        ) if not ranking_df.empty else 0
    )

# =========================================================
# RANKING TABLE
# =========================================================

st.subheader("Institutional Alpha Rankings")

if not display_df.empty:

    st.dataframe(
        display_df,
        width="stretch",
        height=700
    )

else:

    st.warning("No rankings available")

# =========================================================
# SYMBOLS
# =========================================================

all_symbols = (
    ranking_df["Symbol"].tolist()
    if not ranking_df.empty
    else []
)

symbols = all_symbols[:watchlist_size]

# =========================================================
# EMPTY CHECK
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
# DOWNLOAD
# =========================================================

st.download_button(
    label="Download Ranked Universe",
    data=ranking_df.to_csv(index=False),
    file_name="institutional_rankings.csv",
    mime="text/csv"
)

# =========================================================
# SYSTEM STATUS
# =========================================================

st.success(
    "Institutional Quant Platform Operational"
)
