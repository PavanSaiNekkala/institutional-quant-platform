# =========================================================
# FILE: app/streamlit_app.py
# =========================================================

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import time
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
# CSS
# =========================================================

st.markdown("""
<style>

.stApp{
    background:#F3F4F6;
}

/* ================= SIDEBAR ================= */

section[data-testid="stSidebar"]{
    background:#111827;
    border-right:1px solid #1F2937;
    width:320px !important;
}

section[data-testid="stSidebar"] > div{
    width:320px !important;
}

section[data-testid="stSidebar"] *{
    color:white !important;
}

/* ================= SEARCH BOX ================= */

div[data-baseweb="base-input"] > div{
    background:white !important;
    border:2px solid #2563EB !important;
    border-radius:12px !important;
}

input{
    color:#111827 !important;
    font-weight:700 !important;
}

/* ================= METRICS ================= */

[data-testid="metric-container"]{
    background:white;
    border-radius:18px;
    padding:18px;
    box-shadow:0 4px 14px rgba(0,0,0,0.08);
}

/* ================= TABLE ================= */

[data-testid="stDataFrame"]{
    background:white;
    border-radius:18px;
    padding:10px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================

st.markdown("""
<div style="
    font-size:58px;
    font-weight:900;
    color:#111827;
">
📊 Institutional Quant Platform
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="
    color:#6B7280;
    font-size:20px;
    margin-top:-10px;
">
Executive Institutional Analytics Dashboard
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
        0,
        100,
        60
    )

    search_stock = st.text_input(
        "Search Stock",
        placeholder="Type stock name..."
    )

    if search_stock:

        matches = [
            s for s in stocks
            if search_stock.upper() in s.upper()
        ][:15]

        if matches:

            st.markdown("### 🔍 Matching Stocks")

            for m in matches:

                st.markdown(
                    f"""
                    <div style="
                        background:#1F2937;
                        padding:10px;
                        border-radius:10px;
                        margin-bottom:8px;
                        border-left:4px solid #10B981;
                        font-weight:700;
                    ">
                    {m}
                    </div>
                    """,
                    unsafe_allow_html=True
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
    "WATCH": "#FF8C00",
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

    progress_bar = st.progress(0)

    status_box = st.empty()

    results = []

    failed_stocks = []

    total = len(stock_list)

    completed = 0

    start_time = time.time()

    batch_size = 75

    for i in range(0, total, batch_size):

        batch = stock_list[i:i+batch_size]

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

        except:

            failed_stocks.extend(batch)

            continue

        for symbol in batch:

            completed += 1

            try:

                if symbol not in data.columns.levels[0]:

                    failed_stocks.append(symbol)

                    continue

                close = (
                    data[symbol]["Close"]
                    .dropna()
                )

                if len(close) < 40:

                    failed_stocks.append(symbol)

                    continue

                momentum = (
                    close.iloc[-1]
                    / close.iloc[-20]
                ) - 1

                returns = close.pct_change().dropna()

                sharpe = (
                    returns.mean()
                    / max(returns.std(), 0.0001)
                ) * np.sqrt(252)

                score = (
                    momentum * 0.6
                    + sharpe * 0.4
                )

                if score >= 1.2:
                    signal = "STRONG_BUY"

                elif score >= 0.8:
                    signal = "BUY"

                elif score >= 0.4:
                    signal = "WATCH"

                else:
                    signal = "AVOID"

                results.append({
                    "Symbol": symbol,
                    "CMP": safe_round(close.iloc[-1]),
                    "Momentum": safe_round(momentum * 100),
                    "Sharpe": safe_round(sharpe),
                    "Final Score": safe_round(score),
                    "Classification": signal
                })

            except:

                failed_stocks.append(symbol)

            progress_bar.progress(
                completed / total
            )

            elapsed = (
                time.time() - start_time
            ) / 60

            estimated_total = (
                elapsed / max(completed,1)
            ) * total

            remaining_minutes = round(
                max(
                    estimated_total - elapsed,
                    0
                ),
                1
            )

            completion_pct = round(
                (completed / total) * 100,
                1
            )

            if completed % 10 == 0:

                status_html = f"""
                <div style="
                    background:white;
                    border-radius:24px;
                    padding:30px;
                    box-shadow:0 8px 28px rgba(0,0,0,0.08);
                    margin-top:10px;
                ">

                    <div style="
                        display:flex;
                        justify-content:space-between;
                        align-items:center;
                        margin-bottom:20px;
                    ">

                        <div>

                            <div style="
                                font-size:36px;
                                font-weight:900;
                                color:#111827;
                            ">
                            📊 Institutional Processing Engine
                            </div>

                            <div style="
                                color:#6B7280;
                                font-size:15px;
                                margin-top:4px;
                            ">
                            Real-Time Quant Processing
                            </div>

                        </div>

                        <div style="
                            background:#DBEAFE;
                            color:#1D4ED8;
                            padding:10px 18px;
                            border-radius:12px;
                            font-weight:800;
                        ">
                        LIVE
                        </div>

                    </div>

                    <!-- KPI GRID -->

                    <div style="
                        display:grid;
                        grid-template-columns:repeat(4,1fr);
                        gap:18px;
                    ">

                        <!-- COMPLETED -->

                        <div style="
                            background:#ECFDF5;
                            padding:22px;
                            border-radius:18px;
                            border-left:6px solid #10B981;
                        ">

                            <div style="
                                color:#047857;
                                font-size:14px;
                                font-weight:700;
                            ">
                            COMPLETED
                            </div>

                            <div style="
                                margin-top:10px;
                                font-size:36px;
                                font-weight:900;
                                color:#065F46;
                            ">
                            {completed}
                            </div>

                            <div style="
                                margin-top:4px;
                                color:#10B981;
                                font-size:14px;
                            ">
                            out of {total}
                            </div>

                        </div>

                        <!-- FAILED -->

                        <div style="
                            background:#FEF2F2;
                            padding:22px;
                            border-radius:18px;
                            border-left:6px solid #DC2626;
                        ">

                            <div style="
                                color:#B91C1C;
                                font-size:14px;
                                font-weight:700;
                            ">
                            FAILED
                            </div>

                            <div style="
                                margin-top:10px;
                                font-size:36px;
                                font-weight:900;
                                color:#991B1B;
                            ">
                            {len(set(failed_stocks))}
                            </div>

                            <div style="
                                margin-top:4px;
                                color:#DC2626;
                                font-size:14px;
                            ">
                            failed stocks
                            </div>

                        </div>

                        <!-- UNIVERSE -->

                        <div style="
                            background:#EFF6FF;
                            padding:22px;
                            border-radius:18px;
                            border-left:6px solid #2563EB;
                        ">

                            <div style="
                                color:#1D4ED8;
                                font-size:14px;
                                font-weight:700;
                            ">
                            UNIVERSE
                            </div>

                            <div style="
                                margin-top:10px;
                                font-size:36px;
                                font-weight:900;
                                color:#1E3A8A;
                            ">
                            {total}
                            </div>

                            <div style="
                                margin-top:4px;
                                color:#2563EB;
                                font-size:14px;
                            ">
                            NSE Stocks
                            </div>

                        </div>

                        <!-- ETA -->

                        <div style="
                            background:#FFF7ED;
                            padding:22px;
                            border-radius:18px;
                            border-left:6px solid #F59E0B;
                        ">

                            <div style="
                                color:#D97706;
                                font-size:14px;
                                font-weight:700;
                            ">
                            ETA
                            </div>

                            <div style="
                                margin-top:10px;
                                font-size:36px;
                                font-weight:900;
                                color:#92400E;
                            ">
                            {remaining_minutes}m
                            </div>

                            <div style="
                                margin-top:4px;
                                color:#F59E0B;
                                font-size:14px;
                            ">
                            remaining
                            </div>

                        </div>

                    </div>

                    <!-- PROGRESS -->

                    <div style="margin-top:28px;">

                        <div style="
                            display:flex;
                            justify-content:space-between;
                            margin-bottom:8px;
                        ">

                            <div style="
                                color:#374151;
                                font-weight:700;
                            ">
                            Processing Progress
                            </div>

                            <div style="
                                color:#2563EB;
                                font-weight:800;
                            ">
                            {completion_pct}%
                            </div>

                        </div>

                        <div style="
                            width:100%;
                            height:18px;
                            background:#E5E7EB;
                            border-radius:999px;
                            overflow:hidden;
                        ">

                            <div style="
                                width:{completion_pct}%;
                                height:100%;
                                background:linear-gradient(90deg,#2563EB,#10B981);
                                border-radius:999px;
                            ">
                            </div>

                        </div>

                    </div>

                    <!-- ACTIVE STOCK -->

                    <div style="
                        margin-top:28px;
                        background:#111827;
                        color:white;
                        border-radius:18px;
                        padding:20px;
                        display:flex;
                        justify-content:space-between;
                        align-items:center;
                    ">

                        <div>

                            <div style="
                                color:#9CA3AF;
                                font-size:13px;
                                margin-bottom:6px;
                            ">
                            CURRENTLY ANALYZING
                            </div>

                            <div style="
                                font-size:26px;
                                font-weight:900;
                            ">
                            {symbol}
                            </div>

                        </div>

                        <div style="
                            background:#10B981;
                            padding:10px 18px;
                            border-radius:12px;
                            font-weight:800;
                        ">
                        ACTIVE
                        </div>

                    </div>

                </div>
                """

                status_box.markdown(
                    status_html,
                    unsafe_allow_html=True
                )

    progress_bar.empty()

    return (
        pd.DataFrame(results),
        failed_stocks
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

# =========================================================
# KPIs
# =========================================================

st.markdown("<br>", unsafe_allow_html=True)

k1,k2,k3,k4 = st.columns(4)

with k1:
    st.metric(
        "Universe Size",
        len(results)
    )

with k2:
    st.metric(
        "Average Score",
        safe_round(
            results["Final Score"].mean() * 100
        )
    )

with k3:
    st.metric(
        "Strong Buy",
        len(
            results[
                results["Classification"]
                == "STRONG_BUY"
            ]
        )
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
        height=450
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
        height=450
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# =========================================================
# TABLE
# =========================================================

st.markdown("## 🏦 Institutional Rankings")

st.dataframe(
    results.sort_values(
        "Final Score",
        ascending=False
    ),
    use_container_width=True,
    height=700
)
