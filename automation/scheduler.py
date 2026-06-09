import sys
import time
from pathlib import Path

import schedule

from core.export_engine import export_rankings
from core.orchestrator import orchestrate_portfolio

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

# =========================================================
# SAMPLE UNIVERSE
# =========================================================

STOCKS = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "LT.NS",
    "ITC.NS",
    "SUNPHARMA.NS",
    "BHARTIARTL.NS",
    "MARUTI.NS",
]

# =========================================================
# SCAN FUNCTION
# =========================================================


def institutional_scan():

    print("\nRUNNING INSTITUTIONAL SCAN...")

    results = orchestrate_portfolio(STOCKS, regime="BULL_NORMAL_VOL")

    export_path = export_rankings(results)

    print("\nSCAN COMPLETE")

    print("\nEXPORT GENERATED")

    print(export_path)


# =========================================================
# SCHEDULE
# =========================================================

schedule.every(1).minutes.do(institutional_scan)

print("\nINSTITUTIONAL AUTOMATION ACTIVE")

print("\nWAITING FOR NEXT SCAN...")

# =========================================================
# LOOP
# =========================================================

while True:
    schedule.run_pending()

    time.sleep(1)
