from pathlib import Path
import csv
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
path = PROJECT_ROOT / "data" / "raw" / "products.csv"

print("=" * 70)
print("PRODUCTS CSV DIAGNOSTIC")
print("=" * 70)

# ------------------------------------------------------------
# 1. Pandas parsing
# ------------------------------------------------------------
df = pd.read_csv(path)

print("\n[PANDAS]")
print("Rows:", len(df))
print("Columns:", list(df.columns))
print("Unique product_id:", df["product_id"].nunique())
print("Duplicate product_id rows:", df["product_id"].duplicated().sum())

print("Min product_id:", df["product_id"].min())
print("Max product_id:", df["product_id"].max())

expected_ids = set(range(1, 49689))
actual_ids = set(df["product_id"])

missing_ids = sorted(expected_ids - actual_ids)
extra_ids = sorted(actual_ids - expected_ids)

print("Missing product IDs:", len(missing_ids))
print("First missing IDs:", missing_ids[:50])

print("Unexpected product IDs:", len(extra_ids))
print("First unexpected IDs:", extra_ids[:20])

# ------------------------------------------------------------
# 2. Product name length
# ------------------------------------------------------------
df["product_name_length"] = df["product_name"].astype(str).str.len()

print("\n[PRODUCT NAME LENGTH]")
print("Maximum length:", df["product_name_length"].max())
print("Names > 255 chars:", (df["product_name_length"] > 255).sum())

print("\nLongest product names:")
print(
    df.loc[
        df["product_name_length"].nlargest(20).index,
        ["product_id", "product_name", "product_name_length"]
    ].to_string(index=False)
)

# ------------------------------------------------------------
# 3. Python CSV parser
# ------------------------------------------------------------
print("\n[CSV MODULE PARSING]")

bad_rows = []
raw_rows = 0

with path.open("r", encoding="utf-8-sig", newline="") as f:
    reader = csv.reader(f)

    header = next(reader)
    print("Header:", header)

    for line_no, row in enumerate(reader, start=2):
        raw_rows += 1

        if len(row) != 4:
            bad_rows.append(
                (line_no, len(row), row[:10])
            )

print("Rows parsed by csv.reader:", raw_rows)
print("Rows with field count != 4:", len(bad_rows))

if bad_rows:
    print("\nFirst problematic rows:")
    for row in bad_rows[:20]:
        print(row)

# ------------------------------------------------------------
# 4. Check the product IDs that MySQL reported as missing
# ------------------------------------------------------------
known_missing = [
    1148, 1149, 1150,
    3479, 3480, 3481, 3482, 3483, 3484,
    3485, 3486, 3487, 3488, 3489, 3490,
    3491, 3492, 3493, 3494, 3495
]

print("\n[KNOWN MYSQL-MISSING PRODUCT IDS]")
print(
    df[df["product_id"].isin(known_missing)]
    [["product_id", "product_name", "aisle_id", "department_id"]]
    .to_string(index=False)
)