# =========================================================
# FILE: core/live_regime.py
# =========================================================

import yfinance as yf
import pandas as pd
import numpy as np

# =========================================================
# MARKET REGIME DETECTOR
# =========================================================

def detect_market_regime():

    try:

        # =================================================
        # NIFTY 50 INDEX
        # =================================================

        nifty = yf.download(

            "^NSEI",

            period="6mo",

            interval="1d",

            auto_adjust=True,

            progress=False,

            threads=False
        )

        if nifty.empty:

            return "SIDEWAYS"

        close = nifty["Close"]

        # =================================================
        # MOVING AVERAGES
        # =================================================

        sma20 = (
            close
            .rolling(20)
            .mean()
            .iloc[-1]
        )

        sma50 = (
            close
            .rolling(50)
            .mean()
            .iloc[-1]
        )

        current_price = close.iloc[-1]

        volatility = (
            close
            .pct_change()
            .rolling(20)
            .std()
            .iloc[-1]
        )

        # =================================================
        # REGIME LOGIC
        # =================================================

        if current_price > sma20 > sma50:

            if volatility < 0.015:

                return "BULLISH"

            else:

                return "VOLATILE_BULLISH"

        elif current_price < sma20 < sma50:

            if volatility < 0.015:

                return "BEARISH"

            else:

                return "VOLATILE_BEARISH"

        else:

            return "SIDEWAYS"

    except Exception as e:

        print(f"Market Regime Error: {e}")

        return "SIDEWAYS"
