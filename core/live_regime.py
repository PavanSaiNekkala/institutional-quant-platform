# =========================================================
# FILE: core/live_regime.py
# =========================================================

import yfinance as yf
import pandas as pd
import numpy as np


# =========================================================
# DETECT LIVE MARKET REGIME
# =========================================================

def detect_market_regime():

    try:

        # =================================================
        # NIFTY DATA
        # =================================================

        nifty = yf.download(

            "^NSEI",

            period="6mo",

            progress=False,

            auto_adjust=True
        )

        if nifty.empty:

            return "UNKNOWN"

        close = nifty["Close"].dropna()

        if isinstance(close, pd.DataFrame):

            close = close.iloc[:, 0]

        # =================================================
        # MOVING AVERAGES
        # =================================================

        sma20 = close.rolling(20).mean().iloc[-1]

        sma50 = close.rolling(50).mean().iloc[-1]

        sma200 = close.rolling(200).mean().iloc[-1]

        current = close.iloc[-1]

        # =================================================
        # RETURNS
        # =================================================

        returns = close.pct_change().dropna()

        volatility = (

            returns.std()
            * np.sqrt(252)
        )

        # =================================================
        # RSI
        # =================================================

        delta = close.diff()

        gain = (

            delta.where(delta > 0, 0)
            .rolling(14)
            .mean()
        )

        loss = (

            -delta.where(delta < 0, 0)
            .rolling(14)
            .mean()
        )

        rs = gain / loss

        rsi = 100 - (

            100 / (1 + rs)
        )

        rsi = rsi.iloc[-1]

        # =================================================
        # TREND LOGIC
        # =================================================

        bullish_trend = (

            current > sma20 >

            sma50 > sma200
        )

        bearish_trend = (

            current < sma20 <

            sma50 < sma200
        )

        # =================================================
        # REGIME DETECTION
        # =================================================

        if bullish_trend:

            if volatility > 0.30:

                return "BULLISH_HIGH_VOL"

            return "BULLISH"

        elif bearish_trend:

            if volatility > 0.30:

                return "BEARISH_HIGH_VOL"

            return "BEARISH"

        else:

            if rsi > 60:

                return "SIDEWAYS_BULLISH"

            elif rsi < 40:

                return "SIDEWAYS_BEARISH"

            else:

                return "SIDEWAYS"

    except Exception:

        return "UNKNOWN"