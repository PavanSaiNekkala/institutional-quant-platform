# =========================================================
# FILE: core/sector_models.py
# FINAL DYNAMIC INSTITUTIONAL SECTOR ENGINE
# =========================================================

import numpy as np
import pandas as pd

# =========================================================
# DYNAMIC SECTOR KEYWORDS
# =========================================================

SECTOR_KEYWORDS = {

    # =====================================================
    # BANKS & FINANCIALS
    # =====================================================

    "BANK": "PRIVATE_BANKS",
    "FINANCE": "PRIVATE_BANKS",
    "FINANCIAL": "PRIVATE_BANKS",
    "NBFC": "PRIVATE_BANKS",

    # =====================================================
    # IT & SOFTWARE
    # =====================================================

    "IT": "PRIVATE_IT",
    "TECH": "PRIVATE_IT",
    "SOFTWARE": "PRIVATE_IT",
    "DIGITAL": "PRIVATE_IT",

    # =====================================================
    # PHARMA
    # =====================================================

    "PHARMA": "PRIVATE_PHARMA",
    "HEALTH": "PRIVATE_PHARMA",
    "BIO": "PRIVATE_PHARMA",
    "LIFE SCIENCE": "PRIVATE_PHARMA",

    # =====================================================
    # AUTO
    # =====================================================

    "AUTO": "PRIVATE_AUTO",
    "MOTOR": "PRIVATE_AUTO",
    "TYRE": "PRIVATE_AUTO",
    "AUTOMOBILE": "PRIVATE_AUTO",

    # =====================================================
    # ENERGY
    # =====================================================

    "ENERGY": "PRIVATE_ENERGY",
    "POWER": "PSU_ENERGY",
    "OIL": "PSU_ENERGY",
    "GAS": "PSU_ENERGY",
    "PETROLEUM": "PSU_ENERGY",
    "COAL": "PSU_ENERGY",

    # =====================================================
    # FMCG
    # =====================================================

    "FMCG": "PRIVATE_FMCG",
    "CONSUMER": "PRIVATE_CONSUMER",
    "FOOD": "PRIVATE_FMCG",
    "BEVERAGE": "PRIVATE_FMCG",

    # =====================================================
    # REALTY
    # =====================================================

    "REALTY": "PRIVATE_REALTY",
    "REAL ESTATE": "PRIVATE_REALTY",
    "PROPERTY": "PRIVATE_REALTY",

    # =====================================================
    # CHEMICALS
    # =====================================================

    "CHEMICAL": "PRIVATE_CHEMICALS",
    "FERTILIZER": "PRIVATE_CHEMICALS",
    "SPECIALTY": "PRIVATE_CHEMICALS",

    # =====================================================
    # METALS
    # =====================================================

    "METAL": "PRIVATE_METALS",
    "STEEL": "PRIVATE_METALS",
    "MINING": "PRIVATE_METALS",
    "ALUMINIUM": "PRIVATE_METALS",

    # =====================================================
    # DEFENCE
    # =====================================================

    "DEFENCE": "PSU_DEFENCE",
    "AEROSPACE": "PSU_DEFENCE",
    "SHIP": "PSU_DEFENCE",

    # =====================================================
    # TELECOM
    # =====================================================

    "TELECOM": "PRIVATE_TELECOM",
    "COMMUNICATION": "PRIVATE_TELECOM",

    # =====================================================
    # CEMENT
    # =====================================================

    "CEMENT": "PRIVATE_CEMENT",

    # =====================================================
    # INFRA
    # =====================================================

    "INFRA": "PRIVATE_INFRA",
    "ENGINEERING": "PRIVATE_INFRA",
    "CONSTRUCTION": "PRIVATE_INFRA"
}

# =========================================================
# SECTOR IMPACT WEIGHTS
# =========================================================

SECTOR_IMPACT = {

    "PRIVATE_BANKS": 1.40,
    "PSU_BANKS": 1.20,

    "PRIVATE_IT": 1.30,

    "PRIVATE_FMCG": 1.10,

    "PRIVATE_AUTO": 1.05,

    "PRIVATE_PHARMA": 1.00,

    "PRIVATE_ENERGY": 1.25,
    "PSU_ENERGY": 1.20,

    "PSU_DEFENCE": 1.10,

    "PRIVATE_METALS": 0.95,

    "PRIVATE_REALTY": 0.90,

    "PRIVATE_CONSUMER": 1.00,

    "PRIVATE_CHEMICALS": 0.95,

    "PRIVATE_TELECOM": 1.00,

    "PRIVATE_CEMENT": 0.90,

    "PRIVATE_INFRA": 1.05,

    "OTHER": 0.70
}

# =========================================================
# PSU DETECTION WORDS
# =========================================================

PSU_WORDS = [

    "STATE",
    "INDIA",
    "POWER",
    "OIL",
    "COAL",
    "RAIL",
    "NTPC",
    "GAIL",
    "ONGC",
    "IOC",
    "BPCL",
    "SAIL",
    "NMDC",
    "HAL",
    "BEL"
]

# =========================================================
# DYNAMIC SECTOR DETECTION
# =========================================================

def detect_sector(symbol, info):

    try:

        # =================================================
        # YAHOO METADATA
        # =================================================

        sector_name = str(

            info.get(
                "sector",
                ""
            )
        ).upper()

        industry_name = str(

            info.get(
                "industry",
                ""
            )
        ).upper()

        long_name = str(

            info.get(
                "longName",
                ""
            )
        ).upper()

        combined = (

            sector_name
            + " "
            + industry_name
            + " "
            + long_name
        )

        # =================================================
        # PSU DETECTION
        # =================================================

        is_psu = False

        for word in PSU_WORDS:

            if word in combined:

                is_psu = True
                break

        # =================================================
        # KEYWORD MATCHING
        # =================================================

        for keyword, sector in (

            SECTOR_KEYWORDS.items()
        ):

            if keyword in combined:

                # =========================================
                # PSU OVERRIDE
                # =========================================

                if is_psu:

                    if sector == "PRIVATE_BANKS":

                        return "PSU_BANKS"

                    elif sector == "PRIVATE_ENERGY":

                        return "PSU_ENERGY"

                    elif sector == "PRIVATE_METALS":

                        return "PSU_METALS"

                return sector

        # =================================================
        # FALLBACK PSU
        # =================================================

        if is_psu:

            return "PSU_ENERGY"

        return "OTHER"

    except Exception:

        return "OTHER"

# =========================================================
# SECTOR FACTOR ENGINE
# =========================================================

def sector_factor_score(

    sector,
    momentum,
    sharpe,
    trend_strength,
    total_return,
    volatility,
    risk_reward,
    regime
):

    # =====================================================
    # PRIVATE BANKS
    # =====================================================

    if sector == "PRIVATE_BANKS":

        raw_score = (

            sharpe * 0.30 +
            momentum * 0.25 +
            trend_strength * 0.20 +
            total_return * 0.25
        )

    # =====================================================
    # PSU BANKS
    # =====================================================

    elif sector == "PSU_BANKS":

        raw_score = (

            momentum * 0.35 +
            total_return * 0.30 +
            sharpe * 0.20 -
            volatility * 0.15
        )

    # =====================================================
    # PRIVATE IT
    # =====================================================

    elif sector == "PRIVATE_IT":

        raw_score = (

            momentum * 0.30 +
            sharpe * 0.25 +
            total_return * 0.25 +
            trend_strength * 0.20
        )

    # =====================================================
    # PRIVATE FMCG
    # =====================================================

    elif sector == "PRIVATE_FMCG":

        raw_score = (

            sharpe * 0.35 -
            volatility * 0.25 +
            trend_strength * 0.20 +
            total_return * 0.20
        )

    # =====================================================
    # PRIVATE AUTO
    # =====================================================

    elif sector == "PRIVATE_AUTO":

        raw_score = (

            momentum * 0.35 +
            total_return * 0.30 +
            trend_strength * 0.20 +
            sharpe * 0.15
        )

    # =====================================================
    # PRIVATE PHARMA
    # =====================================================

    elif sector == "PRIVATE_PHARMA":

        raw_score = (

            sharpe * 0.30 +
            momentum * 0.25 +
            total_return * 0.25 -
            volatility * 0.20
        )

    # =====================================================
    # PRIVATE ENERGY
    # =====================================================

    elif sector == "PRIVATE_ENERGY":

        raw_score = (

            total_return * 0.30 +
            trend_strength * 0.25 +
            sharpe * 0.25 +
            momentum * 0.20
        )

    # =====================================================
    # PSU ENERGY
    # =====================================================

    elif sector == "PSU_ENERGY":

        raw_score = (

            total_return * 0.25 +
            momentum * 0.25 +
            sharpe * 0.25 -
            volatility * 0.15
        )

    # =====================================================
    # PSU DEFENCE
    # =====================================================

    elif sector == "PSU_DEFENCE":

        raw_score = (

            momentum * 0.40 +
            total_return * 0.30 +
            trend_strength * 0.20 -
            volatility * 0.10
        )

    # =====================================================
    # PRIVATE METALS
    # =====================================================

    elif sector == "PRIVATE_METALS":

        raw_score = (

            momentum * 0.35 +
            total_return * 0.30 +
            trend_strength * 0.20 -
            volatility * 0.15
        )

    # =====================================================
    # PSU METALS
    # =====================================================

    elif sector == "PSU_METALS":

        raw_score = (

            momentum * 0.30 +
            total_return * 0.25 +
            sharpe * 0.25 -
            volatility * 0.20
        )

    # =====================================================
    # PRIVATE REALTY
    # =====================================================

    elif sector == "PRIVATE_REALTY":

        raw_score = (

            momentum * 0.30 +
            total_return * 0.30 +
            trend_strength * 0.20 -
            volatility * 0.20
        )

    # =====================================================
    # PRIVATE CONSUMER
    # =====================================================

    elif sector == "PRIVATE_CONSUMER":

        raw_score = (

            sharpe * 0.30 +
            trend_strength * 0.25 +
            total_return * 0.25 -
            volatility * 0.20
        )

    # =====================================================
    # PRIVATE CHEMICALS
    # =====================================================

    elif sector == "PRIVATE_CHEMICALS":

        raw_score = (

            momentum * 0.30 +
            sharpe * 0.25 +
            total_return * 0.25 -
            volatility * 0.20
        )

    # =====================================================
    # TELECOM
    # =====================================================

    elif sector == "PRIVATE_TELECOM":

        raw_score = (

            sharpe * 0.30 +
            total_return * 0.30 +
            trend_strength * 0.20 +
            momentum * 0.20
        )

    # =====================================================
    # CEMENT
    # =====================================================

    elif sector == "PRIVATE_CEMENT":

        raw_score = (

            momentum * 0.30 +
            total_return * 0.25 +
            sharpe * 0.25 -
            volatility * 0.20
        )

    # =====================================================
    # INFRA
    # =====================================================

    elif sector == "PRIVATE_INFRA":

        raw_score = (

            momentum * 0.35 +
            total_return * 0.30 +
            trend_strength * 0.20 -
            volatility * 0.15
        )

    # =====================================================
    # DEFAULT
    # =====================================================

    else:

        raw_score = (

            momentum * 0.25 +
            sharpe * 0.25 +
            total_return * 0.25 +
            trend_strength * 0.15 -
            volatility * 0.10
        )

    # =====================================================
    # MARKET IMPACT
    # =====================================================

    sector_weight = SECTOR_IMPACT.get(

        sector,
        0.70
    )

    impact_adjusted_score = (

        raw_score
        * sector_weight
    )

    # =====================================================
    # REGIME BOOST
    # =====================================================

    if "BULLISH" in regime:

        if sector in [

            "PRIVATE_BANKS",
            "PRIVATE_IT",
            "PRIVATE_AUTO",
            "PRIVATE_REALTY"
        ]:

            impact_adjusted_score *= 1.10

    elif "BEARISH" in regime:

        if sector in [

            "PRIVATE_FMCG",
            "PRIVATE_PHARMA",
            "PRIVATE_CONSUMER"
        ]:

            impact_adjusted_score *= 1.10

    # =====================================================
    # FINAL SCORE
    # =====================================================

    final_score = (

        impact_adjusted_score
        * risk_reward
    )

    return final_score
