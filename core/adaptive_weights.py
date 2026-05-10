# =========================================================
# REGIME-BASED FACTOR WEIGHTS
# =========================================================

REGIME_WEIGHTS = {

    "BULL_LOW_VOL": {

        "momentum": 0.40,
        "relative_strength": 0.30,
        "flows": 0.20,
        "quality": 0.10
    },

    "BULL_NORMAL_VOL": {

        "momentum": 0.35,
        "relative_strength": 0.25,
        "flows": 0.20,
        "quality": 0.20
    },

    "BULL_HIGH_VOL": {

        "quality": 0.35,
        "volatility": 0.30,
        "flows": 0.20,
        "momentum": 0.15
    },

    "BEAR_LOW_VOL": {

        "quality": 0.40,
        "volatility": 0.30,
        "flows": 0.20,
        "momentum": 0.10
    },

    "BEAR_NORMAL_VOL": {

        "quality": 0.45,
        "volatility": 0.35,
        "flows": 0.15,
        "momentum": 0.05
    },

    "BEAR_HIGH_VOL": {

        "volatility": 0.50,
        "quality": 0.30,
        "flows": 0.15,
        "momentum": 0.05
    }
}

# =========================================================
# GET REGIME WEIGHTS
# =========================================================

def get_regime_weights(

    regime
):

    return REGIME_WEIGHTS.get(

        regime,

        REGIME_WEIGHTS["BULL_NORMAL_VOL"]
    )

# =========================================================
# NORMALIZE WEIGHTS
# =========================================================

def normalize_weights(

    weights
):

    total = sum(weights.values())

    normalized = {

        k: v / total

        for k, v in weights.items()
    }

    return normalized

# =========================================================
# ADAPTIVE FACTOR SCORE
# =========================================================

def adaptive_factor_score(

    factor_values,

    regime
):

    weights = get_regime_weights(

        regime
    )

    weights = normalize_weights(

        weights
    )

    score = 0

    contributions = {}

    for factor, value in factor_values.items():

        weight = weights.get(

            factor,

            0
        )

        contribution = (

            value * weight
        )

        contributions[factor] = contribution

        score += contribution

    return (

        score,

        contributions,

        weights
    )

# =========================================================
# FACTOR PRIORITY
# =========================================================

def dominant_weight(

    weights
):

    dominant = max(

        weights,

        key=weights.get
    )

    return dominant