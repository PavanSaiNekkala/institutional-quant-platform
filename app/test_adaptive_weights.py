import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from core.adaptive_weights import (
    get_regime_weights,
    normalize_weights,
    adaptive_factor_score,
    dominant_weight
)

# =====================================================
# SAMPLE REGIME
# =====================================================

regime = "BULL_NORMAL_VOL"

# =====================================================
# SAMPLE FACTORS
# =====================================================

factor_values = {

    "momentum": 0.82,

    "relative_strength": 0.74,

    "flows": 0.61,

    "quality": 0.55,

    "volatility": 0.40
}

# =====================================================
# GET WEIGHTS
# =====================================================

weights = get_regime_weights(

    regime
)

weights = normalize_weights(

    weights
)

print("\nREGIME")

print(regime)

print("\nADAPTIVE WEIGHTS")

print(weights)

# =====================================================
# ADAPTIVE SCORE
# =====================================================

score, contributions, final_weights = (

    adaptive_factor_score(

        factor_values,

        regime
    )
)

print("\nADAPTIVE FACTOR SCORE")

print(score)

print("\nFACTOR CONTRIBUTIONS")

print(contributions)

# =====================================================
# DOMINANT FACTOR
# =====================================================

dominant = dominant_weight(

    final_weights
)

print("\nDOMINANT FACTOR")

print(dominant)