import numpy as np
import pandas as pd

# =========================================================
# EXPONENTIAL MOVING AVERAGE
# =========================================================


def EMA(series, period):

    return series.ewm(span=period, adjust=False).mean()


# =========================================================
# RELATIVE STRENGTH INDEX
# =========================================================


def RSI(close, period=14):

    delta = close.diff()

    gain = delta.clip(lower=0)

    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()

    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / (avg_loss + 1e-9)

    rsi = 100 - (100 / (1 + rs))

    return rsi


# =========================================================
# AVERAGE TRUE RANGE
# =========================================================


def ATR(df, period=14):

    tr = pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - df["close"].shift()).abs(),
            (df["low"] - df["close"].shift()).abs(),
        ],
        axis=1,
    ).max(axis=1)

    atr = tr.rolling(period).mean()

    return atr


# =========================================================
# HISTORICAL VOLATILITY
# =========================================================


def volatility(close, period=20):

    returns = close.pct_change()

    vol = returns.rolling(period).std() * np.sqrt(252)

    return vol


# =========================================================
# MOMENTUM
# =========================================================


def momentum(close, period):

    return close.pct_change(period)


# =========================================================
# DISTANCE FROM HIGH
# =========================================================


def distance_from_high(close, period=252):

    rolling_high = close.rolling(period).max()

    distance = close / rolling_high

    return distance


# =========================================================
# VOLUME RATIO
# =========================================================


def volume_ratio(volume, period=20):

    avg_volume = volume.rolling(period).mean()

    ratio = volume / (avg_volume + 1e-9)

    return ratio


# =========================================================
# TREND QUALITY
# =========================================================


def trend_quality(df):

    trend = (
        (df["ema20"] > df["ema50"]).astype(int)
        + (df["ema50"] > df["ema100"]).astype(int)
        + (df["ema100"] > df["ema200"]).astype(int)
    )

    return trend


# =========================================================
# VOLATILITY CONTRACTION
# =========================================================


def volatility_contraction(df):

    vc = df["atr"] / df["close"]

    return vc


# =========================================================
# BETA VS BENCHMARK
# =========================================================


def beta(stock_returns, benchmark_returns):

    covariance = np.cov(stock_returns.dropna(), benchmark_returns.dropna())[0][1]

    benchmark_variance = np.var(benchmark_returns.dropna())

    beta_value = covariance / (benchmark_variance + 1e-9)

    return beta_value


# =========================================================
# ALPHA
# =========================================================


def alpha(stock_return, benchmark_return, beta_value):

    alpha_value = stock_return - beta_value * benchmark_return

    return alpha_value
