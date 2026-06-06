import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from automation.notifications import (
    send_telegram_alert
)

# =====================================================
# TELEGRAM TEST
# =====================================================

telegram_success = send_telegram_alert(

    "🚀 Institutional Quant Platform Active"
)

print("\nTELEGRAM STATUS")

print(telegram_success)
