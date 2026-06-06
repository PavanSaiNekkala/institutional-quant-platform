import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import pandas as pd
import numpy as np

from core.alpha_model import (
    cross_sectional_score,
    alpha_ranking,
    percentile_rank,
    alpha_classification
)

# =====================================================
# SAMPLE STOCKS
# =====================================================

stocks = [

    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "LT.NS",
    "ITC.NS",
    "SUNPHARMA.NS"
]

# =====================================================
# SAMPLE FACTORS
# =====================================================

np.random.seed(42)

factor_df = pd.DataFrame({

    "momentum":

        np.random.normal(

            0.8,

            0.2,

            len(stocks)
        ),

    "relative_strength":

        np.random.normal(

            0.7,

            0.15,

            len(stocks)
        ),

    "quality":

        np.random.normal(

            0.6,

            0.10,

            len(stocks)
        ),

    "flows":

        np.random.normal(

            0.75,

            0.18,

            len(stocks)
        ),

    "volatility":

        np.random.normal(

            -0.3,

            0.12,

            len(stocks)
        )

}, index=stocks)

# =====================================================
# FACTOR WEIGHTS
# =====================================================

factor_weights = {

    "momentum": 0.30,

    "relative_strength": 0.25,

    "quality": 0.20,

    "flows": 0.15,

    "volatility": 0.10
}

# =====================================================
# ALPHA SCORES
# =====================================================

alpha_scores, contributions = (

    cross_sectional_score(

        factor_df,

        factor_weights
    )
)

# =====================================================
# RANKING
# =====================================================

ranking = alpha_ranking(

    alpha_scores
)

# =====================================================
# PERCENTILES
# =====================================================

percentiles = percentile_rank(

    alpha_scores
)

# =====================================================
# RESULTS
# =====================================================

results = pd.DataFrame({

    "Alpha Score": alpha_scores,

    "Percentile": percentiles
})

results["Classification"] = (

    results["Percentile"]

    .apply(alpha_classification)
)

results = results.sort_values(

    "Alpha Score",

    ascending=False
)

print("\nCROSS-SECTIONAL ALPHA MODEL")

print(results)
