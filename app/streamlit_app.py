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
        ]
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

    batch_size = 50

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

            for symbol in batch:

                if symbol not in failed_stocks:
                    failed_stocks.add(symbol)

            continue

        for symbol in batch:

            try:

                if symbol not in data.columns.levels[0]:

                    if symbol not in failed_stocks:
                        failed_stocks.add(symbol)

                    continue

                close = data[symbol]["Close"].dropna()
                # =====================================================
                # MARKET CAP FROM CSV
                # =====================================================

                clean_symbol = symbol.replace(
                    ".NS",
                    ""
                )

                market_cap = market_cap_map.get(
                    clean_symbol,
                    0
                )

                # =====================================================
                # MARKET CAP CATEGORY
                # =====================================================

                if market_cap >= 2_00_000_00_00_000:

                    market_cap_category = "Large Cap"

                elif market_cap >= 20_000_00_000:

                    market_cap_category = "Mid Cap"

                else:

                    market_cap_category = "Small Cap"

                # =====================================================
                # MARKET CAP DISPLAY
                # =====================================================

                if market_cap >= 1_00_000_00_00_000:

                    market_cap_display = (
                        f"{round(market_cap / 1_00_000_00_00_000, 2)} LCr"
                    )

                elif market_cap >= 1_00_00_00_000:

                    market_cap_display = (
                        f"{round(market_cap / 1_00_00_00_000, 2)} Cr"
                    )

                else:

                    market_cap_display = str(market_cap)
                
                if len(close) < 40:

                    if symbol not in failed_stocks:
                        failed_stocks.add(symbol)

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

                # =====================================================
                # RAW SCORE
                # =====================================================

                score = (
                    momentum * 0.6
                    + sharpe * 0.4
                )

                # =====================================================
                # INSTITUTIONAL CLASSIFICATION
                # =====================================================

                if score >= 1.0:

                    signal = "STRONG_BUY"

                elif score >= 0.75:

                    signal = "BUY"

                elif score >= 0.5:

                    signal = "WATCH"

                elif score >= 0.25:

                    signal = "HOLD"

                else:

                    signal = "AVOID"
                    
                # =====================================================
                # STOPLOSS
                # =====================================================

                stop_loss = round(
                    close.iloc[-1] - (
                        close.iloc[-1] * 0.04
                    ),
                    2
                )

                # =====================================================
                # TARGET
                # =====================================================

                target = round(
                    close.iloc[-1] + (
                        close.iloc[-1] * 0.10
                    ),
                    2
                )

                # =====================================================
                # UPSIDE %
                # =====================================================

                upside_pct = round(
                    (
                        (
                            target - close.iloc[-1]
                        )
                        /
                        close.iloc[-1]
                    ) * 100,
                    2
                )

                # =====================================================
                # RISK REWARD
                # =====================================================

                risk = max(
                    close.iloc[-1] - stop_loss,
                    1
                )

                reward = max(
                    target - close.iloc[-1],
                    0
                )

                rr_ratio = round(
                    reward / risk,
                    2
                )

                # =====================================================
                # ESTIMATED DAYS
                # =====================================================

                daily_move = max(
                    close.pct_change().std() * close.iloc[-1],
                    1
                )

                estimated_days = round(
                    max(
                       reward / daily_move,
                        1
                    )
                )
                results.append({
                    "Symbol": symbol,
                    "MARKET_CAP": market_cap_display,
                    "MARKET_CAP_CATEGORY": market_cap_category,
                    "CMP": safe_round(close.iloc[-1]),
                    "STOP_LOSS": stop_loss,
                    "TARGET": target,
                    "Momentum": safe_round(momentum * 100), 
                    "Sharpe": safe_round(sharpe),
                    "Final Score": safe_round(score),
                    "Classification": signal,
                    "UPSIDE_%": upside_pct,
                    "RR_RATIO": rr_ratio,
                    "ESTIMATED_DAYS": estimated_days
                })
                
                completed += 1

            except:

                if symbol not in failed_stocks:
                    failed_stocks.add(symbol)

            elapsed = (time.time() - start_time) / 60

            processed_count = (
                completed +
                len(failed_stocks)
            )

            estimated_total = (
                elapsed /
                max(processed_count,1)
            ) * total

            remaining_minutes = round(
                max(estimated_total - elapsed, 0),
                1
            )

            completion_pct = round(
                (
                    (
                        completed +
                        len(failed_stocks)
                    ) / total
                ) * 100,
                1
            )

            if completed % 50 == 0:

                status_html = f"""
                <div class="processing-container" style="
                    background:white;
                    border-radius:18px;
                    padding:20px;
                    width:100%;
                    box-sizing:border-box;
                    box-shadow:0 6px 20px rgba(0,0,0,0.08);
                    margin-top:8px;
                    font-family:Segoe UI;
                ">

                <div style="
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                    margin-bottom:14px;
                ">

                    <div>

                        <div style="
                            font-size:30px;
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
                        padding:8px 14px;
                        border-radius:10px;
                        font-weight:800;
                        font-size:12px;
                    ">
                    LIVE
                    </div>

                </div>

                <div style="
                    display:grid;
                    grid-template-columns:
                    repeat(auto-fit,minmax(180px,1fr));
                    gap:12px;
                ">

                    <div style="
                        background:#ECFDF5;
                        padding:16px;
                        border-radius:14px;
                        border-left:5px solid #10B981;
                    ">
                        <div style="
                            color:#047857;
                            font-size:12px;
                            font-weight:700;
                        ">
                        COMPLETED
                        </div>

                        <div style="
                            margin-top:8px;
                            font-size:28px;
                            font-weight:900;
                            color:#065F46;
                        ">
                        {completed + len(failed_stocks)}
                        </div>

                        <div style="
                            margin-top:2px;
                            color:#10B981;
                            font-size:12px;
                        ">
                        out of {total}
                        </div>
                    </div>

                    <div style="
                        background:#FEF2F2;
                        padding:16px;
                        border-radius:14px;
                        border-left:5px solid #DC2626;
                    ">
                        <div style="
                            color:#B91C1C;
                            font-size:12px;
                            font-weight:700;
                        ">
                        FAILED
                        </div>

                        <div style="
                            margin-top:8px;
                            font-size:28px;
                            font-weight:900;
                            color:#991B1B;
                        ">
                        {len(failed_stocks)}
                        </div>

                        <div style="
                            margin-top:2px;
                            color:#DC2626;
                            font-size:12px;
                        ">
                        failed stocks
                        </div>
                    </div>

                    <div style="
                        background:#EFF6FF;
                        padding:16px;
                        border-radius:14px;
                        border-left:5px solid #2563EB;
                    ">
                        <div style="
                            color:#1D4ED8;
                            font-size:12px;
                            font-weight:700;
                        ">
                        UNIVERSE
                        </div>

                        <div style="
                            margin-top:8px;
                            font-size:28px;
                            font-weight:900;
                            color:#1E3A8A;
                        ">
                        {total}
                        </div>

                        <div style="
                            margin-top:2px;
                            color:#2563EB;
                            font-size:12px;
                        ">
                        NSE Stocks
                        </div>
                    </div>

                    <div style="
                        background:#FFF7ED;
                        padding:16px;
                        border-radius:14px;
                        border-left:5px solid #F59E0B;
                    ">
                        <div style="
                            color:#D97706;
                            font-size:12px;
                            font-weight:700;
                        ">
                        ETA
                        </div>

                        <div style="
                            margin-top:8px;
                            font-size:28px;
                            font-weight:900;
                            color:#92400E;
                        ">
                        {remaining_minutes}m
                        </div>

                        <div style="
                            margin-top:2px;
                            color:#F59E0B;
                            font-size:12px;
                        ">
                        remaining
                        </div>
                    </div>

                </div>

                <div style="margin-top:18px;">

                    <div style="
                        display:flex;
                        justify-content:space-between;
                        margin-bottom:6px;
                    ">

                        <div style="
                            color:#374151;
                            font-weight:700;
                            font-size:13px;
                        ">
                        Processing Progress
                        </div>

                        <div style="
                            color:#2563EB;
                            font-weight:800;
                            font-size:13px;
                        ">
                        {completion_pct}%
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
                            border-radius:999px;
                        ">
                        </div>

                    </div>

                </div>

                </div>
                """

                with status_placeholder:
                    st.html(status_html)

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
# FILTERS
# =========================================================

results["Percentile"] = (
    results["Final Score"] * 100
)

results = results[
    results["Percentile"] >= min_score
]

if signal_filter:
    # =========================================================
    # MARKET CAP FILTER
    # =========================================================

    if market_cap_filter:
        results = results[
            results["MARKET_CAP_CATEGORY"]
            .isin(market_cap_filter)
        ]

    # =========================================================
    # SIGNAL FILTER
    # =========================================================

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
    st.metric("NSE Universe", len(stocks))

with k2:
    st.metric(
        "Processed Stocks",
        completed + len(failed_stocks)
    )

with k3:
    st.metric(
        "Filtered Opportunities",
        len(results)
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
        height=380,
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

    "Final Score",

    "UPSIDE_%",

    "RR_RATIO",

    "ESTIMATED_DAYS"
]

# =====================================================
# SORT RESULTS
# =====================================================

# =====================================================
# APPLY MARKET CAP FILTER
# =====================================================

filtered_results = results.copy()

# =====================================================
# APPLY SIGNAL FILTER
# =====================================================

if signal_filter:

    filtered_results = filtered_results[

        filtered_results[
            "Classification"
        ].isin(signal_filter)

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

st.dataframe(

    export_df,

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
