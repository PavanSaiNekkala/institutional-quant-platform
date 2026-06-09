import pandas as pd

# =========================================================
# NORMALIZE FACTOR
# =========================================================


def normalize_series(series):

    normalized = (series - series.mean()) / (series.std() + 1e-9)

    return normalized


# =========================================================
# CROSS SECTIONAL SCORE
# =========================================================


def cross_sectional_score(factor_df, factor_weights):

    total_score = pd.Series(0, index=factor_df.index, dtype=float)

    contributions = {}

    for factor in factor_df.columns:
        normalized = normalize_series(factor_df[factor])

        weight = factor_weights.get(factor, 0)

        contribution = normalized * weight

        contributions[factor] = contribution

        total_score += contribution

    return total_score, contributions


# =========================================================
# ALPHA RANKING
# =========================================================


def alpha_ranking(alpha_scores):

    ranked = alpha_scores.sort_values(ascending=False)

    return ranked


# =========================================================
# PERCENTILE RANK
# =========================================================


def percentile_rank(alpha_scores):

    percentile = alpha_scores.rank(pct=True)

    return percentile


# =========================================================
# CLASSIFICATION
# =========================================================


def alpha_classification(percentile):

    if percentile >= 0.90:
        return "ELITE_ALPHA"

    elif percentile >= 0.75:
        return "HIGH_ALPHA"

    elif percentile >= 0.50:
        return "NEUTRAL"

    return "WEAK_ALPHA"
