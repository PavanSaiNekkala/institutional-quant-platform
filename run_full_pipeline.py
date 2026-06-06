import subprocess
import time
import os
import sys
import pandas as pd

from pathlib import Path

PIPELINE_VERSION = "2.0"
STALE_FILE_THRESHOLD_HOURS = 24

# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent

ANALYTICS_DIR = ROOT_DIR / "analytics"

DATA_DIR = ROOT_DIR / "data"

# =========================================================
# PIPELINE
# =========================================================

PIPELINE = [

    #{
       #"script": "updated_stocks.py",
       #"requires": [],
       #"produces": ["updated_stocks.xlsx"]
    #},
   
    {
        "script": "news_engine.py",
        "requires": [
                "updated_stocks.xlsx"
            ],
        "produces": ["news_rankings.csv"]
    },
    
    {
        "script": "factor_model.py",
        "requires": [],
        "produces": ["factor_model_rankings.csv"]
    },

    {
        "script": "entry_quality_engine.py",
        "requires": [],
        "produces": ["entry_quality_scores.csv"]
    },

    {
        "script": "market_breadth_engine.py",
        "requires": [
            "factor_model_rankings.csv"
        ],
        "produces": [
            "market_breadth.csv"
        ]
    },

    {
        "script": "regime_engine.py",
        "requires": [
            "market_breadth.csv"
        ],
        "produces": ["market_regime.csv"]
    },
    
    {
        "script": "expected_return_engine.py",
        "requires": ["factor_model_rankings.csv"],
        "produces": ["expected_returns.csv"]
    },

    {
        "script": "conviction_engine.py",
        "requires": [
            "factor_model_rankings.csv",
            "entry_quality_scores.csv",
            "expected_returns.csv"
        ],
        "produces": ["conviction_scores.csv"]
    },

    {
        "script": "turnover_control.py",
        "requires": ["conviction_scores.csv"],
        "produces": ["target_portfolio.csv"]
    },

    {
        "script": "position_sizing_engine.py",
        "requires": ["target_portfolio.csv"],
        "produces": ["position_sized_portfolio.csv"]
    },

    {
        "script": "risk_parity_engine.py",
        "requires": ["position_sized_portfolio.csv"],
        "produces": ["risk_parity_portfolio.csv"]
    },

    {
        "script": "sector_exposure_engine.py",
        "requires": ["risk_parity_portfolio.csv"],
        "produces": ["sector_controlled_portfolio.csv"]
    },

    {
        "script": "portfolio_optimiser.py",
        "requires": ["sector_controlled_portfolio.csv"],
        "produces": ["optimised_portfolio.csv"]
    },

    {
        "script": "risk_engine.py",
        "requires": ["optimised_portfolio.csv"],
        "produces": ["portfolio_risk_report.csv"]
    },

    {
        "script": "factor_attribution_engine.py",
        "requires": ["optimised_portfolio.csv"],
        "produces": ["factor_attribution.csv"]
    },

    {
        "script": "rebalance_engine.py",
        "requires": ["optimised_portfolio.csv"],
        "produces": ["rebalance_plan.csv"]
    },

    {
        "script": "stop_loss_engine.py",
        "requires": ["optimised_portfolio.csv"],
        "produces": ["stoploss_signals.csv"]
    },

    {
        "script": "portfolio_lifecycle_engine.py",
        "requires": ["optimised_portfolio.csv"],
        "produces": [
            "portfolio_lifecycle.csv",
            "current_positions.csv",
            "exited_positions.csv"
        ]
    },

    {
        "script": "final_execution_engine.py",
        "requires": [
            "rebalance_plan.csv",
            "stoploss_signals.csv"
        ],
        "produces": ["execution_orders.csv"]
    },

    {
        "script": "portfolio_monitor_engine.py",
        "requires": [
            "optimised_portfolio.csv",
            "current_positions.csv"
        ],
        "produces": [
            "portfolio_monitor.csv"
        ],
        "optional": True
    },

    {
        "script": "portfolio_returns_engine.py",
        "requires": [
            "portfolio_monitor.csv"
        ],
        "produces": [
            "portfolio_returns.csv"
        ],
        "optional": True
    },

    {
        "script": "performance_analytics_engine.py",
        "requires": [
            "portfolio_returns.csv"
        ],
        "produces": [
            "performance_analytics.csv"
        ],
        "optional": True
    },

    {
        "script": "monthly_factsheet_generator.py",
        "requires": [
            "optimised_portfolio.csv",
            "portfolio_risk_report.csv"
        ],
        "produces": [
            "monthly_factsheet.xlsx"
        ],
        "optional": True
    },

    {
        "script": "experiment_tracker.py",
        "requires": [
            "walk_forward_stats.csv",
            "market_regime.csv",
            "optimised_portfolio.csv"
        ],
        "produces": [
            "strategy_versions.csv"
        ],
        "optional": True
    },
    
    {
        "script": "capacity_analysis_engine.py",
        "requires": [
            "optimised_portfolio.csv",
            "factor_model_rankings.csv"
        ],
        "produces": [
            "capacity_report.csv"
        ],
        "optional": True
    },
    
    {
        "script": "signal_database.py",
        "requires": [
            "optimised_portfolio.csv"
        ],
        "produces": [
            "historical_signals.parquet",
            "historical_signals.csv"
        ],
        "optional": True
    },

    {
        "script": "strategy_version_control.py",
        "requires": [
            "walk_forward_stats.csv",
            "market_regime.csv",
            "optimised_portfolio.csv"
        ],
        "produces": [
            "strategy_registry.csv"
        ],
        "optional": True
    },
]
    
from datetime import datetime

# =========================================================
# VALIDATION
# =========================================================

def validate_files(files):

    missing = []

    for file in files:

        path = DATA_DIR / file

        if (
            not path.exists()
            or path.stat().st_size == 0
        ):

            missing.append(file)

        else:

            age_hours = (
                datetime.now().timestamp()
                - path.stat().st_mtime
            ) / 3600

            if age_hours > STALE_FILE_THRESHOLD_HOURS:

                print(
                    f"⚠ WARNING: {file} is "
                    f"{round(age_hours,1)} hours old"
                )

    return missing
# =========================================================
# EXECUTE SCRIPT
# =========================================================

def run_script(config):

    script = config["script"]

    requires = config["requires"]

    produces = config["produces"]

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

            print(
                f"\n⚠ OPTIONAL MODULE SKIPPED: {script}"
            )

            return True
    
        return False

    start = time.time()
    
    if not script_path.exists():

        print(
            f"\n❌ Script Not Found: "
            f"{script}"
        )

        return False

    try:

        result = subprocess.run(
            [sys.executable, "-u", str(script_path)],
            capture_output=True,
            text=True,
            timeout=3600
        )
        
        runtime = round(
            time.time() - start,
            2
        )

        if result.returncode != 0:

            runtime = round(
                time.time() - start,
                2
            )

            print("\n❌ FAILED\n")

            print(
                f"⏱ Runtime Before Failure: {runtime}s"
            )

            print(result.stderr)

            # ==========================================
            # SAVE FAILURE LOG
            # ==========================================

            with open(
                DATA_DIR / "pipeline_failure.log",
                "w",
                encoding="utf-8"
            ) as f:

                f.write(
                    f"SCRIPT: {script}\n\n"
                )

                f.write(result.stderr)

            if config.get("optional", False):

                print(
                    f"\n⚠ OPTIONAL MODULE FAILED: {script}"
                )

                return True

            return False

        missing_outputs = validate_files(produces)

        if missing_outputs:

            print("\n❌ Output Validation Failed")

            for file in missing_outputs:

                print(f"   • {file}")

            if config.get("optional", False):

                print(
                    f"\n⚠ OPTIONAL MODULE OUTPUT MISSING: {script}"
                )

                return True

            return False

        print(f"\n✅ SUCCESS")
        print(f"⏱ Runtime: {runtime}s")

        if result.stdout:

            print("\n📄 LOG:")
            lines = result.stdout.splitlines()

            print(
                "\n".join(lines[-100:])
            )

        return True
        
    except subprocess.TimeoutExpired:

        with open(
            DATA_DIR / "pipeline_failure.log",
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                f"SCRIPT: {script}\n\n"
                f"TIMEOUT AFTER 3600 SECONDS"
            )

        print(
            f"\n⏰ TIMEOUT: {script}"
        )

        return False

    except Exception as e:

        with open(
            DATA_DIR / "pipeline_failure.log",
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                f"SCRIPT: {script}\n\n"
            )

            f.write(str(e))

        print("\n❌ EXCEPTION")

        print(
            f"{type(e).__name__}: {e}"
        )
        
        if config.get("optional", False):

            print(
                f"\n⚠ OPTIONAL MODULE FAILED: {script}"
            )

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

        print(
            f"\n🛑 PIPELINE STOPPED AT: "
            f"{failed_script}"
        )

        break

    success_count += 1

# =========================================================
# SUMMARY
# =========================================================

total_runtime = round(
    time.time() - pipeline_start,
    2
)

print("\n" + "=" * 80)

print("🏁 PIPELINE SUMMARY")

print("=" * 80)

print(
    f"\n✅ Completed: "
    f"{success_count}/{len(PIPELINE)}"
)

print(
    f"⏱ Total Runtime: "
    f"{total_runtime}s"
)

if failed_script:

    print(
        f"\n❌ Failed At: "
        f"{failed_script}"
    )

else:

    print(
        "\n🏆 ALL SYSTEMS OPERATIONAL"
    )

print(
    "\n🏦 Institutional Quant Platform Ready"
)

print("\nGenerated Files:")

for file in sorted(
    DATA_DIR.glob("*.csv")
):

    print(
        f"{file.name:<40}"
        f"{round(file.stat().st_size/1024,2)} KB"
    )
    
health_file = DATA_DIR / "pipeline_health.csv"

new_row = pd.DataFrame({

    "TIMESTAMP":[pd.Timestamp.now()],
    "PIPELINE_VERSION":[PIPELINE_VERSION],
    "SUCCESS":[failed_script is None],
    "RUNTIME_SEC":[total_runtime],
    "MODULES_COMPLETED":[success_count],
    "GIT_SHA":[
        os.getenv(
            "GITHUB_SHA",
            "LOCAL"
        )
    ],
    "MODULES_TOTAL":[len(PIPELINE)]

})

if health_file.exists():

    history = pd.read_csv(
        health_file
    )

    history = pd.concat(
        [history, new_row],
        ignore_index=True
    )

    history = history.tail(1000)

else:

    history = new_row

history.to_csv(
    health_file,
    index=False
)
