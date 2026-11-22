"""Build and execute Jupyter_Lab/Jupyter_Analytics_Workflow.ipynb."""

import os

import nbformat
from nbclient import NotebookClient

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "Jupyter_Lab", "Jupyter_Analytics_Workflow.ipynb")


def md(text):
    return nbformat.v4.new_markdown_cell(text)


def code(text):
    return nbformat.v4.new_code_cell(text.strip("\n"))


def build():
    nb = nbformat.v4.new_notebook()
    nb.metadata = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.13"},
    }
    nb.cells = [
        md("# Jupyter Analytics Workflow — Lab 7\n"
           "**Data Analyst Internship · Task 4 · Tool Mastery Project**\n\n"
           "This notebook combines the core Python analytical techniques used by a "
           "working Data Analyst: data loading, cleaning, transformation, exploratory "
           "analysis, visualisation and statistical summary — all in one reproducible "
           "document.\n\n"
           "**Dataset:** `data/online_retail_sales_sample.csv` — 12,177 real transaction "
           "lines from the UCI *Online Retail* dataset "
           "(DOI [10.24432/C5BW33](https://doi.org/10.24432/C5BW33))."),

        md("## 1. Environment and reproducibility\n"
           "The kernel, package versions and random seed are fixed up front so that "
           "every run produces identical numbers."),
        code("""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)
sns.set_theme(style="whitegrid")
pd.set_option("display.float_format", lambda v: f"{v:,.2f}")

print(f"numpy {np.__version__} | pandas {pd.__version__} | scipy {stats.__name__}")
print(f"random state = {RANDOM_STATE}")
"""),

        md("## 2. Load the data\n"
           "`pd.read_csv` with explicit dtypes and date parsing. Explicit dtypes stop "
           "pandas guessing, which matters when invoice numbers look numeric."),
        code("""
DATA = "../data/online_retail_sales_sample.csv"
raw = pd.read_csv(DATA, parse_dates=["InvoiceDate"],
                  dtype={"InvoiceNo": str, "StockCode": str})
print(f"shape : {raw.shape[0]:,} rows x {raw.shape[1]} columns")
print(f"memory: {raw.memory_usage(deep=True).sum() / 1024:.1f} KB")
raw.head()
"""),
        code("""
raw.info()
"""),
        code("""
raw.describe().T
"""),

        md("## 3. Data quality check\n"
           "Quantify problems before touching the data — missing values, duplicates, "
           "impossible ranges."),
        code("""
quality = pd.DataFrame({
    "missing": raw.isna().sum(),
    "missing_pct": (raw.isna().mean() * 100).round(2),
    "nunique": raw.nunique(),
})
print(quality)
print(f"\\nduplicate rows: {raw.duplicated().sum():,}")
print(f"non-positive quantity: {(raw['Quantity'] <= 0).sum():,}")
print(f"non-positive unit price: {(raw['UnitPrice'] <= 0).sum():,}")
"""),

        md("## 4. Clean and transform\n"
           "Rule: **flag, don't delete** — rows with business meaning are kept and "
           "marked, so no information is silently lost."),
        code("""
df = raw.copy()
df = df.drop_duplicates()
df["Country"] = df["Country"].str.strip().str.title()
df["Description"] = df["Description"].str.strip().str.upper()
df["month"] = df["InvoiceDate"].dt.strftime("%Y-%m")
df["revenue"] = (df["Quantity"] * df["UnitPrice"]).round(2)
df["value_band"] = pd.cut(df["revenue"], bins=[-np.inf, 50, 200, np.inf],
                          labels=["Small", "Medium", "Large"])

q1, q3 = df["UnitPrice"].quantile([0.25, 0.75])
fence = q3 + 1.5 * (q3 - q1)
df["price_outlier"] = df["UnitPrice"] > fence

print(f"rows after cleaning: {len(df):,}")
print(f"price outlier fence: GBP {fence:,.2f} -> {df['price_outlier'].sum():,} flagged")
df.head()
"""),

        md("## 5. Exploratory analysis with pandas and NumPy\n"
           "Monthly trend, country mix and customer concentration."),
        code("""
monthly = (df.groupby("month")
           .agg(lines=("revenue", "size"), revenue=("revenue", "sum"),
                units=("Quantity", "sum"), invoices=("InvoiceNo", "nunique"))
           .round(2))
monthly
"""),
        code("""
country = (df.groupby("Country")
           .agg(lines=("revenue", "size"), revenue=("revenue", "sum"),
                invoices=("InvoiceNo", "nunique"))
           .sort_values("revenue", ascending=False))
country["share"] = (country["revenue"] / country["revenue"].sum() * 100).round(2)
country.head(10)
"""),
        code("""
revenue = df["revenue"].to_numpy()
print(f"revenue  mean {revenue.mean():,.2f} | median {np.median(revenue):,.2f} | "
      f"std {revenue.std(ddof=1):,.2f}")
print(f"quartiles {np.percentile(revenue, [25, 50, 75]).round(2)}")
print(f"skewness {stats.skew(revenue):,.2f}")
"""),

        md("## 6. Customer concentration (Pareto)\n"
           "How much of the revenue comes from the top slice of customers?"),
        code("""
cust = (df.dropna(subset=["CustomerID"])
        .groupby("CustomerID")["revenue"].sum().sort_values(ascending=False))
top20_n = int(len(cust) * 0.2)
share = cust.head(top20_n).sum() / cust.sum() * 100
print(f"registered customers : {len(cust):,}")
print(f"top 20% ({top20_n}) share of revenue: {share:.1f}%")
"""),

        md("## 7. Visualisation\n"
           "Publication-ready figures with labelled axes, units and titles."),
        code("""
fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(monthly.index, monthly["revenue"], color="#2F5597")
ax.set_title("Monthly revenue")
ax.set_xlabel("Month")
ax.set_ylabel("Revenue (GBP)")
ax.tick_params(axis="x", rotation=45)
plt.show()
"""),
        code("""
fig, ax = plt.subplots(figsize=(9, 5))
top = country.head(10)["revenue"].sort_values()
ax.barh(top.index, top.values, color="#4472C4")
ax.set_title("Revenue by country (top 10)")
ax.set_xlabel("Revenue (GBP)")
plt.show()
"""),
        code("""
fig, ax = plt.subplots(figsize=(9, 5))
sns.histplot(df.loc[df["UnitPrice"] <= 50, "UnitPrice"], bins=50, ax=ax,
             color="#8FAADC")
ax.set_title("Unit price distribution (truncated at GBP 50)")
ax.set_xlabel("Unit price (GBP)")
plt.show()
"""),
        code("""
corr = df[["Quantity", "UnitPrice", "revenue"]].corr(method="spearman")
fig, ax = plt.subplots(figsize=(7, 5))
sns.heatmap(corr, annot=True, fmt=".3f", cmap="RdBu_r", center=0, ax=ax)
ax.set_title("Spearman correlation")
plt.show()
"""),

        md("## 8. Statistical summary\n"
           "A Welch t-test comparing UK and overseas line values, with the assumptions "
           "stated."),
        code("""
uk = df.loc[df["Country"] == "United Kingdom", "revenue"]
os_ = df.loc[df["Country"] != "United Kingdom", "revenue"]
t_stat, p = stats.ttest_ind(uk, os_, equal_var=False)
print(f"UK       n={len(uk):,}  mean {uk.mean():,.2f}")
print(f"Overseas n={len(os_):,}  mean {os_.mean():,.2f}")
print(f"Welch t = {t_stat:.3f}, p = {p:.3e}")
print("Decision:", "reject H0" if p < 0.05 else "do not reject H0")
"""),

        md("## 9. Export the results\n"
           "Writing analysis outputs to disk so other tools (SQL, Excel, Power BI) can "
           "consume them."),
        code("""
os.makedirs("../Jupyter_Lab/outputs", exist_ok=True)
monthly.to_csv("../Jupyter_Lab/outputs/monthly_summary.csv")
country.to_csv("../Jupyter_Lab/outputs/country_summary.csv")
print("written: outputs/monthly_summary.csv, outputs/country_summary.csv")
"""),

        md("## 10. Reproducibility checklist\n"
           "- [x] Random seed fixed (`RANDOM_STATE = 42`)\n"
           "- [x] Package versions printed\n"
           "- [x] Relative paths only\n"
           "- [x] No hard-coded results — every figure is computed above\n"
           "- [x] Outputs written to `outputs/`\n\n"
           "**Exporting:** `File → Download as → Notebook (.ipynb)` or "
           "`jupyter nbconvert --to html`."),
    ]
    return nb


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    nb = build()
    client = NotebookClient(nb, timeout=600, kernel_name="python3",
                            resources={"metadata": {"path": os.path.dirname(OUT)}})
    client.execute()
    nbformat.write(nb, OUT)
    errs = [o for c in nb.cells if c.cell_type == "code"
            for o in c.outputs if o.output_type == "error"]
    print(f"notebook written: {OUT}")
    print(f"cells: {len(nb.cells)} | code cells: "
          f"{sum(1 for c in nb.cells if c.cell_type == 'code')} | errors: {len(errs)}")


if __name__ == "__main__":
    main()
