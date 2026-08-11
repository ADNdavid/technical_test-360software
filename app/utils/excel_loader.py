from pathlib import Path
import re
from typing import Any

import pandas as pd

REQUIRED_PRODUCT_COLUMNS = ["PLU", "descripcion", "codpro", "nompro"]
REQUIRED_SALES_COLUMNS = ["nitcli", "descrip", "cantped"]


def _clean_value(value: Any) -> Any:
    if isinstance(value, str):
        # Remove leading/trailing whitespace and normalize internal whitespace
        return re.sub(r"\s+", " ", value.strip())
    return value


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean string values in a DataFrame by stripping whitespace."""
    df = df.copy()
    for column in df.columns:
        if pd.api.types.is_string_dtype(df[column].dtype) or df[column].dtype == object:
            df[column] = df[column].astype(str).map(_clean_value)
    return df


def load_table(path: Path, required_columns: list[str] | None = None) -> pd.DataFrame:
    if not path.exists():
        # fallback to CSV if xlsx not present
        alt = path.with_suffix('.csv')
        if alt.exists():
            path = alt
        else:
            raise FileNotFoundError(f"Data file not found: {path}")

    if path.suffix.lower() in ('.xls', '.xlsx'):
        df = pd.read_excel(path)
    else:
        df = pd.read_csv(path)

    # normalize
    df = df.fillna("")
    df = clean_dataframe(df)

    if required_columns:
        missing = [c for c in required_columns if c not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
    return df
