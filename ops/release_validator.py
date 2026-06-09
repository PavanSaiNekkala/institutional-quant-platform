import os

from ops.backup_manager import list_backups
from ops.system_health import health_report

# =========================================================
# REQUIRED FILES
# =========================================================

REQUIRED_FILES = [
    "requirements.txt",
    ".env",
    "dashboard/master_dashboard.py",
    "core/orchestrator.py",
    "signals/live_signals.py",
    "portfolio/live_monitor.py",
    "ops/logger.py",
]

# =========================================================
# FILE VALIDATION
# =========================================================


def validate_files():

    results = {}

    for file in REQUIRED_FILES:
        results[file] = os.path.exists(file)

    return results


# =========================================================
# BACKUP VALIDATION
# =========================================================


def validate_backups():

    backups = list_backups()

    return len(backups) > 0


# =========================================================
# SYSTEM VALIDATION
# =========================================================


def validate_system():

    report = health_report()

    return report is not None


# =========================================================
# RELEASE VALIDATION
# =========================================================


def release_validation():

    validation = {
        "Files Valid": all(validate_files().values()),
        "Backup Available": validate_backups(),
        "System Healthy": validate_system(),
    }

    validation["Release Approved"] = all(validation.values())

    return validation
