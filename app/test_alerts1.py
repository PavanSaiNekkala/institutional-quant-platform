import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from monitoring.alerts import (
    AlertManager
)

# =====================================================
# ALERT SYSTEM
# =====================================================

alerts = AlertManager()

# =====================================================
# CREATE ALERTS
# =====================================================

alerts.risk_alert(

    drawdown=-0.15
)

alerts.volatility_alert(

    volatility=0.42
)

alerts.signal_alert(

    symbol="RELIANCE.NS",

    decision="BUY"
)

# =====================================================
# OUTPUT
# =====================================================

print("\nINSTITUTIONAL ALERTS\n")

for alert in alerts.get_alerts():

    print(alert)