import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from core.orchestrator1 import (
    InstitutionalOrchestrator
)

# =====================================================
# START
# =====================================================

orchestrator1 = InstitutionalOrchestrator()

print("\nINSTITUTIONAL ORCHESTRATOR RUNNING\n")

orchestrator1.start()
