# =========================================================
# ENTERPRISE INSTITUTIONAL QUANT PLATFORM
# =========================================================

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
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
# POWERBI + BLOOMBERG STYLE CSS
# =========================================================

st.markdown("""
<style>

.stApp{
    background:#F4F7FB;
    font-family:'Segoe UI',sans-serif;
}

.block-container{
    padding-top:1rem;
    padding-bottom:1rem;
    max-width:100%;
}

section[data-testid="stSidebar"]{
    background:#0F172A;
    border-right:1px solid #1E293B;
}

section[data-testid="stSidebar"] *{
    color:white !important;
}

.metric-card{
    background:white;
    padding:22px;
    border-radius:18px;
    box-shadow:0 6px 18px rgba(0,0,0,0.08);
    border-left:6px solid #2563EB;
}

.metric-title{
    font-size:15px;
    color:#64748B;
    font-weight:600;
}

.metric-value{
    font-size:34px;
    font-weight:800;
    color:#111827;
}

.glass-card{
    background:white;
    border-radius:20px;
    padding:18px;
    box-shadow:0 8px 20px rgba(0,0,0,0.06);
    margin-bottom:16px;
}

.progress-container{
    background:#E5E7EB;
    border-radius:12px;
    overflow:hidden;
    height:20px;
}

.progress-bar{
    height:20px;
    border-radius:12px;
    background:linear-gradient(90deg,#2563EB,#06B6D4);
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div style="
font-size:48px;
font-weight:900;
color:#0F172A;
">
📊 Institutional Quant Platform
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="
font-size:18px;
font-weight:600;
color:#475569;
margin-bottom:15px;
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
# LOAD STOCK UNIVERSE
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

    st.markdown("## ⚙️ Institutional Controls")

    signal_filter = st.multiselect(
        "Trade Signal",
        [
            "STRONG_BUY",
            "BUY",
            "WATCH",
            "HOLD",
            "AVOID"
        ]
    )

    min_score = st.slider(
        "Minimum Score",
        0,
        100,
        60
    )

    search_stock = st.text_input(
        "Search Stock"
    )

    st.markdown("---")

    st.success(
        f"Universe Loaded: {len(stocks)}"
    )

# =========================================================
# SIGNAL COLORS
# =========================================================

signal_colors = {

    "STRONG_BUY":"#006400",

    "BUY":"#32CD32",

    "WATCH":"#F59E0B",

    "HOLD":"#2563EB",

    "AVOID":"#DC2626"
}

# =========================================================
# PROGRESS BAR
# =========================================================

progress_placeholder = st.empty()

progress_bar = st.progress(0)

# =========================================================
# ANALYSIS ENGINE
# =========================================================

@st.cache_data(ttl=3600, show_spinner=False)
def run_analysis(stock_list):

    results = []

    total = len(stock_list)

    processed = 0

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

            continue

        for stock in batch:

            try:

                close = data[stock]["Close"].dropna()

                high = data[stock]["High"].dropna()

                low = data[stock]["Low"].dropna()

                if len(close) < 40:
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

                tr1 = high - low

                tr2 = abs(high - close.shift(1))

                tr3 = abs(low - close.shift(1))

                tr = pd.concat(
                    [tr1,tr2,tr3],
                    axis=1
                ).max(axis=1)

                atr = tr.rolling(14).mean().iloc[-1]

                score = (
                    momentum * 0.6
                    +
                    sharpe * 0.4
                )

                percentile = min(
                    max(
                        score * 100,
                        0
                    ),
                    100
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

                cmp_price = close.iloc[-1]

                stop_loss = round(
                    cmp_price - (atr * 2),
                    2
                )

                target = round(
                    cmp_price + (atr * 3),
                    2
                )

                rr = round(
                    (
                        target - cmp_price
                    )
                    /
                    max(
                        cmp_price - stop_loss,
                        1
                    ),
                    2
                )

                results.append({

                    "Symbol": stock,

                    "CMP": round(cmp_price,2),

                    "Momentum": round(momentum*100,2),

                    "Sharpe": round(sharpe,2),

                    "Final Score": round(score,2),

                    "Percentile": round(percentile,2),

                    "Classification": signal,

                    "ATR": round(atr,2),

                    "TARGET": target,

                    "STOP_LOSS": stop_loss,

                    "RR_RATIO": rr

                })

            except:
                pass

            processed += 1

            pct = int((processed/total)*100)

            progress_bar.progress(pct)

            progress_placeholder.info(
                f"Processing Institutional Universe: {pct}%"
            )

    return pd.DataFrame(results)

# =========================================================
# RUN ANALYSIS
# =========================================================

results = run_analysis(stocks)

progress_placeholder.success(
    "Institutional Analysis Completed"
)

# =========================================================
# FILTERS
# =========================================================

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
# KPI DASHBOARD
# =========================================================

c1,c2,c3,c4 = st.columns(4)

with c1:

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">
        NSE Universe
        </div>

        <div class="metric-value">
        {len(stocks)}
        </div>
    </div>
    """, unsafe_allow_html=True)

with c2:

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">
        Opportunities
        </div>

        <div class="metric-value">
        {len(results)}
        </div>
    </div>
    """, unsafe_allow_html=True)

with c3:

    avg_score = round(
        results["Percentile"].mean(),
        2
    )

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">
        Avg Institutional Score
        </div>

        <div class="metric-value">
        {avg_score}
        </div>
    </div>
    """, unsafe_allow_html=True)

with c4:

    elite = len(
        results[
            results["Classification"]
            ==
            "STRONG_BUY"
        ]
    )

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">
        Elite Setups
        </div>

        <div class="metric-value">
        {elite}
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =========================================================
# CHART SECTION
# =========================================================

left,right = st.columns(2)

with left:

    signal_df = (
        results["Classification"]
        .value_counts()
        .reset_index()
    )

    signal_df.columns = [
        "Signal",
        "Count"
    ]

    fig1 = px.pie(

        signal_df,

        names="Signal",

        values="Count",

        hole=0.6,

        color="Signal",

        color_discrete_map=signal_colors,

        title="Institutional Signal Distribution"
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

        size="Percentile",

        color="Classification",

        hover_name="Symbol",

        color_discrete_map=signal_colors,

        title="Institutional Opportunity Matrix"
    )

    fig2.update_layout(
        height=450
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# =========================================================
# TOP OPPORTUNITIES
# =========================================================

st.markdown("## 🏆 Top Institutional Opportunities")

top_df = results.sort_values(
    "Percentile",
    ascending=False
).head(15)

bar_fig = px.bar(

    top_df,

    x="Symbol",

    y="Percentile",

    color="Classification",

    color_discrete_map=signal_colors,

    text="Percentile"
)

bar_fig.update_layout(
    height=500
)

st.plotly_chart(
    bar_fig,
    use_container_width=True
)

# =========================================================
# HEATMAP
# =========================================================

st.markdown("## 🔥 Institutional Heatmap")

heatmap_fig = px.treemap(

    top_df,

    path=["Classification","Symbol"],

    values="Percentile",

    color="Percentile",

    color_continuous_scale="RdYlGn"
)

heatmap_fig.update_layout(
    height=600
)

st.plotly_chart(
    heatmap_fig,
    use_container_width=True
)

# =========================================================
# TABLE
# =========================================================

st.markdown("## 📋 Institutional Rankings")

display_cols = [

    "Symbol",

    "CMP",

    "Classification",

    "Momentum",

    "Sharpe",

    "Percentile",

    "TARGET",

    "STOP_LOSS",

    "RR_RATIO"
]

st.dataframe(

    results[display_cols]

    .sort_values(
        "Percentile",
        ascending=False
    ),

    use_container_width=True,

    height=700
)

# =========================================================
# DOWNLOAD
# =========================================================

csv = results.to_csv(index=False)

st.download_button(

    "⬇ Download Institutional Dataset",

    csv,

    "institutional_quant.csv",

    "text/csv"
)
