from pathlib import Path
import pandas as pd

# =========================================================
# SYSTEM HEALTH MONITOR
# =========================================================

class SystemHealthMonitor:

    def __init__(self):

        pass

    # =====================================================
    # FILE CHECK
    # =====================================================

    def file_status(

        self,

        filepath
    ):

        path = Path(filepath)

        return {

            "Exists":

                path.exists(),

            "Size KB":

                round(

                    path.stat().st_size / 1024,

                    2
                )

                if path.exists()

                else 0
        }

    # =====================================================
    # DIRECTORY CHECK
    # =====================================================

    def directory_status(

        self,

        directory
    ):

        path = Path(directory)

        if not path.exists():

            return {

                "Exists": False,

                "Files": 0
            }

        files = list(

            path.glob("*")
        )

        return {

            "Exists": True,

            "Files": len(files)
        }

    # =====================================================
    # FULL HEALTH REPORT
    # =====================================================

    def full_health_report(self):

        report = {

            "Ranked Universe":

                self.file_status(

                    "ranked_universe.xlsx"
                ),

            "Market Cache":

                self.directory_status(

                    "cache/market_data"
                ),

            "Research Cache":

                self.file_status(

                    "cache/research_cache.db"
                ),

            "Paper Portfolio DB":

                self.file_status(

                    "paper_trading/paper_portfolio.db"
                ),

            "Backups":

                self.directory_status(

                    "backups"
                ),

            "Automation Logs":

                self.file_status(

                    "automation/refresh_log.csv"
                ),

            "Platform Logs":

                self.file_status(

                    "institutional_platform.log"
                )
        }

        return report

    # =====================================================
    # DATAFRAME VIEW
    # =====================================================

    def report_dataframe(self):

        report = self.full_health_report()

        rows = []

        for component, status in report.items():

            row = {

                "Component":

                    component
            }

            row.update(status)

            rows.append(row)

        return pd.DataFrame(rows)