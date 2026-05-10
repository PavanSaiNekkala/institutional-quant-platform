import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import numpy as np
import pandas as pd

from research.bayesian_optimization import (
    optimize_strategy
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
# RUN OPTIMIZATION
# =====================================================

result = optimize_strategy(

    returns
)

# =====================================================
# OUTPUT
# =====================================================

print("\nBAYESIAN OPTIMIZATION RESULT\n")

for k, v in result.items():

    print(f"{k}: {v}")