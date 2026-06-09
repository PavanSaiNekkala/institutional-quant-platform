import time

import schedule

from ops.backup_manager import create_backup
from ops.logger import log_info
from ops.system_health import health_report

# =========================================================
# BACKUP JOB
# =========================================================


def backup_job():

    result = create_backup()

    log_info(f"Backup completed: {result}")


# =========================================================
# HEALTH CHECK JOB
# =========================================================


def health_job():

    report = health_report()

    log_info(f"Health check completed: {report}")


# =========================================================
# REGISTER SCHEDULES
# =========================================================

schedule.every(1).minutes.do(health_job)

schedule.every(5).minutes.do(backup_job)

# =========================================================
# RUNNER
# =========================================================


def run_scheduler():

    log_info("Scheduler started")

    while True:
        schedule.run_pending()

        time.sleep(1)
