import sys

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from execution.transaction_cost_engine import (
    TransactionCostEngine
)

# =====================================================
# SAMPLE PORTFOLIO
# =====================================================

portfolio_values = [

    100000,
    250000,
    500000,
    750000,
    1000000
]

# =====================================================
# ENGINE
# =====================================================

engine = TransactionCostEngine(

    commission_bps=2,

    slippage_bps=5
)

df, summary = engine.analyze_portfolio_costs(

    portfolio_values
)

# =====================================================
# OUTPUT
# =====================================================

print(

    "\nTRANSACTION COST ANALYSIS\n"
)

print(df)

print(

    "\nSUMMARY\n"
)

print(summary)