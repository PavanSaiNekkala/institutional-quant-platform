import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent

PIPELINE = [
    # Refresh shared cache
    "utilities/update_price_cache.py",
    # Build universe
    "utilities/updated_stocks.py",
    # Refresh metadata
    "utilities/generate_metadata.py",
    # Rankings
    "ranking/relative_strength.py",
    "ranking/sector_relative_strength.py",
    "ranking/sector_summary.py",
    "ranking/cross_sectional_ranker.py",
    # Optional
    "ranking/correlation_engine.py",
]

print("\n" + "=" * 80)
print("🚀 DAILY DATA PIPELINE")
print("=" * 80)

pipeline_start = time.time()

success = 0
failed = 0

for script in PIPELINE:
    script_path = ROOT / "analytics" / script

    print("\n" + "=" * 80)
    print(f"🚀 RUNNING: {script}")
    print("=" * 80)

    start = time.time()

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

        runtime = round(time.time() - start, 2)

        if result.returncode == 0:
            print("✅ SUCCESS")
            print(f"⏱ Runtime: {runtime}s")

            success += 1

        else:
            print("❌ FAILED")
            print(result.stderr)

            failed += 1
            break

    except Exception as e:
        print(e)

        failed += 1
        break

print("\n" + "=" * 80)
print("📊 SUMMARY")
print("=" * 80)

print(f"Successful : {success}")
print(f"Failed     : {failed}")
print(f"Runtime    : {round(time.time() - pipeline_start, 2)}s")
