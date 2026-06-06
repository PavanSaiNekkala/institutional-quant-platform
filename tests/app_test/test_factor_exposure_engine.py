import sys

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from core.universe_loader import (
    load_ranked_universe
)

from risk.factor_exposure_engine import (
    FactorExposureEngine
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

engine = FactorExposureEngine()

results = engine.run_analysis(

    symbols
)

# =====================================================
# OUTPUT
# =====================================================

print(

    "\nFACTOR EXPOSURE RESULTS\n"
)

print(results.head())
