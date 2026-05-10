import sys

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from paper_trading.paper_trading_engine import (
    PaperTradingEngine
)

from portfolio.pnl_engine import (
    PNLEngine
)

from portfolio.trade_performance_analytics import (
    TradePerformanceAnalytics
)

# =====================================================
# LOAD PORTFOLIO
# =====================================================

engine = PaperTradingEngine()

report = engine.report()

# =====================================================
# PNL ANALYSIS
# =====================================================

pnl_engine = PNLEngine(

    report["Trades"]
)

positions_df = (

    pnl_engine.position_analysis()
)

# =====================================================
# PERFORMANCE ANALYTICS
# =====================================================

analytics = TradePerformanceAnalytics(

    positions_df
)

summary = analytics.full_report()

# =====================================================
# OUTPUT
# =====================================================

print(

    "\nTRADE PERFORMANCE ANALYTICS\n"
)

print(summary)