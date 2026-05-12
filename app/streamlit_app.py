import pandas as pd

from pathlib import Path

# =========================================================
# ROOT DIRECTORY
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

# =========================================================
# LOAD RANKED UNIVERSE
# =========================================================

def load_ranked_universe():

    try:

        file_path = (

            ROOT_DIR

            / "ranked_universe.xlsx"
        )

        if not file_path.exists():

            print(

                "ranked_universe.xlsx "
                "NOT FOUND"
            )

            return pd.DataFrame()

        df = pd.read_excel(

            file_path
        )

        if df.empty:

            print(

                "ranked_universe.xlsx "
                "IS EMPTY"
            )

            return pd.DataFrame()

        return df

    except Exception as e:

        print(

            f"LOADER ERROR: {e}"
        )

        return pd.DataFrame()
