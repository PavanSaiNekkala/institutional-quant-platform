import numpy as np
import pandas as pd
import yfinance as yf

# =========================================================
# REGIME DETECTOR
# =========================================================


class RegimeDetector:
    def __init__(self, volatility_threshold=0.25):

        self.volatility_threshold = volatility_threshold

    # =====================================================
    # DETECT REGIME
    # =====================================================

    def detect(self, symbol="^NSEI", period="1y"):

        try:
            data = yf.download(symbol, period=period, progress=False, auto_adjust=True)

            if data.empty:
                return None

            close = data["Close"]

            if isinstance(close, pd.DataFrame):
                close = close.iloc[:, 0]

            returns = close.pct_change().dropna()

            if len(returns) < 50:
                return None

            # =================================================
            # METRICS
            # =================================================

            annual_volatility = returns.std() * np.sqrt(252)

            momentum = (close.iloc[-1] / close.iloc[-50]) - 1

            moving_average = close.rolling(50).mean().iloc[-1]

            current_price = close.iloc[-1]

            # =================================================
            # REGIME CLASSIFICATION
            # =================================================

            if annual_volatility > self.volatility_threshold:
                volatility_regime = "HIGH VOL"

            else:
                volatility_regime = "LOW VOL"

            if current_price > moving_average:
                trend_regime = "BULL"

            else:
                trend_regime = "BEAR"

            if momentum > 0:
                momentum_regime = "POSITIVE"

            else:
                momentum_regime = "NEGATIVE"

            overall_regime = f"{trend_regime} | {volatility_regime} | {momentum_regime}"

            return {
                "Symbol": symbol,
                "Current Price": round(current_price, 2),
                "50D Moving Average": round(moving_average, 2),
                "Annual Volatility": round(annual_volatility, 4),
                "Momentum": round(momentum, 4),
                "Trend Regime": trend_regime,
                "Volatility Regime": volatility_regime,
                "Momentum Regime": momentum_regime,
                "Overall Regime": overall_regime,
            }

        except Exception as e:
            print(f"REGIME ERROR: {e}")

            return None
