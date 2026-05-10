import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import pandas as pd
import numpy as np

from core.factor_attribution import (
    normalize_factor,
    factor_score,
    contribution_table,
    dominant_factor,
    factor_stability
)

# =====================================================
# SAMPLE FACTORS
# =====================================================

np.random.seed(42)

factors = {

    "momentum":

        normalize_factor(

            pd.Series(

                np.random.normal(

                    0.10,

                    0.05,

                    100
                )
            )
        ),

    "quality":

        normalize_factor(

            pd.Series(

                np.random.normal(

                    0.08,

                    0.03,

                    100
                )
            )
        ),

    "volatility":

        normalize_factor(

            pd.Series(

                np.random.normal(

                    -0.05,

                    0.04,

                    100
                )
            )
        ),

    "flows":

        normalize_factor(

            pd.Series(

                np.random.normal(

                    0.12,

                    0.06,

                    100
                )
            )
        )
}

# =====================================================
# WEIGHTS
# =====================================================

weights = {

    "momentum": 0.35,

    "quality": 0.25,

    "volatility": 0.15,

    "flows": 0.25
}

# =====================================================
# FACTOR SCORE
# =====================================================

total_score, contributions = factor_score(

    factors,

    weights
)

print("\nTOTAL FACTOR SCORE")

print(total_score.tail())

# =====================================================
# CONTRIBUTION TABLE
# =====================================================

table = contribution_table(

    contributions
)

print("\nFACTOR CONTRIBUTIONS")

print(table.tail())

# =====================================================
# DOMINANT FACTOR
# =====================================================

latest = {

    k: v.iloc[-1]

    for k, v in contributions.items()
}

dominant = dominant_factor(

    latest
)

print("\nDOMINANT FACTOR")

print(dominant)

# =====================================================
# STABILITY
# =====================================================

print("\nFACTOR STABILITY")

for factor, values in contributions.items():

    stability = factor_stability(

        values
    )

    print(factor, stability)
