# =========================================================
# POSITION EXPOSURE
# =========================================================


def calculate_exposure(weights):

    total = sum(weights.values())

    normalized = {k: v / total for k, v in weights.items()}

    return normalized
