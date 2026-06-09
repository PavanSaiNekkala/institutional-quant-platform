import numpy as np
import pandas as pd

# =========================================================
# BUILD RETURNS MATRIX
# =========================================================


def build_returns_matrix(stock_data, symbols):

    returns_list = []

    valid_symbols = []

    for symbol in symbols:
        try:
            df = stock_data[symbol]

            close = df["close"]

            returns = close.pct_change()

            returns.name = symbol

            returns_list.append(returns)

            valid_symbols.append(symbol)

        except Exception:
            continue

    returns_df = pd.concat(returns_list, axis=1).dropna()

    return returns_df


# =========================================================
# COVARIANCE MATRIX
# =========================================================


def covariance_matrix(returns_df):

    cov_matrix = returns_df.cov() * 252

    return cov_matrix


# =========================================================
# CORRELATION MATRIX
# =========================================================


def correlation_matrix(returns_df):

    corr_matrix = returns_df.corr()

    return corr_matrix


# =========================================================
# PORTFOLIO VOLATILITY
# =========================================================


def portfolio_volatility(weights, cov_matrix):

    weights = np.array(weights)

    volatility = np.sqrt(weights.T @ cov_matrix @ weights)

    return volatility


# =========================================================
# CORRELATION FILTER
# =========================================================


def correlation_filter(returns_df, threshold=0.80):

    corr_matrix = returns_df.corr()

    selected = []

    symbols = corr_matrix.columns.tolist()

    for symbol in symbols:
        keep = True

        for existing in selected:
            correlation = corr_matrix.loc[symbol, existing]

            if correlation > threshold:
                keep = False

                break

        if keep:
            selected.append(symbol)

    return selected
