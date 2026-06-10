from pathlib import Path

import pandas as pd


def validate_columns(
    file_path: str | Path,
    required_columns: list[str],
) -> pd.DataFrame:
    """
    Validate required columns exist in a CSV/Excel file.

    Parameters
    ----------
    file_path : str | Path
        Input file path

    required_columns : list[str]
        Required schema columns

    Returns
    -------
    pd.DataFrame
        Loaded dataframe

    Raises
    ------
    FileNotFoundError
        If file does not exist

    ValueError
        If required columns are missing
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"\n❌ File not found:\n{file_path}"
        )

    suffix = file_path.suffix.lower()

    if suffix == ".csv":
        df = pd.read_csv(file_path)

    elif suffix in [".xlsx", ".xls"]:
        df = pd.read_excel(file_path)

    elif suffix == ".parquet":
        df = pd.read_parquet(file_path)

    else:
        raise ValueError(
            f"\n❌ Unsupported file type: {suffix}"
        )

    df.columns = (
        df.columns.astype(str)
        .str.strip()
    )

    missing_columns = sorted(
        set(required_columns)
        - set(df.columns)
    )

    if missing_columns:
        available = sorted(df.columns.tolist())

        error_message = (
            "\n"
            + "=" * 60
            + "\nSCHEMA VALIDATION FAILED\n"
            + "=" * 60
            + f"\n\nFile:\n{file_path}"
            + "\n\nMissing Columns:"
            + "\n- "
            + "\n- ".join(missing_columns)
            + "\n\nAvailable Columns:"
            + "\n- "
            + "\n- ".join(available)
            + "\n"
        )

        raise ValueError(error_message)

    print(
        f"\n✅ Schema Validated: {file_path.name}"
    )

    return df


def validate_dataframe(
    df: pd.DataFrame,
    required_columns: list[str],
    dataframe_name: str = "DataFrame",
) -> None:
    """
    Validate dataframe columns directly.
    """

    df.columns = (
        df.columns.astype(str)
        .str.strip()
    )

    missing_columns = sorted(
        set(required_columns)
        - set(df.columns)
    )

    if missing_columns:
        raise ValueError(
            "\n"
            + "=" * 60
            + "\nSCHEMA VALIDATION FAILED\n"
            + "=" * 60
            + f"\n\nObject: {dataframe_name}"
            + "\n\nMissing Columns:"
            + "\n- "
            + "\n- ".join(missing_columns)
        )

    print(
        f"\n✅ Schema Validated: {dataframe_name}"
    )


if __name__ == "__main__":

    REQUIRED = [
        "Symbol",
        "Market_Cap",
    ]

    validate_columns(
        "data/raw/stock_metadata.csv",
        REQUIRED,
    )
