import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import pandas as pd

PIPELINE_VERSION = "2.0"
STALE_FILE_THRESHOLD_HOURS = 24

# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent

ANALYTICS_DIR = ROOT_DIR / "analytics"

DATA_DIR = ROOT_DIR / "data"

RISK_DIR = ROOT_DIR / "risk"

EXECUTION_DIR = ROOT_DIR / "execution"

# =========================================================
# PIPELINE
# =========================================================

PIPELINE = [
    {
        "script": "ranking/entry_quality_engine.py",
        "requires": ["processed/cross_sectional_rankings.csv"],
        "produces": ["processed/entry_quality_scores.csv"],
    },
    {
        "script": "ranking/liquidity_engine.py",
        "requires": ["processed/cross_sectional_rankings.csv"],
        "produces": ["processed/liquidity_scores.csv"],
    },
    {
        "script": "research/news_engine.py",
        "requires": ["processed/cross_sectional_rankings.csv"],
        "produces": ["processed/news_rankings.csv"],
    },
    {
        "script": "ranking/factor_model.py",
        "requires": [
            "processed/cross_sectional_rankings.csv",
            "processed/entry_quality_scores.csv",
            "processed/liquidity_scores.csv",
        ],
        "produces": ["processed/factor_model_rankings.csv"],
    },
    {
        "script": "regime/market_breadth_engine.py",
        "requires": ["processed/factor_model_rankings.csv"],
        "produces": ["processed/market_breadth.csv"],
    },
    {
        "script": "regime/regime_engine.py",
        "requires": ["processed/market_breadth.csv"],
        "produces": ["processed/market_regime.csv"],
    },
    {
        "script": "alpha/expected_return_engine.py",
        "requires": ["processed/factor_model_rankings.csv"],
        "produces": ["processed/expected_returns.csv"],
    },
    {
        "script": "alpha/conviction_engine.py",
        "requires": [
            "processed/factor_model_rankings.csv",
            "processed/entry_quality_scores.csv",
            "processed/expected_returns.csv",
        ],
        "produces": ["processed/conviction_scores.csv"],
    },
    {
        "script": "portfolio/turnover_control.py",
        "requires": ["processed/conviction_scores.csv"],
        "produces": ["portfolio/target_portfolio.csv"],
    },
    {
        "script": "portfolio/position_sizing_engine.py",
        "requires": ["portfolio/target_portfolio.csv"],
        "produces": ["portfolio/position_sized_portfolio.csv"],
    },
    {
        "script": "portfolio/risk_parity_engine.py",
        "requires": ["portfolio/position_sized_portfolio.csv"],
        "produces": ["portfolio/risk_parity_portfolio.csv"],
    },
    {
        "script": "portfolio/sector_exposure_engine.py",
        "requires": ["portfolio/risk_parity_portfolio.csv"],
        "produces": ["portfolio/sector_controlled_portfolio.csv"],
    },
    {
        "script": "portfolio/portfolio_optimiser.py",
        "requires": ["portfolio/sector_controlled_portfolio.csv"],
        "produces": ["optimised_portfolio.csv"],
    },
    {
        "script": "ranking/entry_quality_engine.py",
        "requires": [],
        "produces": ["processed/entry_quality_scores.csv"],
    },
    {
        "script": "ranking/factor_model.py",
        "requires": ["processed/cross_sectional_rankings.csv"],
        "produces": ["processed/factor_model_rankings.csv"],
    },
    {
        "script": "research/news_engine.py",
        "requires": ["processed/cross_sectional_rankings.csv"],
        "produces": ["processed/news_rankings.csv"],
    },
    {
        "script": "regime/market_breadth_engine.py",
        "requires": ["processed/factor_model_rankings.csv"],
        "produces": ["processed/market_breadth.csv"],
    },
    {
        "script": "regime/regime_engine.py",
        "requires": ["processed/market_breadth.csv"],
        "produces": ["processed/market_regime.csv"],
    },
    {
        "script": "alpha/expected_return_engine.py",
        "requires": ["processed/factor_model_rankings.csv"],
        "produces": ["processed/expected_returns.csv"],
    },
    {
        "script": "alpha/conviction_engine.py",
        "requires": [
            "processed/factor_model_rankings.csv",
            "processed/entry_quality_scores.csv",
            "processed/expected_returns.csv",
        ],
        "produces": ["processed/conviction_scores.csv"],
    },
    {
        "script": "portfolio/turnover_control.py",
        "requires": ["processed/conviction_scores.csv"],
        "produces": ["portfolio/target_portfolio.csv"],
    },
    {
        "script": "portfolio/position_sizing_engine.py",
        "requires": ["portfolio/target_portfolio.csv"],
        "produces": ["portfolio/position_sized_portfolio.csv"],
    },
    {
        "script": "portfolio/risk_parity_engine.py",
        "requires": ["portfolio/position_sized_portfolio.csv"],
        "produces": ["portfolio/risk_parity_portfolio.csv"],
    },
    {
        "script": "portfolio/sector_exposure_engine.py",
        "requires": ["portfolio/risk_parity_portfolio.csv"],
        "produces": ["portfolio/sector_controlled_portfolio.csv"],
    },
    {
        "script": "portfolio/portfolio_optimiser.py",
        "requires": ["portfolio/sector_controlled_portfolio.csv"],
        "produces": ["optimised_portfolio.csv"],
    },
    {
        "script": "risk/risk_engine.py",
        "requires": ["optimised_portfolio.csv"],
        "produces": ["portfolio_risk_report.csv"],
    },
    {
        "script": "attribution/factor_attribution_engine.py",
        "requires": ["optimised_portfolio.csv"],
        "produces": ["factor_attribution.csv"],
    },
    {
        "script": "portfolio/rebalance_engine.py",
        "requires": ["optimised_portfolio.csv"],
        "produces": ["rebalance_plan.csv"],
    },
    {
        "script": "execution/stop_loss_engine.py",
        "requires": ["optimised_portfolio.csv"],
        "produces": ["stoploss_signals.csv"],
    },
    {
        "script": "portfolio/portfolio_lifecycle_engine.py",
        "requires": ["optimised_portfolio.csv"],
        "produces": ["portfolio_lifecycle.csv", "current_positions.csv", "exited_positions.csv"],
    },
    {
        "script": "execution/final_execution_engine.py",
        "requires": ["rebalance_plan.csv", "stoploss_signals.csv"],
        "produces": ["execution_orders.csv"],
    },
    {
        "script": "portfolio/portfolio_monitor_engine.py",
        "requires": ["optimised_portfolio.csv", "current_positions.csv"],
        "produces": ["portfolio_monitor.csv"],
        "optional": True,
    },
    {
        "script": "portfolio/portfolio_returns_engine.py",
        "requires": ["portfolio_monitor.csv"],
        "produces": ["portfolio_returns.csv"],
        "optional": True,
    },
    {
        "script": "monitoring/performance_analytics_engine.py",
        "requires": ["portfolio_returns.csv"],
        "produces": ["performance_analytics.csv"],
        "optional": True,
    },
    {
        "script": "utilities/monthly_factsheet_generator.py",
        "requires": ["optimised_portfolio.csv", "portfolio_risk_report.csv"],
        "produces": ["monthly_factsheet.xlsx"],
        "optional": True,
    },
    {
        "script": "utilities/experiment_tracker.py",
        "requires": ["walk_forward_stats.csv", "market_regime.csv", "optimised_portfolio.csv"],
        "produces": ["strategy_versions.csv"],
        "optional": True,
    },
    {
        "script": "research/capacity_analysis_engine.py",
        "requires": ["optimised_portfolio.csv", "factor_model_rankings.csv"],
        "produces": ["capacity_report.csv"],
        "optional": True,
    },
    {
        "script": "monitoring/signal_database.py",
        "requires": ["optimised_portfolio.csv"],
        "produces": ["historical_signals.parquet", "historical_signals.csv"],
        "optional": True,
    },
    {
        "script": "utilities/strategy_version_control.py",
        "requires": ["walk_forward_stats.csv", "market_regime.csv", "optimised_portfolio.csv"],
        "produces": ["strategy_registry.csv"],
        "optional": True,
    },
]


# =========================================================
# VALIDATION
# =========================================================


def validate_files(files):

    missing = []

    for file in files:
        path = DATA_DIR / file

        if not path.exists() or path.stat().st_size == 0:
            missing.append(file)

        else:
            age_hours = (datetime.now().timestamp() - path.stat().st_mtime) / 3600

            if age_hours > STALE_FILE_THRESHOLD_HOURS:
                print(f"⚠ WARNING: {file} is {round(age_hours, 1)} hours old")

    return missing


# =========================================================
# EXECUTE SCRIPT
# =========================================================


def run_script(config):

    script = config["script"]

    requires = config["requires"]

    produces = config["produces"]

    if script.startswith("risk/"):
        script_path = ROOT_DIR / script

    elif script.startswith("execution/"):
        script_path = ROOT_DIR / script

    else:
        script_path = ANALYTICS_DIR / script

    print("\n" + "=" * 80)
    print(f"🚀 RUNNING: {script}")
    print("=" * 80)

    missing_inputs = validate_files(requires)

    if missing_inputs:
        print("\n❌ Missing Dependencies:")

        for file in missing_inputs:
            print(f"   • {file}")

        if config.get("optional", False):
            print(f"\n⚠ OPTIONAL MODULE SKIPPED: {script}")

            return True

        return False

    start = time.time()

    if not script_path.exists():
        print(f"\n❌ Script Not Found: {script}")

        return False

    try:
        result = subprocess.run(
            [sys.executable, "-u", str(script_path)], capture_output=True, text=True, timeout=3600
        )

        runtime = round(time.time() - start, 2)

        if result.returncode != 0:
            runtime = round(time.time() - start, 2)

            print("\n❌ FAILED\n")

            print(f"⏱ Runtime Before Failure: {runtime}s")

            print(result.stderr)

            # ==========================================
            # SAVE FAILURE LOG
            # ==========================================

            with open(DATA_DIR / "pipeline_failure.log", "w", encoding="utf-8") as f:
                f.write(f"SCRIPT: {script}\n\n")

                f.write(result.stderr)

            if config.get("optional", False):
                print(f"\n⚠ OPTIONAL MODULE FAILED: {script}")

                return True

            return False

        missing_outputs = validate_files(produces)

        if missing_outputs:
            print("\n❌ Output Validation Failed")

            for file in missing_outputs:
                print(f"   • {file}")

            if config.get("optional", False):
                print(f"\n⚠ OPTIONAL MODULE OUTPUT MISSING: {script}")

                return True

            return False

        print("\n✅ SUCCESS")
        print(f"⏱ Runtime: {runtime}s")

        if result.stdout:
            print("\n📄 LOG:")
            lines = result.stdout.splitlines()

            print("\n".join(lines[-100:]))

        return True

    except subprocess.TimeoutExpired:
        with open(DATA_DIR / "pipeline_failure.log", "w", encoding="utf-8") as f:
            f.write(f"SCRIPT: {script}\n\nTIMEOUT AFTER 3600 SECONDS")

        print(f"\n⏰ TIMEOUT: {script}")

        return False

    except Exception as e:
        with open(DATA_DIR / "pipeline_failure.log", "w", encoding="utf-8") as f:
            f.write(f"SCRIPT: {script}\n\n")

            f.write(str(e))

        print("\n❌ EXCEPTION")

        print(f"{type(e).__name__}: {e}")

        if config.get("optional", False):
            print(f"\n⚠ OPTIONAL MODULE FAILED: {script}")

            return True

        return False


# =========================================================
# MAIN
# =========================================================

failure_log = DATA_DIR / "pipeline_failure.log"

if failure_log.exists():
    failure_log.unlink()
print("\n🏦 INSTITUTIONAL QUANT PIPELINE")
print("\n🚀 Starting End-to-End Workflow")

pipeline_start = time.time()

success_count = 0

failed_script = None

for config in PIPELINE:
    success = run_script(config)

    if not success:
        failed_script = config["script"]

        print(f"\n🛑 PIPELINE STOPPED AT: {failed_script}")

        break

    success_count += 1

# =========================================================
# SUMMARY
# =========================================================

total_runtime = round(time.time() - pipeline_start, 2)

print("\n" + "=" * 80)

print("🏁 PIPELINE SUMMARY")

print("=" * 80)

print(f"\n✅ Completed: {success_count}/{len(PIPELINE)}")

print(f"⏱ Total Runtime: {total_runtime}s")

if failed_script:
    print(f"\n❌ Failed At: {failed_script}")

else:
    print("\n🏆 ALL SYSTEMS OPERATIONAL")

print("\n🏦 Institutional Quant Platform Ready")

print("\nGenerated Files:")

for file in sorted(DATA_DIR.rglob("*.csv")):
    print(f"{file.name:<40}{round(file.stat().st_size / 1024, 2)} KB")

health_file = DATA_DIR / "pipeline_health.csv"

new_row = pd.DataFrame(
    {
        "TIMESTAMP": [pd.Timestamp.now()],
        "PIPELINE_VERSION": [PIPELINE_VERSION],
        "SUCCESS": [failed_script is None],
        "RUNTIME_SEC": [total_runtime],
        "MODULES_COMPLETED": [success_count],
        "GIT_SHA": [os.getenv("GITHUB_SHA", "LOCAL")],
        "MODULES_TOTAL": [len(PIPELINE)],
    }
)

if health_file.exists():
    history = pd.read_csv(health_file)

    history = pd.concat([history, new_row], ignore_index=True)

    history = history.tail(1000)

else:
    history = new_row

history.to_csv(health_file, index=False)
