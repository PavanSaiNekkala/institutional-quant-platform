# =========================================================
# INSTITUTIONAL SCORING ENGINE
# =========================================================


def calculate_score(last, sector="GENERIC"):

    # =====================================================
    # MOMENTUM SCORE
    # =====================================================

    momentum_score = (
        0.15 * last["momentum_1m"]
        + 0.25 * last["momentum_3m"]
        + 0.35 * last["momentum_6m"]
        + 0.25 * last["momentum_12m"]
    )

    # =====================================================
    # TREND SCORE
    # =====================================================

    trend_score = last["trend_quality"] / 3

    # =====================================================
    # VOLUME PARTICIPATION
    # =====================================================

    volume_score = min(2, last["volume_ratio"]) / 2

    # =====================================================
    # VOLATILITY QUALITY
    # =====================================================

    volatility_score = 1 / (1 + last["volatility"])

    # =====================================================
    # BREAKOUT QUALITY
    # =====================================================

    breakout_score = last["distance_from_high"]

    # =====================================================
    # VOLATILITY CONTRACTION
    # =====================================================

    contraction_score = 1 / (1 + last["volatility_contraction"])

    # =====================================================
    # COMPOSITE SCORE
    # =====================================================

    score = (
        0.30 * momentum_score
        + 0.20 * trend_score
        + 0.15 * volume_score
        + 0.10 * volatility_score
        + 0.15 * breakout_score
        + 0.10 * contraction_score
    )

    # =====================================================
    # SECTOR ADAPTIVE BONUS
    # =====================================================

    sector_bonus = {
        "IT": 1.10,
        "BANK": 1.08,
        "PHARMA": 1.07,
        "ENERGY": 1.05,
        "FMCG": 1.04,
        "GENERIC": 1.00,
    }

    score *= sector_bonus.get(sector, 1.00)

    return score


# =========================================================
# SIGNAL CLASSIFICATION
# =========================================================


def classify_signal(score):

    if score >= 0.85:
        return "STRONG BUY"

    elif score >= 0.65:
        return "BUY"

    elif score >= 0.45:
        return "WATCH"

    return "AVOID"
