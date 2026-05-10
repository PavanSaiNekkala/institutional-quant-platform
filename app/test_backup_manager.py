import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from ops.backup_manager import (

    create_backup,
    list_backups
)

# =====================================================
# CREATE BACKUP
# =====================================================

result = create_backup()

# =====================================================
# OUTPUT
# =====================================================

print("\nBACKUP CREATED\n")

for k, v in result.items():

    print(f"{k}: {v}")

print("\nAVAILABLE BACKUPS\n")

print(

    list_backups()
)