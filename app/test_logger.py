import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from ops.logger import (

    log_info,
    log_warning,
    log_error,
    log_critical
)

# =====================================================
# TEST LOGGING
# =====================================================

log_info(

    "System initialized"
)

log_warning(

    "High volatility detected"
)

log_error(

    "Market data fetch failed"
)

log_critical(

    "Critical drawdown breach"
)

print("\nLOGGING TEST COMPLETED\n")