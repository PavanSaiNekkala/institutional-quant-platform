import pandas as pd

# =========================================================
# GENERATE FACTORS
# =========================================================


def generate_factors(prices):

    df = pd.DataFrame()

    # =====================================================
    # RETURNS
    # =====================================================

    df["returns"] = prices.pct_change()

    # =====================================================
    # MOMENTUM
    # =====================================================

    df["momentum_20"] = prices / prices.shift(20)

    # =====================================================
    # VOLATILITY
    # =====================================================

    df["volatility_20"] = df["returns"].rolling(20).std()

    # =====================================================
    # MEAN REVERSION
    # =====================================================

    ma20 = prices.rolling(20).mean()

    df["mean_reversion"] = (prices - ma20) / ma20

    # =====================================================
    # TARGET
    # =====================================================

    df["future_return"] = df["returns"].shift(-1)

    return df.dropna()


# =========================================================
# FACTOR CORRELATION
# =========================================================


def factor_correlation(factors):

    correlations = {}

    target = factors["future_return"]

    for col in factors.columns:
        if col != "future_return":
            corr = factors[col].corr(target)

            correlations[col] = corr

    return pd.Series(correlations)


# =========================================================
# ALPHA RANKING
# =========================================================


def alpha_ranking(correlations):

    ranking = correlations.abs().sort_values(ascending=False)

    return ranking


# =========================================================
# ALPHA REPORT
# =========================================================


def alpha_report(prices):

    factors = generate_factors(prices)

    correlations = factor_correlation(factors)

    ranking = alpha_ranking(correlations)

    report = pd.DataFrame({"Factor": ranking.index, "Alpha Score": ranking.values})

    return report
