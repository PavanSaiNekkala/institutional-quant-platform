import sys

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from ai.distributed_forecasting import (
    DistributedForecasting
)

# =====================================================
# SYMBOLS
# =====================================================

from core.universe_loader import (
    load_ranked_universe
)

symbols = load_ranked_universe(

    top_n=25
)
# =====================================================
# FORECASTING
# =====================================================

engine = DistributedForecasting()

results = engine.run_forecasts(

    symbols,

    workers=4
)

# =====================================================
# OUTPUT
# =====================================================

print(

    "\nDISTRIBUTED FORECAST RESULTS\n"
)

print(results)