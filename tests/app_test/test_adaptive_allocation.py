import sys
import numpy as np

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from core.universe_loader import (
    load_ranked_universe
)

from portfolio.adaptive_allocation import (
    AdaptiveAllocation
)

# =====================================================
# SYMBOLS
# =====================================================

symbols = load_ranked_universe(

    top_n=10
)

# =====================================================
# SAMPLE DATA
# =====================================================

np.random.seed(42)

expected_returns = np.random.normal(

    0.02,

    0.05,

    len(symbols)
)

volatilities = np.random.uniform(

    0.10,

    0.40,

    len(symbols)
)

# =====================================================
# ENGINE
# =====================================================

engine = AdaptiveAllocation(

    target_volatility=0.15
)

df, summary = engine.allocate(

    symbols,

    expected_returns,

    volatilities
)

# =====================================================
# OUTPUT
# =====================================================

print(

    "\nADAPTIVE ALLOCATION\n"
)

print(df)

print(

    "\nSUMMARY\n"
)

print(summary)
