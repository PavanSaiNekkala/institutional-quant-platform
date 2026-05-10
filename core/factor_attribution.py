import pandas as pd
import numpy as np

# =========================================================
# NORMALIZE FACTORS
# =========================================================

def normalize_factor(

    series
):

    normalized = (

        (series - series.mean())

        /

        (series.std() + 1e-9)
    )

    return normalized

# =========================================================
# FACTOR SCORE
# =========================================================

def factor_score(

    factors,

    weights
):

    total = 0

    contributions = {}

    for factor_name, values in factors.items():

        factor_weight = weights.get(

            factor_name,

            0
        )

        contribution = (

            values * factor_weight
        )

        contributions[factor_name] = contribution

        total += contribution

    return total, contributions

# =========================================================
# FACTOR CONTRIBUTION TABLE
# =========================================================

def contribution_table(

    contributions
):

    table = pd.DataFrame(

        contributions
    )

    return table

# =========================================================
# TOP FACTOR
# =========================================================

def dominant_factor(

    latest_contributions
):

    abs_values = {

        k: abs(v)

        for k, v in latest_contributions.items()
    }

    dominant = max(

        abs_values,

        key=abs_values.get
    )

    return dominant

# =========================================================
# FACTOR STABILITY
# =========================================================

def factor_stability(

    contribution_series
):

    stability = (

        contribution_series.mean()

        /

        (contribution_series.std() + 1e-9)
    )

    return stability