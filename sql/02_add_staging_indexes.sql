-- Project 3: E-Commerce Customer Behavior & Reorder Analytics
-- 02_add_staging_indexes.sql
-- Run AFTER all six CSV files have been imported.

USE ecommerce_customer_reorder;

CREATE INDEX idx_aisles_id
    ON stg_aisles (aisle_id);

CREATE INDEX idx_departments_id
    ON stg_departments (department_id);

CREATE INDEX idx_products_product_id
    ON stg_products (product_id);

CREATE INDEX idx_products_aisle
    ON stg_products (aisle_id);

CREATE INDEX idx_products_department
    ON stg_products (department_id);

CREATE INDEX idx_orders_order_id
    ON stg_orders (order_id);

CREATE INDEX idx_orders_user_order
    ON stg_orders (user_id, order_number);

CREATE INDEX idx_orders_eval_set
    ON stg_orders (eval_set);

CREATE INDEX idx_orders_dow_hour
    ON stg_orders (order_dow, order_hour_of_day);

CREATE INDEX idx_prior_order
    ON stg_order_products__prior (order_id);

CREATE INDEX idx_prior_product
    ON stg_order_products__prior (product_id);

CREATE INDEX idx_prior_order_product
    ON stg_order_products__prior (order_id, product_id);

CREATE INDEX idx_train_order
    ON stg_order_products__train (order_id);

CREATE INDEX idx_train_product
    ON stg_order_products__train (product_id);

CREATE INDEX idx_train_order_product
    ON stg_order_products__train (order_id, product_id);
