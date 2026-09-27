# Data

This directory documents data provenance and stores compact analytical outputs.

## Source Dataset

**Instacart Market Basket Analysis**

https://www.kaggle.com/datasets/psparks/instacart-market-basket-analysis

## Raw Source Files

Download and place these files into `data/raw/`:

```text
aisles.csv
departments.csv
orders.csv
products.csv
order_products__prior.csv
order_products__train.csv
```

The raw files are intentionally excluded from Git because of their size.

## Processed Analytical Marts

The final Power BI layer uses these compact analytical marts:

```text
processed/
├── mart_customer_behavior.csv
├── mart_customer_reorder.csv
├── mart_order_timing.csv
├── product_performance.csv
├── department_performance.csv
├── aisle_performance.csv
└── order_sequence_performance.csv
```

### Grain

- `mart_customer_behavior.csv` — one row per customer
- `mart_customer_reorder.csv` — one row per customer
- `mart_order_timing.csv` — one row per day/hour combination
- `product_performance.csv` — one row per product
- `department_performance.csv` — one row per department
- `aisle_performance.csv` — one row per aisle
- `order_sequence_performance.csv` — one row per order number

## Staging / Temporary Files

`data/staging/` is reserved for local ingestion-normalization files. These files are excluded from Git.

## Definitions

`reordered = 1` means that the product on the order line had previously been purchased by the same customer.

```text
Item Reorder Rate = Reordered Items / Total Items
```

## Reproducibility

1. Download the source dataset from Kaggle.
2. Extract the six CSV files into `data/raw/`.
3. Run the profiling script.
4. Load the source files into the MySQL staging tables.
5. Run the validation SQL.
6. Build the customer and timing marts.
7. Run the chunked Python scripts to generate product, department, aisle, and sequence marts.
8. Use the resulting files in `data/processed/` for Power BI.

The raw source files remain outside version control.
