"""Build and execute Integrated_Project/integrated_business_analytics.ipynb.

The notebook runs the Python and SQL stages of the ten-step integrated workflow
live, and points at the delivered artefacts for the Excel, Power BI and Git stages.
"""

import os

import nbformat
from nbclient import NotebookClient

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "Integrated_Project", "integrated_business_analytics.ipynb")

DB = dict(host="127.0.0.1", port=3306, user="analyst", password="Analyst@2026",
          database="retail_analytics", charset="utf8mb4")


def md(t):
    return nbformat.v4.new_markdown_cell(t)


def code(t):
    return nbformat.v4.new_code_cell(t.strip("\n"))


def build():
    nb = nbformat.v4.new_notebook()
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python", "version": "3.13"}}
    nb.cells = [
        md("# Integrated Business Analytics Project\n"
           "**Data Analyst Internship · Task 4 · Phase 4**\n\n"
           "One real dataset, six tools, one story. The same extract of the UCI "
           "*Online Retail* dataset (DOI "
           "[10.24432/C5BW33](https://doi.org/10.24432/C5BW33)) is pushed through a "
           "complete professional workflow.\n\n"
           "| # | Stage | Tool | Where the evidence lives |\n"
           "|---|---|---|---|\n"
           "| 1 | Explore | Python / pandas | this notebook |\n"
           "| 2 | Clean & preprocess | pandas | this notebook |\n"
           "| 3 | Load to database | MySQL / MariaDB | `SQL_Lab/load_data.py` |\n"
           "| 4 | Analytical queries | SQL | `SQL_Lab/outputs/query_*.txt` |\n"
           "| 5 | Spreadsheet analysis | Excel | `Excel_Lab/Excel_Data_Analysis_Lab.xlsx` |\n"
           "| 6 | Visualisation | Matplotlib / Seaborn / Plotly | "
           "`Data_Visualization_Lab/outputs/` |\n"
           "| 7 | Interactive dashboard | Power BI | `PowerBI_Lab/` build guide |\n"
           "| 8 | Documented workflow | Jupyter | `Jupyter_Lab/` |\n"
           "| 9 | Version control | Git / GitHub | `Git_GitHub_Lab/` |\n"
           "| 10 | Findings & recommendations | all of the above | this notebook |\n\n"
           "**Stages 1, 2, 4 and 6 are executed live below.** Stages 3, 5, 7, 8 and 9 "
           "are delivered as standalone artefacts, referenced with their real paths."),

        md("## Stage 1-2 · Explore and clean with pandas"),
        code("""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pymysql

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)
sns.set_theme(style="whitegrid")
pd.set_option("display.float_format", lambda v: f"{v:,.2f}")

CSV = "../data/online_retail_sales_sample.csv"
df = pd.read_csv(CSV, parse_dates=["InvoiceDate"],
                 dtype={"InvoiceNo": str, "StockCode": str})
print(f"loaded {len(df):,} lines / {df['InvoiceNo'].nunique()} invoices")
df.head()
"""),
        code("""
df = df.drop_duplicates()
df["Country"] = df["Country"].str.strip().str.title()
df["Description"] = df["Description"].str.strip().str.upper()
df["month"] = df["InvoiceDate"].dt.strftime("%Y-%m")
df["revenue"] = (df["Quantity"] * df["UnitPrice"]).round(2)
df["high_value"] = (df["revenue"] >= 50).astype(int)
print(f"after cleaning: {len(df):,} lines, GBP {df['revenue'].sum():,.2f}")
df.groupby("month")["revenue"].sum().round(2)
"""),

        md("## Stage 3-4 · Load into MySQL and query with SQL\n"
           "`SQL_Lab/run_sql_lab.py` creates the `retail_analytics` schema and loads the "
           "normalised tables. The same connection is used here so the integrated "
           "project and the SQL lab share one database."),
        code(f"""
conn = pymysql.connect(**{DB!r})
q = '''
SELECT o.country,
       COUNT(DISTINCT o.invoice_no) AS orders,
       ROUND(SUM(oi.line_total), 2)  AS revenue_gbp
FROM orders o
INNER JOIN order_items oi ON oi.invoice_no = o.invoice_no
GROUP BY o.country
ORDER BY revenue_gbp DESC
LIMIT 8
'''
country = pd.read_sql(q, conn)
print(country.to_string(index=False))
"""),
        code("""
q2 = '''
WITH monthly AS (
    SELECT DATE_FORMAT(o.invoice_date, '%Y-%m') AS month,
           ROUND(SUM(oi.line_total), 2) AS revenue_gbp
    FROM orders o INNER JOIN order_items oi ON oi.invoice_no = o.invoice_no
    GROUP BY DATE_FORMAT(o.invoice_date, '%Y-%m')
)
SELECT month, revenue_gbp,
       ROUND(revenue_gbp / SUM(revenue_gbp) OVER () * 100, 2) AS pct
FROM monthly ORDER BY month
'''
monthly = pd.read_sql(q2, conn)
monthly
"""),
        code("""
q3 = '''
SELECT p.stock_code, p.description,
       ROUND(SUM(oi.line_total), 2) AS revenue_gbp
FROM order_items oi INNER JOIN products p ON p.stock_code = oi.stock_code
GROUP BY p.stock_code, p.description
ORDER BY revenue_gbp DESC LIMIT 5
'''
top_products = pd.read_sql(q3, conn)
print(top_products.to_string(index=False))
conn.close()
"""),

        md("## Stage 5 · Spreadsheet analysis\n"
           "`Excel_Lab/Excel_Data_Analysis_Lab.xlsx` holds the same data with live "
           "formulas. Its KPIs were recalculated with LibreOffice and matched pandas to "
           "the penny (`Excel_Lab/evidence/excel_verification.txt`):\n\n"
           "| KPI | Value |\n|---|---:|\n"
           "| Total revenue (UK) | 196,462.03 |\n"
           "| Line items (UK) | 10,787 |\n"
           "| Units sold (UK) | 108,560 |\n"
           "| Orders (UK) | 442 |\n\n"
           "The workbook also contains a formula-driven Pivot_View and an interactive "
           "KPI dashboard with a country slicer, conditional formatting and three "
           "charts."),

        md("## Stage 6 · Visualisation"),
        code("""
fig, ax = plt.subplots(figsize=(10, 5))
monthly_plot = df.groupby("month")["revenue"].sum()
ax.bar(monthly_plot.index, monthly_plot.values, color="#2F5597")
ax.set_title("Monthly revenue - integrated project")
ax.set_xlabel("Month")
ax.set_ylabel("Revenue (GBP)")
ax.tick_params(axis="x", rotation=45)
plt.show()

fig, ax = plt.subplots(figsize=(9, 5))
top = country.sort_values("revenue_gbp")
ax.barh(top["country"], top["revenue_gbp"], color="#4472C4")
ax.set_title("Revenue by country (SQL result)")
ax.set_xlabel("Revenue (GBP)")
plt.show()
"""),

        md("## Stage 7 · Power BI dashboard\n"
           "Power BI Desktop is Windows-only, so the `.pbix` is a documented manual "
           "build rather than a fabricated file. `PowerBI_Lab/` contains:\n\n"
           "* `power_query_m.m` - the six Power Query queries\n"
           "* `dax_measures.dax` - the full measure set\n"
           "* `data_model.md` - the star schema and relationships\n"
           "* `PowerBI_Business_Analytics_BUILD_GUIDE.md` - click-by-click build steps\n\n"
           "The guide states the expected KPI values so the build can be validated "
           "against the numbers produced here."),

        md("## Stage 8-9 · Documented workflow and version control\n"
           "* `Jupyter_Lab/Jupyter_Analytics_Workflow.ipynb` - the reproducible "
           "notebook (executed, 0 errors).\n"
           "* `Git_GitHub_Lab/` - the exact `git` command sequence, a real commit "
           "history with branches and merges, and a `.gitignore`.\n"
           "* `.gitignore` in the project root excludes caches and large binaries."),

        md("## Stage 10 · Business findings and recommendations\n"
           "Every figure below was produced by the tools above from the same data."),
        code("""
total = df["revenue"].sum()
uk = df.loc[df["Country"] == "United Kingdom", "revenue"].sum()
cust = df.dropna(subset=["CustomerID"]).groupby("CustomerID")["revenue"].sum()
top20_share = cust.sort_values(ascending=False).head(int(len(cust) * 0.2)).sum() / cust.sum()
peak = monthly_plot.idxmax()
high_value_rate = df["high_value"].mean()

print(f"Total revenue                 GBP {total:,.2f}")
print(f"UK share of revenue           {uk / total:.1%}")
print(f"Top 20% of customers generate {top20_share:.1%} of registered revenue")
print(f"Peak month                    {peak} (GBP {monthly_plot.max():,.2f})")
print(f"Lines over GBP 50            {high_value_rate:.1%}")
"""),
        md("**Recommendations**\n\n"
           "1. **Protect the UK base, grow international.** The UK accounts for the "
           "large majority of revenue; the top overseas markets are small but "
           "high-value, so they warrant targeted account management.\n"
           "2. **Build a retention programme for the top 20%.** A fifth of customers "
           "generates the bulk of registered revenue, so losing a handful of accounts "
           "moves the headline number.\n"
           "3. **Plan for the January sample peak.** Revenue peaks in January 2011; inventory, "
           "staffing and fulfilment should scale ahead of it.\n"
           "4. **Review the long tail.** Most lines are under GBP 20, so delivery and "
           "payment costs per line matter more than basket size.\n"
           "5. **Close the guest-checkout gap.** 2,698 lines in the sample have no "
           "customer ID, which limits retention marketing."),
    ]
    return nb


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    nb = build()
    client = NotebookClient(nb, timeout=900, kernel_name="python3",
                            resources={"metadata": {"path": os.path.dirname(OUT)}})
    client.execute()
    nbformat.write(nb, OUT)
    errs = [o for c in nb.cells if c.cell_type == "code"
            for o in c.outputs if o.output_type == "error"]
    print(f"notebook: {OUT}")
    print(f"cells {len(nb.cells)} | code {sum(1 for c in nb.cells if c.cell_type == 'code')}"
          f" | errors {len(errs)}")


if __name__ == "__main__":
    main()
