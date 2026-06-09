# =========================================================
# SECTOR MAPPING
# =========================================================

SECTOR_MAP = {
    "RELIANCE.NS": "ENERGY",
    "TCS.NS": "IT",
    "INFY.NS": "IT",
    "HDFCBANK.NS": "BANK",
    "ICICIBANK.NS": "BANK",
    "LT.NS": "INFRA",
    "SUNPHARMA.NS": "PHARMA",
    "ITC.NS": "FMCG",
    "BHARTIARTL.NS": "TELECOM",
}

# =========================================================
# SECTOR CAP FILTER
# =========================================================


def apply_sector_caps(ranked_symbols, max_per_sector=2):

    selected = []

    sector_counts = {}

    for symbol in ranked_symbols:
        sector = SECTOR_MAP.get(symbol, "OTHER")

        current_count = sector_counts.get(sector, 0)

        if current_count >= max_per_sector:
            continue

        selected.append(symbol)

        sector_counts[sector] = current_count + 1

    return (selected, sector_counts)
