import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import pandas as pd
import numpy as np

from core.ensemble import (
    ensemble_score,
    ensemble_ranking,
    confidence_score,
    ensemble_classification
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
# SAMPLE MODEL SCORES
# =====================================================

np.random.seed(42)

model_scores = pd.DataFrame({

    "momentum_model":

        np.random.normal(

            0.8,

            0.2,

            len(stocks)
        ),

    "quality_model":

        np.random.normal(

            0.7,

            0.15,

            len(stocks)
        ),

    "flow_model":

        np.random.normal(

            0.75,

            0.18,

            len(stocks)
        ),

    "volatility_model":

        np.random.normal(

            0.65,

            0.10,

            len(stocks)
        ),

    "relative_strength_model":

        np.random.normal(

            0.78,

            0.16,

            len(stocks)
        )

}, index=stocks)

# =====================================================
# MODEL WEIGHTS
# =====================================================

model_weights = {

    "momentum_model": 0.30,

    "quality_model": 0.20,

    "flow_model": 0.20,

    "volatility_model": 0.10,

    "relative_strength_model": 0.20
}

# =====================================================
# ENSEMBLE
# =====================================================

ensemble_scores, contributions = (

    ensemble_score(

        model_scores,

        model_weights
    )
)

# =====================================================
# CONTRIBUTION DF
# =====================================================

contribution_df = pd.DataFrame(

    contributions
)

# =====================================================
# CONFIDENCE
# =====================================================

confidence = confidence_score(

    contribution_df
)

# =====================================================
# RESULTS
# =====================================================

results = pd.DataFrame({

    "Ensemble Score": ensemble_scores,

    "Confidence": confidence
})

results["Percentile"] = (

    results["Ensemble Score"]

    .rank(

        pct=True
    )
)

results["Classification"] = (

    results["Percentile"]

    .apply(ensemble_classification)
)

results = results.sort_values(

    "Ensemble Score",

    ascending=False
)

print("\nENSEMBLE ALPHA ENGINE")

print(results)