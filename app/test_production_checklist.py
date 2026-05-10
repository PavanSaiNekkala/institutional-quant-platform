import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from ops.production_checklist import (

    run_production_checklist,
    production_ready
)

# =====================================================
# CHECKLIST
# =====================================================

results = run_production_checklist()

# =====================================================
# OUTPUT
# =====================================================

print("\nPRODUCTION READINESS CHECKLIST\n")

for k, v in results.items():

    print(f"{k}: {v}")

print("\nPRODUCTION READY\n")

print(

    production_ready()
)