import sys

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from automation.scheduled_refresh import (
    refresh_ranked_universe
)

# =====================================================
# RUN MANUAL TEST
# =====================================================

refresh_ranked_universe()
