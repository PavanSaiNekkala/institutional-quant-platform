import subprocess
import time

from pathlib import Path

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

    {
        "script": "market_regime.py",
        "requires": [],
        "produces": [
            "market_regime_v2.csv"
        ]
    },

    {
        "script": "relative_strength.py",
        "requires": [
            "valid_stocks.xlsx"
        ],
        "produces": [
            "institutional_rankings.csv"
        ]
    },

    {
        "script": "generate_metadata.py",
        "requires": [
            "valid_stocks.xlsx"
        ],
        "produces": [
            "stock_metadata.csv"
        ]
    },

    {
        "script": "sector_relative_strength.py",
        "requires": [
            "institutional_rankings.csv",
            "stock_metadata.csv"
        ],
        "produces": [
            "sector_relative_strength.csv"
        ]
    },

    {
        "script": "sector_summary.py",
        "requires": [
            "institutional_rankings.csv",
            "stock_metadata.csv"
        ],
        "produces": [
            "sector_summary.csv"
        ]
    },

    {
        "script": "cross_sectional_ranker.py",
        "requires": [
            "institutional_rankings.csv"
        ],
        "produces": [
            "cross_sectional_rankings.csv"
        ]
    },

    {
        "script": "factor_model.py",
        "requires": [
            "cross_sectional_rankings.csv"
        ],
        "produces": [
            "factor_model_rankings.csv"
        ]
    },

    {
        "script": "expected_return_engine.py",
        "requires": [
           "factor_model_rankings.csv"
        ],
        "produces": [
            "expected_returns.csv"
        ]
    },

    {
        "script": "ml_alpha_engine.py",
        "requires": [
            "factor_model_rankings.csv"
        ],
        "produces": [
            "ml_alpha_predictions.csv"
        ]
    },

    {
        "script": "meta_strategy_engine.py",
        "requires": [
            "ml_alpha_predictions.csv"
        ],
        "produces": [
            "meta_strategy_portfolio.csv"
        ]
    },

    {
        "script": "reinforcement_allocator.py",
        "requires": [
            "ml_alpha_predictions.csv",
            "market_regime_v2.csv"
        ],
        "produces": [
            "reinforcement_portfolio.csv"
        ]
    },

    {
        "script": "portfolio_optimizer.py",
        "requires": [
            "reinforcement_portfolio.csv"
        ],
        "produces": [
            "portfolio_allocation.csv"
        ]
    },

    {
        "script": "risk_engine.py",
        "requires": [
            "portfolio_allocation.csv"
        ],
        "produces": [
            "portfolio_risk_report.csv"
        ]
    },

    {
        "script": "portfolio_intelligence.py",
        "requires": [
            "ml_alpha_predictions.csv",
            "sector_summary.csv",
            "market_regime_v2.csv"
        ],
        "produces": [
            "portfolio_intelligence.csv"
        ]
    },

    {
        "script": "execution_engine.py",
        "requires": [
            "portfolio_allocation.csv",
            "portfolio_risk_report.csv"
        ],
        "produces": [
            "execution_simulation.csv"
        ]
    },

    {
        "script": "walk_forward_optimizer.py",
        "requires": [
            "cross_sectional_rankings.csv"
        ],
        "produces": [
            "walk_forward_equity_curve.csv"
        ]
    }
]

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

        return False

    start = time.time()

    try:

        result = subprocess.run(
            ["python", str(script_path)],
            capture_output=True,
            text=True
        )

        runtime = round(
            time.time() - start,
            2
        )

        if result.returncode != 0:

            print("\n❌ FAILED\n")

            print(result.stderr)

            return False

        missing_outputs = validate_files(produces)

        if missing_outputs:

            print("\n❌ Output Validation Failed")

            for file in missing_outputs:

                print(f"   • {file}")

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

    except Exception as e:

        print("\n❌ EXCEPTION")
        print(str(e))
        return False

# =========================================================
# MAIN
# =========================================================

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

for file in DATA_DIR.glob("*.csv"):

    print(
        f"{file.name:<40}"
        f"{round(file.stat().st_size/1024,2)} KB"
    )
