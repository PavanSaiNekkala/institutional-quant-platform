import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import numpy as np
import pandas as pd

from ai.transformer_forecaster import (
    train_transformer
)

# =====================================================
# SAMPLE DATA
# =====================================================

np.random.seed(42)

prices = pd.Series(

    100

    + np.cumsum(

        np.random.normal(

            0,

            1,

            400
        )
    )
)

# =====================================================
# TRAIN TRANSFORMER
# =====================================================

result = train_transformer(

    prices
)

print("\nTRANSFORMER FORECAST\n")

print(

    "Next Price Forecast:",

    round(

        result["Prediction"],

        2
    )
)
