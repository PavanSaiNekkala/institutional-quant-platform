import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from portfolio.sector_caps import (
    apply_sector_caps
)

# =====================================================
# SAMPLE RANKED STOCKS
# =====================================================

ranked = [

    "TCS.NS",
    "INFY.NS",
    "LTIM.NS",
    "RELIANCE.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "SUNPHARMA.NS",
    "ITC.NS"
]

# =====================================================
# APPLY CAPS
# =====================================================

selected, sector_counts = (

    apply_sector_caps(

        ranked,

        max_per_sector=2
    )
)

print("\nSELECTED PORTFOLIO")

print(selected)

print("\nSECTOR DISTRIBUTION")

print(sector_counts)
