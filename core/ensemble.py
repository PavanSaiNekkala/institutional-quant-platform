import pandas as pd
import numpy as np

# =========================================================
# NORMALIZE MODEL SCORES
# =========================================================

def normalize_scores(

    scores
):

    normalized = (

        (scores - scores.mean())

        /

        (scores.std() + 1e-9)
    )

    return normalized

# =========================================================
# ENSEMBLE SCORE
# =========================================================

def ensemble_score(

    model_scores,

    model_weights
):

    combined = pd.Series(

        0,

        index=model_scores.index,

        dtype=float
    )

    contributions = {}

    for model in model_scores.columns:

        normalized = normalize_scores(

            model_scores[model]
        )

        weight = model_weights.get(

            model,

            0
        )

        contribution = (

            normalized * weight
        )

        contributions[model] = contribution

        combined += contribution

    return combined, contributions

# =========================================================
# ENSEMBLE RANKING
# =========================================================

def ensemble_ranking(

    ensemble_scores
):

    ranking = (

        ensemble_scores

        .sort_values(

            ascending=False
        )
    )

    return ranking

# =========================================================
# CONFIDENCE SCORE
# =========================================================

def confidence_score(

    contribution_df
):

    dispersion = contribution_df.std(

        axis=1
    )

    confidence = 1 / (

        dispersion + 1e-9
    )

    return confidence

# =========================================================
# ENSEMBLE CLASSIFICATION
# =========================================================

def ensemble_classification(

    percentile
):

    if percentile >= 0.90:

        return "INSTITUTIONAL_LONG"

    elif percentile >= 0.75:

        return "HIGH_CONVICTION"

    elif percentile >= 0.50:

        return "WATCHLIST"

    return "AVOID"