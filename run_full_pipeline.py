import subprocess
import time

from pathlib import Path

# =========================================================
# ROOT
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent

ANALYTICS_DIR = ROOT_DIR / "analytics"

DATA_DIR = ROOT_DIR / "data"

# =========================================================
# PIPELINE ORDER
# =========================================================

PIPELINE = [

    # =====================================================
    # FOUNDATION
    # =====================================================

    {
        "script": "relative_strength.py",

        "requires": [
            "valid_stocks.xlsx"
        ],

        "produces": [
            "institutional_rankings.csv"
        ]
    },

    # =====================================================
    # SECTOR ENGINES
    # =====================================================

    {
        "script": "sector_relative_strength.py",

        "requires": [
            "stock_metadata.csv",
            "institutional_rankings.csv"
        ],

        "produces": [
            "sector_relative_strength.csv"
        ]
    },

    {
        "script": "sector_summary.py",

        "requires": [
            "institutional_rankings.csv"
        ],

        "produces": [
            "sector_summary.csv"
        ]
    },

    # =====================================================
    # CROSS SECTIONAL
    # =====================================================

    {
        "script": "cross_sectional_ranker.py",

        "requires": [
            "institutional_rankings.csv"
        ],

        "produces": [
            "cross_sectional_rankings.csv"
        ]
    },

    # =====================================================
    # FACTOR MODEL
    # =====================================================

    {
        "script": "factor_model.py",

        "requires": [
            "cross_sectional_rankings.csv"
        ],

        "produces": [
            "factor_model_rankings.csv"
        ]
    },

    # =====================================================
    # MARKET REGIME
    # =====================================================

    {
        "script": "market_regime.py",

        "requires": [],

        "produces": [
            "market_regime.csv"
        ]
    },

    # =====================================================
    # AI ENGINES
    # =====================================================

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
            "factor_model_rankings.csv"
        ],

        "produces": [
            "meta_strategy_output.csv"
        ]
    },

    {
        "script": "reinforcement_allocator.py",

        "requires": [
            "ml_alpha_predictions.csv"
        ],

        "produces": [
            "reinforcement_portfolio.csv"
        ]
    },

    # =====================================================
    # PORTFOLIO
    # =====================================================

    {
        "script": "portfolio_optimizer.py",

        "requires": [
            "factor_model_rankings.csv"
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
            "risk_report.csv"
        ]
    },

    {
        "script": "portfolio_intelligence.py",

        "requires": [
            "cross_sectional_rankings.csv"
        ],

        "produces": [
            "portfolio_intelligence.csv"
        ]
    },

    # =====================================================
    # EXECUTION
    # =====================================================

    {
        "script": "execution_engine.py",

        "requires": [
            "reinforcement_portfolio.csv"
        ],

        "produces": [
            "execution_orders.csv"
        ]
    },

    # =====================================================
    # WALK FORWARD
    # =====================================================

    {
        "script": "walk_forward_optimizer.py",

        "requires": [
            "cross_sectional_rankings.csv"
        ],

        "produces": [
            "walk_forward_results.csv"
        ]
    }

]

# =========================================================
# VALIDATE FILES
# =========================================================

def validate_required_files(files):

    missing = []

    for file in files:

        path = DATA_DIR / file

        if not path.exists():

            missing.append(file)

    return missing

# =========================================================
# VALIDATE OUTPUTS
# =========================================================

def validate_output_files(files):

    missing = []

    for file in files:

        path = DATA_DIR / file

        if not path.exists():

            missing.append(file)

    return missing

# =========================================================
# RUN SCRIPT
# =========================================================

def run_script(config):

    script_name = config["script"]

    requires = config["requires"]

    produces = config["produces"]

    script_path = ANALYTICS_DIR / script_name

    print("\n" + "=" * 70)

    print(f"🚀 Running: {script_name}")

    print("=" * 70)

    # =====================================================
    # VALIDATE INPUTS
    # =====================================================

    missing_inputs = validate_required_files(requires)

    if missing_inputs:

        print("\n❌ MISSING DEPENDENCIES:\n")

        for file in missing_inputs:

            print(f"- {file}")

        return False

    start = time.time()

    try:

        result = subprocess.run(

            ["python", str(script_path)],

            capture_output=True,

            text=True
        )

        duration = round(
            time.time() - start,
            2
        )

        # =================================================
        # SUCCESS
        # =================================================

        if result.returncode == 0:

            missing_outputs = validate_output_files(produces)

            if missing_outputs:

                print(
                    "\n❌ OUTPUT VALIDATION FAILED\n"
                )

                for file in missing_outputs:

                    print(f"- {file}")

                return False

            print(
                f"\n✅ SUCCESS: {script_name}"
            )

            print(
                f"⏱ Runtime: {duration}s"
            )

            if result.stdout:

                print("\n📄 OUTPUT:\n")

                print(result.stdout[-3000:])

            return True

        # =================================================
        # FAILURE
        # =================================================

        else:

            print(
                f"\n❌ FAILED: {script_name}"
            )

            print("\n⚠ ERROR:\n")

            print(result.stderr)

            return False

    except Exception as e:

        print(
            f"\n❌ EXCEPTION: {script_name}"
        )

        print(str(e))

        return False

# =========================================================
# MAIN
# =========================================================

print("\n🏦 INSTITUTIONAL QUANT PIPELINE")

print("\n🚀 Starting Full AI Workflow...")

pipeline_start = time.time()

success_count = 0

failed_scripts = []

# =========================================================
# EXECUTION LOOP
# =========================================================

for config in PIPELINE:

    success = run_script(config)

    if success:

        success_count += 1

    else:

        failed_scripts.append(
            config["script"]
        )

# =========================================================
# SUMMARY
# =========================================================

total_runtime = round(

    time.time() - pipeline_start,

    2
)

print("\n" + "=" * 70)

print("🏁 PIPELINE EXECUTION COMPLETE")

print("=" * 70)

print(
    f"\n✅ Successful Scripts: "
    f"{success_count}/{len(PIPELINE)}"
)

print(
    f"⏱ Total Runtime: "
    f"{total_runtime}s"
)

if failed_scripts:

    print("\n❌ Failed Scripts:\n")

    for script in failed_scripts:

        print(f"- {script}")

else:

    print("\n🏆 ALL SYSTEMS OPERATIONAL")

print("\n🏦 Institutional Quant Platform Ready")
