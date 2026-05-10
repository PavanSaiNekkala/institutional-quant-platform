import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import numpy as np
import pandas as pd

from ai.multi_agent import (
    coordinate_agents
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

assets = [

    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS"
]

# =====================================================
# RUN AGENTS
# =====================================================

result = coordinate_agents(

    prices,

    assets
)

# =====================================================
# OUTPUT
# =====================================================

print("\nMULTI-AGENT AI SYSTEM\n")

print(

    "Decision:",

    result["Decision"]
)

print(

    "Final Signal:",

    result["Final Signal"]
)

print("\nAGENT OUTPUTS\n")

for agent in result["Agents"]:

    print(agent)