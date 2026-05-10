import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from monitoring.logger import (
    log_info,
    log_warning,
    log_error
)

from monitoring.health import (
    health_snapshot
)

# =====================================================
# TEST LOGGING
# =====================================================

log_info(

    "Institutional monitoring active"
)

log_warning(

    "Sample warning generated"
)

log_error(

    "Sample error generated"
)

# =====================================================
# HEALTH SNAPSHOT
# =====================================================

snapshot = health_snapshot()

print("\nSYSTEM HEALTH")

for k, v in snapshot.items():

    print(f"{k}: {v}")

print("\nLOGGING COMPLETE")