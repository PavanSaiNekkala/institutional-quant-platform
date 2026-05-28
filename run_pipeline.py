import subprocess
import time

# =========================================================
# PIPELINE MODULES
# =========================================================

PIPELINE = [

    "data/live_data.py",

    "analytics/relative_strength.py",

    "analytics/sector_relative_strength.py",

    "analytics/market_regime.py",

    "analytics/cross_sectional_ranker.py",

    "analytics/portfolio_constructor.py",

    "analytics/risk_engine.py",

    "analytics/backtest_engine.py",

    "analytics/monte_carlo_simulator.py",

    "analytics/walk_forward_optimizer.py",

    "analytics/sector_summary.py"
]

# =========================================================
# EXECUTION ENGINE
# =========================================================

start_time = time.time()

print("\n🚀 STARTING INSTITUTIONAL QUANT PIPELINE\n")

success = []

failed = []

for script in PIPELINE:

    print("=" * 60)

    print(f"\n▶ Running: {script}\n")

    try:

        result = subprocess.run(

            ["python", script],

            capture_output=True,

            text=True
        )

        print(result.stdout)

        if result.returncode == 0:

            print(
                f"\n✅ SUCCESS: {script}"
            )

            success.append(script)

        else:

            print(result.stderr)

            print(
                f"\n❌ FAILED: {script}"
            )

            failed.append(script)

    except Exception as e:

        print(
            f"\n❌ ERROR: {script}"
        )

        print(e)

        failed.append(script)

# =========================================================
# SUMMARY
# =========================================================

elapsed = round(

    time.time() - start_time,

    2
)

print("\n" + "=" * 60)

print("\n🏁 PIPELINE COMPLETED\n")

print(
    f"✅ Successful Modules: "
    f"{len(success)}"
)

print(
    f"❌ Failed Modules: "
    f"{len(failed)}"
)

print(
    f"⏱ Total Runtime: "
    f"{elapsed} seconds"
)

print("\n✅ SUCCESS MODULES:\n")

for s in success:

    print(f"   ✔ {s}")

if failed:

    print("\n❌ FAILED MODULES:\n")

    for f in failed:

        print(f"   ✖ {f}")

else:

    print(
        "\n🏆 ALL MODULES EXECUTED SUCCESSFULLY"
    )