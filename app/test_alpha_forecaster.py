import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import numpy as np
import pandas as pd

from ai.alpha_forecaster import (
    train_alpha_model,
    forecast_next_return
)

# =====================================================
# SAMPLE PRICE SERIES
# =====================================================

np.random.seed(42)

prices = pd.Series(

    100

    + np.cumsum(

        np.random.normal(

            0,

            1,

            500
        )
    )
)

# =====================================================
# TRAIN MODEL
# =====================================================

result = train_alpha_model(

    prices
)

print("\nAI ALPHA MODEL\n")

print(

    "MSE:",

    round(result["mse"], 6)
)

# =====================================================
# FORECAST
# =====================================================

latest_features = (

    result["features"]

    .tail(1)
)

forecast = forecast_next_return(

    result["model"],

    latest_features
)

print(

    "\nNEXT RETURN FORECAST:",

    round(forecast, 6)
)