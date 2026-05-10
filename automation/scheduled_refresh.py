import sys
import time
import schedule
import pandas as pd

from pathlib import Path
from datetime import datetime

# =========================================================
# ROOT DIRECTORY
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

# =========================================================
# IMPORTS
# =========================================================

from core.universe_loader import (
    load_ranked_universe
)

# =========================================================
# REFRESH TASK
# =========================================================

def refresh_ranked_universe():

    try:

        symbols = load_ranked_universe(

            top_n=25
        )

        timestamp = datetime.now()

        log_file = (

            ROOT_DIR

            / "automation"

            / "refresh_log.csv"
        )

        log = pd.DataFrame({

            "Timestamp": [

                str(timestamp)
            ],

            "Universe Size": [

                len(symbols)
            ]
        })

        file_exists = log_file.exists()

        log.to_csv(

            log_file,

            mode="a",

            index=False,

            header=not file_exists
        )

        print(

            f"\nREFRESH COMPLETED "

            f"| {timestamp} "

            f"| Universe Size: {len(symbols)}"
        )

    except Exception as e:

        print(

            f"\nREFRESH ERROR: {e}"
        )

# =========================================================
# SCHEDULER
# =========================================================

schedule.every(1).hours.do(

    refresh_ranked_universe
)

# =========================================================
# STARTUP MESSAGE
# =========================================================

print(

    "\nAUTOMATED REFRESH SYSTEM STARTED\n"
)

# =========================================================
# INITIAL REFRESH
# =========================================================

refresh_ranked_universe()

# =========================================================
# MAIN LOOP
# =========================================================

while True:

    schedule.run_pending()

    time.sleep(1)