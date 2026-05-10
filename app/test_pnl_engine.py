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

# =====================================================
# LOAD TRADES
# =====================================================

engine = PaperTradingEngine()

report = engine.report()

# =====================================================
# PNL ENGINE
# =====================================================

pnl_engine = PNLEngine(

    report["Trades"]
)

positions_df = (

    pnl_engine.position_analysis()
)

summary = pnl_engine.total_pnl()

# =====================================================
# OUTPUT
# =====================================================

print(

    "\nPOSITION PNL ANALYSIS\n"
)

print(positions_df)

print(

    "\nTOTAL PNL\n"
)

print(summary)