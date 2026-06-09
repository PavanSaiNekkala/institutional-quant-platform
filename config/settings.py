import os

from dotenv import load_dotenv

# =========================================================
# LOAD ENV
# =========================================================

load_dotenv()

# =========================================================
# APP CONFIG
# =========================================================

APP_NAME = os.getenv("APP_NAME")

ENVIRONMENT = os.getenv("ENVIRONMENT")

# =========================================================
# RISK CONFIG
# =========================================================

MAX_POSITION_SIZE = float(os.getenv("MAX_POSITION_SIZE", 0.25))

MAX_DRAWDOWN = float(os.getenv("MAX_DRAWDOWN", -0.20))

TARGET_VOLATILITY = float(os.getenv("TARGET_VOLATILITY", 0.15))

# =========================================================
# DATA CONFIG
# =========================================================

DEFAULT_LOOKBACK = int(os.getenv("DEFAULT_LOOKBACK", 252))

DEFAULT_SYMBOL = os.getenv("DEFAULT_SYMBOL", "RELIANCE.NS")

# =========================================================
# API CONFIG
# =========================================================

BROKER_API_KEY = os.getenv("BROKER_API_KEY")

DATA_API_KEY = os.getenv("DATA_API_KEY")

# =========================================================
# CONFIG SUMMARY
# =========================================================


def config_summary():

    return {
        "APP_NAME": APP_NAME,
        "ENVIRONMENT": ENVIRONMENT,
        "MAX_POSITION_SIZE": MAX_POSITION_SIZE,
        "MAX_DRAWDOWN": MAX_DRAWDOWN,
        "TARGET_VOLATILITY": TARGET_VOLATILITY,
        "DEFAULT_LOOKBACK": DEFAULT_LOOKBACK,
        "DEFAULT_SYMBOL": DEFAULT_SYMBOL,
    }
