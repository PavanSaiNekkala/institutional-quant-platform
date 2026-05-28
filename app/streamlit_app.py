# =========================================================
# FILE: app/streamlit_app.py
# FINAL ENTERPRISE INSTITUTIONAL QUANT DASHBOARD
# =========================================================

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import pytz

from pathlib import Path
from datetime import datetime

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
# GLOBAL CSS
# =========================================================

st.markdown("""
<style>

.stApp{
    background:#F3F4F6;
    font-family:"Segoe UI",sans-serif;
}

.block-container{
    padding-top:1rem;
    padding-bottom:1rem;
    max-width:100%;
}

section[data-testid="stSidebar"]{
    background:#111827;
    border-right:1px solid #1F2937;
}

section[data-testid="stSidebar"] *{
    color:white !important;
}

[data-testid="metric-container"]{
    background:white;
    border-radius:18px;
    padding:14px;
    box-shadow:0 4px 12px rgba(0,0,0,0.08);
}

.element-container:has(.js-plotly-plot){
    background:white;
    border-radius:18px;
    padding:10px;
    box-shadow:0 4px 14px rgba(0,0,0,0.08);
    margin-bottom:16px;
}

[data-testid="stDataFrame"]{
    background:white;
    border-radius:18px;
    padding:10px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div style="
    font-size:42px;
    font-weight:900;
    color:#111827;
">
📊 Institutional Quant Platform
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="
    font-size:16px;
    color:#111827;
    font-weight:700;
    margin-top:6px;
    margin-bottom:12px;
">
Enterprise Institutional Analytics Dashboard
</div>
""", unsafe_allow_html=True)

india = pytz.timezone("Asia/Kolkata")

st.caption(
    f"Updated: {datetime.now(india).strftime('%d-%m-%Y %I:%M:%S %p IST')}"
)

st.markdown("---")

# =========================================================
# LOAD STOCKS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

excel_path = (
    ROOT_DIR /
    "data" /
    "valid_stocks.xlsx"
)

universe_df = pd.read_excel(excel_path)

stocks = (
    universe_df.iloc[:,0]
    .dropna()
    .astype(str)
    .str.upper()
    .tolist()
)

stocks = [s for s in stocks if ".NS" in s]

stocks = list(dict.fromkeys(stocks))

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## ⚙️ Dashboard Controls")

    st.markdown("---")

    signal_filter = st.multiselect(
        "📈 Trade Signal Filter",
        options=[
            "STRONG_BUY",
            "BUY",
            "WATCH",
            "HOLD",
            "AVOID"
        ]
    )

    min_score = st.slider(
        "Minimum Institutional Score",
        0,
        100,
        60
    )

    search_stock = st.text_input(
        "Search Stock",
        placeholder="Type stock name..."
    )

    st.markdown("---")

    st.success(
        f"✅ NSE Universe Loaded: {len(stocks)}"
    )

# =========================================================
# COLORS
# =========================================================

signal_colors = {
    "STRONG_BUY": "#006400",
    "BUY": "#32CD32",
    "WATCH": "#F59E0B",
    "HOLD": "#3B82F6",
    "AVOID": "#DC2626"
}

# =========================================================
# SAFE ROUND
# =========================================================

def safe_round(x, n=2):

    try:
        return round(float(x), n)

    except:
        return 0

# =========================================================
# ANALYSIS ENGINE
# =========================================================

@st.cache_data(ttl=3600, show_spinner=False)
def run_analysis(stock_list):

    results = []

    failed_stocks = set()

    total = len(stock_list)

    completed = 0

    batch_size = 50

    status_placeholder = st.empty()

    status_placeholder.info(
        "⚡ Running institutional analysis..."
    )

    for i in range(0, total, batch_size):

        batch = stock_list[i:i + batch_size]

        try:

            data = yf.download(
                tickers=batch,
                period="6mo",
                interval="1d",
                auto_adjust=True,
                progress=False,
                threads=False,
                group_by="ticker"
            )

        except Exception:

            failed_stocks.update(batch)

            continue

        for symbol in batch:

            completed += 1

            try:

                if symbol not in data.columns.levels[0]:

                    failed_stocks.add(symbol)

                    continue

                close = data[symbol]["Close"].dropna()

                high = data[symbol]["High"].dropna()

                low = data[symbol]["Low"].dropna()

                if len(close) < 40:

                    failed_stocks.add(symbol)

                    continue

                returns = close.pct_change().dropna()

                momentum = (
                    close.iloc[-1]
                    /
                    close.iloc[-20]
                ) - 1

                sharpe = (
                    returns.mean()
                    /
                    max(returns.std(), 0.0001)
                ) * np.sqrt(252)

                # =====================================================
                # ATR
                # =====================================================

                tr1 = high - low

                tr2 = abs(
                    high - close.shift(1)
                )

                tr3 = abs(
                    low - close.shift(1)
                )

                tr = pd.concat(
                    [tr1, tr2, tr3],
                    axis=1
                ).max(axis=1)

                atr = tr.rolling(14).mean().iloc[-1]

                if pd.isna(atr) or atr <= 0:

                    atr = close.iloc[-1] * 0.02

                # =====================================================
                # SCORE
                # =====================================================

                score = (
                    momentum * 0.6
                    +
                    sharpe * 0.4
                )

                # =====================================================
                # SIGNAL
                # =====================================================

                if score >= 1.5:

                    signal = "STRONG_BUY"

                elif score >= 1.0:

                    signal = "BUY"

                elif score >= 0.6:

                    signal = "WATCH"

                elif score >= 0.2:

                    signal = "HOLD"

                else:

                    signal = "AVOID"

                # =====================================================
                # PRICE
                # =====================================================

                cmp_price = close.iloc[-1]

                # =====================================================
                # STOPLOSS
                # =====================================================

                stop_loss = round(
                    cmp_price - (atr * 2),
                    2
                )

                # =====================================================
                # TARGET
                # =====================================================

                target = round(
                    cmp_price + (atr * 3),
                    2
                )

                # =====================================================
                # RR RATIO
                # =====================================================

                risk = max(
                    cmp_price - stop_loss,
                    1
                )

                reward = max(
                    target - cmp_price,
                    0
                )

                rr_ratio = round(
                    reward / risk,
                    2
                )

                # =====================================================
                # ESTIMATED DAYS
                # =====================================================

                expected_daily_move = atr * 0.6

                estimated_days = round(

                    max(
                        1,
                        reward /
                        max(expected_daily_move, 1)
                    )

                )

                # =====================================================
                # UPSIDE / DOWNSIDE
                # =====================================================

                upside_pct = round(
                    (
                        (
                            target - cmp_price
                        )
                        /
                        cmp_price
                    ) * 100,
                    2
                )

                downside_pct = round(
                    (
                        (
                            cmp_price - stop_loss
                        )
                        /
                        cmp_price
                    ) * 100,
                    2
                )

                # =====================================================
                # TRADE QUALITY
                # =====================================================

                if rr_ratio >= 3:

                    trade_quality = "EXCELLENT"

                elif rr_ratio >= 2:

                    trade_quality = "STRONG"

                elif rr_ratio >= 1:

                    trade_quality = "MODERATE"

                else:

                    trade_quality = "WEAK"

                # =====================================================
                # APPEND
                # =====================================================

                results.append({

                    "Symbol": symbol,

                    "CMP": round(cmp_price, 2),

                    "Momentum": round(
                        momentum * 100,
                        2
                    ),

                    "Sharpe": round(
                        sharpe,
                        2
                    ),

                    "Final Score": round(
                        score,
                        2
                    ),

                    "Classification": signal,

                    "ATR": round(
                        atr,
                        2
                    ),

                    "STOP_LOSS": stop_loss,

                    "TARGET": target,

                    "UPSIDE_%": upside_pct,

                    "DOWNSIDE_%": downside_pct,

                    "RR_RATIO": rr_ratio,

                    "ESTIMATED_DAYS": estimated_days,

                    "TRADE_QUALITY": trade_quality

                })

            except Exception:

                failed_stocks.add(symbol)

        completion_pct = round(
            (completed / total) * 100,
            1
        )

        status_placeholder.caption(
            f"Processed {completed}/{total} stocks "
            f"({completion_pct}%)"
        )

    status_placeholder.success(
        "✅ Institutional analysis completed"
    )

    return (
        pd.DataFrame(results),
        list(failed_stocks)
    )

# =========================================================
# RUN ANALYSIS
# =========================================================

results, failed_stocks = run_analysis(stocks)

if results.empty:

    st.error("No valid results.")

    st.stop()

# =========================================================
# FILTERS
# =========================================================

results["Percentile"] = (
    results["Final Score"] * 100
)

results = results[
    results["Percentile"] >= min_score
]

if signal_filter:

    results = results[
        results["Classification"]
        .isin(signal_filter)
    ]

if search_stock:

    results = results[
        results["Symbol"]
        .str.contains(
            search_stock.upper(),
            na=False
        )
    ]

# =========================================================
# KPI CARDS
# =========================================================

st.markdown("<br>", unsafe_allow_html=True)

k1,k2,k3,k4 = st.columns(4)

with k1:

    st.metric(
        "NSE Universe",
        len(stocks)
    )

with k2:

    st.metric(
        "Processed Stocks",
        len(results)
    )

with k3:

    st.metric(
        "Filtered Opportunities",
        len(results)
    )

with k4:

    st.metric(
        "Failed Stocks",
        len(set(failed_stocks))
    )

# =========================================================
# CHARTS
# =========================================================

left,right = st.columns(2)

with left:

    signal_data = (
        results["Classification"]
        .value_counts()
        .reset_index()
    )

    signal_data.columns = [
        "Signal",
        "Count"
    ]

    fig1 = px.pie(
        signal_data,
        names="Signal",
        values="Count",
        hole=0.6,
        color="Signal",
        color_discrete_map=signal_colors,
        title="Signal Distribution"
    )

    fig1.update_layout(
        height=400
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

with right:

    fig2 = px.scatter(
        results,
        x="Momentum",
        y="Sharpe",
        color="Classification",
        size="Final Score",
        hover_name="Symbol",
        color_discrete_map=signal_colors,
        title="Risk Reward Opportunity Matrix"
    )

    fig2.update_layout(
        height=400
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# =========================================================
# TABLE
# =========================================================

st.markdown("## 🏦 Institutional Rankings")

display_cols = [

    "Symbol",

    "CMP",

    "Classification",

    "Momentum",

    "Sharpe",

    "Final Score",

    "ATR",

    "STOP_LOSS",

    "TARGET",

    "UPSIDE_%",

    "DOWNSIDE_%",

    "RR_RATIO",

    "ESTIMATED_DAYS",

    "TRADE_QUALITY"

]

available_cols = [

    c for c in display_cols

    if c in results.columns

]

st.dataframe(

    results[available_cols]

    .sort_values(
        "Final Score",
        ascending=False
    ),

    use_container_width=True,

    height=650

)
