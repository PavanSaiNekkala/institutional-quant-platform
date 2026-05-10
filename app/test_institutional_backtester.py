import sys

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from core.universe_loader import (
    load_ranked_universe
)

from backtesting.institutional_backtester import (
    InstitutionalBacktester
)

# =====================================================
# SYMBOLS
# =====================================================

symbols = load_ranked_universe(

    top_n=10
)

# =====================================================
# ENGINE
# =====================================================

engine = InstitutionalBacktester(

    initial_capital=100000
)

results = engine.run_backtest(

    symbols,

    period="1y"
)

# =====================================================
# OUTPUT
# =====================================================

print(

    "\nBACKTEST RESULTS\n"
)

print(

    results["metrics"]
)

print(

    "\nEQUITY CURVE\n"
)

print(

    results["equity_curve"].tail()
)