# =========================================================
# ENTERPRISE INSTITUTIONAL QUANT PLATFORM
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
# CSS
# =========================================================

st.markdown("""

<style>

.stApp{
    background:#F3F4F6;
    font-family:'Segoe UI';
}

.block-container{
    padding-top:1rem;
}

section[data-testid="stSidebar"]{
    background:#071028;
    border-right:1px solid #1E293B;
}

section[data-testid="stSidebar"] *{
    color:white !important;
}

.metric-card{

    background:white;

    border-radius:22px;

    padding:20px;

    box-shadow:0 4px 16px rgba(0,0,0,0.08);

    height:140px;
}

.metric-title{

    font-size:13px;

    font-weight:700;

    margin-bottom:14px;
}

.metric-value{

    font-size:48px;

    font-weight:900;
}

.engine-card{

    background:white;

    border-radius:28px;

    padding:28px;

    box-shadow:0 8px 20px rgba(0,0,0,0.08);
}

.live-badge{

    background:#DBEAFE;

    color:#2563EB;

    padding:8px 18px;

    border-radius:12px;

    font-weight:800;

    font-size:14px;
}

</style>

""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================

india = pytz.timezone("Asia/Kolkata")

st.caption(

    f"Updated: {datetime.now(india).strftime('%d-%m-%Y %I:%M:%S %p IST')}"

)

# =========================================================
# LOAD NSE UNIVERSE
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

    st.markdown("# ⚙ Dashboard Controls")

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

    st.markdown("<br>", unsafe_allow_html=True)

    st.success(

        f"✅ NSE Universe Loaded: {len(stocks)}"

    )

# =========================================================
# PROCESSING ALERT
# =========================================================

st.info(

    "⚡ Running institutional analysis across full NSE universe..."

)

# =========================================================
# PROGRESS BAR
# =========================================================

progress_bar = st.progress(0)

# =========================================================
# ANALYSIS
# =========================================================

@st.cache_data(ttl=3600)

def run_analysis(stock_list):

    results = []

    failed = 0

    completed = 0

    total = len(stock_list)

    batch_size = 50

    start = time.time()

    status_cards = st.empty()

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

            failed += len(batch)

            continue

        for stock in batch:

            try:

                close = data[stock]["Close"].dropna()

                if len(close) < 40:

                    failed += 1

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

                    max(returns.std(),0.0001)

                ) * np.sqrt(252)

                score = (

                    momentum * 0.6

                    +

                    sharpe * 0.4

                )

                percentile = min(

                    max(score * 100,0),

                    100
                )

                if score >= 1.5:

                    signal = "STRONG_BUY"

                elif score >= 1:

                    signal = "BUY"

                elif score >= 0.6:

                    signal = "WATCH"

                elif score >= 0.2:

                    signal = "HOLD"

                else:

                    signal = "AVOID"

                results.append({

                    "Symbol":stock,

                    "Momentum":round(momentum*100,2),

                    "Sharpe":round(sharpe,2),

                    "Score":round(score,2),

                    "Percentile":round(percentile,2),

                    "Signal":signal
                })

                completed += 1

            except:

                failed += 1

            # ============================================
            # PROGRESS
            # ============================================

            pct = round(

                (completed + failed)

                /

                total

                * 100,

                1
            )

            progress_bar.progress(int(pct))

            elapsed = time.time() - start

            remaining = max(

                ((elapsed/max(pct,1))*100) - elapsed,

                0
            )

            eta = round(

                remaining / 60,

                1
            )

            # ============================================
            # ENGINE CARD
            # ============================================

            status_cards.markdown(f"""

            <div class="engine-card">

            <div style="
            display:flex;
            justify-content:space-between;
            align-items:center;
            ">

            <div>

            <div style="
            font-size:28px;
            font-weight:900;
            color:#071028;
            ">
            📊 Institutional Processing Engine
            </div>

            <div style="
            color:#64748B;
            margin-top:8px;
            ">
            Real-Time Quant Processing
            </div>

            </div>

            <div class="live-badge">
            LIVE
            </div>

            </div>

            <br>

            <div style="
            display:grid;
            grid-template-columns:repeat(4,1fr);
            gap:16px;
            ">

            <div class="metric-card"
            style="border-left:5px solid #10B981;">

            <div class="metric-title"
            style="color:#047857;">
            COMPLETED
            </div>

            <div class="metric-value"
            style="color:#065F46;">
            {completed}
            </div>

            <div style="color:#10B981;">
            out of {total}
            </div>

            </div>

            <div class="metric-card"
            style="border-left:5px solid #DC2626;">

            <div class="metric-title"
            style="color:#DC2626;">
            FAILED
            </div>

            <div class="metric-value"
            style="color:#991B1B;">
            {failed}
            </div>

            <div style="color:#DC2626;">
            failed stocks
            </div>

            </div>

            <div class="metric-card"
            style="border-left:5px solid #2563EB;">

            <div class="metric-title"
            style="color:#2563EB;">
            UNIVERSE
            </div>

            <div class="metric-value"
            style="color:#1E40AF;">
            {total}
            </div>

            <div style="color:#2563EB;">
            NSE Stocks
            </div>

            </div>

            <div class="metric-card"
            style="border-left:5px solid #F59E0B;">

            <div class="metric-title"
            style="color:#D97706;">
            ETA
            </div>

            <div class="metric-value"
            style="color:#92400E;">
            {eta}m
            </div>

            <div style="color:#F59E0B;">
            remaining
            </div>

            </div>

            </div>

            <br>

            <div style="
            font-weight:700;
            margin-bottom:10px;
            ">
            Processing Progress
            </div>

            <div style="
            width:100%;
            background:#E5E7EB;
            border-radius:20px;
            overflow:hidden;
            height:16px;
            ">

            <div style="
            width:{pct}%;
            background:linear-gradient(
            90deg,
            #2563EB,
            #10B981
            );
            height:16px;
            border-radius:20px;
            ">
            </div>

            </div>

            <div style="
            text-align:right;
            margin-top:8px;
            font-weight:800;
            color:#2563EB;
            ">
            {pct}%
            </div>

            </div>

            """, unsafe_allow_html=True)

    return pd.DataFrame(results)

# =========================================================
# RUN
# =========================================================

results = run_analysis(stocks)

# =========================================================
# FILTERS
# =========================================================

results = results[

    results["Percentile"] >= min_score

]

if signal_filter:

    results = results[

        results["Signal"]

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
# FINAL TABLE
# =========================================================

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("## 📈 Institutional Opportunities")

st.dataframe(

    results.sort_values(

        "Percentile",

        ascending=False
    ),

    use_container_width=True,

    height=700
)
