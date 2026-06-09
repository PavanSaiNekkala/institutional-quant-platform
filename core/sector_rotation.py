# =========================================================
# SECTOR ETF MAP
# =========================================================

SECTOR_ETFS = {
    "BANK": "^NSEBANK",
    "IT": "^CNXIT",
    "PHARMA": "^CNXPHARMA",
    "FMCG": "^CNXFMCG",
    "AUTO": "^CNXAUTO",
    "ENERGY": "^CNXENERGY",
}

# =========================================================
# SECTOR MOMENTUM
# =========================================================


def sector_momentum(price_series, window=63):

    momentum = price_series.pct_change(window)

    return momentum


# =========================================================
# RELATIVE SECTOR STRENGTH
# =========================================================


def relative_sector_strength(sector_returns, benchmark_returns):

    rs = (1 + sector_returns).cumprod() / (1 + benchmark_returns).cumprod()

    return rs


# =========================================================
# SECTOR RANKING
# =========================================================


def sector_ranking(sector_scores):

    ranked = sector_scores.sort_values(ascending=False)

    return ranked


# =========================================================
# ROTATION CLASSIFICATION
# =========================================================


def classify_sector(percentile_rank):

    if percentile_rank >= 0.80:
        return "LEADING"

    elif percentile_rank >= 0.60:
        return "OUTPERFORMING"

    elif percentile_rank >= 0.40:
        return "NEUTRAL"

    return "WEAK"
