import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from execution.cost_model import (
    total_execution_cost
)

# =====================================================
# SAMPLE EXECUTION DATA
# =====================================================

turnover = 0.45

volatility = 0.02

position_size = 50000

avg_daily_volume = 5000000

# =====================================================
# COST ANALYSIS
# =====================================================

report = total_execution_cost(

    turnover,

    volatility,

    position_size,

    avg_daily_volume
)

# =====================================================
# OUTPUT
# =====================================================

print("\nEXECUTION COST REPORT\n")

for k, v in report.items():

    print(f"{k}: {v}")