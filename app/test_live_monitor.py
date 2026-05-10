import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import numpy as np

from portfolio.live_monitor import (
    live_portfolio_report
)

# =====================================================
# PORTFOLIO
# =====================================================

symbols = [

    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS"
]

weights = np.array([

    0.30,
    0.25,
    0.25,
    0.20
])

# =====================================================
# REPORT
# =====================================================

report = live_portfolio_report(

    symbols,

    weights
)

# =====================================================
# OUTPUT
# =====================================================

print("\nLIVE PORTFOLIO REPORT\n")

for k, v in report.items():

    print(f"{k}: {v}")