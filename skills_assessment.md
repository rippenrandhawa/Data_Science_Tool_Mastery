# Practical Skills Assessment — Data Science Tool Mastery

**Instructions.** Answer by producing working code, queries or workbook steps, not by
describing them. Each question lists a difficulty, the expected outcome and the
evaluation criteria. The answer key is in `answer_key.md`.

**Scoring.** Each question is worth 2 marks: 1 for a correct, runnable answer and 1
for a correct explanation of the result. A skill is considered **demonstrated** at
80% or above on its section, and only when the answer was produced without reference
to the key.

---

## Section A — Python (10 questions)

| # | Difficulty | Question | Expected outcome | Evaluation criteria |
|---|---|---|---|---|
| A1 | Beginner | Load `data/online_retail_sales_sample.csv` with pandas and print the shape, dtypes and number of missing values per column. | A script that prints `12,177 x 9`, the dtype table and the missing-value counts. | Correct dtype handling for `InvoiceNo`; missing values reported per column. |
| A2 | Beginner | Write a list comprehension that returns all invoices whose total revenue exceeds GBP 500. | A comprehension over a grouped DataFrame. | Uses `groupby` + `sum`, not a loop over rows. |
| A3 | Beginner | Explain the difference between `df.shape` and `len(df)`, and between `df.count()` and `df.size`. | Four correct definitions with a small example. | All four distinguished correctly. |
| A4 | Intermediate | Write a function `summarise_country(df, country)` that returns revenue, line count and distinct invoices for one country, and raises `ValueError` for an unknown country. | A documented function with exception handling. | Correct aggregation; `nunique` used; exception raised and caught. |
| A5 | Intermediate | Detect duplicate rows and rows with non-positive quantity or unit price, and report the counts. | Counts for each condition. | Uses `duplicated()` and boolean masks; no rows deleted silently. |
| A6 | Intermediate | Compute the monthly revenue series and the month-on-month percentage change. | A 13-row table with a `pct_change` column. | Correct date truncation; `pct_change` used; first row handled. |
| A7 | Intermediate | Use NumPy to compute the mean, median, standard deviation and the 25th/50th/75th percentiles of `line_total`. | Four statistics plus three percentiles. | Vectorised; `ddof=1` for sample std; percentiles correct. |
| A8 | Advanced | Write a reusable function that flags price outliers using the IQR fence and returns the flagged rows plus the fence value. | A function returning `(flagged_df, fence)`. | Correct fence formula; returns both outputs; documented. |
| A9 | Advanced | Read the Excel file `Python_Lab/evidence/exercise1_sample_subset.xlsx` and write the top 10 countries by revenue to a new Excel file with one sheet per country. | A workbook with one sheet per country. | Uses `ExcelWriter` with `sheet_name`; values match the source. |
| A10 | Advanced | Refactor Exercise 5 of Lab 1 so the cleaning logic is a function, and add a `main()` guard and a `--country` command-line argument. | A script that runs with an argument and without. | `argparse` used; `if __name__ == "__main__"` present; no side effects on import. |

## Section B — SQL (15 questions)

| # | Difficulty | Question | Expected outcome | Evaluation criteria |
|---|---|---|---|---|
| B1 | Beginner | Write a query that lists the 10 most recent invoices with their country. | 10 rows ordered by date descending. | `ORDER BY` + `LIMIT`; correct join. |
| B2 | Beginner | Write a query that returns the total revenue and the number of line items. | One row with two aggregates. | `SUM` and `COUNT` used correctly. |
| B3 | Beginner | Write a query that returns revenue by country, ordered descending. | One row per country. | `GROUP BY` with the correct column. |
| B4 | Beginner | Write a query that returns the number of distinct invoices per country. | One row per country. | `COUNT(DISTINCT …)`, not `COUNT(*)`. |
| B5 | Intermediate | Write a query that returns countries whose total revenue exceeds GBP 5,000. | Filtered country list. | `HAVING` used, not `WHERE`. |
| B6 | Intermediate | Write a query that returns customers who have never placed an order in the sample. | Customer list with no orders. | `LEFT JOIN` + `IS NULL`. |
| B7 | Intermediate | Write a query that returns the top 5 products by revenue using a CTE. | 5 rows with product and revenue. | CTE used; `ORDER BY` + `LIMIT`. |
| B8 | Intermediate | Write a query that returns the average order value per month. | 13 rows. | Correct month truncation and division. |
| B9 | Intermediate | Write a query that returns customers whose total spend is above the overall average customer spend. | Customer list. | Subquery in `WHERE` or `HAVING`. |
| B10 | Intermediate | Write a query that classifies each order as Small (< 50), Medium (50–200) or Large (> 200) and counts orders and revenue per band. | Three rows. | `CASE` expression correct; bands exhaustive. |
| B11 | Advanced | Write a query that ranks products within each country by revenue and returns the top product per country. | One row per country. | `RANK()` or `ROW_NUMBER()` window function. |
| B12 | Advanced | Write a query that returns the cumulative revenue by month and the percentage of the total. | 13 rows with a running total and a percentage. | Window `SUM() OVER (ORDER BY …)`. |
| B13 | Advanced | Write a query that returns the top 20% of customers by revenue and their share of total revenue. | Customer list plus a share figure. | Uses a CTE and a percentile or `LIMIT` with `COUNT`. |
| B14 | Advanced | Write a query that returns, for each month, the revenue and the revenue of the previous month. | 13 rows with two revenue columns. | `LAG()` window function. |
| B15 | Advanced | Write a query that returns the best-selling product in each country by quantity, excluding the United Kingdom. | One row per non-UK country. | Window function + `WHERE` filter. |

## Section C — Excel (10 questions)

| # | Difficulty | Question | Expected outcome | Evaluation criteria |
|---|---|---|---|---|
| C1 | Beginner | Using `SUMIFS`, compute the total revenue for the United Kingdom from `Raw_Data`. | `196,462.03`. | Correct criteria range and sum range. |
| C2 | Beginner | Using `COUNTIFS`, count the line items for the United Kingdom. | `10,787`. | Two criteria used correctly. |
| C3 | Beginner | Use `IF` and `IFERROR` to return "High" if a line total is at least 200, "Medium" if at least 50, otherwise "Low", and handle errors. | A formula that returns the three labels. | Nested `IF` correct; `IFERROR` wraps the result. |
| C4 | Intermediate | Use `INDEX` and `MATCH` to return the description of the product with stock code `85123A`. | "WHITE HANGING HEART T-LIGHT HOLDER". | Exact match (`0`); ranges locked with `$`. |
| C5 | Intermediate | Use `XLOOKUP` to return the unit price of stock code `10135`. | `1.25`. | Correct lookup and return arrays. |
| C6 | Intermediate | Use `TEXT` and `EOMONTH` to return the last day of the month of the first invoice date, formatted as "31 Dec 2010". | `31 Dec 2010`. | Correct format string. |
| C7 | Intermediate | Use `AVERAGEIF` to compute the average line total for France. | A single value. | Correct criteria and average range. |
| C8 | Advanced | Build a formula that counts distinct invoices for a country without a helper column. | A `SUMPRODUCT` / `COUNTIFS` array formula. | Correct array logic; returns 442 for the UK. |
| C9 | Advanced | Create a data validation dropdown of country names in cell `C6` of `KPI_Dashboard` and explain what happens when it changes. | A working dropdown; all KPIs recalculate. | List source correct; formulas reference `C6`. |
| C10 | Advanced | Apply conditional formatting so that KPI cells turn green when the value is above the overall average and red below it. | Colour-coded KPI cards. | Rule uses a formula, not a fixed value. |

## Section D — Data Visualisation (5 questions)

| # | Difficulty | Question | Expected outcome | Evaluation criteria |
|---|---|---|---|---|
| D1 | Beginner | Produce a bar chart of revenue by country with labelled axes, units and a title that states the message. | A chart saved at 200 DPI. | Axis labels and units present; title is a message, not a topic. |
| D2 | Beginner | Produce a histogram of unit price and explain why the mean is a poor summary. | A histogram plus a two-sentence explanation. | Mentions right skew and the median. |
| D3 | Intermediate | Produce a box plot of invoice value for the top 5 countries and interpret the difference in spread. | A box plot plus an interpretation. | Correct grouping; mentions wholesale vs retail mix. |
| D4 | Intermediate | Produce a correlation heatmap and state which pairs are correlated and which are not. | A heatmap with annotations. | Uses Spearman; interpretation matches the values. |
| D5 | Advanced | Build an interactive Plotly chart with a range slider and explain what interactivity adds for a stakeholder. | An HTML file that loads in a browser. | Slider works; explanation references exploration, not decoration. |

## Section E — Statistics (5 questions)

| # | Difficulty | Question | Expected outcome | Evaluation criteria |
|---|---|---|---|---|
| E1 | Beginner | Compute the mean, median, mode, standard deviation and IQR of `line_total`, and state which summary you would report and why. | Five statistics plus a justified choice. | Chooses the median; cites skewness. |
| E2 | Intermediate | Test whether the line values are normally distributed using the empirical rule and a formal test, and report the conclusion. | Observed vs expected percentages and a test result. | Correctly concludes non-normality. |
| E3 | Intermediate | Compute a 95% confidence interval for the mean line value and interpret it in one sentence. | An interval and an interpretation. | Uses the standard error; interpretation is about the population mean. |
| E4 | Advanced | Run a Welch t-test comparing UK and overseas line values, state the hypotheses, the result and the effect size, and state what the test does **not** prove. | Test output plus a limitation statement. | Correct test choice; mentions association, not causation. |
| E5 | Advanced | Explain why the comparison of two time periods in Lab 5 Exercise 10 is not a true A/B test, and describe what a proper A/B test would require. | A written answer. | Mentions randomisation, a control group and pre-registration. |

## Section F — Power BI (5 questions)

| # | Difficulty | Question | Expected outcome | Evaluation criteria |
|---|---|---|---|---|
| F1 | Beginner | What is the difference between a calculated column and a measure? Give an example of each. | Two correct definitions with examples. | Column = row-level, stored; measure = aggregated, evaluated in context. |
| F2 | Beginner | Write a DAX measure for Total Revenue and one for Average Order Value. | Two measures. | `SUM` and `DIVIDE` used correctly. |
| F3 | Intermediate | Write a DAX measure for Revenue % of Total and explain why `ALL()` is needed. | A measure plus an explanation. | `ALL(dim_customer)` used; explanation correct. |
| F4 | Intermediate | Write a DAX measure that returns the share of revenue from the top 10 products. | A measure using `TOPN` and `CALCULATE`. | Correct filter context handling. |
| F5 | Advanced | Explain why a star schema is preferred to a single wide table, and what happens if you create a many-to-many relationship. | A written answer. | Mentions performance, correctness and double counting. |

## Section G — Git / GitHub (5 questions)

| # | Difficulty | Question | Expected outcome | Evaluation criteria |
|---|---|---|---|---|
| G1 | Beginner | What is the difference between the working tree, the staging area and the repository? | Three correct definitions. | All three distinguished. |
| G2 | Beginner | Write the commands to initialise a repository, stage all files and make a first commit. | Four correct commands. | Correct order; commit message present. |
| G3 | Intermediate | Write the commands to create a branch, make a commit on it, switch back to `main` and merge it. | Six correct commands. | Branch created before the commit; merge after switching back. |
| G4 | Intermediate | How do you undo the last commit but keep the changes? How do you discard local changes to a file? | `git reset --soft HEAD~1` and `git checkout -- <file>`. | Both correct. |
| G5 | Advanced | Explain why `.ipynb_checkpoints/` and `.env` must be in `.gitignore`, and what to do if a secret has already been committed. | A written answer. | Mentions noise, secret leakage and key rotation. |

## Section H — Introductory Machine Learning (5 questions)

| # | Difficulty | Question | Expected outcome | Evaluation criteria |
|---|---|---|---|---|
| H1 | Beginner | What is data leakage, and how does a scikit-learn `Pipeline` prevent it? | A definition plus an explanation. | Mentions fitting the scaler on training data only. |
| H2 | Beginner | Why is accuracy a poor metric when only 7% of rows are positive? | An explanation with the baseline figure. | Cites the 92.6% majority-class baseline. |
| H3 | Intermediate | Using the confusion matrix from Lab 9, compute precision and recall and explain each in plain language. | Two numbers and two explanations. | Correct arithmetic; plain-language meaning. |
| H4 | Intermediate | How do you detect overfitting from the decision-tree depth table in Lab 9? | An explanation referencing the train/test gap. | Correctly identifies the widening gap. |
| H5 | Advanced | Why is 5-fold cross-validation a better estimate than a single train/test split? | An explanation. | Mentions variance and the use of all data. |

---

## Skills matrix

| Tool | Beginner | Intermediate | Advanced exercise | Evidence produced |
|---|---|---|---|---|
| Python | Load and profile a CSV (A1) | Cleaning and aggregation (A5, A6) | Reusable functions, CLI arguments (A8, A10) | `Python_Lab/evidence/` |
| SQL | `SELECT`, `WHERE`, `GROUP BY` (B1–B4) | Joins, CTEs, `CASE` (B5–B10) | Window functions, ranking (B11–B15) | `SQL_Lab/outputs/query_*.txt` |
| Excel | `SUMIFS`, `COUNTIFS` (C1, C2) | Lookups and date functions (C4–C7) | Distinct counting, dashboards (C8–C10) | `Excel_Lab/evidence/excel_verification.txt` |
| Visualisation | Bar chart, histogram (D1, D2) | Box plot, heatmap (D3, D4) | Interactive Plotly (D5) | `Data_Visualization_Lab/outputs/` |
| Statistics | Descriptive statistics (E1) | Normality, confidence intervals (E2, E3) | Hypothesis testing, A/B reasoning (E4, E5) | `Statistics_Lab/evidence/` |
| Power BI | Columns vs measures (F1, F2) | Filter context, `TOPN` (F3, F4) | Data modelling (F5) | `PowerBI_Lab/` build package |
| Git / GitHub | Concepts, first commit (G1, G2) | Branches, undo (G3, G4) | `.gitignore` and secrets (G5) | `Git_GitHub_Lab/evidence/` |
| Machine Learning | Leakage, metrics (H1, H2) | Confusion matrix, overfitting (H3, H4) | Cross-validation (H5) | `Machine_Learning_Lab/evidence/` |

**Rule applied throughout:** a skill is only marked as demonstrated when the practical
output exists and can be re-run. Completing a tutorial is not evidence.
