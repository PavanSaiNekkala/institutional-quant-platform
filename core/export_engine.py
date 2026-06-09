import os
from datetime import datetime

# =========================================================
# CREATE EXPORT DIRECTORY
# =========================================================

EXPORT_DIR = "exports"

os.makedirs(EXPORT_DIR, exist_ok=True)

# =========================================================
# GENERATE TIMESTAMP
# =========================================================


def timestamp():

    return datetime.now().strftime("%Y%m%d_%H%M%S")


# =========================================================
# EXPORT DATAFRAME
# =========================================================


def export_dataframe(df, filename):

    file_path = os.path.join(EXPORT_DIR, f"{filename}_{timestamp()}.csv")

    df.to_csv(file_path, index=True)

    return file_path


# =========================================================
# EXPORT RANKINGS
# =========================================================


def export_rankings(rankings_df):

    return export_dataframe(rankings_df, "institutional_rankings")


# =========================================================
# EXPORT RISK REPORT
# =========================================================


def export_risk_report(risk_df):

    return export_dataframe(risk_df, "risk_report")


# =========================================================
# EXPORT REGIME REPORT
# =========================================================


def export_regime_report(regime_df):

    return export_dataframe(regime_df, "regime_report")


# =========================================================
# EXPORT PORTFOLIO
# =========================================================


def export_portfolio(portfolio_df):

    return export_dataframe(portfolio_df, "portfolio_report")
