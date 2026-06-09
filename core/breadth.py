# =========================================================
# ADVANCE DECLINE RATIO
# =========================================================


def advance_decline_ratio(returns_df):

    advancing = (returns_df > 0).sum(axis=1)

    declining = (returns_df < 0).sum(axis=1)

    ratio = advancing / (declining + 1e-9)

    return ratio


# =========================================================
# BREADTH MOMENTUM
# =========================================================


def breadth_momentum(returns_df, window=20):

    adv_dec = advance_decline_ratio(returns_df)

    momentum = adv_dec.rolling(window).mean()

    return momentum


# =========================================================
# PERCENT ABOVE MOVING AVERAGE
# =========================================================


def percent_above_ma(price_df, window=50):

    ma = price_df.rolling(window).mean()

    above = price_df > ma

    pct = above.sum(axis=1) / len(price_df.columns)

    return pct


# =========================================================
# MARKET BREADTH SCORE
# =========================================================


def breadth_score(adv_dec_ratio, pct_above_ma):

    score = 0.5 * adv_dec_ratio + 0.5 * pct_above_ma

    return score


# =========================================================
# BREADTH REGIME
# =========================================================


def breadth_regime(breadth_score_series):

    latest = breadth_score_series.iloc[-1]

    if latest > 1.2:
        return "STRONG_BREADTH"

    elif latest > 0.8:
        return "NORMAL_BREADTH"

    return "WEAK_BREADTH"
