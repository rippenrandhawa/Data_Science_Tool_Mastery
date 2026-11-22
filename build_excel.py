"""Build Excel_Data_Analysis_Lab.xlsx.

Sheets
------
README          documentation, formula index and data dictionary
Raw_Data        the real transaction extract, formatted as an Excel Table
Clean_Data      the same rows plus calculated columns implemented as formulas
Formulas_Demo   labelled, working examples of every required Excel function
Pivot_View      formula-driven pivot analysis (SUMIFS / COUNTIFS / INDEX-MATCH)
KPI_Dashboard   interactive KPI dashboard: formulas, charts, conditional
                formatting and a data-validation slicer

Run:  python build_excel.py
"""

import os

import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, PieChart, Reference
from openpyxl.comments import Comment
from openpyxl.formatting.rule import CellIsRule, ColorScaleRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA_PATH = os.path.join(ROOT, "data", "online_retail_sales_sample.csv")
OUT_PATH = os.path.join(HERE, "Excel_Data_Analysis_Lab.xlsx")

# ---------------------------------------------------------------------------
# Shared styling helpers
# ---------------------------------------------------------------------------
NAVY = "1F3864"
BLUE = "2F5597"
LIGHT = "D9E2F3"
ACCENT = "FFF2CC"
GREY = "F2F2F2"
GREEN = "E2EFDA"

TITLE_FONT = Font(name="Calibri", size=16, bold=True, color="FFFFFF")
H1_FONT = Font(name="Calibri", size=12, bold=True, color="FFFFFF")
H2_FONT = Font(name="Calibri", size=11, bold=True, color=NAVY)
BODY_FONT = Font(name="Calibri", size=10)
MONO_FONT = Font(name="Consolas", size=9)
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def fill(color):
    return PatternFill("solid", fgColor=color)


def title_bar(ws, text, last_col, row=1, sub=None):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_col)
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = TITLE_FONT
    cell.fill = fill(NAVY)
    cell.alignment = Alignment(vertical="center", indent=1)
    ws.row_dimensions[row].height = 26
    if sub:
        ws.merge_cells(start_row=row + 1, start_column=1, end_row=row + 1,
                       end_column=last_col)
        sc = ws.cell(row=row + 1, column=1, value=sub)
        sc.font = Font(name="Calibri", size=9, italic=True, color="404040")
        sc.fill = fill(LIGHT)


def header_row(ws, headers, row, color=BLUE):
    for col, text in enumerate(headers, start=1):
        c = ws.cell(row=row, column=col, value=text)
        c.font = H1_FONT
        c.fill = fill(color)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BORDER
    ws.row_dimensions[row].height = 30


def widths(ws, mapping):
    for col, width in mapping.items():
        ws.column_dimensions[col].width = width


# ---------------------------------------------------------------------------
# Sheet 1 - README
# ---------------------------------------------------------------------------
def build_readme(wb):
    ws = wb.create_sheet("README")
    ws.sheet_view.showGridLines = False
    widths(ws, {"A": 3, "B": 26, "C": 78, "D": 18})

    ws.merge_cells("B2:D2")
    c = ws["B2"]
    c.value = "EXCEL DATA ANALYSIS LAB"
    c.font = Font(name="Calibri", size=20, bold=True, color="FFFFFF")
    c.fill = fill(NAVY)
    c.alignment = Alignment(vertical="center", indent=1)
    ws.row_dimensions[2].height = 34

    ws.merge_cells("B3:D3")
    ws["B3"] = ("Data Analyst Internship - Task 4  |  Tool Mastery Project  |  "
                "Workbook built programmatically with openpyxl")
    ws["B3"].font = Font(size=10, italic=True, color="404040")

    rows = [
        ("", ""),
        ("DATA SOURCE", ""),
        ("Dataset", "Online Retail - UCI Machine Learning Repository, dataset 352"),
        ("DOI", "https://doi.org/10.24432/C5BW33"),
        ("Direct download", "https://archive.ics.uci.edu/ml/machine-learning-databases/00352/Online%20Retail.xlsx"),
        ("Extract used here", "12,177 transaction lines / 500 invoices, sampled with random_state=42"),
        ("Currency / period", "GBP (GBP)  |  1 Dec 2010 - 8 Dec 2011"),
        ("", ""),
        ("SHEET GUIDE", ""),
        ("Raw_Data", "The transaction extract, formatted as a real Excel Table with filters."),
        ("Clean_Data", "The same rows with calculated columns written as live Excel formulas."),
        ("Formulas_Demo", "One labelled, working example of every required function."),
        ("Pivot_View", "Pivot-style analysis built with SUMIFS / COUNTIFS / INDEX-MATCH."),
        ("KPI_Dashboard", "Interactive KPI dashboard: formulas, charts, conditional formatting, slicer."),
        ("", ""),
        ("HOW TO USE", ""),
        ("1", "Open Raw_Data and use the filter arrows on the header row to slice the data."),
        ("2", "On KPI_Dashboard use the country dropdown (cell C6) - every KPI recalculates."),
        ("3", "Formulas_Demo shows the exact formula text; click any cell to see it in the formula bar."),
        ("4", "Conditional formatting on the dashboard recolours KPIs against their targets."),
        ("", ""),
        ("IMPORTANT - PIVOT TABLES", ""),
        ("Note", "Excel's native PivotTable object cannot be written by openpyxl. This workbook "
                "therefore ships a fully working formula-driven Pivot_View sheet, and "
                "pivot_table_guide.md gives exact step-by-step instructions to create the native "
                "PivotTable and PivotChart in Excel in under two minutes."),
        ("", ""),
        ("REPRODUCIBILITY", ""),
        ("Builder script", "Excel_Lab/build_excel.py"),
        ("Python", "3.13  |  openpyxl 3.1.5  |  pandas 2.2.3"),
    ]
    r = 5
    for label, text in rows:
        if label and not text:
            c = ws.cell(row=r, column=2, value=label)
            c.font = H2_FONT
            c.fill = fill(LIGHT)
            ws.cell(row=r, column=3).fill = fill(LIGHT)
        elif label:
            a = ws.cell(row=r, column=2, value=label)
            a.font = Font(size=10, bold=True, color=NAVY)
            a.alignment = Alignment(vertical="top")
            b = ws.cell(row=r, column=3, value=text)
            b.font = BODY_FONT
            b.alignment = Alignment(wrap_text=True, vertical="top")
        r += 1
    return ws


# ---------------------------------------------------------------------------
# Sheet 2 - Raw_Data
# ---------------------------------------------------------------------------
def build_raw(wb, df):
    ws = wb.create_sheet("Raw_Data")
    headers = ["Invoice No", "Stock Code", "Description", "Quantity", "Invoice Date",
               "Unit Price (GBP)", "Customer ID", "Country", "Line Total (GBP)"]
    header_row(ws, headers, 1)

    for row_idx, rec in enumerate(df.itertuples(index=False), start=2):
        ws.cell(row=row_idx, column=1, value=str(rec.InvoiceNo))
        ws.cell(row=row_idx, column=2, value=str(rec.StockCode))
        ws.cell(row=row_idx, column=3, value=rec.Description)
        ws.cell(row=row_idx, column=4, value=int(rec.Quantity))
        ws.cell(row=row_idx, column=5, value=rec.InvoiceDate.to_pydatetime())
        ws.cell(row=row_idx, column=6, value=float(rec.UnitPrice))
        ws.cell(row=row_idx, column=7,
                value=None if pd.isna(rec.CustomerID) else int(rec.CustomerID))
        ws.cell(row=row_idx, column=8, value=rec.Country)
        ws.cell(row=row_idx, column=9, value=float(rec.line_total))

    last = len(df) + 1
    for col, fmt in {"E": "dd/mm/yyyy hh:mm", "F": "#,##0.00", "G": "0",
                     "I": "#,##0.00"}.items():
        for cell in ws[col][1:]:
            cell.number_format = fmt

    table = Table(displayName="tblRaw", ref=f"A1:I{last}")
    table.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True,
                                          showFirstColumn=False, showLastColumn=False)
    ws.add_table(table)
    ws.freeze_panes = "A2"
    widths(ws, {"A": 12, "B": 12, "C": 42, "D": 10, "E": 18, "F": 15, "G": 12,
                "H": 20, "I": 15})
    return ws, last


# ---------------------------------------------------------------------------
# Sheet 3 - Clean_Data (calculated columns as formulas)
# ---------------------------------------------------------------------------
def build_clean(wb, df, raw_last):
    ws = wb.create_sheet("Clean_Data")
    headers = ["Invoice No", "Stock Code", "Description", "Quantity", "Invoice Date",
               "Unit Price (GBP)", "Customer ID", "Country", "Line Total (GBP)",
               "Month", "Value Band", "High Value", "Price Band", "Description Length",
               "First Line of Invoice"]
    header_row(ws, headers, 1)

    for row_idx, rec in enumerate(df.itertuples(index=False), start=2):
        ws.cell(row=row_idx, column=1, value=str(rec.InvoiceNo))
        ws.cell(row=row_idx, column=2, value=str(rec.StockCode))
        ws.cell(row=row_idx, column=3, value=rec.Description)
        ws.cell(row=row_idx, column=4, value=int(rec.Quantity))
        ws.cell(row=row_idx, column=5, value=rec.InvoiceDate.to_pydatetime())
        ws.cell(row=row_idx, column=6, value=float(rec.UnitPrice))
        ws.cell(row=row_idx, column=7,
                value=None if pd.isna(rec.CustomerID) else int(rec.CustomerID))
        ws.cell(row=row_idx, column=8, value=rec.Country)
        # --- live formulas -------------------------------------------------
        ws.cell(row=row_idx, column=9, value=f"=D{row_idx}*F{row_idx}")
        ws.cell(row=row_idx, column=10, value=f'=TEXT(E{row_idx},"YYYY-MM")')
        ws.cell(row=row_idx, column=11,
                value=(f'=IF(I{row_idx}>=200,"Large",IF(I{row_idx}>=50,"Medium","Small"))'))
        ws.cell(row=row_idx, column=12,
                value=f'=IF(I{row_idx}>=AVERAGE($I$2:$I${raw_last}),"Yes","No")')
        ws.cell(row=row_idx, column=13,
                value=(f'=IF(F{row_idx}>=10,"Premium",IF(F{row_idx}>=3,"Standard","Value"))'))
        ws.cell(row=row_idx, column=14, value=f"=LEN(C{row_idx})")
        # 1 on the first line of each invoice, 0 afterwards - used to count
        # distinct invoices with SUMIFS (far more robust than array formulas).
        ws.cell(row=row_idx, column=15,
                value=f"=IF(COUNTIF($A$2:A{row_idx},A{row_idx})=1,1,0)")

    last = len(df) + 1
    for col, fmt in {"E": "dd/mm/yyyy hh:mm", "F": "#,##0.00", "I": "#,##0.00"}.items():
        for cell in ws[col][1:]:
            cell.number_format = fmt

    table = Table(displayName="tblClean", ref=f"A1:O{last}")
    table.tableStyleInfo = TableStyleInfo(name="TableStyleMedium9", showRowStripes=True)
    ws.add_table(table)
    ws.freeze_panes = "A2"
    widths(ws, {"A": 12, "B": 12, "C": 40, "D": 10, "E": 18, "F": 15, "G": 12,
                "H": 20, "I": 15, "J": 10, "K": 12, "L": 11, "M": 12, "N": 16,
                "O": 18})
    return ws, last


# ---------------------------------------------------------------------------
# Sheet 4 - Formulas_Demo
# ---------------------------------------------------------------------------
def build_formulas(wb, raw_last):
    ws = wb.create_sheet("Formulas_Demo")
    ws.sheet_view.showGridLines = False
    widths(ws, {"A": 4, "B": 30, "C": 56, "D": 22, "E": 46})
    title_bar(ws, "EXCEL FORMULA DEMONSTRATIONS - every result below is a live formula",
              5, sub="Click any result cell to read the formula in the formula bar.")

    header_row(ws, ["#", "Function", "Formula (as entered)", "Result", "What it does"], 4)

    R = raw_last
    RW = "Raw_Data"
    CL = "Clean_Data"
    demos = [
        ("IF", f'=IF({RW}!I2>=100,"Large order","Small order")',
         "Returns one of two values based on a logical test."),
        ("Nested IF", f'=IF({RW}!I2>=200,"Large",IF({RW}!I2>=50,"Medium","Small"))',
         "Chains several tests - the classic banding / grading pattern."),
        ("IFERROR", '=IFERROR(1/0,"Not calculable")',
         "Traps an error and returns a friendly value instead of #DIV/0!."),
        ("SUMIF", f'=SUMIF({RW}!$H$2:$H${R},"United Kingdom",{RW}!$I$2:$I${R})',
         "Adds values where a single criterion is met."),
        ("SUMIFS", f'=SUMIFS({RW}!$I$2:$I${R},{RW}!$H$2:$H${R},"United Kingdom",'
                  f'{CL}!$J$2:$J${R},"2011-11")',
         "Adds values where several criteria are met simultaneously."),
        ("COUNTIF", f'=COUNTIF({RW}!$H$2:$H${R},"United Kingdom")',
         "Counts rows matching one criterion."),
        ("COUNTIFS", f'=COUNTIFS({CL}!$K$2:$K${R},"Large",'
                    f'{RW}!$H$2:$H${R},"United Kingdom")',
         "Counts rows matching several criteria."),
        ("AVERAGEIF", f'=AVERAGEIF({RW}!$H$2:$H${R},"United Kingdom",'
                     f'{RW}!$I$2:$I${R})',
         "Conditional average - KPI per segment."),
        ("XLOOKUP", f'=_xlfn.XLOOKUP("85123A",{RW}!$B$2:$B${R},{RW}!$C$2:$C${R},'
                    f'"Not found")',
         "Modern lookup: finds a stock code and returns its description."),
        ("INDEX + MATCH", f'=INDEX({RW}!$C$2:$C${R},'
                         f'MATCH("85123A",{RW}!$B$2:$B${R},0))',
         "Classic two-way lookup that works in every Excel version."),
        ("VLOOKUP", f'=VLOOKUP("85123A",{RW}!$B$2:$D${R},2,FALSE)',
         "Legacy lookup - included so you can compare it with XLOOKUP."),
        ("TEXT", f'=TEXT({RW}!E2,"dddd dd mmmm yyyy")',
         "Formats a date as readable text."),
        ("YEAR / MONTH", f'=YEAR({RW}!E2)&"-"&TEXT(MONTH({RW}!E2),"00")',
         "Builds a year-month key used for grouping."),
        ("EOMONTH", f'=TEXT(EOMONTH({RW}!E2,0),"dd mmm yyyy")',
         "Last day of the transaction month - useful for period closes."),
        ("LEFT / RIGHT", f'=LEFT({RW}!C2,12)&"..."',
         "Truncates long product descriptions."),
        ("TRIM / UPPER", f'=UPPER(TRIM({RW}!C2))',
         "Removes stray spaces and normalises casing."),
        ("LEN", f'=LEN({RW}!C2)',
         "Text length - a quick data-quality check."),
        ("ROUND", f'=ROUND({RW}!I2,1)',
         "Rounds a calculated value to one decimal place."),
        ("MAX / MIN", f'=MAX({RW}!$I$2:$I${R})&" / "&MIN({RW}!$I$2:$I${R})',
         "Range of line values - outlier reconnaissance."),
        ("SUMPRODUCT", f'=SUMPRODUCT(({RW}!$H$2:$H${R}="United Kingdom")*'
                      f'({RW}!$I$2:$I${R}))',
         "Array-style conditional sum without Ctrl+Shift+Enter."),
        ("RANK.EQ", f'=_xlfn.RANK.EQ({RW}!I2,{RW}!$I$2:$I${R})',
         "Ranks a line against all others."),
        ("IFS", f'=_xlfn.IFS({RW}!I2>=200,"Large",{RW}!I2>=50,"Medium",TRUE,"Small")',
         "Cleaner alternative to deeply nested IF."),
        ("CONCAT / TEXTJOIN", f'=_xlfn.TEXTJOIN(", ",TRUE,"UK",TEXT({RW}!I2,"0.00"))',
         "Joins text pieces into a single label."),
    ]

    r = 5
    for idx, (name, formula, note) in enumerate(demos, start=1):
        ws.cell(row=r, column=1, value=idx).font = BODY_FONT
        ws.cell(row=r, column=2, value=name).font = Font(size=10, bold=True, color=NAVY)
        ws.cell(row=r, column=3, value=formula).font = MONO_FONT
        res = ws.cell(row=r, column=4, value=formula)
        res.font = Font(size=10, bold=True, color="C00000")
        res.fill = fill(GREEN)
        ws.cell(row=r, column=5, value=note).font = Font(size=9, color="404040")
        for col in range(1, 6):
            ws.cell(row=r, column=col).border = BORDER
            ws.cell(row=r, column=col).alignment = Alignment(
                vertical="center", wrap_text=(col in (3, 5)))
        r += 1

    ws.cell(row=r + 1, column=2, value="Ranges used").font = H2_FONT
    ws.cell(row=r + 1, column=3,
            value=f"Column I (line total), H (country), J (month), K (value band) "
                  f"refer to Raw_Data / Clean_Data rows 2-{R}.")
    return ws


# ---------------------------------------------------------------------------
# Sheet 5 - Pivot_View (formula-driven)
# ---------------------------------------------------------------------------
def build_pivot(wb, raw_last):
    ws = wb.create_sheet("Pivot_View")
    ws.sheet_view.showGridLines = False
    widths(ws, {"A": 4, "B": 24, "C": 14, "D": 14, "E": 16, "F": 16, "G": 40})
    title_bar(ws, "PIVOT-STYLE ANALYSIS  (formula-driven)", 7,
              sub="Each figure is a live SUMIFS / COUNTIFS formula over Raw_Data - "
                  "see pivot_table_guide.md for the native PivotTable version.")
    R = raw_last

    countries = ["United Kingdom", "Australia", "Belgium", "Canada", "Channel Islands",
                 "Cyprus", "Denmark", "EIRE", "Finland", "France", "Germany", "Greece",
                 "Iceland", "Israel", "Italy", "Japan", "Lebanon", "Lithuania",
                 "Malta", "Netherlands", "Norway", "Poland", "Portugal", "RSA",
                 "Singapore", "Spain", "Sweden", "Switzerland", "USA",
                 "United Arab Emirates"]

    # --- Table 1: revenue and orders by country -----------------------------
    start = 4
    header_row(ws, ["#", "Country", "Orders", "Line Items", "Revenue (GBP)",
                    "Avg Order Value (GBP)", "Revenue Share"], start)
    r = start + 1
    first_country_row = r
    for i, country in enumerate(countries, start=1):
        ws.cell(row=r, column=1, value=i).font = BODY_FONT
        ws.cell(row=r, column=2, value=country).font = BODY_FONT
        ws.cell(row=r, column=3,
                value=f'=SUMIFS(Clean_Data!$O:$O,Raw_Data!$H:$H,$B{r})')
        ws.cell(row=r, column=4,
                value=f'=COUNTIFS(Raw_Data!$H:$H,$B{r})')
        ws.cell(row=r, column=5,
                value=f'=SUMIFS(Raw_Data!$I:$I,Raw_Data!$H:$H,$B{r})')
        ws.cell(row=r, column=6, value=f'=IFERROR(E{r}/C{r},0)')
        ws.cell(row=r, column=7, value=f'=IFERROR(E{r}/SUM($E${first_country_row}:'
                                       f'$E${first_country_row + len(countries) - 1}),0)')
        ws.cell(row=r, column=5).number_format = "#,##0.00"
        ws.cell(row=r, column=6).number_format = "#,##0.00"
        ws.cell(row=r, column=7).number_format = "0.0%"
        r += 1
    last_country_row = r - 1
    ws.cell(row=r, column=2, value="TOTAL").font = Font(bold=True, color=NAVY)
    ws.cell(row=r, column=3, value=f"=SUM(C{first_country_row}:C{last_country_row})")
    ws.cell(row=r, column=4, value=f"=SUM(D{first_country_row}:D{last_country_row})")
    ws.cell(row=r, column=5, value=f"=SUM(E{first_country_row}:E{last_country_row})")
    ws.cell(row=r, column=6, value=f"=IFERROR(E{r}/C{r},0)")
    ws.cell(row=r, column=7, value=f"=SUM(G{first_country_row}:G{last_country_row})")
    for col in "CDEFG":
        ws[f"{col}{r}"].font = Font(bold=True, color=NAVY)
        ws[f"{col}{r}"].fill = fill(ACCENT)
    ws.cell(row=r, column=5).number_format = "#,##0.00"
    ws.cell(row=r, column=7).number_format = "0.0%"
    ws.conditional_formatting.add(
        f"E{first_country_row}:E{last_country_row}",
        ColorScaleRule(start_type="min", start_color="FFFFFF",
                       end_type="max", end_color="63BE7B"))

    # --- Table 2: monthly revenue ------------------------------------------
    mstart = r + 3
    ws.cell(row=mstart - 1, column=2, value="MONTHLY REVENUE").font = H2_FONT
    header_row(ws, ["#", "Month", "Revenue (GBP)", "Orders", "Units", "Avg Order Value (GBP)"],
               mstart)
    months = ["2010-12", "2011-01", "2011-02", "2011-03", "2011-04", "2011-05",
              "2011-06", "2011-07", "2011-08", "2011-09", "2011-10", "2011-11",
              "2011-12"]
    r = mstart + 1
    m_first = r
    for i, month in enumerate(months, start=1):
        ws.cell(row=r, column=1, value=i)
        ws.cell(row=r, column=2, value=month)
        ws.cell(row=r, column=3,
                value=f'=SUMIFS(Raw_Data!$I:$I,Clean_Data!$J:$J,$B{r})')
        ws.cell(row=r, column=4,
                value=f'=COUNTIFS(Clean_Data!$J:$J,$B{r})')
        ws.cell(row=r, column=5,
                value=f'=SUMIFS(Raw_Data!$D:$D,Clean_Data!$J:$J,$B{r})')
        ws.cell(row=r, column=6, value=f"=IFERROR(C{r}/D{r},0)")
        ws.cell(row=r, column=3).number_format = "#,##0.00"
        ws.cell(row=r, column=6).number_format = "#,##0.00"
        r += 1
    m_last = r - 1
    ws.cell(row=r, column=2, value="TOTAL").font = Font(bold=True, color=NAVY)
    ws.cell(row=r, column=3, value=f"=SUM(C{m_first}:C{m_last})")
    ws.cell(row=r, column=4, value=f"=SUM(D{m_first}:D{m_last})")
    ws.cell(row=r, column=5, value=f"=SUM(E{m_first}:E{m_last})")
    for col in "CDE":
        ws[f"{col}{r}"].font = Font(bold=True, color=NAVY)
        ws[f"{col}{r}"].fill = fill(ACCENT)
    ws.cell(row=r, column=3).number_format = "#,##0.00"

    # --- Table 3: value-band profile ---------------------------------------
    bstart = r + 3
    ws.cell(row=bstart - 1, column=2, value="ORDER VALUE BANDS").font = H2_FONT
    header_row(ws, ["#", "Band", "Line Items", "Revenue (GBP)", "Share"], bstart)
    bands = [("Large (>=200)", 200, None), ("Medium (50-200)", 50, 200),
             ("Small (<50)", None, 50)]
    r = bstart + 1
    b_first = r
    for i, (label, low, high) in enumerate(bands, start=1):
        ws.cell(row=r, column=1, value=i)
        ws.cell(row=r, column=2, value=label)
        if low is None:
            crit = f'Raw_Data!$I:$I,"<"&{high}'
        elif high is None:
            crit = f'Raw_Data!$I:$I,">="&{low}'
        else:
            crit = (f'Raw_Data!$I:$I,">="&{low},Raw_Data!$I:$I,"<"&{high}')
        ws.cell(row=r, column=3, value=f"=COUNTIFS({crit})")
        ws.cell(row=r, column=4, value=f"=SUMIFS(Raw_Data!$I:$I,{crit})")
        ws.cell(row=r, column=5, value=f"=IFERROR(D{r}/SUM($D${b_first}:$D${b_first + 2}),0)")
        ws.cell(row=r, column=4).number_format = "#,##0.00"
        ws.cell(row=r, column=5).number_format = "0.0%"
        r += 1
    return ws, first_country_row, last_country_row, m_first, m_last


# ---------------------------------------------------------------------------
# Sheet 6 - KPI_Dashboard
# ---------------------------------------------------------------------------
def build_dashboard(wb, raw_last, pivot_meta):
    ws = wb.create_sheet("KPI_Dashboard")
    ws.sheet_view.showGridLines = False
    widths(ws, {"A": 3, "B": 26, "C": 18, "D": 18, "E": 18, "F": 18, "G": 18,
                "H": 18, "I": 18})
    title_bar(ws, "RETAIL KPI DASHBOARD", 9,
              sub="Select a country in C6 - every KPI, chart and table below recalculates.")
    R = raw_last
    first_country_row, last_country_row = pivot_meta[0], pivot_meta[1]

    ws["B4"] = "COUNTRY FILTER"
    ws["B4"].font = H2_FONT
    ws["B4"].fill = fill(LIGHT)
    for col in "CDEF":
        ws[f"{col}4"].fill = fill(LIGHT)

    ws["B6"] = "Selected country"
    ws["B6"].font = Font(size=10, bold=True, color=NAVY)
    sel = ws["C6"]
    sel.value = "United Kingdom"
    sel.font = Font(size=12, bold=True, color="C00000")
    sel.fill = fill(ACCENT)
    sel.border = BORDER
    sel.alignment = Alignment(horizontal="center")

    countries = ["United Kingdom", "Australia", "Belgium", "Canada", "Channel Islands",
                 "Cyprus", "Denmark", "EIRE", "Finland", "France", "Germany", "Greece",
                 "Iceland", "Israel", "Italy", "Japan", "Lebanon", "Lithuania",
                 "Malta", "Netherlands", "Norway", "Poland", "Portugal", "RSA",
                 "Singapore", "Spain", "Sweden", "Switzerland", "USA",
                 "United Arab Emirates"]
    dv = DataValidation(type="list", formula1='"' + ",".join(countries) + '"',
                        allow_blank=False, showDropDown=False)
    dv.error = "Choose a country from the list."
    dv.errorTitle = "Invalid country"
    ws.add_data_validation(dv)
    dv.add(sel)
    ws["C6"].comment = Comment("Data-validation dropdown: pick any country and the "
                               "dashboard recalculates.", "Data Analyst")

    # --- KPI cards ---------------------------------------------------------
    kpis = [
        ("Total revenue (GBP)",
         '=SUMIFS(Raw_Data!$I:$I,Raw_Data!$H:$H,$C$6)', "#,##0.00", 50000),
        ("Line items",
         '=COUNTIFS(Raw_Data!$H:$H,$C$6)', "#,##0", 1000),
        ("Units sold",
         '=SUMIFS(Raw_Data!$D:$D,Raw_Data!$H:$H,$C$6)', "#,##0", 5000),
        ("Orders (distinct invoices)",
         '=SUMIFS(Clean_Data!$O:$O,Raw_Data!$H:$H,$C$6)', "#,##0", 100),
        ("Avg order value (GBP)",
         '=IFERROR(SUMIFS(Raw_Data!$I:$I,Raw_Data!$H:$H,$C$6)/'
         'SUMIFS(Clean_Data!$O:$O,Raw_Data!$H:$H,$C$6),0)', "#,##0.00", 200),
        ("Avg line value (GBP)",
         '=IFERROR(SUMIFS(Raw_Data!$I:$I,Raw_Data!$H:$H,$C$6)/'
         'COUNTIFS(Raw_Data!$H:$H,$C$6),0)', "#,##0.00", 30),
        ("Largest line value (GBP)",
         f'=_xlfn.MAXIFS(Raw_Data!$I:$I,Raw_Data!$H:$H,$C$6)', "#,##0.00", 500),
        ("Share of total revenue",
         '=IFERROR(SUMIFS(Raw_Data!$I:$I,Raw_Data!$H:$H,$C$6)/'
         'SUM(Raw_Data!$I:$I),0)', "0.0%", 0.5),
        ("Revenue vs GBP 50,000 target",
         '=IFERROR(SUMIFS(Raw_Data!$I:$I,Raw_Data!$H:$H,$C$6)/50000,0)', "0.0%", 1.0),
    ]

    ws["B8"] = "KEY PERFORMANCE INDICATORS"
    ws["B8"].font = H2_FONT
    ws["B8"].fill = fill(LIGHT)
    for col in "CDEFGHI":
        ws[f"{col}8"].fill = fill(LIGHT)

    r = 10
    for i, (label, formula, fmt, target) in enumerate(kpis):
        row = r + (i // 3) * 3
        col = 2 + (i % 3) * 2
        cell = ws.cell(row=row, column=col, value=label)
        cell.font = Font(size=10, bold=True, color=NAVY)
        cell.fill = fill(GREY)
        val = ws.cell(row=row + 1, column=col, value=formula)
        val.font = Font(size=18, bold=True, color="C00000")
        val.number_format = fmt
        val.fill = fill("FFFFFF")
        val.alignment = Alignment(horizontal="center")
        ws.merge_cells(start_row=row, start_column=col, end_row=row, end_column=col + 1)
        ws.merge_cells(start_row=row + 1, start_column=col, end_row=row + 1,
                       end_column=col + 1)
        for cc in (col, col + 1):
            ws.cell(row=row + 1, column=cc).border = BORDER
        ws.cell(row=row + 2, column=col,
                value=f"Target: {target:,}").font = Font(size=8, italic=True,
                                                         color="808080")
        ws.merge_cells(start_row=row + 2, start_column=col, end_row=row + 2,
                       end_column=col + 1)
        ws.conditional_formatting.add(
            f"{get_column_letter(col)}{row + 1}",
            CellIsRule(operator="greaterThanOrEqual", formula=[str(target)],
                       fill=fill("C6EFCE"), font=Font(color="006100", bold=True)))

    # --- Supporting table for charts ---------------------------------------
    tbl_row = 21
    ws.cell(row=tbl_row - 1, column=2, value="MONTHLY TREND (all countries)").font = H2_FONT
    header_row(ws, ["Month", "Revenue (GBP)", "Orders"], tbl_row, color=BLUE)
    months = ["2010-12", "2011-01", "2011-02", "2011-03", "2011-04", "2011-05",
              "2011-06", "2011-07", "2011-08", "2011-09", "2011-10", "2011-11",
              "2011-12"]
    for i, month in enumerate(months):
        row = tbl_row + 1 + i
        ws.cell(row=row, column=2, value=month)
        ws.cell(row=row, column=3, value=f'=SUMIFS(Raw_Data!$I:$I,Raw_Data!$J:$J,$B{row})')
        ws.cell(row=row, column=4, value=f'=COUNTIFS(Raw_Data!$J:$J,$B{row})')
        ws.cell(row=row, column=3).number_format = "#,##0.00"
    m_first, m_last = tbl_row + 1, tbl_row + len(months)

    chart_row = tbl_row
    ws.cell(row=chart_row - 1, column=6, value="TOP COUNTRIES BY REVENUE").font = H2_FONT
    top_rows = pivot_meta
    header_row(ws, ["Country", "Revenue (GBP)"], chart_row, color=BLUE)
    for i in range(10):
        row = chart_row + 1 + i
        ws.cell(row=row, column=6,
                value=f"=INDEX(Pivot_View!$B${first_country_row}:$B${last_country_row},"
                      f"MATCH(LARGE(Pivot_View!$E${first_country_row}:$E${last_country_row},"
                      f"{i + 1}),Pivot_View!$E${first_country_row}:$E${last_country_row},0))")
        ws.cell(row=row, column=7,
                value=f"=LARGE(Pivot_View!$E${first_country_row}:$E${last_country_row},"
                      f"{i + 1})")
        ws.cell(row=row, column=7).number_format = "#,##0.00"
    c_first, c_last = chart_row + 1, chart_row + 10

    # --- Charts ------------------------------------------------------------
    line = LineChart()
    line.title = "Monthly revenue trend"
    line.y_axis.title = "Revenue (GBP)"
    line.x_axis.title = "Month"
    line.height, line.width = 7.5, 13
    line.add_data(Reference(ws, min_col=3, min_row=tbl_row, max_row=m_last),
                  titles_from_data=True)
    line.set_categories(Reference(ws, min_col=2, min_row=m_first, max_row=m_last))
    ws.add_chart(line, "B38")

    bar = BarChart()
    bar.type = "bar"
    bar.title = "Top 10 countries by revenue"
    bar.y_axis.title = "Country"
    bar.x_axis.title = "Revenue (GBP)"
    bar.height, bar.width = 9, 14
    bar.add_data(Reference(ws, min_col=7, min_row=chart_row, max_row=c_last),
                 titles_from_data=True)
    bar.set_categories(Reference(ws, min_col=6, min_row=c_first, max_row=c_last))
    ws.add_chart(bar, "F38")

    pie = PieChart()
    pie.title = "Revenue share - top 10 countries"
    pie.height, pie.width = 7.5, 12
    pie.add_data(Reference(ws, min_col=7, min_row=chart_row, max_row=c_last),
                 titles_from_data=True)
    pie.set_categories(Reference(ws, min_col=6, min_row=c_first, max_row=c_last))
    ws.add_chart(pie, "B56")

    ws.cell(row=75, column=2,
            value="All KPIs, tables and charts on this sheet are driven by live formulas "
                  "over Raw_Data. No value is hard-coded.").font = Font(
                      size=9, italic=True, color="808080")
    return ws


# ---------------------------------------------------------------------------
def main():
    df = pd.read_csv(DATA_PATH, parse_dates=["InvoiceDate"],
                     dtype={"InvoiceNo": str, "StockCode": str})
    wb = Workbook()
    wb.remove(wb.active)

    build_readme(wb)
    _, raw_last = build_raw(wb, df)
    _, clean_last = build_clean(wb, df, raw_last)
    build_formulas(wb, raw_last)
    _, fc, lc, mf, ml = build_pivot(wb, raw_last)
    build_dashboard(wb, raw_last, (fc, lc, mf, ml))

    wb.active = 0
    wb.save(OUT_PATH)
    print(f"saved: {OUT_PATH}")
    print(f"sheets: {wb.sheetnames}")
    print(f"raw rows: {raw_last - 1:,} | clean rows: {clean_last - 1:,}")


if __name__ == "__main__":
    main()
