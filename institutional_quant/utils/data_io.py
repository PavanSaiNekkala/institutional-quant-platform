from pathlib import Path

import pandas as pd

# =========================================================
# SAVE PARQUET
# =========================================================

def save_parquet(df, path):

    path = Path(path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_parquet(

        path,

        engine="pyarrow",

        index=False
    )

# =========================================================
# LOAD PARQUET
# =========================================================

def load_parquet(path):

    path = Path(path)

    if not path.exists():

        raise FileNotFoundError(
            f"Missing file: {path}"
        )

    return pd.read_parquet(

        path,

        engine="pyarrow"
    )