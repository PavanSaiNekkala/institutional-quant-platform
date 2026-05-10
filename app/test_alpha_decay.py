import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import numpy as np
import pandas as pd

from research.alpha_decay import (
    alpha_decay_analysis
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

            700
        )
    )
)

# =====================================================
# RUN DECAY ANALYSIS
# =====================================================

report, ic_series = alpha_decay_analysis(

    prices
)

# =====================================================
# OUTPUT
# =====================================================

print("\nALPHA DECAY REPORT\n")

for k, v in report.items():

    print(f"{k}: {v}")

print("\nROLLING IC SAMPLE\n")

print(

    ic_series.tail()
)