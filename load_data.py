"""Load the normalised CSVs into the retail_analytics MySQL/MariaDB database.

Uses PyMySQL with executemany batch inserts (fast, parameterised, no SQL
injection risk).  Run after schema.sql:

    python load_data.py
"""

import os
import sys

import pandas as pd
import pymysql

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA_DIR = os.path.join(ROOT, "data")

CONNECTION = {
    "host": os.environ.get("DB_HOST", "127.0.0.1"),
    "port": int(os.environ.get("DB_PORT", "3306")),
    "user": os.environ.get("DB_USER", "analyst"),
    "password": os.environ.get("DB_PASSWORD", "Analyst@2026"),
    "database": "retail_analytics",
    "charset": "utf8mb4",
}

BATCH = 1000


def connect():
    try:
        return pymysql.connect(**CONNECTION)
    except pymysql.err.OperationalError as exc:
        print(f"Could not connect to MySQL: {exc}")
        print("Start the server and create the schema first (see README.md).")
        sys.exit(1)


def insert_many(cursor, sql, rows):
    total = 0
    for start in range(0, len(rows), BATCH):
        batch = rows[start:start + BATCH]
        cursor.executemany(sql, batch)
        total += len(batch)
    return total


def load():
    customers = pd.read_csv(os.path.join(DATA_DIR, "customers.csv"),
                            parse_dates=["first_order", "last_order"])
    customers = customers.rename(columns={"CustomerID": "customer_id"})
    products = pd.read_csv(os.path.join(DATA_DIR, "products.csv"))
    products = products.rename(columns={"StockCode": "stock_code"})
    orders = pd.read_csv(os.path.join(DATA_DIR, "orders.csv"),
                         parse_dates=["invoice_date"], dtype={"invoice_no": str})
    orders = orders.rename(columns={"InvoiceNo": "invoice_no", "CustomerID": "customer_id"})
    items = pd.read_csv(os.path.join(DATA_DIR, "order_items.csv"),
                        dtype={"invoice_no": str, "stock_code": str})
    items = items.rename(columns={"InvoiceNo": "invoice_no", "StockCode": "stock_code",
                                  "Quantity": "quantity", "UnitPrice": "unit_price",
                                  "line_total": "line_total"})

    conn = connect()
    try:
        with conn.cursor() as cur:
            cur.execute("SET FOREIGN_KEY_CHECKS = 0")
            for table in ("order_items", "orders", "products", "customers"):
                cur.execute(f"TRUNCATE TABLE {table}")
            cur.execute("SET FOREIGN_KEY_CHECKS = 1")

            n = insert_many(
                cur,
                "INSERT INTO customers (customer_id, country, first_order, last_order) "
                "VALUES (%s, %s, %s, %s)",
                [(int(r.customer_id), r.country, r.first_order.to_pydatetime(),
                  r.last_order.to_pydatetime()) for r in customers.itertuples()])
            print(f"customers   : {n:,} rows")

            n = insert_many(
                cur,
                "INSERT INTO products (stock_code, description, modal_unit_price) "
                "VALUES (%s, %s, %s)",
                [(r.stock_code, r.description[:200], float(r.modal_unit_price))
                 for r in products.itertuples()])
            print(f"products    : {n:,} rows")

            n = insert_many(
                cur,
                "INSERT INTO orders (invoice_no, invoice_date, customer_id, country) "
                "VALUES (%s, %s, %s, %s)",
                [(r.invoice_no, r.invoice_date.to_pydatetime(), int(r.customer_id),
                  r.country) for r in orders.itertuples()])
            print(f"orders      : {n:,} rows")

            n = insert_many(
                cur,
                "INSERT INTO order_items (invoice_no, stock_code, quantity, unit_price, "
                "line_total) VALUES (%s, %s, %s, %s, %s)",
                [(r.invoice_no, r.stock_code, int(r.quantity), float(r.unit_price),
                  float(r.line_total)) for r in items.itertuples()])
            print(f"order_items : {n:,} rows")
        conn.commit()

        with conn.cursor() as cur:
            cur.execute("ANALYZE TABLE customers, products, orders, order_items")
            cur.execute(
                "SELECT (SELECT COUNT(*) FROM customers), (SELECT COUNT(*) FROM products), "
                "(SELECT COUNT(*) FROM orders), (SELECT COUNT(*) FROM order_items)")
            counts = cur.fetchone()
        print(f"\nloaded -> customers={counts[0]:,} products={counts[1]:,} "
              f"orders={counts[2]:,} order_items={counts[3]:,}")
    finally:
        conn.close()


if __name__ == "__main__":
    load()
