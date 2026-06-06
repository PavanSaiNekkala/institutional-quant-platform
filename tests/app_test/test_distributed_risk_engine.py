import sys

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from core.universe_loader import (
    load_ranked_universe
)

from risk.distributed_risk_engine import (
    DistributedRiskEngine
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

engine = DistributedRiskEngine()

results = engine.run_risk_analysis(

    symbols,

    workers=4
)

# =====================================================
# OUTPUT
# =====================================================

print(

    "\nDISTRIBUTED RISK RESULTS\n"
)

print(results.head())
