import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import numpy as np
import pandas as pd

from research.research_pipeline import (
    ResearchPipeline
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

            800
        )
    )
)

# =====================================================
# PIPELINE
# =====================================================

pipeline = ResearchPipeline()

result = pipeline.run_pipeline(

    prices
)

# =====================================================
# OUTPUT
# =====================================================

print("\nAUTOMATED RESEARCH PIPELINE\n")

for k, v in result.items():

    print(f"{k}: {v}")

print("\nPIPELINE HISTORY\n")

print(

    pipeline.pipeline_history()
)
