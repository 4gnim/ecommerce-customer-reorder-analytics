# Python Analytics Pipeline

## Scripts

- `profile_dataset.py` — profile all raw files.
- `normalize_products_for_mysql.py` — create a temporary TSV serialization for reliable MySQL ingestion of `products.csv` without changing source values.
- `build_large_scale_marts.py` — chunked product, department, and aisle aggregation.
- `build_sequence_mart.py` — chunked order-sequence aggregation.

Run from the repository root:

```bash
python python/profile_dataset.py
python python/normalize_products_for_mysql.py
python python/build_large_scale_marts.py
python python/build_sequence_mart.py
```
