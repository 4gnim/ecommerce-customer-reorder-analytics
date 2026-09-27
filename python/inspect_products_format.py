from pathlib import Path
import csv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
path = PROJECT_ROOT / "data" / "raw" / "products.csv"

raw = path.read_text(encoding="utf-8-sig")

print("=" * 70)
print("PRODUCTS CSV FORMAT INSPECTION")
print("=" * 70)

# Physical line count
physical_lines = raw.count("\n")
print(f"Physical LF count        : {physical_lines:,}")

# Parse using Python CSV
with path.open("r", encoding="utf-8-sig", newline="") as f:
    reader = csv.reader(f)
    rows = list(reader)

print(f"Logical CSV rows         : {len(rows)-1:,}")

# Check embedded newlines
multiline_rows = []

for line_no, row in enumerate(rows[1:], start=2):
    if len(row) == 4:
        product_id, product_name, aisle_id, department_id = row

        if "\n" in product_name or "\r" in product_name:
            multiline_rows.append(
                (line_no, product_id, repr(product_name))
            )

print(f"Names containing newline : {len(multiline_rows):,}")

if multiline_rows:
    print("\nFirst 20 multiline records:")
    for row in multiline_rows[:20]:
        print(row)

# Check quotes / backslashes in product names
quote_rows = []
backslash_rows = []

for line_no, row in enumerate(rows[1:], start=2):
    if len(row) == 4:
        product_id, product_name, _, _ = row

        if '"' in product_name:
            quote_rows.append(
                (line_no, product_id, product_name)
            )

        if "\\" in product_name:
            backslash_rows.append(
                (line_no, product_id, product_name)
            )

print(f'\nNames containing "     : {len(quote_rows):,}')
print(f"Names containing backslash: {len(backslash_rows):,}")

if quote_rows:
    print('\nFirst 10 names containing ":\n')
    for row in quote_rows[:10]:
        print(row)

if backslash_rows:
    print("\nFirst 10 names containing backslash:\n")
    for row in backslash_rows[:10]:
        print(row)