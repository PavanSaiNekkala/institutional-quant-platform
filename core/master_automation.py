from datetime import datetime

from ops.backup_manager import create_backup
from ops.data_refresh_scheduler import refresh_market_database
from ops.system_health import health_report

# =========================================================
# MASTER AUTOMATION
# =========================================================


class MasterAutomation:
    def __init__(self):

        self.logs = []

    # =====================================================
    # LOGGING
    # =====================================================

    def log(self, message):

        timestamp = datetime.now()

        entry = f"[{timestamp}] {message}"

        self.logs.append(entry)

        print(entry)

    # =====================================================
    # DATA REFRESH
    # =====================================================

    def refresh_data(self, limit=50):

        self.log("STARTING MARKET REFRESH")

        results = refresh_market_database(limit=limit)

        self.log(f"REFRESH COMPLETE: {results}")

        return results

    # =====================================================
    # BACKUP
    # =====================================================

    def backup_system(self):

        self.log("STARTING BACKUP")

        backup = create_backup()

        self.log(f"BACKUP COMPLETE: {backup}")

        return backup

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def check_health(self):

        self.log("RUNNING HEALTH CHECK")

        report = health_report()

        self.log(f"HEALTH REPORT: {report}")

        return report

    # =====================================================
    # FULL CYCLE
    # =====================================================

    def run_full_cycle(self, refresh_limit=50):

        self.log("MASTER AUTOMATION STARTED")

        refresh = self.refresh_data(limit=refresh_limit)

        health = self.check_health()

        backup = self.backup_system()

        self.log("MASTER AUTOMATION COMPLETE")

        return {"refresh": refresh, "health": health, "backup": backup, "logs": self.logs}
