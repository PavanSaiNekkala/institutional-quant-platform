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

/* =====================================================
GLOBAL
===================================================== */

.stApp{
    background:#F3F4F6;
    font-family:"Segoe UI",sans-serif;
}

/* =====================================================
MAIN CONTAINER
===================================================== */

.block-container{
    padding-top:0.5rem !important;
    padding-bottom:0.5rem !important;
    padding-left:1rem !important;
    padding-right:1rem !important;
}

/* =====================================================
RESPONSIVE SIDEBAR
===================================================== */

section[data-testid="stSidebar"]{
    background:#111827;
    border-right:1px solid #1F2937;

    min-width:260px !important;
    max-width:260px !important;
    width:260px !important;

    position:fixed !important;
    left:0;
    top:0;

    height:100vh !important;
    overflow-y:auto !important;
    overflow-x:hidden !important;
}

section[data-testid="stSidebar"] > div{
    height:100vh !important;
    overflow-y:auto !important;
    overflow-x:hidden !important;
}

/* =====================================================
RESPONSIVE MAIN AREA
===================================================== */

@media (max-width:768px){

    .main .block-container{
        margin-left:0 !important;
    }
}

/* =====================================================
PROCESSING ENGINE
===================================================== */

.processing-container{
    width:100% !important;
    max-width:100% !important;
    overflow:hidden !important;
}

/* =====================================================
SEARCH INPUT FIX
===================================================== */

div[data-baseweb="base-input"]{
    background:white !important;
    border-radius:12px !important;
}

div[data-baseweb="base-input"] > div{
    background:white !important;
    border:2px solid #2563EB !important;
    border-radius:12px !important;
    min-height:50px !important;
}

input[type="text"]{
    color:#111827 !important;
    background:white !important;
    font-size:18px !important;
    font-weight:800 !important;
    opacity:1 !important;
    -webkit-text-fill-color:#111827 !important;
    caret-color:#2563EB !important;
}

input[type="text"]::placeholder{
    color:#6B7280 !important;
    opacity:1 !important;
    font-weight:700 !important;
}

/* =====================================================
SELECT BOX
===================================================== */

div[data-baseweb="select"] > div{
    background:#1F2937 !important;
    border:1px solid #374151 !important;
    border-radius:12px !important;
}

/* =====================================================
MULTISELECT
===================================================== */

[data-baseweb="tag"]{
    background:#2563EB !important;
    color:white !important;
}

/* =====================================================
METRICS
===================================================== */

[data-testid="metric-container"]{
    background:white;
    border-radius:18px;
    padding:14px;
    min-height:80px;
    box-shadow:0 4px 12px rgba(0,0,0,0.08);
}

/* =====================================================
PLOTLY
===================================================== */

.element-container:has(.js-plotly-plot){
    background:white;
    border-radius:18px;
    padding:10px;
    box-shadow:0 4px 14px rgba(0,0,0,0.08);
    margin-bottom:16px;
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
MOBILE RESPONSIVE
===================================================== */

@media (max-width: 1200px){

    section[data-testid="stSidebar"]{
        overflow-y:auto !important;
        overflow-x:hidden !important;
    }

    section[data-testid="stSidebar"] > div{
        overflow-y:auto !important;
        overflow-x:hidden !important;
    }

}

@media (max-width: 768px){

    section[data-testid="stSidebar"]{
        width:100% !important;
    }

    section[data-testid="stSidebar"] > div{
        width:100% !important;
    }

}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div style="
font-size:22px;
font-weight:800;
color:#111827;
margin-bottom:0;
line-height:1;
">
📊 Institutional Quant Platform
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="
font-size:13px;
color:#6B7280;
margin-top:2px;
margin-bottom:4px;
">
Enterprise Institutional Analytics Dashboard
</div>
""", unsafe_allow_html=True)

india = pytz.timezone("Asia/Kolkata")

st.caption(
    f"Updated: {datetime.now(india).strftime('%d-%m-%Y %I:%M:%S %p IST')}"
)

# =========================================================
# LOAD STOCKS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

excel_path = (
    ROOT_DIR /
    "data" /
    "valid_stocks.xlsx"
)

if not excel_path.exists():

    st.error(
        f"Dataset not found: {excel_path}"
    )

    st.stop()

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

    if search_stock:

        matches = [
            s for s in stocks
            if s.upper().startswith(
                search_stock.upper()
            )
        ][:10]

        if matches:

            st.markdown("### 🔍 Matching Stocks")

            for m in matches:

                st.markdown(
                    f"""
                    <div style="
                        background:#1F2937;
                        padding:8px;
                        border-radius:8px;
                        margin-bottom:6px;
                        border-left:4px solid #10B981;
                        font-weight:700;
                        font-size:14px;
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
# ANALYSIS ENGINE
# =========================================================

@st.cache_data(ttl=3600, show_spinner=False)
def run_analysis(stock_list):

    filtered_df = []

    failed_stocks = []

    total = len(stock_list)

    completed = 0

    start_time = time.time()

    batch_size = 50

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

            for symbol in batch:

                if symbol not in failed_stocks:
                    failed_stocks.append(symbol)

            continue

        for symbol in batch:

            completed += 1
            completion_pct = round(
                (completed / total) * 100,
                1
            )

            elapsed = (time.time() - start_time) / 60

            estimated_total = (
                elapsed / max(completed, 1)
            ) * total

            remaining_minutes = round(
                max(estimated_total - elapsed, 0),
                1
            )
            if completed % 10 == 0:

                status_html = f"""
                <div style="
                background:white;
                padding:20px;
                border-radius:18px;
                box-shadow:0 4px 15px rgba(0,0,0,.08);
                margin-bottom:20px;
                ">

                    <div style="
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                    margin-bottom:15px;
                    ">

                        <div>

                            <div style="
                            font-size:28px;
                            font-weight:800;
                            color:#111827;
                            ">
                            📊 Institutional Processing Engine
                            </div>

                            <div style="
                            font-size:14px;
                            color:#6B7280;
                            ">
                            Real-Time Quant Processing
                            </div>

                        </div>

                        <div style="
                        background:#DBEAFE;
                        color:#1D4ED8;
                        padding:8px 14px;
                        border-radius:10px;
                        font-weight:700;
                        ">
                        LIVE
                        </div>

                    </div>

                    <div style="
                    display:grid;
                    grid-template-columns:repeat(4,1fr);
                    gap:12px;
                    ">

                        <div style="
                        background:#ECFDF5;
                        padding:15px;
                        border-radius:12px;
                        border-left:5px solid #10B981;
                        ">
                        <h3>{completed}</h3>
                        Processed
                        </div>

                        <div style="
                        background:#FEF2F2;
                        padding:15px;
                        border-radius:12px;
                        border-left:5px solid #DC2626;
                        ">
                        <h3>{len(set(failed_stocks))}</h3>
                        Failed
                        </div>

                        <div style="
                        background:#EFF6FF;
                        padding:15px;
                        border-radius:12px;
                        border-left:5px solid #2563EB;
                        ">
                        <h3>{total}</h3>
                        Universe
                        </div>

                        <div style="
                        background:#FFF7ED;
                        padding:15px;
                        border-radius:12px;
                        border-left:5px solid #F59E0B;
                        ">
                        <h3>{remaining_minutes}m</h3>
                        ETA
                        </div>

                    </div>

                    <div style="
                    margin-top:20px;
                    width:100%;
                    height:14px;
                    background:#E5E7EB;
                    border-radius:999px;
                    overflow:hidden;
                    ">

                        <div style="
                        width:{completion_pct}%;
                        height:100%;
                        background:linear-gradient(
                        90deg,
                        #2563EB,
                        #10B981
                        );
                        ">
                        </div>

                    </div>

                    <div style="
                    text-align:right;
                    margin-top:6px;
                    font-weight:700;
                    color:#2563EB;
                    ">
                    {completion_pct}%
                    </div>

                </div>
                """

                status_placeholder.markdown(
                    status_html,
                    unsafe_allow_html=True
                )
                
            try:

                if symbol not in data.columns.levels[0]:

                    if symbol not in failed_stocks:
                        failed_stocks.append(symbol)

                    continue

                close = data[symbol]["Close"].dropna()

                if len(close) < 40:

                    if symbol not in failed_stocks:
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

                sharpe = np.clip(
                    sharpe,
                    -5,
                    5
                )

                momentum_score = np.clip(
                    momentum * 100,
                    -100,
                    100
                )

                sharpe_score = sharpe * 20

                score = (
                    momentum_score * 0.5
                    + sharpe_score * 0.5
                )

                # =====================================================
                # SIGNAL CLASSIFICATION
                # =====================================================

                if score >= 40:
                    signal = "STRONG_BUY"

                elif score >= 20:
                    signal = "BUY"

                elif score >= 0:
                    signal = "WATCH"

                elif score >= -20:
                    signal = "HOLD"

                else:
                    signal = "AVOID"

                filtered_df.append({
                    "Symbol": symbol,
                    "CMP": safe_round(close.iloc[-1]),
                    "Momentum": safe_round(momentum * 100),
                    "Sharpe": safe_round(sharpe),
                    "Final Score": safe_round(score),
                    "Classification": signal
                })

            except:

                if symbol not in failed_stocks:
                    failed_stocks.append(symbol)


            elapsed = (time.time() - start_time) / 60

            estimated_total = (
                elapsed / max(completed,1)
            ) * total

            remaining_minutes = round(
                max(estimated_total - elapsed, 0),
                1
            )

            completion_pct = round(
                (completed / total) * 100,
                1
            )
           
    return (
        pd.DataFrame(filtered_df),
        failed_stocks
    )

# =========================================================
# RUN ANALYSIS
# =========================================================

status_placeholder = st.empty()

filtered_df, failed_stocks = run_analysis(stocks)

if filtered_df.empty:

    st.error("No valid filtered_df.")
    st.stop()
# =========================================================
# FINAL PROCESSING SUMMARY
# =========================================================

st.markdown(f"""
<div style="
background:white;
padding:20px;
border-radius:18px;
box-shadow:0 4px 15px rgba(0,0,0,.08);
margin-bottom:20px;
">

<div style="
display:flex;
justify-content:space-between;
align-items:center;
margin-bottom:15px;
">

<div>

<div style="
font-size:28px;
font-weight:800;
color:#111827;
">
📊 Institutional Processing Engine
</div>

<div style="
font-size:14px;
color:#6B7280;
">
Real-Time Quant Processing Complete
</div>

</div>

<div style="
background:#DCFCE7;
color:#166534;
padding:8px 14px;
border-radius:10px;
font-weight:700;
">
COMPLETED
</div>

</div>

<div style="
display:grid;
grid-template-columns:repeat(4,1fr);
gap:12px;
">

<div style="
background:#ECFDF5;
padding:15px;
border-radius:12px;
">
<h3>{len(filtered_df)}</h3>
Processed
</div>

<div style="
background:#FEF2F2;
padding:15px;
border-radius:12px;
">
<h3>{len(set(failed_stocks))}</h3>
Failed
</div>

<div style="
background:#EFF6FF;
padding:15px;
border-radius:12px;
">
<h3>{len(stocks)}</h3>
Universe
</div>

<div style="
background:#FFF7ED;
padding:15px;
border-radius:12px;
">
<h3>100%</h3>
Completed
</div>

</div>

<div style="
margin-top:15px;
width:100%;
height:12px;
background:#E5E7EB;
border-radius:999px;
overflow:hidden;
">

<div style="
width:100%;
height:100%;
background:linear-gradient(
90deg,
#2563EB,
#10B981
);
">
</div>

</div>

</div>
""",
unsafe_allow_html=True)
# =========================================================
# FILTERS
# =========================================================

filtered_df = filtered_df.copy()

filtered_df["Percentile"] = (
    filtered_df["Final Score"]
    .rank(pct=True)
    * 100
)

filtered_df = filtered_df[
    filtered_df["Percentile"] >= min_score
]

if signal_filter:
    filtered_df = filtered_df[
        filtered_df["Classification"]
        .isin(signal_filter)
    ]

if search_stock:
    filtered_df = filtered_df[
        filtered_df["Symbol"]
        .str.contains(
            search_stock.upper(),
            na=False
        )
    ]

if filtered_df.empty:

    st.warning(
        "No stocks match selected filters."
    )

    st.stop()
advancers = len(
    filtered_df[
        filtered_df["Momentum"] > 0
    ]
)

decliners = len(
    filtered_df[
        filtered_df["Momentum"] <= 0
    ]
)

breadth = round(
    advancers /
    max(decliners,1),
    2
)
# =========================================================
# KPI CARDS
# =========================================================

st.markdown("<br>", unsafe_allow_html=True)

k1,k2,k3,k4 = st.columns(4)

with k1:
    st.metric("NSE Universe", len(stocks))

with k2:
    st.metric(
        "Processed Stocks",
        len(filtered_df)
    )

with k3:
    st.metric(
        "Filtered Opportunities",
        len(filtered_df)
    )

with k4:
    st.metric(
        "Failed Stocks",
        len(set(failed_stocks))
    )
breadth_col1, breadth_col2, breadth_col3 = st.columns(3)

with breadth_col1:
    st.metric(
        "📈 Advancers",
        advancers
    )

with breadth_col2:
    st.metric(
        "📉 Decliners",
        decliners
    )

with breadth_col3:
    st.metric(
        "⚖ A/D Ratio",
        breadth
    )

st.markdown("---")
# =========================================================
# CHARTS
# =========================================================

left,right = st.columns(2)

with left:

    signal_data = (
        filtered_df["Classification"]
        .value_counts()
        .reset_index()
    )

    signal_data.columns = [
        "Signal",
        "Count"
    ]

    if not signal_data.empty:
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
            height=300,
            margin=dict(l=10,r=10,t=40,b=10)
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

with right:

    fig2 = px.scatter(
        filtered_df,
        x="Momentum",
        y="Sharpe",
        color="Classification",
        size="Final Score",
        hover_name="Symbol",
        color_discrete_map=signal_colors,
        title="Risk Reward Opportunity Matrix"
    )
    fig2.add_hline(
        y=0,
        line_dash="dash"
    )

    fig2.add_vline(
        x=0,
        line_dash="dash"
    )

    fig2.update_layout(
        height=300,
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

csv = filtered_df.to_csv(index=False)

st.download_button(
    "📥 Download Rankings",
    csv,
    "institutional_rankings.csv",
    "text/csv"
)
st.data_editor(
    filtered_df.sort_values(
        "Final Score",
        ascending=False
    ),
    use_container_width=True,
    height=550,
    disabled=filtered_df.columns.tolist()
)
