# E-Commerce Customer Behavior & Reorder Analytics

A large-scale **Data Analyst portfolio project** focused on customer behavior, repeat purchasing, order timing, and product performance using more than 33 million order-item records.

## Project Objective

This project analyzes the Instacart Market Basket Analysis dataset to answer practical e-commerce questions:

- How frequently do customers place orders?
- When are customers most active?
- How does reorder behavior change across order sequences?
- What proportion of purchased items are reordered?
- Which products have the highest item volume?
- Which products have higher reorder rates?
- Which departments and aisles show stronger reorder behavior?
- How does customer-level reorder behavior vary?

The project is intentionally focused on **Data Analyst skills**: SQL, Python/pandas, data quality, large-scale aggregation, analytical modeling, and Power BI.

## Dataset

**Instacart Market Basket Analysis**

Kaggle source:
https://www.kaggle.com/datasets/psparks/instacart-market-basket-analysis

The raw dataset is intentionally excluded from Git because of its size. See `data/README.md` for provenance and reproducibility instructions.

## Scope

The analysis population uses the `prior` and `train` order populations.

`test` orders are excluded from product-level analysis because the provided source files do not contain corresponding product-level order records for the test population.

## Validated Dataset Scale

| Metric | Value |
|---|---:|
| Customers analyzed | 206,209 |
| Orders analyzed | 3,346,083 |
| Order-item records | 33,819,106 |
| Products | 49,688 |
| Aisles | 134 |
| Departments | 21 |
| Overall item reorder rate | 59.01% |

## Metric Definition

At item level:

```text
Item Reorder Rate = Reordered Items / Total Items
```

In the source data, `reordered = 1` means the product on that order line had been purchased previously by the same customer.

The project also calculates customer-level reorder rates. These are kept separate from the overall weighted item reorder rate.

## Data Quality

Before analytical processing, the dataset was validated for:

- Row counts
- Duplicate keys
- Duplicate order-product combinations
- Product → aisle integrity
- Product → department integrity
- Order-product → order integrity
- Order-product → product integrity
- Valid `eval_set` values
- Valid day-of-week values
- Valid hour-of-day values
- Non-negative `days_since_prior_order`
- Valid `reordered` flags
- Valid `add_to_cart_order` values
- Consistency between order populations and order-product populations
- Presence of order items for analyzed orders

All final validation checks passed.

## Processing Architecture

```text
Raw Kaggle CSV files
        |
        v
Data profiling
        |
        v
MySQL staging + validation
        |
        +--------------------------+
        |                          |
        v                          v
Customer analytical marts     Timing mart
        |                          |
        +------------+-------------+
                     |
                     v
          Python chunked processing
                     |
          +----------+----------+
          |          |          |
          v          v          v
      Product   Department    Aisle
       marts       mart        mart
                     |
                     v
           Order sequence mart
                     |
                     v
                  Power BI
                     |
                     v
                GitHub Pages
```

## Why MySQL + Python?

The raw order-product layer contains **33.8 million rows**. Instead of materializing another 33.8-million-row analytical fact table locally, the project uses:

- **MySQL** for relational staging, data validation, customer-level analysis, and timing analysis.
- **Python + Pandas chunked processing** for large product and order-sequence aggregations.
- **Power BI** for business-facing visualization.

This keeps the final analytical marts compact while preserving a reproducible large-scale workflow.

## Analytical Marts

The final processed layer contains:

| File | Grain | Purpose |
|---|---|---|
| `mart_customer_behavior.csv` | Customer | Order frequency and inter-order behavior |
| `mart_customer_reorder.csv` | Customer | Customer-level reorder metrics |
| `mart_order_timing.csv` | Day × Hour | Ordering activity by time |
| `product_performance.csv` | Product | Product item and reorder performance |
| `department_performance.csv` | Department | Department-level reorder behavior |
| `aisle_performance.csv` | Aisle | Aisle-level reorder behavior |
| `order_sequence_performance.csv` | Order number | Reorder behavior across order sequence |

## Power BI Dashboard

### Page 1 — Customer Overview

Answers:

> Who are the customers, how frequently do they order, and when are they most active?

Main visuals:

- Customer distribution by order frequency
- Orders by day of week
- Order activity by day and hour

### Page 2 — Customer Reorder Behavior

Answers:

> How does repeat-purchase behavior evolve across customers and order sequences?

Main visuals:

- Item reorder rate by order sequence
- Customer distribution by order frequency
- Average inter-order gap by order frequency
- Distribution of customer item reorder rate
- Customer reorder profile

### Page 3 — Product & Category Performance

Answers:

> Which products, departments, and aisles show stronger repeat-purchase behavior?

Main visuals:

- Top products by item volume
- Top products by reorder rate with a minimum volume threshold
- Reorder rate by department
- Top aisles by reorder rate
- Product detail table

## Important Analytical Notes

- `59.01%` is the **overall weighted item reorder rate**.
- The customer-level average item reorder rate is approximately `44.43%` and is a different statistic.
- Product reorder-rate rankings use a minimum item-volume threshold to reduce instability from products with very few observations.
- The source dataset does not contain transaction revenue, price, margin, or demographic attributes, so this project focuses on behavioral and product analytics rather than financial or demographic analysis.
- Results should be interpreted within the supplied dataset population and split rather than generalized to all e-commerce customers.

## Tools

- MySQL 8.x
- Python
- Pandas
- NumPy
- Power BI
- Git / GitHub
- GitHub Pages

## Reproducibility

1. Download the Kaggle dataset.
2. Place the six source CSVs into `data/raw/`.
3. Run `python/profile_dataset.py`.
4. Create and validate the MySQL staging layer using the SQL scripts.
5. Build customer and timing marts.
6. Run the Python large-scale processing scripts.
7. Put the seven compact analytical marts into `data/processed/`.
8. Import the seven processed CSV files into Power BI.
9. Recreate or update the three dashboard pages using `powerbi/README.md`.
10. Place the final screenshots in `screenshots/`.
11. Publish the `docs/` folder with GitHub Pages.

## Repository Structure

```text
ecommerce-customer-reorder-analytics/
├── README.md
├── .gitignore
├── requirements.txt
├── data/
│   ├── README.md
│   ├── raw/
│   ├── staging/
│   └── processed/
├── sql/
├── python/
├── powerbi/
├── screenshots/
└── docs/
```

## Portfolio Site

The static portfolio page is in `docs/index.html`.

## Source

https://www.kaggle.com/datasets/psparks/instacart-market-basket-analysis
