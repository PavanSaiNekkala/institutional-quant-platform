import sys
import pandas as pd

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from core.incremental_refresh_engine import (
    IncrementalRefreshEngine
)

# =====================================================
# LOAD UNIVERSE
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
# ENGINE
# =====================================================

engine = IncrementalRefreshEngine(

    refresh_hours=24
)

summary = engine.refresh_summary(

    symbols
)

# =====================================================
# OUTPUT
# =====================================================

print(

    "\nINCREMENTAL REFRESH SUMMARY\n"
)

print(summary)

print(

    "\nFIRST STALE SYMBOLS\n"
)

print(

    engine.stale_symbols(

        symbols
    )[:20]
)
