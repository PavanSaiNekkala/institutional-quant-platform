import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import numpy as np
import pandas as pd

from portfolio.regime_allocator import (
    regime_report
)

# =====================================================
# SAMPLE RETURNS
# =====================================================

np.random.seed(42)

returns = pd.Series(

    np.random.normal(

        0.001,

        0.02,

        700
    )
)

# =====================================================
# REGIME REPORT
# =====================================================

regime, report = regime_report(

    returns
)

# =====================================================
# OUTPUT
# =====================================================

print("\nMARKET REGIME\n")

print(regime)

print("\nADAPTIVE ALLOCATION\n")

print(report)
