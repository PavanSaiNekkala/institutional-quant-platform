import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from ops.data_refresh_scheduler import (
    refresh_market_database
)

# =====================================================
# REFRESH
# =====================================================

results = refresh_market_database(

    limit=10
)

# =====================================================
# OUTPUT
# =====================================================

print(

    "\nREFRESH RESULTS\n"
)

print(

    results
)