import sys
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

# =========================================================
# EXPORT DIRECTORY
# =========================================================

EXPORT_DIR = ROOT_DIR / "cache" / "dashboard_exports"

EXPORT_DIR.mkdir(parents=True, exist_ok=True)

# =========================================================
# EXPORT RANKED UNIVERSE
# =========================================================


def export_ranked_universe():

    source = ROOT_DIR / "ranked_universe.xlsx"

    if not source.exists():
        print("\nRANKED UNIVERSE MISSING\n")

        return

    df = pd.read_excel(source)

    output = EXPORT_DIR / "ranked_universe.parquet"

    df.to_parquet(output, index=False)

    print("\nRANKED UNIVERSE EXPORTED\n")


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    export_ranked_universe()
