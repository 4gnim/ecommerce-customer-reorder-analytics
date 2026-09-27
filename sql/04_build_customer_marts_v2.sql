-- Project 3: E-Commerce Customer Behavior & Reorder Analytics
-- 04_build_customer_marts_v2.sql
--
-- Optimization:
-- Do NOT join 33.8M order-item rows directly to orders and then GROUP BY user.
-- Instead:
--   1) Aggregate order items to order grain first (~3.3M orders).
--   2) Join that compact result to orders.
--   3) Aggregate to customer grain (~206K customers).
--
-- Staging tables are untouched.

USE ecommerce_customer_reorder;

DROP TABLE IF EXISTS mart_customer_reorder;
DROP TABLE IF EXISTS mart_customer_behavior;

-- ============================================================
-- 1. Customer behavior from orders only
-- ============================================================

CREATE TABLE mart_customer_behavior AS
SELECT
    user_id,
    COUNT(*) AS total_orders,
    SUM(eval_set = 'prior') AS prior_orders,
    SUM(eval_set = 'train') AS train_orders,
    MIN(order_number) AS first_order_number,
    MAX(order_number) AS last_order_number,
    ROUND(
        AVG(
            CASE
                WHEN days_since_prior_order IS NOT NULL
                THEN days_since_prior_order
            END
        ),
        2
    ) AS avg_days_between_orders,
    SUM(order_number > 1) AS repeat_order_count
FROM stg_orders
WHERE eval_set IN ('prior', 'train')
GROUP BY user_id;

ALTER TABLE mart_customer_behavior
    ADD PRIMARY KEY (user_id);

-- ============================================================
-- 2. Aggregate PRIOR order items to ORDER grain
--    Expected output: 3,214,874 rows, one per prior order.
-- ============================================================

DROP TEMPORARY TABLE IF EXISTS tmp_prior_order_metrics;

CREATE TEMPORARY TABLE tmp_prior_order_metrics AS
SELECT
    order_id,
    COUNT(*) AS total_items,
    SUM(reordered) AS reordered_items
FROM stg_order_products__prior
GROUP BY order_id;

ALTER TABLE tmp_prior_order_metrics
    ADD PRIMARY KEY (order_id);

-- ============================================================
-- 3. Aggregate TRAIN order items to ORDER grain
--    Expected output: 131,209 rows, one per train order.
-- ============================================================

DROP TEMPORARY TABLE IF EXISTS tmp_train_order_metrics;

CREATE TEMPORARY TABLE tmp_train_order_metrics AS
SELECT
    order_id,
    COUNT(*) AS total_items,
    SUM(reordered) AS reordered_items
FROM stg_order_products__train
GROUP BY order_id;

ALTER TABLE tmp_train_order_metrics
    ADD PRIMARY KEY (order_id);

-- ============================================================
-- 4. Aggregate compact order-level metrics to USER grain
-- ============================================================

CREATE TABLE mart_customer_reorder (
    user_id INT NOT NULL,
    total_items BIGINT NOT NULL,
    reordered_items BIGINT NOT NULL,
    item_reorder_rate_pct DECIMAL(7,2) NOT NULL,
    PRIMARY KEY (user_id)
) ENGINE=InnoDB;

INSERT INTO mart_customer_reorder (
    user_id,
    total_items,
    reordered_items,
    item_reorder_rate_pct
)
SELECT
    o.user_id,
    SUM(m.total_items) AS total_items,
    SUM(m.reordered_items) AS reordered_items,
    ROUND(
        100.0 * SUM(m.reordered_items) / NULLIF(SUM(m.total_items), 0),
        2
    ) AS item_reorder_rate_pct
FROM (
    SELECT order_id, total_items, reordered_items
    FROM tmp_prior_order_metrics

    UNION ALL

    SELECT order_id, total_items, reordered_items
    FROM tmp_train_order_metrics
) m
INNER JOIN stg_orders o
    ON m.order_id = o.order_id
WHERE o.eval_set IN ('prior', 'train')
GROUP BY o.user_id;

DROP TEMPORARY TABLE IF EXISTS tmp_prior_order_metrics;
DROP TEMPORARY TABLE IF EXISTS tmp_train_order_metrics;

-- ============================================================
-- 5. Validation
-- ============================================================

SELECT 'mart_customer_behavior' AS table_name, COUNT(*) AS row_count
FROM mart_customer_behavior
UNION ALL
SELECT 'mart_customer_reorder', COUNT(*)
FROM mart_customer_reorder;

SELECT
    COUNT(*) AS behavior_without_reorder_metrics
FROM mart_customer_behavior b
LEFT JOIN mart_customer_reorder r
    ON b.user_id = r.user_id
WHERE r.user_id IS NULL;

SELECT
    COUNT(*) AS reorder_without_behavior
FROM mart_customer_reorder r
LEFT JOIN mart_customer_behavior b
    ON b.user_id = r.user_id
WHERE b.user_id IS NULL;

SELECT
    MIN(item_reorder_rate_pct) AS min_reorder_rate_pct,
    MAX(item_reorder_rate_pct) AS max_reorder_rate_pct,
    ROUND(AVG(item_reorder_rate_pct), 2) AS avg_reorder_rate_pct
FROM mart_customer_reorder;
