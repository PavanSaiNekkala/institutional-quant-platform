import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from core.master_automation import (
    MasterAutomation
)

# =====================================================
# ENGINE
# =====================================================

engine = MasterAutomation()

# =====================================================
# RUN
# =====================================================

results = engine.run_full_cycle(

    refresh_limit=5
)

# =====================================================
# OUTPUT
# =====================================================

print(

    "\nMASTER AUTOMATION RESULTS\n"
)

print(results)
