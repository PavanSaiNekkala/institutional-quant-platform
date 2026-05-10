import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import pandas as pd

from portfolio.performance_attribution import (

    contribution_report,
    top_contributors,
    worst_contributors
)

# =====================================================
# SAMPLE FACTORS
# =====================================================

factor_returns = pd.Series({

    "Momentum":

        0.12,

    "Value":

        0.05,

    "Quality":

        0.08,

    "LowVol":

        0.03,

    "Growth":

        -0.02
})

factor_weights = pd.Series({

    "Momentum":

        0.30,

    "Value":

        0.20,

    "Quality":

        0.25,

    "LowVol":

        0.15,

    "Growth":

        0.10
})

# =====================================================
# REPORT
# =====================================================

report = contribution_report(

    factor_returns,

    factor_weights
)

# =====================================================
# OUTPUT
# =====================================================

print("\nPERFORMANCE ATTRIBUTION REPORT\n")

print(report)

print("\nTOP CONTRIBUTORS\n")

print(

    top_contributors(report)
)

print("\nWORST CONTRIBUTORS\n")

print(

    worst_contributors(report)
)