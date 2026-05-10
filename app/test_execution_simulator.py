import sys

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from core.universe_loader import (
    load_ranked_universe
)

from execution.execution_simulator import (
    ExecutionSimulator
)

# =====================================================
# SYMBOLS
# =====================================================

symbols = load_ranked_universe(

    top_n=25
)

# =====================================================
# ENGINE
# =====================================================

engine = ExecutionSimulator(

    slippage_bps=5,

    transaction_cost_bps=2
)

results = engine.simulate_portfolio_execution(

    symbols,

    quantity=100
)

# =====================================================
# OUTPUT
# =====================================================

print(

    "\nEXECUTION SIMULATION RESULTS\n"
)

print(results.head())