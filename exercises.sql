-- ===========================================================================
-- LAB 2 - SQL AND DATABASE ANALYSIS : 15 practical exercises
-- Database : retail_analytics   Engine : MySQL 8 / MariaDB 10.4+
--
-- Every block below is prefixed with `-- @Qnn`.  run_sql_lab.py splits the
-- file on those markers and executes each query against a live database,
-- writing the real result set to SQL_Lab/outputs/query_nn.txt
--
-- Exercise topics, in order:
--   Q01 SELECT & column projection          Q09 Subquery
--   Q02 WHERE filtering                     Q10 Common Table Expression
--   Q03 ORDER BY + LIMIT                    Q11 CASE expression
--   Q04 Aggregate functions                 Q12 Window functions
--   Q05 GROUP BY                            Q13 Business: repeat customers
--   Q06 HAVING                              Q14 Business: customer recency
--   Q07 INNER JOIN                          Q15 Business: top product per country
--   Q08 LEFT JOIN
-- ===========================================================================

USE retail_analytics;

-- @Q01
-- Projection: inspect the product catalogue.
SELECT stock_code, description, modal_unit_price
FROM products
ORDER BY stock_code
LIMIT 5;

-- @Q02
-- Filtering: every invoice issued in November 2011 (the peak month).
SELECT invoice_no, invoice_date, customer_id, country
FROM orders
WHERE invoice_date >= '2011-11-01' AND invoice_date < '2011-12-01'
ORDER BY invoice_date
LIMIT 10;

-- @Q03
-- Sorting and limiting: the ten best revenue-generating products.
SELECT p.stock_code,
       p.description,
       SUM(oi.quantity)      AS units_sold,
       ROUND(SUM(oi.line_total), 2) AS revenue_gbp
FROM order_items oi
INNER JOIN products p ON p.stock_code = oi.stock_code
GROUP BY p.stock_code, p.description
ORDER BY revenue_gbp DESC
LIMIT 10;

-- @Q04
-- Aggregation: headline business KPIs.
SELECT COUNT(DISTINCT o.invoice_no)              AS invoices,
       COUNT(DISTINCT o.customer_id)             AS customers,
       ROUND(SUM(oi.line_total), 2)              AS revenue_gbp,
       ROUND(AVG(oi.line_total), 2)              AS avg_line_value_gbp,
       ROUND(SUM(oi.line_total) / COUNT(DISTINCT o.invoice_no), 2) AS avg_order_value_gbp
FROM orders o
INNER JOIN order_items oi ON oi.invoice_no = o.invoice_no;

-- @Q05
-- Grouping: revenue by country, largest first.
SELECT o.country,
       COUNT(DISTINCT o.invoice_no)   AS orders,
       COUNT(DISTINCT o.customer_id)  AS customers,
       ROUND(SUM(oi.line_total), 2)   AS revenue_gbp
FROM orders o
INNER JOIN order_items oi ON oi.invoice_no = o.invoice_no
GROUP BY o.country
ORDER BY revenue_gbp DESC
LIMIT 10;

-- @Q06
-- Group filtering: only countries contributing more than GBP 5,000.
SELECT o.country,
       COUNT(DISTINCT o.invoice_no) AS orders,
       ROUND(SUM(oi.line_total), 2) AS revenue_gbp
FROM orders o
INNER JOIN order_items oi ON oi.invoice_no = o.invoice_no
GROUP BY o.country
HAVING revenue_gbp > 5000
ORDER BY revenue_gbp DESC;

-- @Q07
-- Inner join: invoice value with the customer's registered country.
SELECT o.invoice_no,
       o.invoice_date,
       c.customer_id,
       c.country,
       ROUND(SUM(oi.line_total), 2) AS order_value_gbp
FROM orders o
INNER JOIN customers c  ON c.customer_id = o.customer_id
INNER JOIN order_items oi ON oi.invoice_no = o.invoice_no
GROUP BY o.invoice_no, o.invoice_date, c.customer_id, c.country
ORDER BY order_value_gbp DESC
LIMIT 10;

-- @Q08
-- Left join: registered customers who placed no order in November 2011.
SELECT c.customer_id,
       c.country,
       COUNT(o.invoice_no) AS orders_in_nov_2011
FROM customers c
LEFT JOIN orders o
       ON o.customer_id = c.customer_id
      AND DATE_FORMAT(o.invoice_date, '%Y-%m') = '2011-11'
GROUP BY c.customer_id, c.country
HAVING orders_in_nov_2011 = 0
ORDER BY c.customer_id
LIMIT 10;

-- @Q09
-- Subquery: products priced above the catalogue average.
SELECT stock_code, description, modal_unit_price
FROM products
WHERE modal_unit_price > (SELECT AVG(modal_unit_price) FROM products)
ORDER BY modal_unit_price DESC
LIMIT 10;

-- @Q10
-- CTE: monthly revenue and each month's share of the total.
WITH monthly AS (
    SELECT DATE_FORMAT(o.invoice_date, '%Y-%m') AS month,
           ROUND(SUM(oi.line_total), 2)          AS revenue_gbp
    FROM orders o
    INNER JOIN order_items oi ON oi.invoice_no = o.invoice_no
    GROUP BY DATE_FORMAT(o.invoice_date, '%Y-%m')
)
SELECT month,
       revenue_gbp,
       ROUND(revenue_gbp / SUM(revenue_gbp) OVER () * 100, 2) AS pct_of_total
FROM monthly
ORDER BY month;

-- @Q11
-- CASE: band orders by value and profile each band.
SELECT CASE
           WHEN order_value < 50  THEN 'Small  (under 50)'
           WHEN order_value < 200 THEN 'Medium (50 - 200)'
           ELSE                       'Large  (200 and over)'
       END AS value_band,
       COUNT(*)                  AS orders,
       ROUND(AVG(order_value), 2) AS avg_order_value_gbp,
       ROUND(SUM(order_value), 2) AS revenue_gbp
FROM (
    SELECT o.invoice_no, SUM(oi.line_total) AS order_value
    FROM orders o
    INNER JOIN order_items oi ON oi.invoice_no = o.invoice_no
    GROUP BY o.invoice_no
) AS order_totals
GROUP BY value_band
ORDER BY revenue_gbp DESC;

-- @Q12
-- Window functions: rank products and compute a running revenue total.
SELECT stock_code,
       description,
       revenue_gbp,
       RANK() OVER (ORDER BY revenue_gbp DESC) AS revenue_rank,
       ROUND(SUM(revenue_gbp) OVER (ORDER BY revenue_gbp DESC
                                    ROWS UNBOUNDED PRECEDING), 2) AS running_total_gbp
FROM (
    SELECT p.stock_code, p.description, SUM(oi.line_total) AS revenue_gbp
    FROM order_items oi
    INNER JOIN products p ON p.stock_code = oi.stock_code
    GROUP BY p.stock_code, p.description
) AS product_revenue
ORDER BY revenue_gbp DESC
LIMIT 10;

-- @Q13
-- Business question: which customers place the most orders?
SELECT customer_id,
       COUNT(*) AS orders,
       ROUND(SUM(order_value), 2) AS revenue_gbp
FROM (
    SELECT o.customer_id, o.invoice_no, SUM(oi.line_total) AS order_value
    FROM orders o
    INNER JOIN order_items oi ON oi.invoice_no = o.invoice_no
    GROUP BY o.customer_id, o.invoice_no
) AS per_order
GROUP BY customer_id
HAVING orders > 1
ORDER BY orders DESC, revenue_gbp DESC
LIMIT 10;

-- @Q14
-- Business question: how recently has each customer bought?
SELECT customer_id,
       country,
       MAX(invoice_date) AS last_order_date,
       DATEDIFF((SELECT MAX(invoice_date) FROM orders), MAX(invoice_date)) AS days_since_last_order
FROM orders
GROUP BY customer_id, country
ORDER BY days_since_last_order DESC
LIMIT 10;

-- @Q15
-- Business question: the single best product in each country (window + CTE).
WITH country_product AS (
    SELECT o.country,
           p.stock_code,
           p.description,
           ROUND(SUM(oi.line_total), 2) AS revenue_gbp,
           RANK() OVER (PARTITION BY o.country
                        ORDER BY SUM(oi.line_total) DESC) AS rank_in_country
    FROM orders o
    INNER JOIN order_items oi ON oi.invoice_no = o.invoice_no
    INNER JOIN products p     ON p.stock_code  = oi.stock_code
    GROUP BY o.country, p.stock_code, p.description
)
SELECT country, stock_code, description, revenue_gbp
FROM country_product
WHERE rank_in_country = 1
ORDER BY revenue_gbp DESC
LIMIT 15;
