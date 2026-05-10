import shutil
from pathlib import Path
from datetime import datetime

# =========================================================
# BACKUP DIRECTORY
# =========================================================

BACKUP_DIR = Path(

    "backups"
)

BACKUP_DIR.mkdir(

    exist_ok=True
)

# =========================================================
# FILES TO BACKUP
# =========================================================

FILES_TO_BACKUP = [

    "research_lab.db",

    ".env",

    "requirements.txt"
]

# =========================================================
# CREATE BACKUP
# =========================================================

def create_backup():

    timestamp = datetime.now().strftime(

        "%Y%m%d_%H%M%S"
    )

    snapshot_dir = (

        BACKUP_DIR

        / f"snapshot_{timestamp}"
    )

    snapshot_dir.mkdir(

        exist_ok=True
    )

    backed_up = []

    for file in FILES_TO_BACKUP:

        path = Path(file)

        if path.exists():

            shutil.copy(

                path,

                snapshot_dir / path.name
            )

            backed_up.append(file)

    return {

        "Snapshot":

            str(snapshot_dir),

        "Files Backed Up":

            backed_up
    }

# =========================================================
# LIST BACKUPS
# =========================================================

def list_backups():

    backups = [

        p.name

        for p in BACKUP_DIR.iterdir()

        if p.is_dir()
    ]

    return backups