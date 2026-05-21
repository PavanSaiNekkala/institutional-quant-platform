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
    padding-top:1rem;
    padding-bottom:1rem;
    max-width:100%;
}

/* =====================================================
RESPONSIVE SIDEBAR
===================================================== */

section[data-testid="stSidebar"]{
    background:#111827;
    border-right:1px solid #1F2937;
    min-width:280px !important;
    max-width:340px !important;
    width:22vw !important;
}

section[data-testid="stSidebar"] > div{
    min-width:280px !important;
    max-width:340px !important;
    width:22vw !important;
}

section[data-testid="stSidebar"] *{
    color:white !important;
}

/* =====================================================
RESPONSIVE MAIN AREA
===================================================== */

.main .block-container{
    max-width:100% !important;
    width:100% !important;
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
    min-height:110px;
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
        width:280px !important;
    }

    section[data-testid="stSidebar"] > div{
        width:280px !important;
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
    font-weight:800;
    margin-top:6px;
    margin-bottom:12px;
">
Enterprise Institutional Analytics Dashboard
</div>
""", unsafe_allow_html=True)

india = pytz.timezone("Asia/Kolkata")

st.markdown(
    f"""
    <div style="
        color:#111827;
        font-size:14px;
        font-weight:500;
        margin-top:6px;
        margin-bottom:12px;
    ">
        Updated: {datetime.now(india).strftime('%d-%m-%Y %I:%M:%S %p IST')}
    </div>
    """,
    unsafe_allow_html=True
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

    # =====================================================
    # MARKET CAP FILTER
    # =====================================================

    market_cap_filter = st.multiselect(
        "🏢 Market Cap Filter",
        options=[
            "Large Cap",
            "Mid Cap",
            "Small Cap"
        ],
        default=[]
    )

    # =====================================================
    # TRADE SIGNAL FILTER
    # =====================================================

    signal_filter = st.multiselect(
        "📈 Trade Signal Filter",
        options=[
            "STRONG_BUY",
            "BUY",
            "WATCH",
            "HOLD",
            "AVOID"
        ],
        default=[]
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
# LOAD MARKET CAPS CSV
# =========================================================

market_cap_file = (

    ROOT_DIR
    / "data"
    / "market_caps.csv"

)

market_cap_df = pd.read_csv(
    market_cap_file
)

market_cap_df["Symbol"] = (

    market_cap_df["Symbol"]
    .astype(str)
    .str.replace(".NS", "", regex=False)
)

market_cap_map = dict(

    zip(

        market_cap_df["Symbol"],

        market_cap_df["MarketCap"]

    )

)
# =========================================================
# ANALYSIS ENGINE
# =========================================================

@st.cache_data(ttl=3600, show_spinner=False)
def run_analysis(stock_list):

        results = []

        failed_stocks = set()

        total = len(stock_list)

        completed = 0

        start_time = time.time()

        batch_size = 20

        status_placeholder = st.empty()

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

                        for symbol in batch:

                                failed_stocks.add(symbol)

                        continue

                # =====================================================
                # PROCESS EACH STOCK
                # =====================================================

                for symbol in batch:

                        try:

                                # ============================================
                                # SYMBOL EXISTS CHECK
                                # ============================================

                                if symbol not in data.columns.levels[0]:

                                        failed_stocks.add(symbol)
                                        continue

                                close = data[symbol]["Close"].dropna()

                                # ============================================
                                # MINIMUM DATA CHECK
                                # ============================================

                                if len(close) < 40:

                                        failed_stocks.add(symbol)
                                        continue

                                # ============================================
                                # MARKET CAP
                                # ============================================

                                clean_symbol = symbol.replace(".NS", "")

                                market_cap = market_cap_map.get(
                                        clean_symbol,
                                        0
                                )

                                # ============================================
                                # MARKET CAP CATEGORY
                                # ============================================

                                if market_cap >= 1000000000000:

                                        market_cap_category = "Large Cap"

                                elif market_cap >= 200000000000:

                                        market_cap_category = "Mid Cap"

                                else:

                                        market_cap_category = "Small Cap"

                                # ============================================
                                # MARKET CAP DISPLAY
                                # ============================================

                                if market_cap >= 1_00_000_00_00_000:

                                        market_cap_display = (
                                                f"{round(market_cap / 1_00_000_00_00_000, 2)} LCr"
                                        )

                                elif market_cap >= 1_00_00_00_000:

                                        market_cap_display = (
                                                f"{round(market_cap / 1_00_00_000, 2)} Cr"
                                        )

                                else:

                                        market_cap_display = str(market_cap)

                                # ============================================
                                # MOMENTUM
                                # ============================================

                                momentum = (
                                        close.iloc[-1] /
                                        close.iloc[-20]
                                ) - 1

                                # ============================================
                                # RETURNS
                                # ============================================

                                ret_5d = round(momentum * 5, 2)
                                ret_15d = round(momentum * 15, 2)
                                ret_30d = round(momentum * 30, 2)

                                # ============================================
                                # SHARPE
                                # ============================================

                                returns = close.pct_change().dropna()

                                sharpe = (
                                        returns.mean()
                                        / max(returns.std(), 0.0001)
                                ) * np.sqrt(252)

                                # ============================================
                                # SCORE ENGINE
                                # ============================================

                                raw_score = (
                                        momentum * 0.6 +
                                        sharpe * 0.4
                                )

                                final_score = round(
                                        min(
                                                max(raw_score * 50, 0),
                                                100
                                        ),
                                        2
                                )

                                institutional_confidence = final_score

                                # ============================================
                                # CONVICTION
                                # ============================================

                                if institutional_confidence >= 85:

                                        conviction = "ELITE"

                                elif institutional_confidence >= 70:

                                        conviction = "HIGH"

                                elif institutional_confidence >= 55:

                                        conviction = "MEDIUM"

                                elif institutional_confidence >= 40:

                                        conviction = "LOW"

                                else:

                                        conviction = "AVOID"

                                # ============================================
                                # SIGNAL
                                # ============================================

                                if raw_score >= 1.0:

                                        signal = "STRONG_BUY"

                                elif raw_score >= 0.75:

                                        signal = "BUY"

                                elif raw_score >= 0.5:

                                        signal = "WATCH"

                                elif raw_score >= 0.25:

                                        signal = "HOLD"

                                else:

                                        signal = "AVOID"

                                # ============================================
                                # TARGETS
                                # ============================================

                                cmp_price = round(close.iloc[-1], 2)

                                stop_loss = round(
                                        cmp_price * 0.96,
                                        2
                                )

                                target = round(
                                        cmp_price * 1.10,
                                        2
                                )

                                upside_pct = round(
                                        (
                                                (target - cmp_price)
                                                / cmp_price
                                        ) * 100,
                                        2
                                )

                                # ============================================
                                # RR
                                # ============================================

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

                                # ============================================
                                # ETA
                                # ============================================

                                daily_move = max(
                                        close.pct_change().std() * cmp_price,
                                        1
                                )

                                estimated_days = round(
                                        max(reward / daily_move, 1)
                                )

                                # ============================================
                                # SAVE RESULT
                                # ============================================

                                results.append({

                                        "Symbol": symbol,
                                        "MARKET_CAP": market_cap_display,
                                        "MARKET_CAP_CATEGORY": market_cap_category,
                                        "CMP": cmp_price,
                                        "STOP_LOSS": stop_loss,
                                        "TARGET": target,
                                        "Momentum": safe_round(momentum * 100),
                                        "Sharpe": safe_round(sharpe),
                                        "5D_RETURN_%": ret_5d,
                                        "15D_RETURN_%": ret_15d,
                                        "30D_RETURN_%": ret_30d,
                                        "Final Score": final_score,
                                        "Institutional_Confidence": institutional_confidence,
                                        "Conviction": conviction,
                                        "Classification": signal,
                                        "UPSIDE_%": upside_pct,
                                        "RR_RATIO": rr_ratio,
                                        "ESTIMATED_DAYS": estimated_days

                                })

                                completed += 1

                        except Exception:

                                failed_stocks.add(symbol)

                                # =====================================================
                                                # LIVE STATUS PANEL
                                                # =====================================================
                                
                                                elapsed = (time.time() - start_time) / 60
                                
                                                processed_count = (
                                                        completed +
                                                        len(failed_stocks)
                                                )

                                                estimated_total = (
                                                        elapsed /
                                                        max(processed_count, 1)
                                                ) * total

                                                remaining_minutes = round(
                                                        max(estimated_total - elapsed, 0),
                                                        1
                                                )

                                                completion_pct = round(
                                                        (
                                                                processed_count / total
                                                        ) * 100,
                                                        1
                                                )

                                                status_html = f"""
                                                <div style="
                                                        background:white;
                                                        border-radius:18px;
                                                        padding:20px;
                                                        box-shadow:0 6px 20px rgba(0,0,0,0.08);
                                                        margin-bottom:18px;
                                                ">

                                                        <div style="
                                                                display:flex;
                                                                justify-content:space-between;
                                                                align-items:center;
                                                                flex-wrap:wrap;
                                                                gap:12px;
                                                        ">

                                                                <div>

                                                                        <h2 style="
                                                                                margin:0;
                                                                                color:#111827;
                                                                                font-size:20px;
                                                                                font-weight:800;
                                                                        ">
                                                                        📊 Institutional Processing Engine
                                                                        </h2>
                                
                                                                        <p style="
                                                                                color:#6B7280;
                                                                                margin-top:6px;
                                                                                margin-bottom:0;
                                                                                font-size:14px;
                                                                        ">
                                                                        Real-Time Quant Processing
                                                                        </p>

                                                                </div>

                                                                <div style="
                                                                        background:#DBEAFE;
                                                                        color:#1D4ED8;
                                                                        padding:8px 14px;
                                                                        border-radius:12px;
                                                                        font-weight:700;
                                                                        font-size:13px;
                                                                ">
                                                                LIVE
                                                                </div>

                                                        </div>

                                                        <br>

                                                        <div style="
                                                                display:grid;
                                                                grid-template-columns:
                                                                repeat(auto-fit,minmax(180px,1fr));
                                                                gap:14px;
                                                        ">

                                                                <div style="
                                                                        background:#ECFDF5;
                                                                        padding:18px;
                                                                        border-radius:14px;
                                                                        border-left:5px solid #10B981;
                                                                ">
                                                                        <div style="
                                                                                color:#047857;
                                                                                font-size:13px;
                                                                                font-weight:700;
                                                                        ">
                                                                        COMPLETED
                                                                        </div>

                                                                        <h1 style="
                                                                                margin:8px 0 4px 0;
                                                                                color:#065F46;
                                                                        ">
                                                                        {processed_count}
                                                                        </h1>

                                                                        <div style="
                                                                                color:#10B981;
                                                                                font-size:13px;
                                                                        ">
                                                                        out of {total}
                                                                        </div>

                                                                </div>

                                                                <div style="
                                                                        background:#FEF2F2;
                                                                        padding:18px;
                                                                        border-radius:14px;
                                                                        border-left:5px solid #DC2626;
                                                                ">
                                                                        <div style="
                                                                                color:#B91C1C;
                                                                                font-size:13px;
                                                                                font-weight:700;
                                                                        ">
                                                                        FAILED
                                                                        </div>

                                                                        <h1 style="
                                                                                margin:8px 0 4px 0;
                                                                                color:#991B1B;
                                                                        ">
                                                                        {len(failed_stocks)}
                                                                        </h1>

                                                                        <div style="
                                                                                color:#EF4444;
                                                                                font-size:13px;
                                                                        ">
                                                                        failed stocks
                                                                        </div>

                                                                </div>

                                                                <div style="
                                                                        background:#EFF6FF;
                                                                        padding:18px;
                                                                        border-radius:14px;
                                                                        border-left:5px solid #2563EB;
                                                                ">
                                                                        <div style="
                                                                                color:#1D4ED8;
                                                                               font-size:13px;
                                                                                font-weight:700;
                                                                        ">
                                                                        UNIVERSE
                                                                        </div>

                                                                        <h1 style="
                                                                                margin:8px 0 4px 0;
                                                                                color:#1E3A8A;
                                                                        ">
                                                                        {total}
                                                                        </h1>

                                                                        <div style="
                                                                                color:#2563EB;
                                                                                font-size:13px;
                                                                        ">
                                                                        NSE Stocks
                                                                        </div>

                                                                </div>

                                                                <div style="
                                                                        background:#FFF7ED;
                                                                        padding:18px;
                                                                        border-radius:14px;
                                                                        border-left:5px solid #F59E0B;
                                                                ">
                                                                        <div style="
                                                                                color:#C2410C;
                                                                                font-size:13px;
                                                                                font-weight:700;
                                                                        ">
                                                                        ETA
                                                                        </div>

                                                                        <h1 style="
                                                                                margin:8px 0 4px 0;
                                                                                color:#9A3412;
                                                                        ">
                                                                        {remaining_minutes}m
                                                                        </h1>

                                                                        <div style="
                                                                                color:#F59E0B;
                                                                                font-size:13px;
                                                                        ">
                                                                        remaining
                                                                        </div>

                                                                </div>

                                                        </div>

                                                        <br>

                                                        <div style="
                                                                font-size:14px;
                                                                font-weight:700;
                                                                margin-bottom:8px;
                                                                color:#374151;
                                                        ">                                
                                                        Processing Progress
                                                        </div>

                                                        <div style="
                                                                width:100%;
                                                                height:14px;
                                                                background:#E5E7EB;
                                                                border-radius:999px;
                                                                overflow:hidden;
                                                        ">

                                                                <div style="
                                                                        width:{completion_pct}%;
                                                                        height:100%;
                                                                        border-radius:999px;
                                                                        background:linear-gradient(
                                                                                90deg,
                                                                                #2563EB,
                                                                                #10B981
                                                                        );
                                                                ">
                                                                </div>

                                                        </div>

                                                        <div style="
                                                                margin-top:10px;
                                                                text-align:right;
                                                                font-weight:800;
                                                                color:#2563EB;
                                                        ">
                                                        {completion_pct}%
                                                        </div>

                                                </div>
                                                """

                                                with status_placeholder:

                                                        st.markdown(
                                                                status_html,
                                                                unsafe_allow_html=True
                                                        )

                                        return (
                                                pd.DataFrame(results),
                                                failed_stocks,
                                                completed
                                        )

# =========================================================
# RUN ANALYSIS
# =========================================================

results, failed_stocks, completed = run_analysis(stocks)

if results.empty:

    st.error("No valid results.")
    st.stop()

# =========================================================
# MASTER FILTER ENGINE
# =========================================================

filtered_results = results.copy()

# =========================================================
# SCORE FILTER
# =========================================================

filtered_results["Percentile"] = (
    filtered_results["Final Score"] * 100
)

filtered_results = filtered_results[

    filtered_results["Percentile"] >= min_score

]

# =========================================================
# MARKET CAP FILTER
# =========================================================

if market_cap_filter:

    filtered_results = filtered_results[

        filtered_results[
            "MARKET_CAP_CATEGORY"
        ].isin(market_cap_filter)

    ]

# =========================================================
# SIGNAL FILTER
# =========================================================

if signal_filter:

    filtered_results = filtered_results[

        filtered_results[
            "Classification"
        ].isin(signal_filter)

    ]

# =========================================================
# SEARCH FILTER
# =========================================================

if search_stock:

    filtered_results = filtered_results[

        filtered_results[
            "Symbol"
        ].str.contains(
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
    st.metric("NSE Universe", len(stocks))

with k2:
    st.metric(
        "Processed Stocks",
        completed + len(failed_stocks)
    )

with k3:
    st.metric(
        "Filtered Opportunities",
        len(filtered_results)
    )

with k4:
    st.metric(
        "Failed Stocks",
        len(failed_stocks)
    )
    
# =========================================================
# CHARTS
# =========================================================

left,right = st.columns(2)

with left:

    signal_data = (
        filtered_results["Classification"]
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
        height=380,
        margin=dict(l=10,r=10,t=40,b=10)
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

with right:

    fig2 = px.scatter(
        filtered_results,
        x="Momentum",
        y="Sharpe",
        color="Classification",
        size="Final Score",
        hover_name="Symbol",
        color_discrete_map=signal_colors,
        title="Risk Reward Opportunity Matrix"
    )

    fig2.update_layout(
        height=380,
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

display_cols = [

    "Symbol",
    "MARKET_CAP",
    "MARKET_CAP_CATEGORY",
    "CMP",
    "STOP_LOSS",
    "TARGET",
    "Classification",
    "Momentum",
    "Sharpe",
    "5D_RETURN_%",
    "15D_RETURN_%",
    "30D_RETURN_%",
    "Final Score",
    "Institutional_Confidence",
    "Conviction",
    "UPSIDE_%",
    "RR_RATIO",
    "ESTIMATED_DAYS"
]

# =====================================================
# FINAL EXPORT DATAFRAME
# =====================================================

export_df = (

    filtered_results[display_cols]

    .sort_values(
        "Final Score",
        ascending=False
    )

)

# =====================================================
# DISPLAY TABLE
# =====================================================

styled_df = export_df.style.background_gradient(

    subset=[

        "Institutional_Confidence",

        "Final Score"

    ],

    cmap="RdYlGn"

)

st.dataframe(

    styled_df,

    use_container_width=True,

    height=550

)

# =====================================================
# EXCEL EXPORT WITH AUTO WIDTH
# =====================================================

from io import BytesIO

output = BytesIO()

with pd.ExcelWriter(
    output,
    engine="openpyxl"
) as writer:

    export_df.to_excel(

        writer,

        index=False,

        sheet_name="Institutional Rankings"

    )

    worksheet = writer.sheets[
        "Institutional Rankings"
    ]

    # =================================================
    # AUTO FIT COLUMN WIDTH
    # =================================================

    for column_cells in worksheet.columns:

        max_length = 0

        column_letter = (
            column_cells[0].column_letter
        )

        for cell in column_cells:

            try:

                cell_length = len(
                    str(cell.value)
                )

                if cell_length > max_length:

                    max_length = cell_length

            except:
                pass

        adjusted_width = max_length + 4

        worksheet.column_dimensions[
            column_letter
        ].width = adjusted_width

excel_data = output.getvalue()

# =====================================================
# DOWNLOAD BUTTON
# =====================================================

st.download_button(

    label="📥 Download Excel Report",

    data=excel_data,

    file_name="institutional_rankings.xlsx",

    mime=(
        "application/vnd.openxmlformats-"
        "officedocument.spreadsheetml.sheet"
    )

)
