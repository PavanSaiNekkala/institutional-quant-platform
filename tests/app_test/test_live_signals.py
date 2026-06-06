import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from signals.live_signals import (
    generate_live_signal
)

# =====================================================
# TEST SYMBOL
# =====================================================

report = generate_live_signal(

    "RELIANCE.NS"
)

# =====================================================
# OUTPUT
# =====================================================

print("\nLIVE SIGNAL REPORT\n")

for k, v in report.items():

    print(f"{k}: {v}")
