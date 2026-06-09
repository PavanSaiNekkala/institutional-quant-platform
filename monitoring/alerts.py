from datetime import datetime

# =========================================================
# ALERT CLASS
# =========================================================


class AlertManager:
    def __init__(self):

        self.alerts = []

    # =====================================================
    # CREATE ALERT
    # =====================================================

    def create_alert(self, level, message):

        alert = {"Timestamp": datetime.now(), "Level": level, "Message": message}

        self.alerts.append(alert)

    # =====================================================
    # RISK ALERT
    # =====================================================

    def risk_alert(self, drawdown, threshold=-0.10):

        if drawdown < threshold:
            self.create_alert("CRITICAL", f"Drawdown breach: {drawdown:.2%}")

    # =====================================================
    # VOLATILITY ALERT
    # =====================================================

    def volatility_alert(self, volatility, threshold=0.30):

        if volatility > threshold:
            self.create_alert("WARNING", f"High volatility detected: {volatility:.2%}")

    # =====================================================
    # SIGNAL ALERT
    # =====================================================

    def signal_alert(self, symbol, decision):

        self.create_alert("INFO", f"{symbol} signal changed to {decision}")

    # =====================================================
    # RETURN ALERTS
    # =====================================================

    def get_alerts(self):

        return self.alerts
