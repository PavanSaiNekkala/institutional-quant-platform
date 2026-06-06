import sys

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from paper_trading.paper_trading_engine import (
    PaperTradingEngine
)

# =====================================================
# ENGINE
# =====================================================

engine = PaperTradingEngine(

    initial_cash=100000
)

# =====================================================
# EXECUTE TRADES
# =====================================================

print(

    engine.buy(

        "RELIANCE.NS",

        10
    )
)

print(

    engine.buy(

        "TCS.NS",

        5
    )
)

print(

    engine.sell(

        "RELIANCE.NS",

        5
    )
)

# =====================================================
# REPORT
# =====================================================

report = engine.report()

print(

    "\nPAPER TRADING REPORT\n"
)

print(report)
