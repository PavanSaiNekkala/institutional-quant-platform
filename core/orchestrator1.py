import threading
import time

from ops.logger import (
    log_info,
    log_error
)

from ops.system_health import (
    health_report
)

from ops.backup_manager import (
    create_backup
)

from monitoring.alerts import (
    AlertManager
)

from signals.live_signals import (
    generate_live_signal
)

from portfolio.live_monitor import (
    live_portfolio_report
)

# =========================================================
# GLOBAL CONFIG
# =========================================================

SYMBOLS = [

    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS"
]

WEIGHTS = [

    0.30,
    0.25,
    0.25,
    0.20
]

# =========================================================
# ORCHESTRATOR
# =========================================================

class InstitutionalOrchestrator:

    def __init__(self):

        self.alerts = AlertManager()

        self.running = False

    # =====================================================
    # SYSTEM HEALTH
    # =====================================================

    def run_health_check(self):

        try:

            report = health_report()

            log_info(

                f"Health Report: {report}"
            )

        except Exception as e:

            log_error(

                f"Health Check Failed: {e}"
            )

    # =====================================================
    # LIVE SIGNALS
    # =====================================================

    def run_signals(self):

        try:

            for symbol in SYMBOLS:

                signal = generate_live_signal(

                    symbol
                )

                log_info(

                    f"Signal: {signal}"
                )

        except Exception as e:

            log_error(

                f"Signal Engine Failed: {e}"
            )

    # =====================================================
    # PORTFOLIO MONITOR
    # =====================================================

    def run_portfolio_monitor(self):

        try:

            report = live_portfolio_report(

                SYMBOLS,

                WEIGHTS
            )

            log_info(

                f"Portfolio Report: {report}"
            )

        except Exception as e:

            log_error(

                f"Portfolio Monitor Failed: {e}"
            )

    # =====================================================
    # BACKUP
    # =====================================================

    def run_backup(self):

        try:

            result = create_backup()

            log_info(

                f"Backup Created: {result}"
            )

        except Exception as e:

            log_error(

                f"Backup Failed: {e}"
            )

    # =====================================================
    # ALERT TEST
    # =====================================================

    def run_alerts(self):

        self.alerts.signal_alert(

            "RELIANCE.NS",

            "BUY"
        )

        self.alerts.volatility_alert(

            0.40
        )

        self.alerts.risk_alert(

            -0.15
        )

        log_info(

            f"Alerts: {self.alerts.get_alerts()}"
        )

    # =====================================================
    # MAIN LOOP
    # =====================================================

    def start(self):

        self.running = True

        log_info(

            "Institutional Orchestrator Started"
        )

        while self.running:

            self.run_health_check()

            self.run_signals()

            self.run_portfolio_monitor()

            self.run_alerts()

            self.run_backup()

            time.sleep(60)

    # =====================================================
    # STOP
    # =====================================================

    def stop(self):

        self.running = False

        log_info(

            "Institutional Orchestrator Stopped"
        )