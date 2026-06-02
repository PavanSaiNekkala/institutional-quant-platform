import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent

PIPELINE = [

    "regime_engine.py",

    "factor_model.py",

    "expected_return_engine.py",

    "entry_quality_engine.py",

    "conviction_engine.py",

    "turnover_control.py",

    "sector_exposure_engine.py",

    "position_sizing_engine.py",

    "risk_parity_engine.py",

    "portfolio_optimiser.py",

    "final_execution_engine.py",

    "portfolio_monitor.py",

    "factor_attribution_engine.py",

    "rebalance_engine.py"

]

print("\n🚀 STARTING INSTITUTIONAL PIPELINE\n")

for script in PIPELINE:

    print(f"\n▶ Running {script}")

    result = subprocess.run(

        ["python", str(ROOT / script)]

    )

    if result.returncode != 0:

        raise RuntimeError(

            f"{script} FAILED"
        )

print("\n✅ PIPELINE COMPLETE")