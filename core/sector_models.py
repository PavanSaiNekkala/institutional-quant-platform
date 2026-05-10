# =========================================================
# FILE: core/sector_models.py
# FINAL LIGHTWEIGHT INSTITUTIONAL SECTOR ENGINE
# =========================================================

import numpy as np

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
# LIGHTWEIGHT SECTOR DETECTION
# =========================================================

def detect_sector(symbol):

    symbol = symbol.upper()

    # =====================================================
    # PRIVATE / PSU BANKS
    # =====================================================

    if any(

        x in symbol

        for x in [

            "BANK",
            "FIN",
            "HDFC",
            "ICICI",
            "SBI",
            "KOTAK",
            "AXIS",
            "IDFC"
        ]
    ):

        if any(

            x in symbol

            for x in [

                "SBI",
                "PNB",
                "BANKBARODA",
                "CANBK",
                "UNIONBANK",
                "IOB",
                "PSB"
            ]
        ):

            return "PSU_BANKS"

        return "PRIVATE_BANKS"

    # =====================================================
    # IT
    # =====================================================

    elif any(

        x in symbol

        for x in [

            "TCS",
            "INFY",
            "WIPRO",
            "TECH",
            "SOFT",
            "LTIM",
            "HCL",
            "KPIT",
            "PERSISTENT"
        ]
    ):

        return "PRIVATE_IT"

    # =====================================================
    # PHARMA
    # =====================================================

    elif any(

        x in symbol

        for x in [

            "PHARMA",
            "LAB",
            "MED",
            "DRREDDY",
            "SUN",
            "LUPIN",
            "CIPLA"
        ]
    ):

        return "PRIVATE_PHARMA"

    # =====================================================
    # AUTO
    # =====================================================

    elif any(

        x in symbol

        for x in [

            "AUTO",
            "MOTOR",
            "MARUTI",
            "M&M",
            "TATA",
            "EICHER",
            "BAJAJ"
        ]
    ):

        return "PRIVATE_AUTO"

    # =====================================================
    # ENERGY
    # =====================================================

    elif any(

        x in symbol

        for x in [

            "POWER",
            "OIL",
            "GAS",
            "ENERGY",
            "ONGC",
            "IOC",
            "BPCL",
            "NTPC",
            "GAIL"
        ]
    ):

        return "PSU_ENERGY"

    # =====================================================
    # FMCG
    # =====================================================

    elif any(

        x in symbol

        for x in [

            "CONSUM",
            "NESTLE",
            "DABUR",
            "MARICO",
            "HINDUNILVR",
            "BRITANNIA"
        ]
    ):

        return "PRIVATE_FMCG"

    # =====================================================
    # METALS
    # =====================================================

    elif any(

        x in symbol

        for x in [

            "STEEL",
            "METAL",
            "HINDALCO",
            "JSW",
            "TATASTEEL",
            "SAIL",
            "NMDC"
        ]
    ):

        return "PRIVATE_METALS"

    # =====================================================
    # REALTY
    # =====================================================

    elif any(

        x in symbol

        for x in [

            "REAL",
            "PROP",
            "DLF",
            "LODHA",
            "OBEROI"
        ]
    ):

        return "PRIVATE_REALTY"

    # =====================================================
    # DEFENCE
    # =====================================================

    elif any(

        x in symbol

        for x in [

            "HAL",
            "BEL",
            "BDL",
            "MAZDOCK",
            "SHIP"
        ]
    ):

        return "PSU_DEFENCE"

    return "OTHER"

# =========================================================
# INSTITUTIONAL FACTOR ENGINE
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
    # FMCG
    # =====================================================

    elif sector == "PRIVATE_FMCG":

        raw_score = (

            sharpe * 0.35 -
            volatility * 0.25 +
            trend_strength * 0.20 +
            total_return * 0.20
        )

    # =====================================================
    # AUTO
    # =====================================================

    elif sector == "PRIVATE_AUTO":

        raw_score = (

            momentum * 0.35 +
            total_return * 0.30 +
            trend_strength * 0.20 +
            sharpe * 0.15
        )

    # =====================================================
    # PHARMA
    # =====================================================

    elif sector == "PRIVATE_PHARMA":

        raw_score = (

            sharpe * 0.30 +
            momentum * 0.25 +
            total_return * 0.25 -
            volatility * 0.20
        )

    # =====================================================
    # ENERGY
    # =====================================================

    elif sector == "PSU_ENERGY":

        raw_score = (

            total_return * 0.25 +
            momentum * 0.25 +
            sharpe * 0.25 -
            volatility * 0.15
        )

    # =====================================================
    # DEFENCE
    # =====================================================

    elif sector == "PSU_DEFENCE":

        raw_score = (

            momentum * 0.40 +
            total_return * 0.30 +
            trend_strength * 0.20 -
            volatility * 0.10
        )

    # =====================================================
    # METALS
    # =====================================================

    elif sector == "PRIVATE_METALS":

        raw_score = (

            momentum * 0.35 +
            total_return * 0.30 +
            trend_strength * 0.20 -
            volatility * 0.15
        )

    # =====================================================
    # REALTY
    # =====================================================

    elif sector == "PRIVATE_REALTY":

        raw_score = (

            momentum * 0.30 +
            total_return * 0.30 +
            trend_strength * 0.20 -
            volatility * 0.20
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
    # SECTOR IMPACT
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
            "PRIVATE_PHARMA"
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
