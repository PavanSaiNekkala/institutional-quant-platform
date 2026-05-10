import sys

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from core.universe_loader import (
    load_ranked_universe
)

from strategy.dynamic_strategy_switcher import (
    DynamicStrategySwitcher
)

# =====================================================
# SYMBOLS
# =====================================================

symbols = load_ranked_universe(

    top_n=10
)

# =====================================================
# ENGINE
# =====================================================

engine = DynamicStrategySwitcher()

results = engine.multi_asset_switching(

    symbols
)

# =====================================================
# OUTPUT
# =====================================================

print(

    "\nDYNAMIC STRATEGY SWITCHING\n"
)

print(results)