from pathlib import Path
import pandas as pd

REQUIRED_PRODUCT_COLUMNS = ["PLU", "descripcion", "codpro", "nompro"]
REQUIRED_SALES_COLUMNS = ["nitcli", "codpro", "descrip", "cantped"]


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

    if required_columns:
        missing = [c for c in required_columns if c not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
    return df
