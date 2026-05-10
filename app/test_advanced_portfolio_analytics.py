import sys

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from paper_trading.paper_trading_engine import (
    PaperTradingEngine
)

from portfolio.advanced_portfolio_analytics import (
    AdvancedPortfolioAnalytics
)

# =====================================================
# LOAD ENGINE
# =====================================================

engine = PaperTradingEngine()

report = engine.report()

# =====================================================
# ANALYTICS
# =====================================================

analytics = AdvancedPortfolioAnalytics(

    positions=report["Positions"],

    trades=report["Trades"],

    cash=report["Cash"]
)

summary, holdings_df = (

    analytics.full_report()
)

# =====================================================
# OUTPUT
# =====================================================

print(

    "\nADVANCED PORTFOLIO ANALYTICS\n"
)

print(summary)

print(

    "\nHOLDINGS\n"
)

print(holdings_df)