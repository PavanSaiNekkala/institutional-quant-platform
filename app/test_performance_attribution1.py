import sys
import numpy as np

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from core.universe_loader import (
    load_ranked_universe
)

from portfolio.performance_attribution1 import (
    PerformanceAttribution
)

# =====================================================
# SYMBOLS
# =====================================================

symbols = load_ranked_universe(

    top_n=10
)

# =====================================================
# SAMPLE RETURNS
# =====================================================

np.random.seed(42)

portfolio_returns = np.random.normal(

    0.02,

    0.05,

    len(symbols)
)

benchmark_returns = np.random.normal(

    0.01,

    0.03,

    len(symbols)
)

weights = np.random.random(

    len(symbols)
)

weights /= weights.sum()

# =====================================================
# ENGINE
# =====================================================

engine = PerformanceAttribution()

df, summary = engine.analyze(

    symbols,

    portfolio_returns,

    benchmark_returns,

    weights
)

# =====================================================
# OUTPUT
# =====================================================

print(

    "\nPERFORMANCE ATTRIBUTION\n"
)

print(df)

print(

    "\nSUMMARY\n"
)

print(summary)