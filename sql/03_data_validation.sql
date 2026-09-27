-- Project 3: E-Commerce Customer Behavior & Reorder Analytics
-- 03_data_validation.sql
-- Run AFTER CSV import and AFTER staging indexes have been created.

USE ecommerce_customer_reorder;

-- ============================================================
-- 1. Row counts
-- ============================================================

SELECT 'stg_aisles' AS table_name, COUNT(*) AS row_count
FROM stg_aisles
UNION ALL
SELECT 'stg_departments', COUNT(*) FROM stg_departments
UNION ALL
SELECT 'stg_products', COUNT(*) FROM stg_products
UNION ALL
SELECT 'stg_orders', COUNT(*) FROM stg_orders
UNION ALL
SELECT 'stg_order_products__prior', COUNT(*) FROM stg_order_products__prior
UNION ALL
SELECT 'stg_order_products__train', COUNT(*) FROM stg_order_products__train;


-- ============================================================
-- 2. Primary-key uniqueness checks
-- ============================================================

SELECT 'orders.order_id duplicate groups' AS check_name, COUNT(*) AS issue_count
FROM (
    SELECT order_id
    FROM stg_orders
    GROUP BY order_id
    HAVING COUNT(*) > 1
) d
UNION ALL
SELECT 'products.product_id duplicate groups', COUNT(*)
FROM (
    SELECT product_id
    FROM stg_products
    GROUP BY product_id
    HAVING COUNT(*) > 1
) d
UNION ALL
SELECT 'aisles.aisle_id duplicate groups', COUNT(*)
FROM (
    SELECT aisle_id
    FROM stg_aisles
    GROUP BY aisle_id
    HAVING COUNT(*) > 1
) d
UNION ALL
SELECT 'departments.department_id duplicate groups', COUNT(*)
FROM (
    SELECT department_id
    FROM stg_departments
    GROUP BY department_id
    HAVING COUNT(*) > 1
) d
UNION ALL
SELECT 'prior(order_id, product_id) duplicate groups', COUNT(*)
FROM (
    SELECT order_id, product_id
    FROM stg_order_products__prior
    GROUP BY order_id, product_id
    HAVING COUNT(*) > 1
) d
UNION ALL
SELECT 'train(order_id, product_id) duplicate groups', COUNT(*)
FROM (
    SELECT order_id, product_id
    FROM stg_order_products__train
    GROUP BY order_id, product_id
    HAVING COUNT(*) > 1
) d;


-- ============================================================
-- 3. Referential integrity / orphan checks
-- ============================================================

SELECT 'products -> aisles' AS check_name, COUNT(*) AS orphan_rows
FROM stg_products p
LEFT JOIN stg_aisles a
    ON p.aisle_id = a.aisle_id
WHERE a.aisle_id IS NULL

UNION ALL

SELECT 'products -> departments', COUNT(*)
FROM stg_products p
LEFT JOIN stg_departments d
    ON p.department_id = d.department_id
WHERE d.department_id IS NULL

UNION ALL

SELECT 'prior -> orders', COUNT(*)
FROM stg_order_products__prior op
LEFT JOIN stg_orders o
    ON op.order_id = o.order_id
WHERE o.order_id IS NULL

UNION ALL

SELECT 'prior -> products', COUNT(*)
FROM stg_order_products__prior op
LEFT JOIN stg_products p
    ON op.product_id = p.product_id
WHERE p.product_id IS NULL

UNION ALL

SELECT 'train -> orders', COUNT(*)
FROM stg_order_products__train op
LEFT JOIN stg_orders o
    ON op.order_id = o.order_id
WHERE o.order_id IS NULL

UNION ALL

SELECT 'train -> products', COUNT(*)
FROM stg_order_products__train op
LEFT JOIN stg_products p
    ON op.product_id = p.product_id
WHERE p.product_id IS NULL;


-- ============================================================
-- 4. Domain / range checks
-- ============================================================

SELECT 'orders.eval_set invalid values' AS check_name, COUNT(*) AS issue_count
FROM stg_orders
WHERE eval_set NOT IN ('prior', 'train', 'test')

UNION ALL
SELECT 'orders.order_dow outside 0-6', COUNT(*)
FROM stg_orders
WHERE order_dow NOT BETWEEN 0 AND 6

UNION ALL
SELECT 'orders.order_hour_of_day outside 0-23', COUNT(*)
FROM stg_orders
WHERE order_hour_of_day NOT BETWEEN 0 AND 23

UNION ALL
SELECT 'orders.days_since_prior_order negative', COUNT(*)
FROM stg_orders
WHERE days_since_prior_order < 0

UNION ALL
SELECT 'prior.reordered outside 0-1', COUNT(*)
FROM stg_order_products__prior
WHERE reordered NOT IN (0, 1)

UNION ALL
SELECT 'train.reordered outside 0-1', COUNT(*)
FROM stg_order_products__train
WHERE reordered NOT IN (0, 1)

UNION ALL
SELECT 'prior.add_to_cart_order below 1', COUNT(*)
FROM stg_order_products__prior
WHERE add_to_cart_order < 1

UNION ALL
SELECT 'train.add_to_cart_order below 1', COUNT(*)
FROM stg_order_products__train
WHERE add_to_cart_order < 1;


-- ============================================================
-- 5. Dataset composition
-- ============================================================

SELECT
    eval_set,
    COUNT(*) AS order_count,
    COUNT(DISTINCT user_id) AS customer_count,
    MIN(order_number) AS min_order_number,
    MAX(order_number) AS max_order_number
FROM stg_orders
GROUP BY eval_set
ORDER BY eval_set;


-- ============================================================
-- 6. Missingness
-- ============================================================

SELECT
    COUNT(*) AS total_orders,
    SUM(days_since_prior_order IS NULL) AS null_days_since_prior,
    ROUND(
        100.0 * SUM(days_since_prior_order IS NULL) / COUNT(*),
        2
    ) AS null_days_pct
FROM stg_orders;


-- ============================================================
-- 7. Basic ranges
-- ============================================================

SELECT
    MIN(order_number) AS min_order_number,
    MAX(order_number) AS max_order_number,
    MIN(order_dow) AS min_order_dow,
    MAX(order_dow) AS max_order_dow,
    MIN(order_hour_of_day) AS min_order_hour,
    MAX(order_hour_of_day) AS max_order_hour
FROM stg_orders;


-- ============================================================
-- 8. Product coverage
-- ============================================================

SELECT
    COUNT(*) AS total_products,
    COUNT(DISTINCT aisle_id) AS aisles_referenced,
    COUNT(DISTINCT department_id) AS departments_referenced
FROM stg_products;
