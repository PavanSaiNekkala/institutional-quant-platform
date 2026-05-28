import subprocess
import time
from pathlib import Path

# =========================================================
# ROOT
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent

ANALYTICS_DIR = ROOT_DIR / "analytics"

# =========================================================
# PIPELINE
# =========================================================

PIPELINE = [

    # ---------------------------------------------
    # DATA + SIGNALS
    # ---------------------------------------------

    "relative_strength.py",

    "sector_summary.py",

    "sector_relative_strength.py",

    # ---------------------------------------------
    # RANKING ENGINES
    # ---------------------------------------------

    "cross_sectional_ranker.py",

    "risk_engine.py",

    "factor_model.py",

    # ---------------------------------------------
    # REGIME DETECTION
    # ---------------------------------------------

    "market_regime.py",

    # ---------------------------------------------
    # AI ENGINES
    # ---------------------------------------------

    "ml_alpha_engine.py",

    "meta_strategy_engine.py",

    "reinforcement_allocator.py",

    # ---------------------------------------------
    # PORTFOLIO
    # ---------------------------------------------

    "portfolio_optimizer.py",

    "portfolio_intelligence.py",

    # ---------------------------------------------
    # EXECUTION
    # ---------------------------------------------

    "execution_engine.py",

    # ---------------------------------------------
    # VALIDATION
    # ---------------------------------------------

    "walk_forward_optimizer.py"

]

# =========================================================
# RUNNER
# =========================================================

def run_script(script_name):

    script_path = (
        ANALYTICS_DIR
        / script_name
    )

    print(
        "\n"
        + "=" * 60
    )

    print(
        f"🚀 Running: {script_name}"
    )

    print(
        "=" * 60
    )

    start = time.time()

    try:

        result = subprocess.run(

            ["python", str(script_path)],

            capture_output=True,

            text=True
        )

        end = time.time()

        duration = round(
            end - start,
            2
        )

        if result.returncode == 0:

            print(
                f"\n✅ SUCCESS: {script_name}"
            )

            print(
                f"⏱ Runtime: {duration}s"
            )

            if result.stdout:

                print(
                    "\n📄 OUTPUT:\n"
                )

                print(
                    result.stdout[-3000:]
                )

        else:

            print(
                f"\n❌ FAILED: {script_name}"
            )

            print(
                "\n⚠ ERROR:\n"
            )

            print(
                result.stderr
            )

            return False

    except Exception as e:

        print(
            f"\n❌ EXCEPTION: {script_name}"
        )

        print(str(e))

        return False

    return True

# =========================================================
# MAIN PIPELINE
# =========================================================

print(
    "\n🏦 INSTITUTIONAL QUANT PIPELINE"
)

print(
    "\n🚀 Starting Full AI Workflow..."
)

pipeline_start = time.time()

success_count = 0

failed_scripts = []

for script in PIPELINE:

    success = run_script(script)

    if success:

        success_count += 1

    else:

        failed_scripts.append(script)

pipeline_end = time.time()

total_runtime = round(
    pipeline_end - pipeline_start,
    2
)

# =========================================================
# FINAL SUMMARY
# =========================================================

print(
    "\n"
    + "=" * 70
)

print(
    "🏁 PIPELINE EXECUTION COMPLETE"
)

print(
    "=" * 70
)

print(
    f"\n✅ Successful Scripts: "
    f"{success_count}/{len(PIPELINE)}"
)

print(
    f"⏱ Total Runtime: "
    f"{total_runtime}s"
)

if len(failed_scripts) > 0:

    print(
        "\n❌ Failed Scripts:\n"
    )

    for script in failed_scripts:

        print(
            f"- {script}"
        )

else:

    print(
        "\n🏆 ALL SYSTEMS OPERATIONAL"
    )

print(
    "\n🏦 Institutional Quant Platform Ready"
)