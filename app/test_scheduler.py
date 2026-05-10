import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from ops.scheduler import (
    run_scheduler
)

# =====================================================
# START SCHEDULER
# =====================================================

print("\nSCHEDULER RUNNING\n")

run_scheduler()