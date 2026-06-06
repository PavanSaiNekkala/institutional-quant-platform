import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import numpy as np
import pandas as pd

from research.alpha_mining import (
    alpha_report
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

            500
        )
    )
)

# =====================================================
# RUN ALPHA MINING
# =====================================================

report = alpha_report(

    prices
)

print("\nALPHA MINING REPORT\n")

print(report)
