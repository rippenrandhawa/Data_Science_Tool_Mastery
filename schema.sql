-- ===========================================================================
-- LAB 2 - SQL AND DATABASE ANALYSIS
-- Schema for the retail_analytics relational database.
--
-- Engine : MySQL 8 / MariaDB 10.4+  (developed and executed on MariaDB 11.8)
-- Source : normalised tables derived from the UCI "Online Retail" dataset
--          (https://doi.org/10.24432/C5BW33)
--
-- Run    : mysql -u analyst -p < schema.sql
-- ===========================================================================

DROP DATABASE IF EXISTS retail_analytics;
CREATE DATABASE retail_analytics
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
USE retail_analytics;

-- ---------------------------------------------------------------------------
-- customers : one row per registered customer
-- ---------------------------------------------------------------------------
CREATE TABLE customers (
    customer_id  INT           NOT NULL,
    country      VARCHAR(60)   NOT NULL,
    first_order  DATETIME      NOT NULL,
    last_order   DATETIME      NOT NULL,
    CONSTRAINT pk_customers PRIMARY KEY (customer_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- products : one row per distinct stock code
-- ---------------------------------------------------------------------------
CREATE TABLE products (
    stock_code        VARCHAR(20)   NOT NULL,
    description       VARCHAR(200)  NOT NULL,
    modal_unit_price  DECIMAL(10,2) NOT NULL,
    CONSTRAINT pk_products PRIMARY KEY (stock_code)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- orders : one row per invoice (a customer places many orders)
-- ---------------------------------------------------------------------------
CREATE TABLE orders (
    invoice_no    VARCHAR(20) NOT NULL,
    invoice_date  DATETIME    NOT NULL,
    customer_id   INT         NOT NULL,
    country       VARCHAR(60) NOT NULL,
    CONSTRAINT pk_orders PRIMARY KEY (invoice_no),
    CONSTRAINT fk_orders_customer
        FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- order_items : one row per invoice line (an order has many items)
-- ---------------------------------------------------------------------------
CREATE TABLE order_items (
    item_id     INT AUTO_INCREMENT,
    invoice_no  VARCHAR(20)   NOT NULL,
    stock_code  VARCHAR(20)   NOT NULL,
    quantity    INT           NOT NULL,
    unit_price  DECIMAL(10,2) NOT NULL,
    line_total  DECIMAL(12,2) NOT NULL,
    CONSTRAINT pk_order_items PRIMARY KEY (item_id),
    CONSTRAINT fk_items_order
        FOREIGN KEY (invoice_no) REFERENCES orders (invoice_no),
    CONSTRAINT fk_items_product
        FOREIGN KEY (stock_code) REFERENCES products (stock_code)
) ENGINE=InnoDB;

-- Supporting indexes for the analytical queries used in the exercises.
CREATE INDEX idx_orders_customer ON orders (customer_id);
CREATE INDEX idx_orders_date    ON orders (invoice_date);
CREATE INDEX idx_items_product  ON order_items (stock_code);

SELECT 'schema created' AS status;
