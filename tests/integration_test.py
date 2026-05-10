import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

# =========================================================
# IMPORTS
# =========================================================

from ops.system_health import (
    health_report
)

from ops.backup_manager import (
    create_backup
)

from signals.live_signals import (
    generate_live_signal
)

from portfolio.live_monitor import (
    live_portfolio_report
)

from monitoring.alerts import (
    AlertManager
)

# =========================================================
# TEST RESULTS
# =========================================================

results = []

# =========================================================
# HEALTH TEST
# =========================================================

try:

    report = health_report()

    results.append(

        ("Health System", "PASS")
    )

except Exception as e:

    results.append(

        ("Health System", f"FAIL: {e}")
    )

# =========================================================
# BACKUP TEST
# =========================================================

try:

    backup = create_backup()

    results.append(

        ("Backup System", "PASS")
    )

except Exception as e:

    results.append(

        ("Backup System", f"FAIL: {e}")
    )

# =========================================================
# SIGNAL TEST
# =========================================================

try:

    signal = generate_live_signal(

        "RELIANCE.NS"
    )

    results.append(

        ("Signal Engine", "PASS")
    )

except Exception as e:

    results.append(

        ("Signal Engine", f"FAIL: {e}")
    )

# =========================================================
# PORTFOLIO TEST
# =========================================================

try:

    portfolio = live_portfolio_report(

        [

            "RELIANCE.NS",
            "TCS.NS",
            "INFY.NS"
        ],

        [

            0.4,
            0.3,
            0.3
        ]
    )

    results.append(

        ("Portfolio Monitor", "PASS")
    )

except Exception as e:

    results.append(

        ("Portfolio Monitor", f"FAIL: {e}")
    )

# =========================================================
# ALERT TEST
# =========================================================

try:

    alerts = AlertManager()

    alerts.signal_alert(

        "RELIANCE.NS",

        "BUY"
    )

    results.append(

        ("Alert System", "PASS")
    )

except Exception as e:

    results.append(

        ("Alert System", f"FAIL: {e}")
    )

# =========================================================
# OUTPUT
# =========================================================

print("\nINTEGRATION TEST RESULTS\n")

for test, result in results:

    print(f"{test}: {result}")