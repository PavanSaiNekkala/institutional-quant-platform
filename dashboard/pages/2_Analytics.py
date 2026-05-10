import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

sys.path.append(str(ROOT_DIR))

import streamlit as st
import pandas as pd

from paper_trading.paper_trading_engine import (
    PaperTradingEngine
)

from portfolio.advanced_portfolio_analytics import (
    AdvancedPortfolioAnalytics
)

# =========================================================
# TITLE
# =========================================================

st.title(

    "Portfolio Analytics"
)

engine = PaperTradingEngine()

report = engine.report()

analytics = AdvancedPortfolioAnalytics(

    positions=report["Positions"],

    trades=report["Trades"],

    cash=report["Cash"]
)

summary, holdings_df = (

    analytics.full_report()
)

# =========================================================
# SUMMARY
# =========================================================

summary_df = pd.DataFrame(

    summary.items(),

    columns=[

        "Metric",

        "Value"
    ]
)

st.dataframe(

    summary_df,

    use_container_width=True
)

# =========================================================
# HOLDINGS
# =========================================================

st.dataframe(

    holdings_df,

    use_container_width=True
)