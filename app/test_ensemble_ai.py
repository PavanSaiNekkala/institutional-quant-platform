import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import numpy as np
import pandas as pd

from ai.ensemble_ai import (
    train_ensemble
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

            1.5,

            500
        )
    )
)

# =====================================================
# TRAIN ENSEMBLE
# =====================================================

result = train_ensemble(

    prices
)

print("\nENSEMBLE AI FORECAST\n")

for k, v in result.items():

    print(

        f"{k}: {round(v, 6)}"
    )