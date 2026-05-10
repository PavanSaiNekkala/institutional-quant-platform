import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from data.live_data import (
    market_snapshot
)

# =====================================================
# TEST SYMBOL
# =====================================================

snapshot = market_snapshot(

    "RELIANCE.NS"
)

# =====================================================
# OUTPUT
# =====================================================

print("\nLIVE MARKET SNAPSHOT\n")

for k, v in snapshot.items():

    print(f"{k}: {v}")