import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from ops.continuous_scheduler import (
    ContinuousScheduler
)

# =====================================================
# SCHEDULER
# =====================================================

scheduler = ContinuousScheduler()

# =====================================================
# RUN
# =====================================================

scheduler.run(

    refresh_limit=5,

    interval_minutes=1
)
