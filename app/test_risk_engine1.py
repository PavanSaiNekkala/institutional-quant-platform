import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import numpy as np
import pandas as pd

from risk.risk_engine import (
    risk_report
)

# =====================================================
# SAMPLE DATA
# =====================================================

np.random.seed(42)

weights = pd.Series([

    0.30,
    0.20,
    0.15,
    0.10,
    0.25
])

returns = pd.Series(

    np.random.normal(

        0.001,

        0.02,

        700
    )
)

returns_df = pd.DataFrame({

    "Asset1":

        np.random.normal(
            0.001,
            0.02,
            700
        ),

    "Asset2":

        np.random.normal(
            0.001,
            0.018,
            700
        ),

    "Asset3":

        np.random.normal(
            0.001,
            0.022,
            700
        )
})

# =====================================================
# REPORT
# =====================================================

report = risk_report(

    weights,

    returns,

    returns_df
)

# =====================================================
# OUTPUT
# =====================================================

print("\nRISK MANAGEMENT REPORT\n")

print(report)