from pathlib import Path
import pandas as pd

# Project root: ecommerce-customer-reorder-analytics/
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"

FILES = [
    "aisles.csv",
    "departments.csv",
    "orders.csv",
    "products.csv",
    "order_products__prior.csv",
    "order_products__train.csv",
]

def profile_small_csv(path: Path) -> None:
    """Profile a small/medium CSV that can safely be loaded into memory."""
    df = pd.read_csv(path)

    print(f"\n{'=' * 70}")
    print(f"FILE: {path.name}")
    print(f"{'=' * 70}")
    print(f"Rows    : {len(df):,}")
    print(f"Columns : {len(df.columns)}")
    print("\nColumns and dtypes:")
    print(df.dtypes.to_string())

    print("\nMissing values:")
    missing = df.isna().sum()
    print(missing[missing > 0].to_string() if (missing > 0).any() else "None")

    print("\nDuplicate rows:")
    print(f"{df.duplicated().sum():,}")

    print("\nSample:")
    print(df.head(5).to_string(index=False))


def profile_large_csv(path: Path, chunksize: int = 250_000) -> None:
    """Profile a large CSV with chunked reads to avoid loading it all at once."""
    print(f"\n{'=' * 70}")
    print(f"FILE: {path.name}")
    print(f"{'=' * 70}")

    total_rows = 0
    missing_counts = {}
    duplicate_key_counts = {}
    min_values = {}
    max_values = {}
    columns = None
    dtypes = None

    # We will validate uniqueness later using database constraints / SQL.
    # For initial profiling, we only summarize shape, nulls, and sample values.
    for chunk_no, chunk in enumerate(pd.read_csv(path, chunksize=chunksize), start=1):
        if columns is None:
            columns = list(chunk.columns)
            dtypes = chunk.dtypes

        total_rows += len(chunk)

        nulls = chunk.isna().sum()
        for col, value in nulls.items():
            missing_counts[col] = missing_counts.get(col, 0) + int(value)

        # Track basic numeric ranges.
        for col in chunk.select_dtypes(include="number").columns:
            col_min = chunk[col].min()
            col_max = chunk[col].max()
            if pd.notna(col_min):
                min_values[col] = min(min_values.get(col, col_min), col_min)
            if pd.notna(col_max):
                max_values[col] = max(max_values.get(col, col_max), col_max)

        if chunk_no == 1:
            print("Columns and dtypes:")
            print(dtypes.to_string())
            print("\nFirst 5 rows:")
            print(chunk.head(5).to_string(index=False))

        print(f"\rProcessed chunks: {chunk_no}", end="")

    print()
    print(f"Rows: {total_rows:,}")
    print("\nMissing values:")
    nonzero_missing = {k: v for k, v in missing_counts.items() if v > 0}
    print(
        pd.Series(nonzero_missing, name="missing_rows").to_string()
        if nonzero_missing else "None"
    )

    if min_values:
        print("\nNumeric ranges:")
        for col in min_values:
            print(f"  {col}: {min_values[col]} -> {max_values[col]}")


def main() -> None:
    if not RAW_DIR.exists():
        raise FileNotFoundError(
            f"Raw data directory not found: {RAW_DIR}\n"
            "Create data/raw/ and place the six CSV files there."
        )

    missing_files = [name for name in FILES if not (RAW_DIR / name).exists()]
    if missing_files:
        raise FileNotFoundError(
            "Missing expected files:\n- " + "\n- ".join(missing_files)
        )

    print("Instacart Dataset Profiling")
    print(f"Raw directory: {RAW_DIR}\n")

    for name in FILES:
        path = RAW_DIR / name

        if name in {"order_products__prior.csv", "order_products__train.csv"}:
            profile_large_csv(path)
        else:
            profile_small_csv(path)


if __name__ == "__main__":
    main()
