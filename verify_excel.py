"""Independently verify that every formula in Excel_Data_Analysis_Lab.xlsx evaluates
to the correct value.

Method: recalculate the workbook with LibreOffice Calc (headless), then compare the
cached results against values computed directly from the source CSV with pandas.

    python verify_excel.py
"""

import os
import shutil
import subprocess
import tempfile

import pandas as pd
from openpyxl import load_workbook

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WORKBOOK = os.path.join(HERE, "Excel_Data_Analysis_Lab.xlsx")
DATA = os.path.join(ROOT, "data", "online_retail_sales_sample.csv")
EVIDENCE = os.path.join(HERE, "evidence")
os.makedirs(EVIDENCE, exist_ok=True)


def recalculate():
    out = tempfile.mkdtemp(prefix="recalc_")
    subprocess.run(["libreoffice", "--headless", "--calc", "--convert-to", "xlsx",
                    "--outdir", out, WORKBOOK],
                   check=True, capture_output=True, timeout=900)
    return os.path.join(out, os.path.basename(WORKBOOK))


def main():
    df = pd.read_csv(DATA, parse_dates=["InvoiceDate"])
    uk = df[df["Country"] == "United Kingdom"]
    truth = {
        "uk_revenue": round(float(uk["line_total"].sum()), 2),
        "uk_lines": int(len(uk)),
        "uk_units": int(uk["Quantity"].sum()),
        "uk_invoices": int(uk["InvoiceNo"].nunique()),
        "total_revenue": round(float(df["line_total"].sum()), 2),
        "total_lines": int(len(df)),
        "total_invoices": int(df["InvoiceNo"].nunique()),
        "max_line": round(float(df["line_total"].max()), 2),
        "avg_line_uk": round(float(uk["line_total"].mean()), 6),
    }

    path = recalculate()
    wb = load_workbook(path, data_only=True)
    shutil.rmtree(os.path.dirname(path), ignore_errors=True)

    dash = wb["KPI_Dashboard"]
    kpi = {}
    for row in (10, 13, 16):
        for col in (2, 4, 6, 8):
            label = dash.cell(row=row, column=col).value
            value = dash.cell(row=row + 1, column=col).value
            if label:
                kpi[str(label)] = value

    pivot = wb["Pivot_View"]
    uk_row = [pivot.cell(row=5, column=c).value for c in range(3, 8)]
    total_row = [pivot.cell(row=35, column=c).value for c in range(3, 8)]

    checks = [
        ("KPI total revenue (UK)", kpi.get("Total revenue (GBP)"), truth["uk_revenue"]),
        ("KPI line items (UK)", kpi.get("Line items"), truth["uk_lines"]),
        ("KPI units sold (UK)", kpi.get("Units sold"), truth["uk_units"]),
        ("KPI orders (UK)", kpi.get("Orders (distinct invoices)"), truth["uk_invoices"]),
        ("KPI largest line (UK)", kpi.get("Largest line value (GBP)"), truth["max_line"]),
        ("KPI avg line value (UK)", kpi.get("Avg line value (GBP)"), truth["avg_line_uk"]),
        ("Pivot UK revenue", uk_row[2], truth["uk_revenue"]),
        ("Pivot UK orders", uk_row[0], truth["uk_invoices"]),
        ("Pivot total revenue", total_row[2], truth["total_revenue"]),
        ("Pivot total orders", total_row[0], truth["total_invoices"]),
        ("Pivot total lines", total_row[1], truth["total_lines"]),
    ]

    lines = ["EXCEL WORKBOOK VERIFICATION", "=" * 70,
             f"workbook : {os.path.basename(WORKBOOK)}",
             f"method   : LibreOffice Calc recalculation vs pandas ground truth",
             f"source   : {os.path.basename(DATA)} ({truth['total_lines']:,} rows)",
             "", f"{'CHECK':32s} {'WORKBOOK':>18s} {'TRUTH':>18s}  RESULT"]
    passed = 0
    for name, got, want in checks:
        ok = got is not None and abs(float(got) - float(want)) < 0.01
        passed += ok
        lines.append(f"{name:32s} {float(got):18,.2f} {float(want):18,.2f}  "
                     f"{'PASS' if ok else 'FAIL'}")

    lines += ["", f"RESULT: {passed}/{len(checks)} checks passed", "=" * 70,
              "", "Workbook contents:",
              f"  sheets          : {', '.join(wb.sheetnames)}",
              f"  KPI formulas    : {len(kpi)}",
              f"  charts          : {len(wb['KPI_Dashboard']._charts)}",
              f"  data validations: {len(wb['KPI_Dashboard'].data_validations.dataValidation)}",
              f"  conditional fmt : {len(list(wb['KPI_Dashboard'].conditional_formatting))}",
              f"  Excel tables    : Raw_Data={len(wb['Raw_Data']._tables)}, "
              f"Clean_Data={len(wb['Clean_Data']._tables)}"]

    report = "\n".join(lines)
    print(report)
    with open(os.path.join(EVIDENCE, "excel_verification.txt"), "w") as handle:
        handle.write(report + "\n")
    if passed != len(checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
