import sys

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from automation.overnight_batch_processor import (
    run_overnight_batch
)

# =====================================================
# RUN TEST
# =====================================================

run_overnight_batch()
