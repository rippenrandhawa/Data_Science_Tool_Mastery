# Power BI Business Analytics — Build Guide

**Deliverable status: manual build required.**

Power BI Desktop is a Windows-only GUI application. It cannot be installed or driven
from this Linux build environment, so this project does **not** ship a fabricated
`.pbix` file or fabricated screenshots. Instead it ships everything needed to build
the dashboard in under 15 minutes:

| File | What it is |
|---|---|
| `power_query_m.m` | The complete Power Query M code for all six model queries |
| `dax_measures.dax` | The complete DAX measure set (KPIs, time intelligence, concentration) |
| `data_model.md` | Star-schema diagram, relationships and cardinality |
| `PowerBI_Business_Analytics_BUILD_GUIDE.md` | This step-by-step build document |

> **Honesty note.** No screenshot in this project claims to be a Power BI window.
> Every number quoted in the report was produced by the Python, SQL and Excel labs
> from the same dataset, not invented to illustrate a dashboard.

---

## 1. Install Power BI Desktop

1. Download from <https://powerbi.microsoft.com/desktop/> (free, Windows only).
2. Run the installer and accept the default options.
3. Sign in with any account, or choose **File → Sign in → Skip** to work locally.
4. Verify: **Help → About** shows a version number (any 2024/2025 release works).

## 2. Create the data model

1. **Get data → Blank query → Advanced editor.** Paste the whole of `power_query_m.m`.
2. In the `Staging` query, edit the `File.Contents(...)` path so it points at your copy
   of `data/online_retail_sales_sample.csv`.
3. Click **Done**, then **Close & Apply**.
4. Power BI creates six queries: `Staging`, `dim_date`, `dim_customer`, `dim_product`,
   `fact_order_items`, `fact_orders`.

### 2.1 Disable relationship auto-detection (optional but recommended)

**File → Options → Current File → Data Load →** uncheck
*“Auto detect new relationships”*. We create the relationships by hand so the model
is deterministic.

### 2.2 Mark the date table

**Table tools → Mark as date table → Date table = `dim_date`, Date column = `date`.**

### 2.3 Create the relationships

**Model view → Manage relationships → New**, then add these five:

| From table | Column | To table | Column | Cardinality | Cross-filter |
|---|---|---|---|---|---|
| `fact_order_items` | `invoice_no` | `fact_orders` | `invoice_no` | Many-to-one | Single |
| `fact_order_items` | `stock_code` | `dim_product` | `stock_code` | Many-to-one | Single |
| `fact_orders` | `customer_id` | `dim_customer` | `customer_id` | Many-to-one | Single |
| `fact_orders` | `invoice_date` | `dim_date` | `date` | Many-to-one | Single |
| `fact_order_items` | `customer_id`* | `dim_customer` | `customer_id` | Many-to-one | Single |

\* Add `customer_id` to `fact_order_items` in Power Query
(`Table.AddColumn` referencing `fact_orders`, or simply include it in the
`fact_order_items` `SelectColumns` list and dedupe separately). The simplest option
is to relate `fact_order_items` to `dim_customer` directly.

## 3. Load the DAX measures

1. Click the `fact_order_items` table in the **Data** pane.
2. **Table tools → New measure.**
3. Paste one measure at a time from `dax_measures.dax`, pressing Enter after each.
4. Verify the two headline measures against the source data:

   | Measure | Expected value (this dataset) |
   |---|---|
   | `Total Revenue` | 239,642.62 |
   | `Total Orders` | 500 |
   | `Total Line Items` | 12,177 |
   | `Average Order Value` | 479.29 |
   | `Distinct Products` | 2,497 |

   If these match, the model is wired correctly.

## 4. Build the report page

### 4.1 KPI cards (top row)

Insert five **Card** visuals, one per measure:

`Total Revenue`, `Total Orders`, `Average Order Value`, `Customers`, `Distinct Products`.

Select the `Revenue vs Target` card, then
**Format visual → Call value → Conditional formatting → Background colour** and
drive it with the `Revenue Status` measure (green / amber / red rules).

### 4.2 Slicers (left rail)

Insert a **Slicer** for `dim_customer[country]` (set to dropdown) and a second
**Slicer** for `dim_date[year]`. Tick **Sync slicers** across pages if you add a
second page.

### 4.3 Charts

| Visual | Type | Fields |
|---|---|---|
| Monthly trend | Line and stacked column | Axis `dim_date[month_name]`, Column `Total Revenue`, Line `Total Orders` |
| Revenue by country | Bar | Axis `dim_customer[country]`, Value `Total Revenue`, Sort descending |
| Product concentration | Treemap | Group `dim_product[description]`, Value `Total Revenue`, Top 15 |
| Customer concentration | Funnel | Group `dim_customer[customer_id]`, Value `Total Revenue` |
| Value-band profile | Donut | Legend `fact_order_items[value_band]`, Value `Total Revenue` |

### 4.4 Drill-down

On the monthly trend visual enable **Drill down** (double chevron in the visual
header) so users can move year → quarter → month → day.

## 5. Validate the dashboard

1. **File → Save As** → `PowerBI_Business_Analytics.pbix`.
2. Open the file again and confirm the KPI cards still read the expected values.
3. Change the country slicer to **France** and confirm every visual updates.
4. Use **View → Mobile layout** to produce a phone-friendly version.

## 6. What is genuinely automated vs. manual

| Step | Status |
|---|---|
| Dataset preparation, cleaning, Python/SQL/Excel analysis | **Automated and verified** |
| Power Query M code | **Written and delivered** (`power_query_m.m`) |
| DAX measures | **Written and delivered** (`dax_measures.dax`) |
| Relationships / star schema | **Specified exactly** (`data_model.md`) |
| `.pbix` file, report visuals, published dashboard | **Requires Power BI Desktop (manual)** |

Everything above the line is reproducible in this repository; everything below it
needs a Windows machine with Power BI Desktop installed.
