import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from ops.release_validator import (
    release_validation
)

# =====================================================
# VALIDATION
# =====================================================

report = release_validation()

# =====================================================
# OUTPUT
# =====================================================

print("\nRELEASE VALIDATION REPORT\n")

for k, v in report.items():

    print(f"{k}: {v}")
