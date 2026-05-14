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
import time

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
    padding-bottom:2rem;
    max-width:100%;
}

section[data-testid="stSidebar"]{
    background:#111827;
    border-right:1px solid #1F2937;
}

section[data-testid="stSidebar"] *{
    color:white !important;
}

div[data-baseweb="base-input"]{
    background:white !important;
    border-radius:12px !important;
}

div[data-baseweb="base-input"] > div{
    background:white !important;
    border:2px solid #2563EB !important;
    border-radius:12px !important;
    min-height:52px !important;
}

input[type="text"]{
    color:#111827 !important;
    background:white !important;
    font-size:18px !important;
    font-weight:700 !important;
    -webkit-text-fill-color:#111827 !important;
}

input[type="text"]::placeholder{
    color:#6B7280 !important;
    opacity:1 !important;
}

div[data-baseweb="select"] > div{
    background:#1F2937 !important;
    border-radius:12px !important;
}

[data-baseweb="tag"]{
    background:#2563EB !important;
    color:white !important;
}

[data-testid="metric-container"]{
    background:white;
    border-radius:18px;
    padding:18px;
    box-shadow:0 6px 20px rgba(0,0,0,0.08);
}

.element-container:has(.js-plotly-plot){
    background:white;
    border-radius:18px;
    padding:12px;
    box-shadow:0 6px 20px rgba(0,0,0,0.08);
    margin-bottom:18px;
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

india = pytz.timezone("Asia/Kolkata")

st.markdown(f"""
<div style="
    background:
    linear-gradient(
        135deg,
        #0F172A,
        #111827
    );
    border-radius:24px;
    padding:24px;
    margin-bottom:18px;
    box-shadow:0 10px 28px rgba(0,0,0,0.18);
">

    <div style="
        display:flex;
        justify-content:space-between;
        align-items:center;
        flex-wrap:wrap;
    ">

        <div>

            <div style="
                font-size:42px;
                font-weight:900;
                color:white;
            ">
                📊 Institutional Quant Platform
            </div>

            <div style="
                color:#CBD5E1;
                margin-top:6px;
                font-size:16px;
            ">
                Enterprise Institutional Analytics Dashboard
            </div>

            <div style="
                color:#94A3B8;
                margin-top:10px;
                font-size:12px;
                font-weight:700;
            ">
                Updated:
                {datetime.now(india).strftime('%d-%m-%Y %I:%M:%S %p IST')}
            </div>

        </div>

        <div style="
            background:#10B981;
            color:white;
            padding:10px 18px;
            border-radius:12px;
            font-weight:900;
            font-size:13px;
        ">
            LIVE NSE ENGINE
        </div>

    </div>

</div>
""", unsafe_allow_html=True)

# =========================================================
# LOAD STOCKS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

excel_path = ROOT_DIR / "data" / "valid_stocks.xlsx"

universe_df = pd.read_excel(excel_path)

stocks = (
    universe_df.iloc[:, 0]
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

    st.markdown("""
    <div style="
        font-size:32px;
        font-weight:900;
        margin-bottom:12px;
    ">
        ⚙️ Dashboard Controls
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    signal_filter = st.multiselect(
        "📈 Trade Signal Filter",
        [
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

    if search_stock:

        matches = [
            s for s in stocks
            if search_stock.upper() in s.upper()
        ][:10]

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
# INFO
# =========================================================

st.info(
    "⚡ Running institutional analysis across full NSE universe..."
)

# =========================================================
# ANALYSIS ENGINE
# =========================================================

@st.cache_data(ttl=3600, show_spinner=False)
def run_analysis(stock_list):

    progress_bar = st.progress(0)

    status_placeholder = st.empty()

    results = []

    failed_stocks = []

    total = len(stock_list)

    completed = 0

    start_time = time.time()

    batch_size = 25

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

        except:

            failed_stocks.extend(batch)
            continue

        for symbol in batch:

            completed += 1

            try:

                if symbol not in data.columns.levels[0]:

                    failed_stocks.append(symbol)
                    continue

                close = data[symbol]["Close"].dropna()

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

                # =====================================================
                # SIGNAL CLASSIFICATION
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
                # EXPECTED RETURNS MODEL
                # =====================================================

                volatility = returns.std() * np.sqrt(252)

                base_strength = (
                    momentum * 100
                    + sharpe * 10
                    + score * 15
                )

                expected_5d = max(
                    min(base_strength * 0.12, 12),
                    -8
                )

                expected_15d = max(
                    min(base_strength * 0.22, 22),
                    -15
                )

                expected_30d = max(
                    min(base_strength * 0.35, 35),
                    -25
                )

                if signal == "STRONG_BUY":

                    hold_days = 30

                elif signal == "BUY":

                    hold_days = 20

                elif signal == "WATCH":

                    hold_days = 10

                elif signal == "HOLD":

                    hold_days = 5

                else:

                    hold_days = 2

                if volatility > 0.60:

                    expected_5d *= 0.7
                    expected_15d *= 0.7
                    expected_30d *= 0.7

                # =====================================================
                # APPEND
                # =====================================================

                results.append({

                    "Symbol": symbol,

                    "CMP": safe_round(close.iloc[-1]),

                    "Momentum": safe_round(momentum * 100),

                    "Sharpe": safe_round(sharpe),

                    "Final Score": safe_round(score),

                    "Classification": signal,

                    "Expected Return 5D %":
                    safe_round(expected_5d),

                    "Expected Return 15D %":
                    safe_round(expected_15d),

                    "Expected Return 30D %":
                    safe_round(expected_30d),

                    "Suggested Hold Days":
                    hold_days

                })

            except:

                failed_stocks.append(symbol)

            # =====================================================
            # PROGRESS
            # =====================================================

            completion_pct = round(
                (completed / total) * 100,
                1
            )

            elapsed = (
                time.time() - start_time
            ) / 60

            estimated_total = (
                elapsed / max(completed, 1)
            ) * total

            remaining_minutes = round(
                max(estimated_total - elapsed, 0),
                1
            )

            progress_bar.progress(
                completed / total
            )

            if completed % 10 == 0:

                status_html = f"""
                <div style="
                    background:white;
                    border-radius:22px;
                    padding:22px;
                    margin-top:14px;
                    box-shadow:0 10px 28px rgba(0,0,0,0.08);
                ">

                    <div style="
                        display:grid;
                        grid-template-columns:
                        repeat(auto-fit,minmax(180px,1fr));
                        gap:14px;
                        margin-bottom:18px;
                    ">

                        <div style="
                            background:#ECFDF5;
                            border-left:6px solid #10B981;
                            border-radius:16px;
                            padding:16px;
                        ">

                            <div style="
                                color:#047857;
                                font-size:12px;
                                font-weight:800;
                            ">
                                COMPLETED
                            </div>

                            <div style="
                                font-size:28px;
                                font-weight:900;
                                color:#065F46;
                                margin-top:6px;
                            ">
                                {completed}
                            </div>

                        </div>

                        <div style="
                            background:#FEF2F2;
                            border-left:6px solid #DC2626;
                            border-radius:16px;
                            padding:16px;
                        ">

                            <div style="
                                color:#B91C1C;
                                font-size:12px;
                                font-weight:800;
                            ">
                                FAILED
                            </div>

                            <div style="
                                font-size:28px;
                                font-weight:900;
                                color:#991B1B;
                                margin-top:6px;
                            ">
                                {len(set(failed_stocks))}
                            </div>

                        </div>

                        <div style="
                            background:#EFF6FF;
                            border-left:6px solid #2563EB;
                            border-radius:16px;
                            padding:16px;
                        ">

                            <div style="
                                color:#1D4ED8;
                                font-size:12px;
                                font-weight:800;
                            ">
                                UNIVERSE
                            </div>

                            <div style="
                                font-size:28px;
                                font-weight:900;
                                color:#1E3A8A;
                                margin-top:6px;
                            ">
                                {total}
                            </div>

                        </div>

                        <div style="
                            background:#FFF7ED;
                            border-left:6px solid #F59E0B;
                            border-radius:16px;
                            padding:16px;
                        ">

                            <div style="
                                color:#D97706;
                                font-size:12px;
                                font-weight:800;
                            ">
                                ETA
                            </div>

                            <div style="
                                font-size:28px;
                                font-weight:900;
                                color:#92400E;
                                margin-top:6px;
                            ">
                                {remaining_minutes}m
                            </div>

                        </div>

                    </div>

                    <div style="
                        width:100%;
                        height:12px;
                        background:#E5E7EB;
                        border-radius:999px;
                        overflow:hidden;
                    ">

                        <div style="
                            width:{completion_pct}%;
                            height:100%;
                            background:
                            linear-gradient(
                                90deg,
                                #2563EB,
                                #10B981
                            );
                        ">
                        </div>

                    </div>

                </div>
                """

                status_placeholder.markdown(
                    status_html,
                    unsafe_allow_html=True
                )

    progress_bar.empty()

    status_placeholder.empty()

    return pd.DataFrame(results), failed_stocks

# =========================================================
# RUN ANALYSIS
# =========================================================

results, failed_stocks = run_analysis(stocks)

if results.empty:

    st.error("No valid results generated.")
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
# KPI SECTION
# =========================================================

st.markdown("<br>", unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric("NSE Universe", len(stocks))

with k2:
    st.metric("Processed Stocks", len(results))

with k3:
    st.metric("Filtered Opportunities", len(results))

with k4:
    st.metric("Failed Stocks", len(set(failed_stocks)))

# =========================================================
# CHARTS
# =========================================================

left, right = st.columns(2)

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

    fig1.update_layout(height=420)

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

    fig2.update_layout(height=420)

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# =========================================================
# TOP PICKS
# =========================================================

st.markdown("## 🚀 Top Institutional Opportunities")

top_picks = results.sort_values(
    "Final Score",
    ascending=False
).head(10)

st.dataframe(

    top_picks[[

        "Symbol",
        "Classification",
        "Final Score",
        "Expected Return 5D %",
        "Expected Return 15D %",
        "Expected Return 30D %",
        "Suggested Hold Days"

    ]],

    use_container_width=True,
    height=420

)

# =========================================================
# FINAL TABLE
# =========================================================

st.markdown("## 🏦 Institutional Rankings")

display_df = results.sort_values(
    "Final Score",
    ascending=False
)

st.dataframe(

    display_df[[

        "Symbol",
        "CMP",
        "Classification",
        "Momentum",
        "Sharpe",
        "Final Score",
        "Expected Return 5D %",
        "Expected Return 15D %",
        "Expected Return 30D %",
        "Suggested Hold Days"

    ]],

    use_container_width=True,
    height=700

)
