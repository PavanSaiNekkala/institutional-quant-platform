import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import numpy as np
import pandas as pd

from ai.deep_forecaster import (
    train_lstm
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

result = train_lstm(

    prices
)

print("\nDEEP LEARNING FORECAST\n")

print(

    "Next Price Forecast:",

    round(

        result["Prediction"],

        2
    )
)
