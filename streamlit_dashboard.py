import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from pathlib import Path

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(

    page_title="Institutional Quant Platform",

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

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🏦 Institutional Quant Platform")

page = st.sidebar.radio(

    "Navigation",

    [

        "Dashboard",

        "Market Regime",

        "Meta Strategy",

        "Reinforcement Learning",

        "ML Alpha",

        "Execution Analytics"

    ]
)

# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":

    st.title(
        "🏦 Institutional Quant Dashboard"
    )

    # -----------------------------------------------------
    # KPIs
    # -----------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    total_stocks = len(factor_df)

    avg_score = round(

        factor_df[
            "MULTI_FACTOR_SCORE"
        ].mean(),

        2
    )

    top_sector = (

        factor_df["Sector"]

        .value_counts()

        .idxmax()
    )

    avg_sharpe = round(

        factor_df["Sharpe"]

        .mean(),

        2
    )

    col1.metric(
        "Total Stocks",
        total_stocks
    )

    col2.metric(
        "Avg Factor Score",
        avg_score
    )

    col3.metric(
        "Top Sector",
        top_sector
    )

    col4.metric(
        "Avg Sharpe",
        avg_sharpe
    )

    st.divider()

    # -----------------------------------------------------
    # TOP STOCKS
    # -----------------------------------------------------

    st.subheader(
        "🏆 Top Multi-Factor Stocks"
    )

    top_df = factor_df.sort_values(

        by="MULTI_FACTOR_SCORE",

        ascending=False
    ).head(25)

    st.dataframe(
        top_df,
        use_container_width=True
    )

    # -----------------------------------------------------
    # SCORE DISTRIBUTION
    # -----------------------------------------------------

    st.subheader(
        "📊 Factor Score Distribution"
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
    # SECTOR DISTRIBUTION
    # -----------------------------------------------------

    st.subheader(
        "🏭 Sector Allocation"
    )

    sector_counts = (

        factor_df["Sector"]

        .value_counts()

        .head(15)
    )

    fig = px.bar(

        sector_counts,

        x=sector_counts.index,

        y=sector_counts.values
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =========================================================
# MARKET REGIME
# =========================================================

elif page == "Market Regime":

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
# META STRATEGY
# =========================================================

elif page == "Meta Strategy":

    st.title(
        "🧠 Meta Strategy Portfolio"
    )

    st.dataframe(
        meta_df,
        use_container_width=True
    )

    # -----------------------------------------------------
    # WEIGHT CHART
    # -----------------------------------------------------

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

    st.title(
        "🧠 ML Alpha Predictions"
    )

    top_ml = ml_df.sort_values(

        by="ML_PREDICTED_ALPHA",

        ascending=False
    ).head(50)

    st.dataframe(
        top_ml,
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