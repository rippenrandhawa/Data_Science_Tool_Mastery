# Practical Skills Assessment — Answer Key

Use this key only after completing the assessment. Equivalent correct implementations
are acceptable. Numerical answers must match the supplied dataset within rounding.

## A — Python

**A1.**
```python
import pandas as pd
df = pd.read_csv("data/online_retail_sales_sample.csv",
                 dtype={"InvoiceNo": str, "StockCode": str},
                 parse_dates=["InvoiceDate"])
print(df.shape)                 # (12177, 9)
print(df.dtypes)
print(df.isna().sum())
```
**A2.**
```python
totals = df.groupby("InvoiceNo")["line_total"].sum()
large = [invoice for invoice, value in totals.items() if value > 500]
# 121 invoices
```
**A3.** `shape` is `(rows, columns)`; `len(df)` is rows; `count()` counts non-null
values by column; `size` is total cells (`rows * columns`).

**A4.**
```python
def summarise_country(df, country):
    """Return revenue, lines and distinct invoices for one country."""
    if country not in set(df["Country"]):
        raise ValueError(f"Unknown country: {country}")
    part = df[df["Country"] == country]
    return {"revenue": part["line_total"].sum(), "lines": len(part),
            "invoices": part["InvoiceNo"].nunique()}
```
**A5.**
```python
print(df.duplicated().sum())
print((df["Quantity"] <= 0).sum())
print((df["UnitPrice"] <= 0).sum())
```
**A6.**
```python
monthly = df.groupby(df["InvoiceDate"].dt.to_period("M"))["line_total"].sum()
out = monthly.to_frame("revenue")
out["pct_change"] = out["revenue"].pct_change().mul(100)
```
**A7.**
```python
import numpy as np
x = df["line_total"].to_numpy()
print(np.mean(x), np.median(x), np.std(x, ddof=1),
      np.percentile(x, [25, 50, 75]))
```
**A8.**
```python
def price_outliers(frame):
    """Return rows above the upper 1.5-IQR fence and the fence."""
    q1, q3 = frame["UnitPrice"].quantile([.25, .75])
    fence = q3 + 1.5 * (q3 - q1)
    return frame[frame["UnitPrice"] > fence].copy(), fence
```
**A9.**
```python
x = pd.read_excel("Python_Lab/evidence/exercise1_sample_subset.xlsx")
top = x.groupby("Country")["line_total"].sum().nlargest(10).index
with pd.ExcelWriter("top_countries.xlsx") as writer:
    for country in top:
        x[x["Country"] == country].to_excel(
            writer, sheet_name=country[:31], index=False)
```
**A10.** A correct solution has a pure cleaning function, `argparse.ArgumentParser`,
a `--country` option, and `if __name__ == "__main__": main()`.

## B — SQL

**B1.**
```sql
SELECT o.invoice_no, o.invoice_date, o.country
FROM orders o ORDER BY o.invoice_date DESC LIMIT 10;
```
**B2.**
```sql
SELECT ROUND(SUM(line_total),2) AS revenue, COUNT(*) AS line_items
FROM order_items;
```
**B3.**
```sql
SELECT o.country, ROUND(SUM(i.line_total),2) revenue
FROM orders o JOIN order_items i ON i.invoice_no=o.invoice_no
GROUP BY o.country ORDER BY revenue DESC;
```
**B4.**
```sql
SELECT country, COUNT(DISTINCT invoice_no) invoices
FROM orders GROUP BY country;
```
**B5.** Add `HAVING SUM(i.line_total) > 5000` to B3.

**B6.**
```sql
SELECT c.customer_id
FROM customers c LEFT JOIN orders o ON o.customer_id=c.customer_id
WHERE o.invoice_no IS NULL;
```
**B7.**
```sql
WITH product_sales AS (
 SELECT p.stock_code,p.description,SUM(i.line_total) revenue
 FROM products p JOIN order_items i ON i.stock_code=p.stock_code
 GROUP BY p.stock_code,p.description)
SELECT * FROM product_sales ORDER BY revenue DESC LIMIT 5;
```
**B8.**
```sql
SELECT DATE_FORMAT(o.invoice_date,'%Y-%m') month,
       SUM(i.line_total)/COUNT(DISTINCT o.invoice_no) avg_order_value
FROM orders o JOIN order_items i ON i.invoice_no=o.invoice_no
GROUP BY month ORDER BY month;
```
**B9.**
```sql
WITH spend AS (SELECT customer_id,SUM(order_total) total
 FROM orders GROUP BY customer_id)
SELECT * FROM spend WHERE total>(SELECT AVG(total) FROM spend);
```
**B10.** Aggregate order totals first, then group a `CASE WHEN total < 50 THEN
'Small' WHEN total <= 200 THEN 'Medium' ELSE 'Large' END` expression.

**B11.**
```sql
WITH sales AS (
 SELECT o.country,p.stock_code,p.description,SUM(i.line_total) revenue
 FROM orders o JOIN order_items i ON i.invoice_no=o.invoice_no
 JOIN products p ON p.stock_code=i.stock_code
 GROUP BY o.country,p.stock_code,p.description),
ranked AS (SELECT sales.*,RANK() OVER(PARTITION BY country ORDER BY revenue DESC) r
 FROM sales)
SELECT * FROM ranked WHERE r=1;
```
**B12.** Aggregate monthly revenue in a CTE, then use
`SUM(revenue) OVER(ORDER BY month)` and `revenue/SUM(revenue) OVER()`.

**B13.** Aggregate customer revenue, assign `NTILE(5) OVER(ORDER BY revenue DESC)`,
filter tile 1, and divide its sum by the unfiltered total.

**B14.** Aggregate by month, then select `LAG(revenue) OVER(ORDER BY month)`.

**B15.** Use B11 with `SUM(i.quantity)`, filter `o.country <> 'United Kingdom'`,
and keep rank 1.

## C — Excel

**C1.** `=SUMIFS(Raw_Data!$I:$I,Raw_Data!$H:$H,"United Kingdom")` → **196,462.03**.

**C2.** `=COUNTIFS(Raw_Data!$H:$H,"United Kingdom",Raw_Data!$A:$A,"<>")` → **10,787**.

**C3.** `=IFERROR(IF(I2>=200,"High",IF(I2>=50,"Medium","Low")),"Error")`.

**C4.** `=INDEX(Raw_Data!$C:$C,MATCH("85123A",Raw_Data!$B:$B,0))` →
**WHITE HANGING HEART T-LIGHT HOLDER**.

**C5.** `=XLOOKUP("10135",Raw_Data!$B:$B,Raw_Data!$F:$F,"Not found",0)` → **1.25**.

**C6.** `=TEXT(EOMONTH(Raw_Data!D2,0),"dd mmm yyyy")` → **31 Dec 2010**.

**C7.** `=AVERAGEIF(Raw_Data!$H:$H,"France",Raw_Data!$I:$I)` → about **18.19**.

**C8.** In Microsoft 365:
`=COUNTA(UNIQUE(FILTER(Raw_Data!$A$2:$A$12178,Raw_Data!$H$2:$H$12178="United Kingdom")))`
→ **442**. A correctly guarded `SUMPRODUCT/COUNTIFS` equivalent is accepted.

**C9.** Data Validation → List → country-name range; all dashboard formulas must use
`$C$6` as their criterion.

**C10.** Use formula rules such as `=C8>AVERAGE($C$8:$C$16)` (green) and the
corresponding `<` rule (red), adjusted to the KPI range.

## D — Data Visualisation

**D1–D5.** Reference implementations are in
`Data_Visualization_Lab/visualization_lab.py`. Full credit requires: correct grouping,
units, informative title, saved output at 200 DPI (D1–D4), and a functioning standalone
Plotly HTML with an x-axis range slider (D5). D2 must mention strong right skew and why
the median is more representative; D4 must use Spearman for these heavy-tailed data.

## E — Statistics

**E1.** Mean **19.6799**, median **10.50**, mode **15.00**, sample standard deviation
**70.8349**, IQR **13.72**. Report median and IQR because skewness is **35.1179**.

**E2.** Only **97.14%** (not 68.27%) lies within one standard deviation; formal tests
reject normality (p approximately zero). Conclusion: not normally distributed.

**E3.** A t-based 95% CI is **GBP 18.42 to GBP 20.94**. Interpretation: under the
sampling assumptions, repeated intervals constructed this way would contain the
population mean 95% of the time.

**E4.** `H0: mu_UK = mu_overseas`; `H1: mu_UK != mu_overseas`. Welch
`t = -7.5911`, `p = 4.8347e-14`; reject H0. The effect is moderate. This observational
comparison does not prove location caused the difference.

**E5.** The periods were not randomised, so seasonality and customer mix confound the
comparison. A proper test needs random assignment, a contemporaneous control, a
pre-specified outcome, sample-size/power planning and a fixed analysis window.

## F — Power BI

**F1.** A calculated column is evaluated per row and stored; a measure is evaluated at
query time in filter context. Example column: `Line Total = Quantity * UnitPrice`;
measure: `Total Revenue = SUM(fact_order_items[line_total])`.

**F2.**
```dax
Total Revenue = SUM(fact_order_items[line_total])
Average Order Value = DIVIDE([Total Revenue], [Total Orders])
```
**F3.**
```dax
Revenue % of Total =
DIVIDE([Total Revenue], CALCULATE([Total Revenue], ALL(dim_customer)))
```
`ALL` removes the current customer filter to provide the denominator.

**F4.** A correct answer builds a `TOPN(10, ALL(dim_product), [Total Revenue], DESC)`
table, calculates revenue over it, then divides by `[Total Revenue]`.

**F5.** A star schema gives clear one-to-many filter paths, smaller dimensions and
predictable measures. Uncontrolled many-to-many relationships create ambiguous filter
paths and can double-count facts.

## G — Git / GitHub

**G1.** Working tree = current files; staging area = next commit's snapshot;
repository = committed history.

**G2.** `git init`, `git add .`, `git status`,
`git commit -m "Initial commit: project structure"`.

**G3.** `git checkout -b feature/name`; edit; `git add .`; `git commit -m "Add …"`;
`git checkout main`; `git merge --no-ff feature/name`.

**G4.** Keep changes: `git reset --soft HEAD~1`. Discard one file:
`git restore <file>` (or legacy `git checkout -- <file>`).

**G5.** Checkpoints are generated noise; `.env` holds secrets. Remove the secret from
history, rotate/revoke the credential immediately, add it to `.gitignore`, and use a
secret manager or environment variable.

## H — Introductory Machine Learning

**H1.** Leakage occurs when information from validation/test data influences fitting.
A pipeline fits scaling/encoding on each training fold only, then applies it to held-out
data.

**H2.** With 7.4% positives, always predicting negative scores **92.57%** accuracy but
has zero recall. Use precision, recall, F1 and ROC/PR curves.

**H3.** From `[[2171,23],[92,84]]`: precision = `84/(84+23) = 0.7850`; recall =
`84/(84+92) = 0.4773`. Precision asks how many predicted positives were correct;
recall asks how many real positives were found.

**H4.** Training accuracy approaches 1.0 as depth grows while test accuracy stops
improving; the train–test gap signals memorisation/overfitting.

**H5.** Five-fold CV rotates the validation fold, uses every row for both training and
validation, and reduces dependence on one lucky split. Report mean and standard
deviation.
