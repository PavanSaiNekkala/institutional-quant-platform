import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from core.macro import (
    volatility_environment,
    interest_rate_regime,
    liquidity_regime,
    macro_composite,
    macro_allocation
)

# =====================================================
# SAMPLE MACRO DATA
# =====================================================

india_vix = 18.5

interest_rate_change = 0.50

market_return = 0.12

breadth_score = 1.15

# =====================================================
# REGIMES
# =====================================================

vol_regime = volatility_environment(

    india_vix
)

rate_regime = interest_rate_regime(

    interest_rate_change
)

liq_regime = liquidity_regime(

    market_return,

    breadth_score
)

# =====================================================
# COMPOSITE
# =====================================================

macro_regime = macro_composite(

    vol_regime,

    rate_regime,

    liq_regime
)

allocation = macro_allocation(

    macro_regime
)

# =====================================================
# RESULTS
# =====================================================

print("\nMACRO INTELLIGENCE ENGINE")

print("\nVOLATILITY REGIME")

print(vol_regime)

print("\nRATE REGIME")

print(rate_regime)

print("\nLIQUIDITY REGIME")

print(liq_regime)

print("\nMACRO COMPOSITE")

print(macro_regime)

print("\nRECOMMENDED EXPOSURE")

print(allocation)
