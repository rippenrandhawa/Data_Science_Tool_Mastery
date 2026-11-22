"""LAB 1 - Python for Data Analytics.

Demonstrates, with a real transaction dataset:
    variables and data structures, functions, loops and conditionals, file
    handling, exception handling, list comprehensions, CSV/Excel I/O, pandas
    DataFrames, NumPy arrays, cleaning, transformation and aggregation.

Run:  python python_lab.py
"""

import csv
import json
import os
from datetime import datetime

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA_PATH = os.path.join(ROOT, "data", "online_retail_sales_sample.csv")
EXCEL_SOURCE = "/tmp/Online_Retail.xlsx"
OUT_DIR = os.path.join(HERE, "evidence")
os.makedirs(OUT_DIR, exist_ok=True)

LINE = "-" * 74


def banner(title):
    print(f"\n{LINE}\n{title}\n{LINE}")


# ---------------------------------------------------------------------------
# Exercise 1 - File handling, exception handling and CSV/Excel I/O
# ---------------------------------------------------------------------------
def exercise_1_load_and_profile():
    banner("EXERCISE 1  Load the data (CSV + Excel) and profile it")

    # 1a. CSV with the standard library -------------------------------------
    try:
        with open(DATA_PATH, newline="", encoding="utf-8") as handle:
            reader = csv.reader(handle)
            header = next(reader)
            first_row = next(reader)
        print(f"csv.reader header      : {header}")
        print(f"csv.reader first row   : {first_row}")
    except FileNotFoundError as exc:                                  # exception handling
        print(f"Could not read {DATA_PATH}: {exc}")
        raise

    # 1b. pandas CSV --------------------------------------------------------
    df = pd.read_csv(DATA_PATH, parse_dates=["InvoiceDate"])
    print(f"\npandas shape           : {df.shape[0]:,} rows x {df.shape[1]} columns")
    print(f"columns                : {list(df.columns)}")
    print(f"memory usage           : {df.memory_usage(deep=True).sum() / 1024:.1f} KB")

    # 1c. Excel I/O (read a real .xlsx, write a subset back out) ------------
    try:
        raw_excel = pd.read_excel(EXCEL_SOURCE, nrows=5)
        print(f"\nExcel read OK          : {raw_excel.shape} (first 5 rows of the original file)")
    except FileNotFoundError:
        print("\nExcel read skipped     : original .xlsx not present in this environment")
        raw_excel = None

    out_excel = os.path.join(OUT_DIR, "exercise1_sample_subset.xlsx")
    df.head(50).to_excel(out_excel, index=False)
    print(f"Excel write OK         : {out_excel}")

    # 1d. dtype audit -------------------------------------------------------
    print("\ndtypes:")
    print(df.dtypes.to_string())
    return df


# ---------------------------------------------------------------------------
# Exercise 2 - Data structures, loops, conditionals, comprehensions
# ---------------------------------------------------------------------------
def exercise_2_structures(df):
    banner("EXERCISE 2  Data structures, loops, conditionals and comprehensions")

    # A dictionary keyed by country, built with a loop ----------------------
    country_revenue = {}
    for _, row in df.head(2000).iterrows():                 # explicit loop
        country = row["Country"]
        value = float(row["line_total"])
        if country in country_revenue:                       # conditional
            country_revenue[country] += value
        else:
            country_revenue[country] = value
    top3 = sorted(country_revenue.items(), key=lambda kv: kv[1], reverse=True)[:3]
    print("Top 3 countries (loop-built dict):")
    for rank, (country, value) in enumerate(top3, start=1):
        print(f"  {rank}. {country:<20} GBP {value:,.2f}")

    # List comprehensions ---------------------------------------------------
    big_orders = [inv for inv, total in
                  df.groupby("InvoiceNo")["line_total"].sum().items() if total > 500]
    print(f"\nInvoices over GBP 500 (list comprehension): {len(big_orders)}")

    prices = df["UnitPrice"].tolist()
    rounded = [round(p, 1) for p in prices if p > 0]        # comprehension + filter
    print(f"Unit prices rounded to 1 dp: {len(rounded):,} values, "
          f"first five {rounded[:5]}")

    # Set + tuple usage -----------------------------------------------------
    countries = {c for c in df["Country"]}                   # set comprehension
    print(f"Distinct countries (set): {len(countries)}")

    record = ("United Kingdom", 500)                         # tuple
    print(f"Tuple example: {record}")


# ---------------------------------------------------------------------------
# Exercise 3 - NumPy arrays
# ---------------------------------------------------------------------------
def exercise_3_numpy(df):
    banner("EXERCISE 3  NumPy arrays and vectorised analytics")

    revenue = df["line_total"].to_numpy(dtype=float)
    qty = df["Quantity"].to_numpy(dtype=float)

    print(f"revenue array : shape={revenue.shape}, dtype={revenue.dtype}")
    print(f"  sum      = {revenue.sum():,.2f}")
    print(f"  mean     = {revenue.mean():,.2f}")
    print(f"  median   = {np.median(revenue):,.2f}")
    print(f"  std      = {revenue.std(ddof=1):,.2f}")
    print(f"  min/max  = {revenue.min():,.2f} / {revenue.max():,.2f}")

    q1, q3 = np.percentile(revenue, [25, 75])
    iqr = q3 - q1
    print(f"  Q1={q1:,.2f}  Q3={q3:,.2f}  IQR={iqr:,.2f}")

    # Vectorised filter - no Python loop
    big = revenue[revenue > q3 + 1.5 * iqr]
    print(f"\nOutliers above upper fence: {len(big):,} lines, "
          f"value GBP {big.sum():,.2f} ({big.sum() / revenue.sum() * 100:.1f}% of revenue)")

    # Broadcasting
    print(f"\nQuantity array: total units = {int(qty.sum()):,}")
    print(f"Revenue per unit (where qty > 0): "
          f"{(revenue[qty > 0] / qty[qty > 0]).mean():,.2f}")

    # Correlation with NumPy
    corr = np.corrcoef(df["Quantity"], df["UnitPrice"])[0, 1]
    print(f"NumPy correlation(Quantity, UnitPrice) = {corr:+.4f}")


# ---------------------------------------------------------------------------
# Exercise 4 - Data cleaning
# ---------------------------------------------------------------------------
def exercise_4_cleaning(df):
    banner("EXERCISE 4  Data cleaning and quality checks")

    print(f"rows before            : {len(df):,}")
    print(f"duplicate rows         : {df.duplicated().sum():,}")
    print(f"missing CustomerID     : {df['CustomerID'].isna().sum():,}")

    work = df.copy()
    work = work.drop_duplicates()

    # Standardise text casing
    work["Country"] = work["Country"].str.strip().str.title()
    work["Description"] = work["Description"].str.strip().str.upper()

    # Range checks
    bad_qty = int((work["Quantity"] <= 0).sum())
    bad_price = int((work["UnitPrice"] <= 0).sum())
    print(f"non-positive Quantity  : {bad_qty:,}")
    print(f"non-positive UnitPrice : {bad_price:,}")

    # IQR outlier flag on unit price (flag, do not delete)
    q1, q3 = work["UnitPrice"].quantile([0.25, 0.75])
    fence = q3 + 1.5 * (q3 - q1)
    work["price_outlier"] = work["UnitPrice"] > fence
    print(f"price outlier fence    : GBP {fence:,.2f} -> {work['price_outlier'].sum():,} flagged")

    work["revenue"] = (work["Quantity"] * work["UnitPrice"]).round(2)
    print(f"rows after             : {len(work):,}")
    return work


# ---------------------------------------------------------------------------
# Exercise 5 - Transformation and aggregation
# ---------------------------------------------------------------------------
def exercise_5_aggregation(work):
    banner("EXERCISE 5  Transformation and aggregation with pandas")

    work = work.copy()
    work["month"] = work["InvoiceDate"].dt.to_period("M").astype(str)

    monthly = (work.groupby("month")
               .agg(lines=("line_total", "size"),
                    revenue=("revenue", "sum"),
                    units=("Quantity", "sum"),
                    invoices=("InvoiceNo", "nunique"))
               .round(2)
               .sort_index())
    print("Monthly summary:")
    print(monthly.to_string())

    customer = (work.dropna(subset=["CustomerID"])
                .groupby("CustomerID")
                .agg(orders=("InvoiceNo", "nunique"),
                     revenue=("revenue", "sum"),
                     country=("Country", "first"))
                .sort_values("revenue", ascending=False))
    print(f"\nTop 5 customers by revenue:")
    print(customer.head(5).to_string())

    total = customer["revenue"].sum()
    top20 = int(len(customer) * 0.2)
    share = customer["revenue"].head(top20).sum() / total * 100
    print(f"\nTop 20% of customers ({top20}) = {share:.1f}% of registered revenue")
    return monthly, customer


# ---------------------------------------------------------------------------
# Exercise 6 - Reusable functions and writing results
# ---------------------------------------------------------------------------
def summarise_country(frame, column="revenue"):
    """Return per-country totals for a numeric column."""
    if column not in frame.columns:
        raise KeyError(f"column '{column}' not found")
    return (frame.groupby("Country")[column]
            .agg(["count", "sum", "mean"])
            .sort_values("sum", ascending=False)
            .round(2))


def exercise_6_reusable(df, work):
    banner("EXERCISE 6  Reusable functions and writing analytical outputs")

    country_stats = summarise_country(work)
    print("Country summary (reusable function):")
    print(country_stats.head(5).to_string())

    outputs = {
        "country_summary.csv": country_stats.reset_index(),
        "monthly_summary.csv": summarise_monthly(work),
    }
    for name, table in outputs.items():
        path = os.path.join(OUT_DIR, name)
        table.to_csv(path, index=False)
        print(f"written: {path}")

    # JSON write + exception handling
    payload = {"generated_at": datetime.now().isoformat(timespec="seconds"),
               "rows": int(len(df)),
               "revenue": round(float(df["line_total"].sum()), 2)}
    with open(os.path.join(OUT_DIR, "exercise6_metadata.json"), "w") as handle:
        json.dump(payload, handle, indent=2)
    print(f"metadata: {payload}")

    try:
        summarise_country(work, "does_not_exist")
    except KeyError as exc:
        print(f"exception handled as expected: {exc}")


def summarise_monthly(frame):
    """Monthly revenue and order counts."""
    return (frame.assign(month=frame["InvoiceDate"].dt.to_period("M").astype(str))
            .groupby("month")["revenue"].agg(["size", "sum"]).round(2))


def main():
    print("LAB 1 - PYTHON FOR DATA ANALYTICS")
    print(f"dataset: {DATA_PATH}")
    df = exercise_1_load_and_profile()
    exercise_2_structures(df)
    exercise_3_numpy(df)
    work = exercise_4_cleaning(df)
    exercise_5_aggregation(work)
    exercise_6_reusable(df, work)
    print(f"\n{LINE}\nLAB 1 COMPLETE - evidence written to {OUT_DIR}\n{LINE}")


if __name__ == "__main__":
    main()
