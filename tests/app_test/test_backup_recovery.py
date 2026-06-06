import sys

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from core.backup_recovery import (
    BackupRecoverySystem
)

# =====================================================
# ENGINE
# =====================================================

engine = BackupRecoverySystem()

# =====================================================
# BACKUP FILE
# =====================================================

result = engine.backup_file(

    "ranked_universe.xlsx"
)

print(

    "\nBACKUP RESULT\n"
)

print(result)
