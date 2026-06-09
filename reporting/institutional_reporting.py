from datetime import datetime

import pandas as pd

# =========================================================
# REPORT GENERATOR
# =========================================================


class InstitutionalReportGenerator:
    def __init__(self):

        self.timestamp = datetime.now()

    # =====================================================
    # CREATE REPORT
    # =====================================================

    def generate_report(self, regime_data, strategy_data, allocation_df, backtest_metrics):

        report = {
            "Generated At": str(self.timestamp),
            "Market Regime": regime_data,
            "Strategy Selection": strategy_data,
            "Backtest Metrics": backtest_metrics,
        }

        allocation_records = allocation_df.to_dict(orient="records")

        report["Portfolio Allocation"] = allocation_records

        return report

    # =====================================================
    # EXPORT REPORT
    # =====================================================

    def export_excel(self, allocation_df, metrics_df, filename="institutional_report.xlsx"):

        with pd.ExcelWriter(filename) as writer:
            allocation_df.to_excel(writer, sheet_name="Allocation", index=False)

            metrics_df.to_excel(writer, sheet_name="Metrics", index=False)

        return filename
