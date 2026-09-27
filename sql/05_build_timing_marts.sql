-- Project 3: E-Commerce Customer Behavior & Reorder Analytics
-- 05_build_timing_marts.sql
--
-- Order timing is based entirely on stg_orders, so no 33.8M-row
-- order-item scan is required for this mart.

USE ecommerce_customer_reorder;

DROP TABLE IF EXISTS mart_order_timing;

CREATE TABLE mart_order_timing AS
SELECT
    order_dow,
    order_hour_of_day,
    COUNT(*) AS total_orders,
    COUNT(DISTINCT user_id) AS unique_customers
FROM stg_orders
WHERE eval_set IN ('prior', 'train')
GROUP BY order_dow, order_hour_of_day;

ALTER TABLE mart_order_timing
    ADD PRIMARY KEY (order_dow, order_hour_of_day);

SELECT COUNT(*) AS timing_rows
FROM mart_order_timing;
