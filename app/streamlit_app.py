# =========================================================
# INSTITUTIONAL QUANT PLATFORM
# FINAL CLEAN ENTERPRISE STREAMLIT APP
# =========================================================

import streamlit as st
import streamlit.components.v1 as components

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
# CSS
# =========================================================

st.markdown("""
<style>

/* =====================================================
GLOBAL
===================================================== */

.stApp{
    background:#F3F4F6;
    font-family:"Segoe UI",sans-serif;
}

/* =====================================================
REMOVE HEADER SPACE
===================================================== */

header[data-testid="stHeader"]{
    background:transparent !important;
    height:0px !important;
}

div[data-testid="stToolbar"]{
    right:1rem !important;
}

/* =====================================================
MAIN CONTAINER
===================================================== */

.block-container{
    padding-top:1rem !important;
    padding-bottom:1rem !important;
    padding-left:1rem !important;
    padding-right:1rem !important;
    max-width:100% !important;
}

/* =====================================================
SIDEBAR
===================================================== */

section[data-testid="stSidebar"]{
    background:#111827;
    border-right:1px solid #1F2937;
}

section[data-testid="stSidebar"] *{
    color:white !important;
}

/* =====================================================
SEARCH INPUT
===================================================== */

div[data-baseweb="base-input"] > div{
    background:white !important;
    border:2px solid #2563EB !important;
    border-radius:12px !important;
}

div[data-baseweb="base-input"] > div:focus-within{
    border:2px solid #10B981 !important;
}

input[type="text"]{
    color:#111827 !important;
    background:white !important;
    font-size:18px !important;
    font-weight:800 !important;
    -webkit-text-fill-color:#111827 !important;
}

input[type="text"]::placeholder{
    color:#6B7280 !important;
    opacity:1 !important;
}

/* =====================================================
SELECT
===================================================== */

div[data-baseweb="select"] > div{
    background:#1F2937 !important;
    border-radius:12px !important;
}

/* =====================================================
METRIC CARDS
===================================================== */

[data-testid="metric-container"]{
    background:white;
    border-radius:18px;
    padding:14px;
    box-shadow:0 4px 14px rgba(0,0,0,0.08);
}

/* =====================================================
PLOTLY
===================================================== */

.element-container:has(.js-plotly-plot){
    background:white;
    border-radius:18px;
    padding:10px;
    box-shadow:0 4px 14px rgba(0,0,0,0.08);
    margin-bottom:18px;
}

/* =====================================================
TABLE
===================================================== */

[data-testid="stDataFrame"]{
    background:white;
    border-radius:18px;
    padding:10px;
}

/* =====================================================
REMOVE SCROLLBARS
===================================================== */

iframe{
    overflow:hidden !important;
}

html, body, [class*="css"]{
    overflow-x:hidden !important;
}

/* =====================================================
RESPONSIVE
===================================================== */

@media (max-width:1200px){

    .processing-container{
        zoom:0.92;
    }

}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div style="
        background:linear-gradient(
            135deg,
            #0F172A,
            #111827
        );
        padding:18px 24px;
        border-radius:22px;
        margin-bottom:12px;
        box-shadow:0 8px 24px rgba(0,0,0,0.15);
    ">

        <div style="
            display:flex;
            justify-content:space-between;
            align-items:center;
            flex-wrap:wrap;
        ">

            <div>

                <div style="
                    font-size:38px;
                    font-weight:900;
                    color:white;
                    line-height:1.1;
                    letter-spacing:-1px;
                ">
                    📊 Institutional Quant Platform
                </div>

                <div style="
                    margin-top:6px;
                    color:#CBD5E1;
                    font-size:14px;
                    font-weight:500;
                ">
                    Enterprise Institutional Analytics Dashboard
                </div>

            </div>

            <div style="
                background:#10B981;
                color:white;
                padding:8px 16px;
                border-radius:12px;
                font-size:13px;
                font-weight:800;
                margin-top:8px;
            ">
                LIVE NSE ENGINE
            </div>

        </div>

    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# TIMESTAMP
# =========================================================

india = pytz.timezone("Asia/Kolkata")

st.markdown(
    f"""
    <div style="
        color:#6B7280;
        font-size:11px;
        margin-top:-2px;
        margin-bottom:12px;
        font-weight:700;
    ">
    Updated:
    {datetime.now(india).strftime('%d-%m-%Y %I:%M:%S %p IST')}
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# LOAD NSE STOCKS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

excel_path = ROOT_DIR / "data" / "valid_stocks.xlsx"

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

    st.markdown("""
    <div style="
        font-size:28px;
        font-weight:900;
        margin-bottom:10px;
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
        ],
        default=[
            "STRONG_BUY",
            "BUY"
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
    "STRONG_BUY":"#006400",
    "BUY":"#32CD32",
    "WATCH":"#F59E0B",
    "HOLD":"#3B82F6",
    "AVOID":"#DC2626"
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
# RUNNING MESSAGE
# =========================================================

st.info(
    "⚡ Running institutional analysis across full NSE universe..."
)

# =========================================================
# ANALYSIS
# =========================================================

@st.cache_data(ttl=3600, show_spinner=False)
def run_analysis(stock_list):

    progress_bar = st.progress(0)

    results = []

    failed_stocks = []

    total = len(stock_list)

    completed = 0

    start_time = time.time()

    batch_size = 25

    status_placeholder = st.empty()

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
                    / max(returns.std(),0.0001)
                ) * np.sqrt(252)

                score = (
                    momentum * 0.6
                    + sharpe * 0.4
                )

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

                results.append({
                    "Symbol":symbol,
                    "CMP":safe_round(close.iloc[-1]),
                    "Momentum":safe_round(momentum*100),
                    "Sharpe":safe_round(sharpe),
                    "Final Score":safe_round(score),
                    "Classification":signal
                })

            except:

                failed_stocks.append(symbol)

            progress_bar.progress(completed / total)

            elapsed = (time.time() - start_time) / 60

            estimated_total = (
                elapsed / max(completed,1)
            ) * total

            remaining_minutes = round(
                max(estimated_total - elapsed,0),
                1
            )

            completion_pct = round(
                (completed / total) * 100,
                1
            )

            if completed % 10 == 0:

                status_html = f"""
                <div class="processing-container" style="
                    background:white;
                    border-radius:18px;
                    padding:14px;
                    box-shadow:0 6px 20px rgba(0,0,0,0.08);
                    font-family:Segoe UI;
                ">

                <div style="
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                    margin-bottom:12px;
                ">

                    <div>

                        <div style="
                            font-size:22px;
                            font-weight:900;
                            color:#111827;
                        ">
                        📊 Institutional Processing Engine
                        </div>

                        <div style="
                            color:#6B7280;
                            font-size:13px;
                        ">
                        Real-Time Quant Processing
                        </div>

                    </div>

                    <div style="
                        background:#DBEAFE;
                        color:#1D4ED8;
                        padding:6px 12px;
                        border-radius:10px;
                        font-weight:800;
                        font-size:11px;
                    ">
                    LIVE
                    </div>

                </div>

                <div style="
                    display:grid;
                    grid-template-columns:
                    repeat(auto-fit,minmax(160px,1fr));
                    gap:10px;
                ">

                    <div style="
                        background:#ECFDF5;
                        padding:10px;
                        border-radius:14px;
                        border-left:5px solid #10B981;
                    ">
                        <div style="
                            color:#047857;
                            font-size:11px;
                            font-weight:700;
                        ">
                        COMPLETED
                        </div>

                        <div style="
                            margin-top:6px;
                            font-size:18px;
                            font-weight:900;
                            color:#065F46;
                        ">
                        {completed}
                        </div>

                        <div style="
                            margin-top:2px;
                            color:#10B981;
                            font-size:11px;
                        ">
                        out of {total}
                        </div>
                    </div>

                    <div style="
                        background:#FEF2F2;
                        padding:10px;
                        border-radius:14px;
                        border-left:5px solid #DC2626;
                    ">
                        <div style="
                            color:#B91C1C;
                            font-size:11px;
                            font-weight:700;
                        ">
                        FAILED
                        </div>

                        <div style="
                            margin-top:6px;
                            font-size:18px;
                            font-weight:900;
                            color:#991B1B;
                        ">
                        {len(set(failed_stocks))}
                        </div>

                        <div style="
                            margin-top:2px;
                            color:#DC2626;
                            font-size:11px;
                        ">
                        failed stocks
                        </div>
                    </div>

                    <div style="
                        background:#EFF6FF;
                        padding:10px;
                        border-radius:14px;
                        border-left:5px solid #2563EB;
                    ">
                        <div style="
                            color:#1D4ED8;
                            font-size:11px;
                            font-weight:700;
                        ">
                        UNIVERSE
                        </div>

                        <div style="
                            margin-top:6px;
                            font-size:18px;
                            font-weight:900;
                            color:#1E3A8A;
                        ">
                        {total}
                        </div>

                        <div style="
                            margin-top:2px;
                            color:#2563EB;
                            font-size:11px;
                        ">
                        NSE Stocks
                        </div>
                    </div>

                    <div style="
                        background:#FFF7ED;
                        padding:10px;
                        border-radius:14px;
                        border-left:5px solid #F59E0B;
                    ">
                        <div style="
                            color:#D97706;
                            font-size:11px;
                            font-weight:700;
                        ">
                        ETA
                        </div>

                        <div style="
                            margin-top:6px;
                            font-size:18px;
                            font-weight:900;
                            color:#92400E;
                        ">
                        {remaining_minutes}m
                        </div>

                        <div style="
                            margin-top:2px;
                            color:#F59E0B;
                            font-size:11px;
                        ">
                        remaining
                        </div>
                    </div>

                </div>

                <div style="margin-top:10px;">

                    <div style="
                        display:flex;
                        justify-content:space-between;
                        margin-bottom:5px;
                    ">

                        <div style="
                            color:#374151;
                            font-weight:700;
                            font-size:12px;
                        ">
                        Processing Progress
                        </div>

                        <div style="
                            color:#2563EB;
                            font-weight:800;
                            font-size:12px;
                        ">
                        {completion_pct}%
                        </div>

                    </div>

                    <div style="
                        width:100%;
                        height:7px;
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
                            border-radius:999px;
                        ">
                        </div>

                    </div>

                </div>

                </div>
                """

                with status_placeholder:

                    components.html(
                        status_html,
                        height=280,
                        scrolling=False
                    )

    progress_bar.empty()

    return pd.DataFrame(results), failed_stocks

# =========================================================
# RUN
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
# KPIs
# =========================================================

st.markdown("<br>", unsafe_allow_html=True)

k1,k2,k3,k4 = st.columns(4)

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
        height=320,
        margin=dict(l=10,r=10,t=40,b=10)
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
        height=320,
        margin=dict(l=10,r=10,t=40,b=10)
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
    height=500
)
