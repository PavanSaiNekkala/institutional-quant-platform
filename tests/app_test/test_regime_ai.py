import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import numpy as np
import pandas as pd

from ai.regime_ai import (
    train_regime_ai
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

            2,

            500
        )
    )
)

# =====================================================
# TRAIN AI
# =====================================================

result = train_regime_ai(

    prices
)

print("\nREGIME AI ENGINE\n")

print(

    "Detected Regime:",

    result["Regime"]
)

print(

    "Selected Model:",

    result["Model"]
)

print(

    "Next Return Forecast:",

    round(

        result["Prediction"],

        6
    )
)
