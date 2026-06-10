import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent

PIPELINE = [
    "utilities/updated_stocks.py",
    "utilities/update_benchmark.py",
    "master/build_security_master.py",
    "utilities/generate_metadata.py",
    "ranking/relative_strength.py",
    "ranking/sector_relative_strength.py",
    "ranking/sector_summary.py",
    "ranking/cross_sectional_ranker.py",
    "risk/correlation_engine.py",
]

TOTAL_STEPS = len(PIPELINE)

print("\n" + "=" * 100)
print("🚀 INSTITUTIONAL QUANT PLATFORM")
print("=" * 100)

pipeline_start = time.time()

success = []
failed = []
completed_times = []

# ==========================================================
# RUN PIPELINE
# ==========================================================

for step, script in enumerate(PIPELINE, start=1):

    script_path = ROOT / "analytics" / script

    print("\n" + "=" * 100)
    print(f"[{step}/{TOTAL_STEPS}] 🚀 {script}")
    print("=" * 100)

    start = time.time()

    try:

        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

        runtime = round(
            time.time() - start,
            2
        )

        if result.returncode == 0:

            success.append(script)
            completed_times.append(runtime)

            avg_runtime = (
                sum(completed_times)
                / len(completed_times)
            )

            remaining_steps = (
                TOTAL_STEPS - step
            )

            progress_pct = round(
                step / TOTAL_STEPS * 100,
                1
            )

            bar_length = 30

            filled = int(
                progress_pct / 100 * bar_length
            )

            bar = (
                "█" * filled
                + "░" * (bar_length - filled)
            )

            print(
                f"✅ SUCCESS ({runtime}s)"
            )

            print(
                f"📊 Progress: "
                f"[{bar}] "
                f"{progress_pct}%"
            )


        else:

            print("\n❌ FAILED\n")

            print(result.stderr)

            failed.append(script)

            break

    except Exception as e:

        print(f"\n❌ EXCEPTION: {e}")

        failed.append(script)

        break

# ==========================================================
# SUMMARY
# ==========================================================

total_runtime = round(
    time.time() - pipeline_start,
    2
)

print("\n" + "=" * 100)
print("📊 PIPELINE SUMMARY")
print("=" * 100)

print(
    f"\nTotal Steps      : {TOTAL_STEPS}"
)

print(
    f"Successful Steps : {len(success)}"
)

print(
    f"Failed Steps     : {len(failed)}"
)

print(
    f"Total Runtime    : {total_runtime}s"
)

if completed_times:

    print(
        f"Average Runtime  : "
        f"{round(sum(completed_times)/len(completed_times),2)}s"
    )

if success:

    print("\n✅ Completed Steps:\n")

    for s in success:
        print(f"   • {s}")

if failed:

    print("\n❌ Failed Step:\n")

    for s in failed:
        print(f"   • {s}")

else:

    print("\n🏆 FULL PIPELINE COMPLETED SUCCESSFULLY")

print("\n" + "=" * 100)
