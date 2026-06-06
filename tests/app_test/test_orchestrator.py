import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from core.orchestrator import (
    orchestrate_portfolio
)

# =====================================================
# SAMPLE UNIVERSE
# =====================================================

stocks = [

    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "LT.NS",
    "ITC.NS",
    "SUNPHARMA.NS",
    "BHARTIARTL.NS",
    "MARUTI.NS"
]

# =====================================================
# ORCHESTRATION
# =====================================================

results = orchestrate_portfolio(

    stocks,

    regime="BULL_NORMAL_VOL"
)

print("\nINSTITUTIONAL ORCHESTRATION ENGINE")

print(results)
