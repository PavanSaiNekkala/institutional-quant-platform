import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import numpy as np
import pandas as pd

from research.walk_forward import (

    walk_forward_validation,
    validation_summary
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

            600
        )
    )
)

# =====================================================
# RUN VALIDATION
# =====================================================

results = walk_forward_validation(

    prices
)

summary = validation_summary(

    results
)

# =====================================================
# OUTPUT
# =====================================================

print("\nWALK-FORWARD VALIDATION\n")

print(results)

print("\nVALIDATION SUMMARY\n")

for k, v in summary.items():

    print(f"{k}: {v}")
