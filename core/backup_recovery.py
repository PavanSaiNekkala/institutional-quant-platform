import shutil
from datetime import datetime
from pathlib import Path

# =========================================================
# BACKUP DIRECTORY
# =========================================================

BACKUP_DIR = Path("backups")

BACKUP_DIR.mkdir(exist_ok=True)

# =========================================================
# BACKUP ENGINE
# =========================================================


class BackupRecoverySystem:
    def __init__(self):

        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # =====================================================
    # BACKUP FILE
    # =====================================================

    def backup_file(self, filepath):

        path = Path(filepath)

        if not path.exists():
            return False

        backup_name = f"{path.stem}_{self.timestamp}{path.suffix}"

        destination = BACKUP_DIR / backup_name

        shutil.copy2(path, destination)

        return destination

    # =====================================================
    # BACKUP DIRECTORY
    # =====================================================

    def backup_directory(self, directory):

        source = Path(directory)

        if not source.exists():
            return False

        destination = BACKUP_DIR / f"{source.name}_{self.timestamp}"

        shutil.copytree(source, destination)

        return destination
