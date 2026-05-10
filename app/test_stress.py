import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import pandas as pd
import numpy as np

from analytics.stress_scenarios import (
    stress_report
)

# =====================================================
# SAMPLE PORTFOLIO
# =====================================================

portfolio = pd.DataFrame({

    "Symbol": [

        "RELIANCE.NS",
        "TCS.NS",
        "INFY.NS",
        "HDFCBANK.NS"
    ],

    "Value": [

        300000,
        250000,
        200000,
        250000
    ]
})

# =====================================================
# RETURNS
# =====================================================

np.random.seed(42)

returns = pd.Series(

    np.random.normal(

        0.001,

        0.02,

        252
    )
)

# =====================================================
# CORRELATION MATRIX
# =====================================================

corr_matrix = pd.DataFrame(

    np.random.uniform(

        0.2,

        0.8,

        (4, 4)
    )
)

# =====================================================
# REPORT
# =====================================================

report = stress_report(

    portfolio,

    returns,

    corr_matrix
)

print("\nINSTITUTIONAL STRESS REPORT\n")

for k, v in report.items():

    print(f"{k}: {v}")