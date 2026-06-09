from datetime import datetime

import pandas as pd
import yfinance as yf

# =========================================================
# STANDARDIZE OHLCV
# =========================================================


def standardize_ohlcv(df):

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df.columns = [str(c).lower() for c in df.columns]

    return df


# =========================================================
# LIVE SINGLE STOCK
# =========================================================


def live_stock_data(symbol, period="5d", interval="15m"):

    data = yf.download(symbol, period=period, interval=interval, progress=False)

    data = standardize_ohlcv(data)

    return data


# =========================================================
# LIVE MULTI STOCK
# =========================================================


def live_market_snapshot(symbols, period="1d", interval="5m"):

    snapshot = {}

    for symbol in symbols:
        try:
            data = live_stock_data(symbol, period, interval)

            snapshot[symbol] = data

        except Exception:
            continue

    return snapshot


# =========================================================
# MARKET STATUS
# =========================================================


def market_timestamp():

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
