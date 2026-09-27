# SQL Pipeline

The SQL layer is used for relational staging, validation, customer-level analytics, and timing analysis.

## Execution Order

```text
01_create_staging_schema.sql
02_add_staging_indexes.sql
03_data_validation.sql
04_build_customer_marts_v2.sql
05_build_timing_marts.sql
```

## Scripts

### 01_create_staging_schema.sql
Creates the source-aligned staging tables.

### 02_add_staging_indexes.sql
Adds indexes after bulk ingestion.

### 03_data_validation.sql
Checks row counts, duplicates, referential integrity, domain values, evaluation-set distribution, and missing values.

### 04_build_customer_marts_v2.sql
Creates the compact customer behavior and customer reorder marts.

### 05_build_timing_marts.sql
Creates the day-of-week / hour-of-day timing mart.

## Large Product Aggregation

Large product-level aggregation is intentionally handled with Python chunked processing rather than materializing another 33.8M-row fact table locally.
