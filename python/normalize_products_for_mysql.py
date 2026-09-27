from pathlib import Path
import csv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
raw_path = PROJECT_ROOT / "data" / "raw" / "products.csv"
staging_dir = PROJECT_ROOT / "data" / "staging"
staging_dir.mkdir(parents=True, exist_ok=True)

output_path = staging_dir / "products_mysql.tsv"

rows = []
with raw_path.open("r", encoding="utf-8-sig", newline="") as f:
    reader = csv.reader(f)
    header = next(reader)

    expected_header = ["product_id", "product_name", "aisle_id", "department_id"]
    if header != expected_header:
        raise ValueError(f"Unexpected header: {header}")

    for line_no, row in enumerate(reader, start=2):
        if len(row) != 4:
            raise ValueError(
                f"Row {line_no} has {len(row)} fields instead of 4: {row}"
            )

        # A tab-delimited staging file is safe only when tabs/newlines do not
        # appear inside fields. The raw diagnostic already showed no newlines;
        # we validate tabs explicitly here before writing.
        if any("\t" in field or "\n" in field or "\r" in field for field in row):
            raise ValueError(
                f"Row {line_no} contains a tab/newline inside a field: {row}"
            )

        rows.append(row)

# Validate source integrity before creating the ingestion file.
product_ids = [int(row[0]) for row in rows]

if len(rows) != 49_688:
    raise ValueError(f"Expected 49,688 source rows, got {len(rows):,}")

if len(set(product_ids)) != 49_688:
    raise ValueError("product_id is not unique in the source CSV.")

if min(product_ids) != 1 or max(product_ids) != 49_688:
    raise ValueError("product_id range is not 1..49,688.")

expected_ids = set(range(1, 49_689))
actual_ids = set(product_ids)
if actual_ids != expected_ids:
    raise ValueError("Source product_id values are not exactly 1..49,688.")

# Write a serialization-only normalization:
# same four fields, same values, tab-delimited, one logical record per line.
with output_path.open("w", encoding="utf-8", newline="\n") as f:
    f.write("\t".join(header) + "\n")
    for row in rows:
        f.write("\t".join(row) + "\n")

print("=" * 70)
print("PRODUCTS MYSQL STAGING FILE CREATED")
print("=" * 70)
print(f"Source rows       : {len(rows):,}")
print(f"Unique product_id : {len(set(product_ids)):,}")
print(f"Output            : {output_path}")
print()
print("This is a serialization-only normalization.")
print("No product values are modified.")
