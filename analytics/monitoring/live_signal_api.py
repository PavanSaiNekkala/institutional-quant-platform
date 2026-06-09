from pathlib import Path
import pandas as pd

# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT / "data"

# =========================================================
# HELPER
# =========================================================

def load_csv(filename):

    file_path = DATA_DIR / filename

    if not file_path.exists():

        return []

    try:

        df = pd.read_csv(file_path)

        return df.to_dict(
            orient="records"
        )

    except Exception as e:

        return {

            "error": str(e)
        }

# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/")

def home():

    return {

        "platform":
            "Institutional Quant Alpha",

        "status":
            "running"
    }

# =========================================================
# CURRENT PORTFOLIO
# =========================================================

@app.get("/api/portfolio")

def portfolio():

    return load_csv(
        "optimised_portfolio.csv"
    )

# =========================================================
# TOP SIGNALS
# =========================================================

@app.get("/api/signals")

def signals():

    return load_csv(
        "conviction_scores.csv"
    )

# =========================================================
# CURRENT REGIME
# =========================================================

@app.get("/api/regime")

def regime():

    data = load_csv(
        "market_regime.csv"
    )

    return data

# =========================================================
# REBALANCE PLAN
# =========================================================

@app.get("/api/rebalance")

def rebalance():

    return load_csv(
        "rebalance_plan.csv"
    )

# =========================================================
# RISK REPORT
# =========================================================

@app.get("/api/risk")

def risk():

    return load_csv(
        "portfolio_risk_report.csv"
    )

# =========================================================
# FACTOR ATTRIBUTION
# =========================================================

@app.get("/api/attribution")

def attribution():

    return load_csv(
        "factor_attribution.csv"
    )

# =========================================================
# STOP LOSS SIGNALS
# =========================================================

@app.get("/api/stoploss")

def stoploss():

    return load_csv(
        "stoploss_signals.csv"
    )

# =========================================================
# CAPACITY REPORT
# =========================================================

@app.get("/api/capacity")

def capacity():

    return load_csv(
        "capacity_report.csv"
    )

# =========================================================
# EXPERIMENT HISTORY
# =========================================================

@app.get("/api/experiments")

def experiments():

    return load_csv(
        "strategy_versions.csv"
    )

# =========================================================
# SIGNAL DATABASE
# =========================================================

@app.get("/api/history")

def signal_history():

    file_path = (
        DATA_DIR
        / "historical_signals.parquet"
    )

    if not file_path.exists():

        return []

    try:

        df = pd.read_parquet(
            file_path
        )

        return (

            df.tail(500)

            .to_dict(
                orient="records"
            )
        )

    except Exception as e:

        return {

            "error": str(e)
        }

# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(

        app,

        host="0.0.0.0",

        port=8000
    )
