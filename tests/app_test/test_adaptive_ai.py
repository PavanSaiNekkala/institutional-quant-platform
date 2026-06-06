import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import pandas as pd
import numpy as np

from core.adaptive_ai import (
    prepare_features,
    train_alpha_model,
    feature_importance,
    ai_alpha_score,
    prediction_confidence
)

# =====================================================
# SAMPLE DATA
# =====================================================

np.random.seed(42)

n = 500

factor_df = pd.DataFrame({

    "momentum":

        np.random.normal(

            0.8,

            0.2,

            n
        ),

    "quality":

        np.random.normal(

            0.7,

            0.15,

            n
        ),

    "flows":

        np.random.normal(

            0.75,

            0.18,

            n
        ),

    "relative_strength":

        np.random.normal(

            0.78,

            0.16,

            n
        ),

    "volatility":

        np.random.normal(

            -0.30,

            0.12,

            n
        )
})

# =====================================================
# TARGET ALPHA
# =====================================================

target = (

    0.30 * factor_df["momentum"]

    + 0.25 * factor_df["quality"]

    + 0.20 * factor_df["flows"]

    + 0.15 * factor_df["relative_strength"]

    - 0.10 * abs(factor_df["volatility"])

    + np.random.normal(0, 0.05, n)
)

# =====================================================
# PREPARE
# =====================================================

X, y = prepare_features(

    factor_df,

    target
)

# =====================================================
# TRAIN MODEL
# =====================================================

model, mse, predictions = (

    train_alpha_model(

        X,

        y
    )
)

print("\nAI ADAPTIVE MODEL")

print("\nMODEL MSE")

print(mse)

# =====================================================
# FEATURE IMPORTANCE
# =====================================================

importance = feature_importance(

    model,

    X.columns
)

print("\nFEATURE IMPORTANCE")

print(importance)

# =====================================================
# LATEST PREDICTION
# =====================================================

latest_features = X.tail(5)

alpha_prediction = ai_alpha_score(

    model,

    latest_features
)

print("\nAI ALPHA PREDICTIONS")

print(alpha_prediction)

# =====================================================
# CONFIDENCE
# =====================================================

confidence = prediction_confidence(

    alpha_prediction
)

print("\nPREDICTION CONFIDENCE")

print(confidence)
