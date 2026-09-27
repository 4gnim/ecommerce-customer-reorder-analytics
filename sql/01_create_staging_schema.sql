-- Project 3: E-Commerce Customer Behavior & Reorder Analytics
-- 01_create_staging_schema.sql
-- Purpose: create a raw/staging layer that mirrors the source CSVs.
--
-- Best-practice note:
-- The staging layer intentionally has NO primary keys or foreign keys.
-- Source assumptions will be validated after loading. Indexes are also added
-- in a separate script after the bulk import to avoid slowing CSV ingestion.

CREATE DATABASE IF NOT EXISTS ecommerce_customer_reorder
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_0900_ai_ci;

USE ecommerce_customer_reorder;

DROP TABLE IF EXISTS stg_order_products__prior;
DROP TABLE IF EXISTS stg_order_products__train;
DROP TABLE IF EXISTS stg_orders;
DROP TABLE IF EXISTS stg_products;
DROP TABLE IF EXISTS stg_aisles;
DROP TABLE IF EXISTS stg_departments;

CREATE TABLE stg_aisles (
    aisle_id INT NOT NULL,
    aisle VARCHAR(255) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE stg_departments (
    department_id INT NOT NULL,
    department VARCHAR(255) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE stg_products (
    product_id INT NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    aisle_id INT NOT NULL,
    department_id INT NOT NULL
) ENGINE=InnoDB;

CREATE TABLE stg_orders (
    order_id INT NOT NULL,
    user_id INT NOT NULL,
    eval_set VARCHAR(10) NOT NULL,
    order_number INT NOT NULL,
    order_dow TINYINT UNSIGNED NOT NULL,
    order_hour_of_day TINYINT UNSIGNED NOT NULL,
    days_since_prior_order DECIMAL(6,2) NULL
) ENGINE=InnoDB;

CREATE TABLE stg_order_products__prior (
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    add_to_cart_order SMALLINT UNSIGNED NOT NULL,
    reordered TINYINT UNSIGNED NOT NULL
) ENGINE=InnoDB;

CREATE TABLE stg_order_products__train (
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    add_to_cart_order SMALLINT UNSIGNED NOT NULL,
    reordered TINYINT UNSIGNED NOT NULL
) ENGINE=InnoDB;
