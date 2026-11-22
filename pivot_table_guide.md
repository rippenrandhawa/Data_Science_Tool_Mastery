# Creating the native PivotTable and PivotChart

`Excel_Data_Analysis_Lab.xlsx` already contains a **formula-driven** `Pivot_View`
sheet that reproduces every pivot figure with live `SUMIFS` / `COUNTIFS` /
`INDEX-MATCH` formulas, and it is verified against the source data
(`evidence/excel_verification.txt`).

The one thing openpyxl cannot write is Excel's **native PivotTable object**. This
guide creates it in Excel in about two minutes. Nothing here changes the numbers —
it re-derives them from `Raw_Data`.

---

## Step 1 — Insert the PivotTable

1. Open `Excel_Data_Analysis_Lab.xlsx`.
2. Click any cell in the **Raw_Data** sheet (the blue Excel Table named `tblRaw`).
3. **Insert → PivotTable → From Table/Range**.
4. Confirm the range is `tblRaw`, choose **New Worksheet**, click **OK**.
5. Rename the new sheet `PivotTable_Country`.

## Step 2 — Build “Revenue by Country”

In the **PivotTable Fields** pane drag:

| Area | Field |
|---|---|
| Rows | `Country` |
| Values | `Line Total (GBP)` → set to **Sum** |

Then:

1. Click the value field → **Value Field Settings** → choose **Sum**, number format
   `#,##0.00`.
2. **Design → Report Layout → Show in Tabular Form**.
3. **Design → Grand Totals → On for Rows and Columns**.
4. **Design → Subtotals → Do Not Show Subtotals**.
5. Sort: right-click a revenue value → **Sort → Largest to Smallest**.

## Step 3 — Add a PivotChart

1. Click inside the PivotTable.
2. **PivotTable Analyze → PivotChart → Bar → Clustered Bar**.
3. Move the chart, set the title to **“Revenue by Country”**.
4. **Chart Design → Switch Row/Column** so the largest country is at the top.
5. Add data labels: **Chart Design → Add Chart Element → Data Labels → Outside End**.

## Step 4 — Second PivotTable: monthly trend

1. **Insert → PivotTable** from `tblRaw` again → new sheet `PivotTable_Monthly`.
2. The `Invoice Date` field is a real date, so Excel will offer to group it.
   Drag `Invoice Date` to **Rows**, right-click → **Group** → select **Months** and
   **Years** → **OK**.
3. Drag `Line Total (GBP)` to **Values** (Sum).
4. **PivotTable Analyze → PivotChart → Line**.
5. Format the axis title as **“Revenue (GBP)”**.

## Step 5 — Add a slicer and connect it

1. Click the country PivotTable → **PivotTable Analyze → Insert Slicer → Country**.
2. Right-click the slicer → **Report Connections** → tick **both** PivotTables.
3. Now selecting a country updates the revenue table, the monthly table and the chart.

## Step 6 — Verify against the source data

| Cell / field | Expected value |
|---|---:|
| United Kingdom revenue | 196,462.03 |
| United Kingdom line items | 10,787 |
| United Kingdom orders (distinct invoices) | 442 |
| Total revenue | 239,642.62 |
| Total invoices | 500 |
| Peak month | 2011-11 |

If any figure differs, check that the PivotTable is based on `tblRaw` and that the
value field is summarised by **Sum**, not Count.

## Optional: Power Query (Get & Transform)

`Data → Get Data → From File → From CSV` and select
`data/online_retail_sales_sample.csv`. In the Power Query editor you can:

* promote the header row,
* set `Invoice Date` to **Date/Time**,
* add a `Line Total` column (`[Quantity] * [UnitPrice]`),
* add a `Year-Month` custom column (`Date.ToText([Invoice Date], "yyyy-MM")`),
* **Close & Load** to a Data Model.

The same transformations are supplied as M code in
`PowerBI_Lab/power_query_m.m`, which works in both Power Query engines.

---

## Why both approaches?

| Approach | Strength |
|---|---|
| Formula-driven `Pivot_View` | Portable, version-controlled, recalculates in LibreOffice/Google Sheets |
| Native PivotTable | Interactive drag-and-drop, slicers, drill-down, PivotCharts |

A working analyst uses both: the formula version for reproducibility, the native
version for exploration.
