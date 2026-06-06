import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import numpy as np
import pandas as pd

from research.factor_clustering import (

    generate_factors,
    cluster_factors,
    cluster_summary
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
# GENERATE FACTORS
# =====================================================

factors = generate_factors(

    prices
)

# =====================================================
# CLUSTER
# =====================================================

clusters, corr = cluster_factors(

    factors
)

summary = cluster_summary(

    clusters
)

# =====================================================
# OUTPUT
# =====================================================

print("\nFACTOR CLUSTERS\n")

print(clusters)

print("\nCLUSTER SUMMARY\n")

print(summary)

print("\nFACTOR CORRELATION MATRIX\n")

print(corr)
