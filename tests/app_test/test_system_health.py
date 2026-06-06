import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from ops.system_health import (
    health_report,
    summary_dataframe
)

# =====================================================
# HEALTH REPORT
# =====================================================

report = health_report()

# =====================================================
# OUTPUT
# =====================================================

print("\nSYSTEM HEALTH REPORT\n")

for k, v in report.items():

    print(f"\n{k}:\n")

    print(v)

print("\nRUNTIME SUMMARY\n")

print(

    summary_dataframe()
)
