import os

# =========================================================
# CHECKLIST ITEMS
# =========================================================

CHECKS = {
    "Environment File": ".env",
    "Requirements": "requirements.txt",
    "Master Dashboard": "dashboard/master_dashboard.py",
    "Orchestrator": "core/orchestrator.py",
    "Signal Engine": "signals/live_signals.py",
    "Portfolio Monitor": "portfolio/live_monitor.py",
    "Logger": "ops/logger.py",
    "Backup System": "ops/backup_manager.py",
    "Scheduler": "ops/scheduler.py",
    "Release Validator": "ops/release_validator.py",
    "Architecture Docs": "docs/ARCHITECTURE.md",
    "Deployment Docs": "docs/DEPLOYMENT.md",
    "Recovery Docs": "docs/RECOVERY.md",
    "Operations Docs": "docs/OPERATIONS.md",
}

# =========================================================
# RUN CHECKLIST
# =========================================================


def run_production_checklist():

    results = {}

    for name, path in CHECKS.items():
        results[name] = os.path.exists(path)

    return results


# =========================================================
# PRODUCTION APPROVAL
# =========================================================


def production_ready():

    results = run_production_checklist()

    return all(results.values())
