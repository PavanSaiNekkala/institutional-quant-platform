import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import numpy as np
import pandas as pd

from features.feature_store import (

    generate_features,
    save_features,
    load_features,
    feature_summary
)

# =====================================================
# SAMPLE PRICE SERIES
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
# GENERATE FEATURES
# =====================================================

features = generate_features(

    prices
)

print("\nFEATURE STORE GENERATED\n")

print(

    features.head()
)

# =====================================================
# SAVE FEATURES
# =====================================================

path = save_features(

    "RELIANCE",

    features
)

print(

    "\nFEATURES SAVED:",

    path
)

# =====================================================
# LOAD FEATURES
# =====================================================

loaded = load_features(

    "RELIANCE"
)

print("\nLOADED FEATURES\n")

print(

    loaded.head()
)

# =====================================================
# SUMMARY
# =====================================================

summary = feature_summary(

    loaded
)

print("\nFEATURE SUMMARY\n")

for k, v in summary.items():

    print(f"{k}: {v}")