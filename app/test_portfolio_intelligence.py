import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import numpy as np
import pandas as pd

from analytics.portfolio_intelligence import (
    portfolio_report
)

# =====================================================
# SAMPLE RETURNS
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
# REPORT
# =====================================================

report = portfolio_report(

    returns
)

print("\nINSTITUTIONAL PORTFOLIO REPORT\n")

for k, v in report.items():

    print(f"{k}: {v}")