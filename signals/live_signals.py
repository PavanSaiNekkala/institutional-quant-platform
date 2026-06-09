import numpy as np
import pandas as pd

from signals.live_data import fetch_stock_data

# =========================================================
# MOMENTUM SIGNAL
# =========================================================


def momentum_signal(prices):

    momentum = (prices.iloc[-1] / prices.iloc[-20]) - 1

    return momentum


# =========================================================
# VOLATILITY SIGNAL
# =========================================================


def volatility_signal(returns):

    vol = returns.std() * np.sqrt(252)

    return vol


# =========================================================
# MEAN REVERSION SIGNAL
# =========================================================


def mean_reversion_signal(prices):

    ma20 = prices.rolling(20).mean()

    signal = (prices.iloc[-1] - ma20.iloc[-1]) / ma20.iloc[-1]

    return signal


# =========================================================
# SIGNAL SCORING
# =========================================================


def signal_score(momentum, volatility, mean_reversion):

    score = float(momentum) * 0.5 - float(volatility) * 0.3 - float(mean_reversion) * 0.2

    return float(score)


# =========================================================
# SIGNAL DECISION
# =========================================================


def signal_decision(score):

    score = float(score)

    if score > 0.05:
        return "BUY"

    elif score < -0.05:
        return "SELL"

    else:
        return "HOLD"


# =========================================================
# LIVE SIGNAL ENGINE
# =========================================================


def generate_live_signal(symbol):

    data = fetch_stock_data(symbol, period="6mo")

    prices = data["Close"]

    # HANDLE DATAFRAME OUTPUT
    if isinstance(prices, pd.DataFrame):
        prices = prices.iloc[:, 0]

    prices = prices.dropna()

    returns = prices.pct_change().dropna()

    momentum = momentum_signal(prices)

    volatility = volatility_signal(returns)

    mean_reversion = mean_reversion_signal(prices)

    score = signal_score(momentum, volatility, mean_reversion)

    decision = signal_decision(score)

    report = {
        "Symbol": symbol,
        "Momentum": round(momentum, 4),
        "Volatility": round(volatility, 4),
        "Mean Reversion": round(mean_reversion, 4),
        "Signal Score": round(score, 4),
        "Decision": decision,
    }

    return report
