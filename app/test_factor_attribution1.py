import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import numpy as np
import pandas as pd

from analytics.factor_attribution import (
    attribution_report
)

# =====================================================
# SAMPLE DATA
# =====================================================

np.random.seed(42)

portfolio_returns = pd.Series(

    np.random.normal(

        0.001,

        0.02,

        252
    )
)

factor_returns = pd.DataFrame({

    "Market":

        np.random.normal(
            0.001,
            0.015,
            252
        ),

    "Momentum":

        np.random.normal(
            0.0005,
            0.012,
            252
        ),

    "Value":

        np.random.normal(
            0.0003,
            0.010,
            252
        ),

    "Quality":

        np.random.normal(
            0.0004,
            0.011,
            252
        )
})

# =====================================================
# REPORT
# =====================================================

result = attribution_report(

    portfolio_returns,

    factor_returns
)

print("\nFACTOR ATTRIBUTION REPORT\n")

print(

    "Alpha:",

    result["Alpha"]
)

print(

    "R2:",

    result["R2"]
)

print("\nFACTOR EXPOSURES\n")

print(

    result["Report"]
)