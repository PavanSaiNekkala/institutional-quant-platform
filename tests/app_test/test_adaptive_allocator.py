import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import numpy as np
import pandas as pd

from ai.adaptive_allocator import (
    adaptive_weights,
    portfolio_summary
)

# =====================================================
# SAMPLE ASSETS
# =====================================================

assets = [

    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ITC.NS"
]

# =====================================================
# SAMPLE RETURNS
# =====================================================

np.random.seed(42)

returns = pd.Series(

    np.random.normal(

        0.001,

        0.02,

        252
    )
)

# =====================================================
# AI ALLOCATION
# =====================================================

allocation, regime = adaptive_weights(

    assets,

    returns
)

summary = portfolio_summary(

    allocation
)

# =====================================================
# OUTPUT
# =====================================================

print("\nADAPTIVE AI PORTFOLIO\n")

print(

    "Detected Regime:",

    regime
)

print("\nALLOCATIONS\n")

print(summary)
