import sys

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from monitoring.system_health_monitor import (
    SystemHealthMonitor
)

# =====================================================
# ENGINE
# =====================================================

engine = SystemHealthMonitor()

df = engine.report_dataframe()

# =====================================================
# OUTPUT
# =====================================================

print(

    "\nSYSTEM HEALTH REPORT\n"
)

print(df)
