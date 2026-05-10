import sys

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from portfolio.distributed_optimizer import (
    DistributedOptimizer
)

# =====================================================
# SYMBOLS
# =====================================================

symbols = [

    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS"
]

# =====================================================
# OPTIMIZATION
# =====================================================

engine = DistributedOptimizer()

results = engine.optimize(

    symbols,

    simulations=20,

    workers=4
)

# =====================================================
# OUTPUT
# =====================================================

print(

    "\nDISTRIBUTED OPTIMIZATION RESULTS\n"
)

print(

    results.head()
)