import numpy as np
import pandas as pd

from core.adaptive_weights import adaptive_factor_score
from core.alpha_model import cross_sectional_score
from core.ensemble import ensemble_score

# =========================================================
# BUILD FACTOR MATRIX
# =========================================================


def build_factor_matrix(stocks):

    np.random.seed(42)

    factor_df = pd.DataFrame(
        {
            "momentum": np.random.normal(0.8, 0.2, len(stocks)),
            "quality": np.random.normal(0.7, 0.15, len(stocks)),
            "flows": np.random.normal(0.75, 0.18, len(stocks)),
            "relative_strength": np.random.normal(0.78, 0.16, len(stocks)),
            "volatility": np.random.normal(-0.30, 0.12, len(stocks)),
        },
        index=stocks,
    )

    return factor_df


# =========================================================
# BASE FACTOR WEIGHTS
# =========================================================

BASE_WEIGHTS = {
    "momentum": 0.30,
    "relative_strength": 0.25,
    "quality": 0.20,
    "flows": 0.15,
    "volatility": 0.10,
}

# =========================================================
# ORCHESTRATION ENGINE
# =========================================================


def orchestrate_portfolio(stocks, regime="BULL_NORMAL_VOL"):

    # =====================================================
    # FACTOR MATRIX
    # =====================================================

    factor_df = build_factor_matrix(stocks)

    # =====================================================
    # CROSS SECTIONAL
    # =====================================================

    alpha_scores, contributions = cross_sectional_score(factor_df, BASE_WEIGHTS)

    # =====================================================
    # ENSEMBLE INPUT
    # =====================================================

    model_scores = pd.DataFrame(
        {
            "alpha_model": alpha_scores,
            "momentum_model": factor_df["momentum"],
            "quality_model": factor_df["quality"],
            "flow_model": factor_df["flows"],
        }
    )

    ensemble_scores, ensemble_contrib = ensemble_score(
        model_scores,
        {"alpha_model": 0.40, "momentum_model": 0.20, "quality_model": 0.20, "flow_model": 0.20},
    )

    # =====================================================
    # ADAPTIVE OVERLAY
    # =====================================================

    adaptive_scores = []

    for stock in factor_df.index:
        row = factor_df.loc[stock]

        factor_values = row.to_dict()

        score, _, _ = adaptive_factor_score(factor_values, regime)

        adaptive_scores.append(score)

    adaptive_scores = pd.Series(adaptive_scores, index=factor_df.index)

    # =====================================================
    # FINAL SCORE
    # =====================================================

    final_score = 0.50 * alpha_scores + 0.30 * ensemble_scores + 0.20 * adaptive_scores

    # =====================================================
    # FINAL RANKING
    # =====================================================

    results = pd.DataFrame(
        {
            "Alpha Score": alpha_scores,
            "Ensemble Score": ensemble_scores,
            "Adaptive Score": adaptive_scores,
            "Final Score": final_score,
        }
    )

    results["Percentile"] = results["Final Score"].rank(pct=True)

    results["Classification"] = np.where(
        results["Percentile"] >= 0.90,
        "INSTITUTIONAL_LONG",
        np.where(
            results["Percentile"] >= 0.75,
            "HIGH_CONVICTION",
            np.where(results["Percentile"] >= 0.50, "WATCHLIST", "AVOID"),
        ),
    )

    results = results.sort_values("Final Score", ascending=False)

    return results
