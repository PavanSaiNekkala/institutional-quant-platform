import time

from core.master_automation import MasterAutomation

# =========================================================
# CONTINUOUS SCHEDULER
# =========================================================


class ContinuousScheduler:
    def __init__(self):

        self.engine = MasterAutomation()

    # =====================================================
    # RUN LOOP
    # =====================================================

    def run(self, refresh_limit=20, interval_minutes=60):

        print("\nCONTINUOUS SCHEDULER STARTED\n")

        while True:
            try:
                results = self.engine.run_full_cycle(refresh_limit=refresh_limit)

                print("\nCYCLE COMPLETE\n")

                print(results)

            except Exception as e:
                print(f"\nSCHEDULER ERROR: {e}\n")

            # =============================================
            # SLEEP
            # =============================================

            sleep_seconds = interval_minutes * 60

            print(f"\nSLEEPING {interval_minutes} MINUTES\n")

            time.sleep(sleep_seconds)
