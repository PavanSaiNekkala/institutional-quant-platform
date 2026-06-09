# =========================================================
# RELATIVE STRENGTH VS BENCHMARK
# =========================================================


def relative_strength(stock_returns, benchmark_returns):

    rs = (1 + stock_returns).cumprod() / (1 + benchmark_returns).cumprod()

    return rs


# =========================================================
# RELATIVE MOMENTUM
# =========================================================


def relative_momentum(stock_returns, benchmark_returns, window=63):

    rs = relative_strength(stock_returns, benchmark_returns)

    momentum = rs.pct_change(window)

    return momentum


# =========================================================
# CROSS-SECTIONAL RANKING
# =========================================================


def cross_sectional_rank(momentum_series):

    ranks = momentum_series.rank(ascending=False, pct=True)

    return ranks


# =========================================================
# LEADERSHIP SCORE
# =========================================================


def leadership_score(relative_momentum, percentile_rank):

    score = 0.7 * relative_momentum + 0.3 * percentile_rank

    return score


# =========================================================
# LEADER CLASSIFICATION
# =========================================================


def classify_leader(score):

    if score > 0.80:
        return "MARKET_LEADER"

    elif score > 0.60:
        return "OUTPERFORMER"

    elif score > 0.40:
        return "NEUTRAL"

    return "LAGGARD"
