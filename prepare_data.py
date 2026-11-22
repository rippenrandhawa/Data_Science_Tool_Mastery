"""Prepare the shared real-world dataset used by every lab and the integrated project.

Source (verified, DOI-documented):
    UCI Machine Learning Repository, "Online Retail", dataset 352
    https://doi.org/10.24432/C5BW33
    direct file: https://archive.ics.uci.edu/ml/machine-learning-databases/00352/Online%20Retail.xlsx

The full file holds 541,909 transaction lines.  For the tool-mastery labs we use a
documented, reproducible subset: every line belonging to 500 invoices sampled with
random_state=42 from the cleaned sales view.  This keeps the relational model small
enough for MySQL/Excel/Power BI while remaining a genuine slice of real transactions.

Outputs (under data/):
    online_retail_sales_sample.csv  - flat transaction lines (all tools)
    customers.csv / products.csv / orders.csv / order_items.csv - normalised tables
"""

import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA_DIR = os.path.join(ROOT, "data")
RAW_PATH = os.path.join(RAW_DIR := "/tmp", "Online_Retail.xlsx")

SAMPLE_INVOICES = 500
RANDOM_STATE = 42

# Stock codes that are not products (postage, manual adjustments, fees, etc.).
NON_PRODUCT_CODES = {
    "POST", "DOT", "M", "C2", "D", "S", "CRUK", "PADS", "B", "AMAZONFEE",
    "BANK CHARGES",
}


def load_and_clean():
    """Load the original UCI export and apply the documented cleaning rules."""
    raw = pd.read_excel(RAW_PATH)

    df = raw.copy()
    df["InvoiceNo"] = df["InvoiceNo"].astype(str).str.strip()
    df["StockCode"] = df["StockCode"].astype(str).str.strip()
    df["Description"] = df["Description"].astype(str).str.strip()
    df["Country"] = df["Country"].astype(str).str.strip()
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["CustomerID"] = pd.to_numeric(df["CustomerID"], errors="coerce")

    before = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    dupes = before - len(df)

    df["is_cancellation"] = df["InvoiceNo"].str.upper().str.startswith("C") | (df["Quantity"] < 0)
    df["is_non_product"] = (
        df["StockCode"].str.upper().isin(NON_PRODUCT_CODES) | (df["UnitPrice"] <= 0)
    )
    df["line_total"] = (df["Quantity"] * df["UnitPrice"]).round(2)

    sales = df[(~df["is_cancellation"]) & (~df["is_non_product"]) & (df["line_total"] > 0)]
    sales = sales.copy()
    print(f"raw={before:,}  duplicates removed={dupes:,}  sales lines={len(sales):,}")
    return df, sales


def build_sample(sales):
    """Take every line of 500 seeded invoices from the cleaned sales view."""
    rng = np.random.default_rng(RANDOM_STATE)
    invoices = sales["InvoiceNo"].drop_duplicates().to_numpy()
    chosen = rng.choice(invoices, size=SAMPLE_INVOICES, replace=False)
    sample = sales[sales["InvoiceNo"].isin(chosen)].copy()
    sample = sample.sort_values(["InvoiceNo", "StockCode"]).reset_index(drop=True)
    print(f"sample: {len(sample):,} lines, {sample['InvoiceNo'].nunique()} invoices, "
          f"{sample['CustomerID'].nunique()} customers, {sample['StockCode'].nunique()} products")
    return sample


def build_normalised(sample):
    """Derive the four relational tables from the sample.

    Guest lines (no CustomerID) cannot satisfy a customer foreign key, so the
    relational model covers registered-customer orders only; the flat sample keeps
    every line so the Python labs can still analyse guest behaviour.
    """
    known = sample[sample["CustomerID"].notna()].copy()
    known["CustomerID"] = known["CustomerID"].astype(int)

    customers = (
        known.groupby("CustomerID")
        .agg(country=("Country", "first"),
             first_order=("InvoiceDate", "min"),
             last_order=("InvoiceDate", "max"))
        .reset_index()
    )

    products = (
        known.groupby("StockCode")
        .agg(description=("Description", "first"),
             modal_unit_price=("UnitPrice", lambda s: s.mode().iloc[0]))
        .reset_index()
    )

    orders = (
        known.groupby("InvoiceNo")
        .agg(invoice_date=("InvoiceDate", "first"),
             customer_id=("CustomerID", "first"),
             country=("Country", "first"))
        .reset_index()
    )

    order_items = (
        known[["InvoiceNo", "StockCode", "Quantity", "UnitPrice", "line_total"]]
        .reset_index(drop=True)
    )

    guest_lines = int(sample["CustomerID"].isna().sum())
    print(f"relational: customers={len(customers):,} products={len(products):,} "
          f"orders={len(orders):,} items={len(order_items):,} (guest lines excluded={guest_lines:,})")
    return customers, products, orders, order_items, guest_lines


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    full, sales = load_and_clean()
    sample = build_sample(sales)

    flat_cols = ["InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate",
                 "UnitPrice", "CustomerID", "Country", "line_total"]
    sample[flat_cols].to_csv(os.path.join(DATA_DIR, "online_retail_sales_sample.csv"),
                             index=False)

    customers, products, orders, order_items, guests = build_normalised(sample)
    customers.to_csv(os.path.join(DATA_DIR, "customers.csv"), index=False)
    products.to_csv(os.path.join(DATA_DIR, "products.csv"), index=False)
    orders.to_csv(os.path.join(DATA_DIR, "orders.csv"), index=False)
    order_items.to_csv(os.path.join(DATA_DIR, "order_items.csv"), index=False)

    summary = {
        "raw_rows": int(len(full)),
        "sales_lines": int(len(sales)),
        "sample_lines": int(len(sample)),
        "sample_invoices": int(sample["InvoiceNo"].nunique()),
        "sample_customers": int(sample["CustomerID"].nunique()),
        "sample_products": int(sample["StockCode"].nunique()),
        "sample_revenue": round(float(sample["line_total"].sum()), 2),
        "date_min": str(sample["InvoiceDate"].min()),
        "date_max": str(sample["InvoiceDate"].max()),
        "guest_lines_in_sample": guests,
        "customers_table": int(len(customers)),
        "products_table": int(len(products)),
        "orders_table": int(len(orders)),
        "order_items_table": int(len(order_items)),
        "random_state": RANDOM_STATE,
        "sample_invoices_used": SAMPLE_INVOICES,
    }
    pd.Series(summary).to_json(os.path.join(DATA_DIR, "sample_summary.json"),
                               indent=2, orient="index")
    print("summary:", summary)


if __name__ == "__main__":
    main()
