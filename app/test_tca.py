import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from execution.tca_engine import (
    tca_report
)

# =====================================================
# SAMPLE REPORT
# =====================================================

report = tca_report(

    symbol="RELIANCE.NS",

    quantity=1000,

    arrival_price=2900,

    execution_price=2912,

    volatility=0.025,

    participation_rate=0.12
)

print("\nTRANSACTION COST ANALYTICS")

print(report)