# Power BI

The dashboard has three pages:

1. **Customer Overview**
2. **Customer Reorder Behavior**
3. **Product & Category Performance**

## Import These Tables

Load the seven compact analytical CSVs from `data/processed/`:

```text
mart_customer_behavior.csv
mart_customer_reorder.csv
mart_order_timing.csv
product_performance.csv
department_performance.csv
aisle_performance.csv
order_sequence_performance.csv
```

Keep the seven marts independent unless a relationship is explicitly needed. They have different grains, so unnecessary relationships can create misleading filter behavior.

## Important Measures

### Overall Item Reorder Rate

```DAX
Overall Item Reorder Rate =
DIVIDE(
    SUM(CustomerReorder[reordered_items]),
    SUM(CustomerReorder[total_items]),
    0
)
```

Format as Percentage with 2 decimal places.

### Customer Reorder Rate

```DAX
Customer Reorder Rate =
DIVIDE(
    SUM(CustomerReorder[reordered_items]),
    SUM(CustomerReorder[total_items]),
    0
)
```

### Product Reorder Rate

```DAX
Product Reorder Rate =
DIVIDE(
    SUM(ProductPerformance[reordered_items]),
    SUM(ProductPerformance[total_items]),
    0
)
```

Format as Percentage with 2 decimal places.

## Product Detail Table

Use row-level fields from **ProductPerformance** only:

- `product_name`
- `department`
- `aisle`
- `total_items`
- `reordered_items`

Use the `Product Reorder Rate` measure as the last column.

Do not combine customer-mart totals with product-mart fields in this table.

## Color Theme

Use one consistent theme across all three pages:

| Role | Hex |
|---|---|
| Navy | `#183B56` |
| Teal | `#0F766E` |
| Blue | `#2563EB` |
| Amber | `#F59E0B` |
| Slate | `#64748B` |
| Background | `#F7F9FC` |

Suggested semantic use:

- **Teal** — primary customer/product metrics
- **Blue** — timing/category analysis
- **Amber** — reorder-focused visuals
- **Navy** — headings and important text
- **Slate** — neutral tables and secondary visuals
