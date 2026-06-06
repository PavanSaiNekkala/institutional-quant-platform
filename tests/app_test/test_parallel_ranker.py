import sys
import time
import pandas as pd

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from core.parallel_universe_ranker import (
    ParallelUniverseRanker
)

# =====================================================
# LOAD STOCKS
# =====================================================

universe = pd.read_excel(

    "valid_stocks.xlsx"
)

symbols = (

    universe.iloc[:, 0]

    .dropna()

    .astype(str)

    .unique()

    .tolist()
)

# =====================================================
# LIMIT FOR TESTING
# =====================================================

symbols = symbols[:200]

# =====================================================
# RANKER
# =====================================================

engine = ParallelUniverseRanker(

    n_jobs=8
)

start = time.time()

ranking_df = engine.rank(

    symbols
)

end = time.time()

# =====================================================
# OUTPUT
# =====================================================

print(

    f"\nTOTAL RANKED: "

    f"{len(ranking_df)}"
)

print(

    f"\nTIME TAKEN: "

    f"{round(end-start, 2)} sec"
)

print(

    "\nTOP RANKED STOCKS\n"
)

print(

    ranking_df.head()
)
