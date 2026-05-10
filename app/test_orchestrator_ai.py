import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import numpy as np
import pandas as pd

from ai.orchestrator import (
    orchestrate_ai
)

np.random.seed(42)

prices = pd.Series(
    100 + np.cumsum(
        np.random.normal(
            0,
            1,
            500
        )
    )
)

result = orchestrate_ai(prices)

print("\nINSTITUTIONAL AI ORCHESTRATOR\n")

for k, v in result.items():

    print(f"{k}: {v}")