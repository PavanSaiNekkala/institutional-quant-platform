import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from pathlib import Path

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(

    page_title="Institutional Quant Platform by Nekky_29",

    layout="wide",

    initial_sidebar_state="expanded"
)

# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent

DATA_DIR = ROOT_DIR / "data"

# =========================================================
# LOAD FILES
# =========================================================

@st.cache_data
def load_csv(file_name):

    path = DATA_DIR / file_name

    if path.exists():

        return pd.read_csv(path)

    return None

factor_df = load_csv(
    "factor_model_rankings.csv"
)
if factor_df is None:

    st.error(
        "factor_model_rankings.csv missing"
    )

    st.stop()

meta_df = load_csv(
    "meta_strategy_portfolio.csv"
)

rl_df = load_csv(
    "reinforcement_portfolio.csv"
)

regime_df = load_csv(
    "market_regime_v2.csv"
)

execution_df = load_csv(
    "execution_simulation.csv"
)

ml_df = load_csv(
    "ml_alpha_predictions.csv"
)

expected_df = load_csv(
    "expected_returns.csv"
)

portfolio_df = load_csv(
    "portfolio_intelligence.csv"
)

risk_summary = load_csv(
    "portfolio_risk_summary.csv"
)

equity_curve_df = load_csv(
    "walk_forward_equity_curve.csv"
)

health_df = load_csv(
    "pipeline_health.csv"
)

required_files = {

    "factor_model_rankings.csv": factor_df,
    "expected_returns.csv": expected_df,
    "walk_forward_equity_curve.csv": equity_curve_df,
    "portfolio_intelligence.csv": portfolio_df,
    "portfolio_risk_summary.csv": risk_summary,
    "meta_strategy_portfolio.csv": meta_df,
    "reinforcement_portfolio.csv": rl_df,
    "market_regime_v2.csv": regime_df,
    "execution_simulation.csv": execution_df,
    "ml_alpha_predictions.csv": ml_df 
}

missing = [

    name

    for name, df in required_files.items()

    if df is None
]

if missing:

    st.error(

        "Missing data files:\n\n"

        + "\n".join(missing)
    )

    st.stop()

 # =========================================================
# DATA VALIDATION
# =========================================================

def validate_dataframe(
    df,
    name,
    required_cols=None
):

    if df is None:

        st.error(
            f"❌ {name} file not found"
        )

        return False

    if required_cols:

        missing = [

            c

            for c in required_cols

            if c not in df.columns
        ]

        if missing:

            st.error(
                f"❌ {name} missing columns: {missing}"
            )

            return False

    return True

# =========================================================
# SIDEBAR
# =========================================================

import subprocess
import sys

if st.sidebar.button(
    "🚀 Run Pipeline"
):

    with st.spinner(
        "Running Pipeline..."
    ):

        result = subprocess.run(
            [
                sys.executable,
                "run_full_pipeline.py"
            ]
        )

    if result.returncode == 0:

        st.success(
            "Pipeline Completed"
        )

        st.rerun()

    else:

        st.error(
            "Pipeline Failed"
        )
        
st.sidebar.title("🏦 Institutional Quant Platform by Nekky_29")

available_cols = [
    c for c in [
        "Symbol",
        "EXPECTED_RETURN_5D",
        "EXPECTED_RETURN_15D",
        "EXPECTED_RETURN_30D",
        "EST_HOLD_DAYS"
    ]
    if c in portfolio_df.columns
]

signals_df = expected_df.copy()

signals_df["CONFIDENCE"] = (
    signals_df["EXPECTED_RETURN_30D"]
    .rank(pct=True) * 100
).round(0)

signals_df = signals_df.sort_values(
    "CONFIDENCE",
    ascending=False
)
# ---------------------------
# Sidebar Page Visibility
# ---------------------------

ALL_PAGES = [
    "Dashboard",
    "Market Regime",
    "Expected Returns",
    "Live Signals",
    "Portfolio Intelligence",
    "Portfolio Performance",
    "Meta Strategy",
    "Reinforcement Learning",
    "ML Alpha",
    "Execution Analytics",
    "Performance Analytics",
    "Pipeline Health"
]

DEFAULT_PAGES = [
    "Dashboard",
    "Live Signals",
    "Expected Returns",
    "Execution Analytics",
    "Portfolio Intelligence",
    "Portfolio Performance"
]

with st.sidebar.expander("⚙️ Customize Sidebar", expanded=False):
    visible_pages = st.multiselect(
        "Visible Pages",
        ALL_PAGES,
        default=DEFAULT_PAGES
    )

page = st.sidebar.radio(
    "Navigation",
    visible_pages
)

# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":

    if not validate_dataframe(
        factor_df,
        "Factor Rankings",
        [
            "MULTI_FACTOR_SCORE",
            "Sharpe",
            "Sector"
        ]
    ):
        st.stop()

    # =====================================
    # MARKET REGIME BANNER
    # =====================================

    if regime_df is not None and len(regime_df):

        regime = regime_df.iloc[0].get(
            "MARKET_REGIME",
            "UNKNOWN"
        )

        if regime.upper() == "BULL":

            st.success(
                f"🟢 Current Market Regime: {regime}"
            )

        elif regime.upper() == "BEAR":

            st.error(
                f"🔴 Current Market Regime: {regime}"
            )

        else:

            st.warning(
                f"🟡 Current Market Regime: {regime}"
            )

    st.title(
        "🏦 Institutional Quant Dashboard"
    )

    # -----------------------------------------------------
    # INSTITUTIONAL KPI CARDS
    # -----------------------------------------------------
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric(
            "Stocks Universe",
            len(factor_df)
        )

    with col2:
        st.metric(
            "Avg Factor Score",
            round(
                factor_df["MULTI_FACTOR_SCORE"].mean(),
                2
            )
        )

    with col3:
        st.metric(
            "Avg Sharpe",
            round(
                factor_df["Sharpe"].mean(),
                2
            )
        )

    with col4:
        st.metric(
            "Expected Return (30D)",
            f"{portfolio_df['EXPECTED_RETURN_30D'].mean():.2f}%"
        )

    with col5:

        portfolio_vol = None

        if risk_summary is not None:

            vol_row = risk_summary[
                risk_summary["Metric"] == "Portfolio Volatility"
            ]

            if not vol_row.empty:
                portfolio_vol = vol_row["Value"].iloc[0]

        st.metric(
            "Portfolio Volatility",
            (
                f"{portfolio_vol:.2f}%"
                if portfolio_vol is not None
                else "N/A"
            )
        )

    with col6:
        st.metric(
            "Holdings",
            len(portfolio_df)
        )

    st.divider()
    # -----------------------------------------------------
    # PORTFOLIO VISUALS
    # -----------------------------------------------------

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:

        st.subheader("📊 Sector Distribution")

        sector_counts = (
            factor_df["Sector"]
            .value_counts()
            .head(10)
        )

        fig = px.pie(
            values=sector_counts.values,
            names=sector_counts.index,
            title="Sector Allocation"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )
        
    with chart_col2:

        st.subheader(
            "📈 Factor Score Distribution"
        )

        fig = px.histogram(
            factor_df,
            x="MULTI_FACTOR_SCORE",
            nbins=40
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )
    # -----------------------------------------------------
    # TOP STOCKS
    # -----------------------------------------------------

    st.subheader(
            "🏆 Top 25 Institutional Picks"
        )

    top_df = (
        factor_df
        .sort_values(
            "MULTI_FACTOR_SCORE",
            ascending=False
        )
        .head(25)
    )

    display_cols = [

        "Symbol",

        "Sector",

        "MULTI_FACTOR_SCORE",

        "Sharpe"
    ]
    
    st.dataframe(
        top_df[display_cols],
        use_container_width=True
    )
        
# =========================================================
# MARKET REGIME
# =========================================================
elif page == "Market Regime":

    if not validate_dataframe(
        regime_df,
        "Market Regime",
        [
            "MARKET_REGIME",
            "MARKET_SCORE"
        ]
    ):
        st.stop()

    st.title(
        "🌍 Institutional Regime Engine"
    )

    if regime_df is None or len(regime_df) == 0:

        st.error(
            "market_regime_v2.csv not found or empty"
        )

    else:

        st.dataframe(
            regime_df,
            use_container_width=True
        )

        # -----------------------------------------
        # SAFE COLUMN ACCESS
        # -----------------------------------------

        regime = regime_df.iloc[0].get(
            "MARKET_REGIME",
            "UNKNOWN"
        )

        score = regime_df.iloc[0].get(
            "MARKET_SCORE",
            0
        )

        col1, col2 = st.columns(2)

        col1.metric(
            "Current Regime",
            regime
        )

        col2.metric(
            "Market Score",
            score
        )

        # -----------------------------------------
        # REGIME INTERPRETATION
        # -----------------------------------------

        if score >= 2:

            st.success(
                "Bullish Regime Detected"
            )

        elif score <= -2:

            st.error(
                "Bearish Regime Detected"
            )

        else:

            st.warning(
                "Neutral Market Regime"
            )

# =========================================================
# EXPECTED RETURNS
# =========================================================
elif page == "Expected Returns":

    if not validate_dataframe(
        expected_df,
        "Expected Returns",
        [
            "EXPECTED_RETURN_5D",
            "EXPECTED_RETURN_15D",
            "EXPECTED_RETURN_30D",
            "EST_HOLD_DAYS",
            "SIGNAL"
        ]
    ):
        st.stop()

    st.title(
        "🎯 Expected Return Engine"
    )
    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Avg 5D Return %",
        round(
            expected_df["EXPECTED_RETURN_5D"].mean(),
            2
        )
    )

    c2.metric(
        "Avg 15D Return %",
        round(
            expected_df["EXPECTED_RETURN_15D"].mean(),
            2
        )
    )

    c3.metric(
        "Avg 30D Return %",
        round(
            expected_df["EXPECTED_RETURN_30D"].mean(),
            2
        )
    )

    c4.metric(
        "Avg Hold Days",
        round(
            expected_df["EST_HOLD_DAYS"].mean(),
            0
        )
    )

    st.dataframe(
        expected_df.sort_values(
            "EXPECTED_RETURN_30D",
            ascending=False
        ),
        use_container_width=True
    )

    st.subheader(
        "Top 20 Expected Return Stocks"
    )

    top20 = expected_df.sort_values(
        "EXPECTED_RETURN_30D",
        ascending=False
    ).head(20)

    fig = px.bar(
        top20,
        x="Symbol",
        y="EXPECTED_RETURN_30D",
        hover_data=[
            "EXPECTED_RETURN_5D",
            "EXPECTED_RETURN_15D",
            "EST_HOLD_DAYS"
        ]
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


elif page == "Live Signals":

    st.title("📡 Live Trading Signals")

    st.dataframe(
        signals_df,
        use_container_width=True
    )

    st.subheader("Top Signals")

    top5 = signals_df.head(5)

    for _, row in top5.iterrows():

        st.success(
            f"""
            🚀 {row['Symbol']}
            Confidence: {row['CONFIDENCE']}%
            30D Return: {row['EXPECTED_RETURN_30D']:.2f}%
            Hold: {row['EST_HOLD_DAYS']} Days
            """
        )
# =========================================================
# PORTFOLIO INTELLIGENCE
# =========================================================

elif page == "Portfolio Intelligence":

    if not validate_dataframe(
        portfolio_df,
        "Portfolio Intelligence",
        [
            "WEIGHTED_5D",
            "WEIGHTED_15D",
            "WEIGHTED_30D",
            "EST_HOLD_DAYS"
        ]
    ):
        st.stop()
        
    st.title(
        "🧠 Portfolio Intelligence"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Exp Return 5D",
        round(
            portfolio_df["WEIGHTED_5D"].sum(),
            2
        )
    )

    c2.metric(
        "Exp Return 15D",
        round(
            portfolio_df["WEIGHTED_15D"].sum(),
            2
        )
    )

    c3.metric(
        "Exp Return 30D",
        round(
            portfolio_df["WEIGHTED_30D"].sum(),
            2
        )
    )

    c4.metric(
        "Avg Hold Days",
        round(
            portfolio_df["EST_HOLD_DAYS"].mean(),
            0
        )
    )

    st.dataframe(
        portfolio_df,
        use_container_width=True
    )

# =========================================================
# PORTFOLIO PERFORMANCE
# =========================================================

elif page == "Portfolio Performance":

    if not validate_dataframe(
        equity_curve_df,
        "Portfolio Performance",
        [
            "Date",
            "Portfolio_Value"
        ]
    ):
        st.stop()

    st.title(
        "📈 Portfolio Performance"
    )

    fig_equity = px.line(
        equity_curve_df,
        x="Date",
        y="Portfolio_Value",
        title="Portfolio Equity Curve"
    )

    st.plotly_chart(
        fig_equity,
        use_container_width=True
    )

    equity_curve_df["Peak"] = (
        equity_curve_df["Portfolio_Value"]
        .cummax()
    )

    equity_curve_df["Drawdown"] = (
        equity_curve_df["Portfolio_Value"]
        /
        equity_curve_df["Peak"]
        - 1
    ) * 100

    fig_dd = px.area(
        equity_curve_df,
        x="Date",
        y="Drawdown",
        title="Portfolio Drawdown (%)"
    )

    st.plotly_chart(
        fig_dd,
        use_container_width=True
    )
    
# =========================================================
# META STRATEGY
# =========================================================

elif page == "Meta Strategy":

    if not validate_dataframe(
        meta_df,
        "Meta Portfolio",
        [
            "Symbol",
            "FINAL_WEIGHT",
            "EXPECTED_RETURN_5D",
            "EXPECTED_RETURN_15D",
            "EXPECTED_RETURN_30D",
            "EST_HOLD_DAYS",
            "SIGNAL"
        ]
    ):
        st.stop()

    st.title(
        "🧠 Meta Strategy Portfolio"
    )


    # ==========================================
    # PORTFOLIO KPIs
    # ==========================================

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Expected 5D Return %",
        round(
            meta_df["EXPECTED_RETURN_5D"].mean(),
            2
        )
    )

    c2.metric(
        "Expected 15D Return %",
        round(
            meta_df["EXPECTED_RETURN_15D"].mean(),
            2
        )
    )

    c3.metric(
        "Expected 30D Return %",
        round(
            meta_df["EXPECTED_RETURN_30D"].mean(),
            2
        )
    )

    c4.metric(
        "Avg Hold Days",
        round(
            meta_df["EST_HOLD_DAYS"].mean(),
            0
        )
    )
    
    st.divider()

    display_cols = [

        "Symbol",

        "FINAL_WEIGHT",

        "EXPECTED_RETURN_5D",

        "EXPECTED_RETURN_15D",

        "EXPECTED_RETURN_30D",

        "EST_HOLD_DAYS",

        "SIGNAL"
    ]

    st.dataframe(

        meta_df[display_cols]

        .sort_values(
            "EXPECTED_RETURN_30D",
            ascending=False
        ),

        use_container_width=True
    )

    fig = px.pie(

        meta_df.head(15),

        names="Symbol",

        values="FINAL_WEIGHT"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
   
# =========================================================
# RL PORTFOLIO
# =========================================================

elif page == "Reinforcement Learning":
    if not validate_dataframe(
        rl_df,
        "RL Portfolio",
        ["FINAL_RL_SCORE"]
    ):
        st.stop()

    st.title(
        "🤖 Reinforcement Learning Portfolio"
    )

    st.dataframe(
        rl_df,
        use_container_width=True
    )

    fig = px.bar(

        rl_df.head(20),

        x="Symbol",

        y="FINAL_RL_SCORE"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =========================================================
# ML ALPHA
# =========================================================

elif page == "ML Alpha":
    if not validate_dataframe(
        ml_df,
        "ML Alpha",
        ["ML_PREDICTED_ALPHA"]
    ):
        st.stop()

    st.title(
        "🧠 ML Alpha Predictions"
    )

    top_ml = ml_df.sort_values(

        by="ML_PREDICTED_ALPHA",

        ascending=False
    ).head(50)

    display_cols = [
        "Symbol",
        "Sector",
        "ML_PREDICTED_ALPHA",
        "Momentum"
    ]

    st.dataframe(
        top_ml[display_cols],
        use_container_width=True
    )

    fig = px.scatter(

        top_ml,

        x="Momentum",

        y="ML_PREDICTED_ALPHA",

        color="Sector",

        hover_data=["Symbol"]
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =========================================================
# EXECUTION ANALYTICS
# =========================================================

elif page == "Execution Analytics":
    if not validate_dataframe(
        execution_df,
        "Execution Analytics"
    ):
        st.stop()

    st.title(
        "🏦 Institutional Execution Analytics"
    )

    st.dataframe(
        execution_df,
        use_container_width=True
    )

    # -----------------------------------------------------
    # COST BREAKDOWN
    # -----------------------------------------------------

    fig = go.Figure()

    fig.add_trace(

        go.Bar(

            x=execution_df["Symbol"],

            y=execution_df["TOTAL_COST"],

            name="Execution Cost"
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # -----------------------------------------------------
    # EXECUTION SCORE
    # -----------------------------------------------------

    fig = px.scatter(

        execution_df,

        x="TARGET_CAPITAL",

        y="EXECUTION_SCORE",

        color="LIQUIDITY_FLAG",

        hover_data=["Symbol"]
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =========================================================
# PERFORMANCE ANALYTICS
# =========================================================

elif page == "Performance Analytics":

    st.title("📊 Performance Analytics")

    if equity_curve_df is None:

        st.error(
            "walk_forward_equity_curve.csv missing"
        )

    else:

        initial = equity_curve_df[
            "Portfolio_Value"
        ].iloc[0]

        final = equity_curve_df[
            "Portfolio_Value"
        ].iloc[-1]

        total_return = (
            (final / initial) - 1
        ) * 100

        c1, c2 = st.columns(2)

        c1.metric(
            "Starting Value",
            f"${initial:,.0f}"
        )

        c2.metric(
            "Total Return",
            f"{total_return:.2f}%"
        )

        fig = px.line(
            equity_curve_df,
            x="Date",
            y="Portfolio_Value",
            title="Portfolio Growth"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )
# =========================================================
# PIPELINE HEALTH
# =========================================================

elif page == "Pipeline Health":

    st.title("🛠 Pipeline Health")

    if health_df is None:

        st.error("pipeline_health.csv not found")

    else:

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Pipeline Runs",
            len(health_df)
        )

        c2.metric(
            "Success Rate",
            f"{health_df['SUCCESS'].mean()*100:.1f}%"
        )

        c3.metric(
            "Avg Runtime",
            f"{health_df['RUNTIME_SEC'].mean():.0f}s"
        )

        fig = px.line(
            health_df,
            x="TIMESTAMP",
            y="RUNTIME_SEC",
            title="Pipeline Runtime Trend"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.dataframe(
            health_df,
            use_container_width=True
        )
