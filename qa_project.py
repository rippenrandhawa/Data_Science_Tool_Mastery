"""Project-wide quality assurance. Writes docs/qa_results.txt."""

import ast
import os
import subprocess
import sys
import zipfile

import nbformat
from docx import Document
from openpyxl import load_workbook
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
checks = []


def add(name, ok, detail=""):
    checks.append((name, bool(ok), detail))


def exists(rel):
    return os.path.exists(os.path.join(ROOT, rel))


# Structure
for folder in ["Python_Lab", "SQL_Lab", "Excel_Lab", "Data_Visualization_Lab",
               "Statistics_Lab", "PowerBI_Lab", "Jupyter_Lab", "Git_GitHub_Lab",
               "Machine_Learning_Lab", "Integrated_Project", "Portfolio",
               "Assessment", "Report", "Screenshots", "data", "docs"]:
    add(f"folder: {folder}", os.path.isdir(os.path.join(ROOT, folder)))

# Python syntax
for rel in ["environment_check.py", "build/prepare_data.py", "Python_Lab/python_lab.py",
            "SQL_Lab/load_data.py", "SQL_Lab/run_sql_lab.py",
            "Excel_Lab/build_excel.py", "Excel_Lab/verify_excel.py",
            "Data_Visualization_Lab/visualization_lab.py",
            "Statistics_Lab/statistics_lab.py", "Machine_Learning_Lab/ml_lab.py"]:
    try:
        ast.parse(open(os.path.join(ROOT, rel), encoding="utf-8").read())
        add(f"syntax: {rel}", True)
    except Exception as exc:
        add(f"syntax: {rel}", False, str(exc))

# Evidence
add("Python evidence", exists("Python_Lab/evidence/python_lab_output.txt"))
sql_outputs = [f"SQL_Lab/outputs/query_{i:02d}.txt" for i in range(1, 16)]
add("15 SQL output files", all(exists(p) and os.path.getsize(os.path.join(ROOT, p)) > 50
                               for p in sql_outputs), f"{sum(exists(p) for p in sql_outputs)}/15")
add("portable SQL database dump", exists("SQL_Lab/retail_analytics_dump.sql") and
    os.path.getsize(os.path.join(ROOT, "SQL_Lab", "retail_analytics_dump.sql")) > 100000)
import re
sql_text = open(os.path.join(ROOT, "SQL_Lab", "exercises.sql")).read()
add("SQL has 15 exercise markers",
    len(re.findall(r"^-- @Q\d{2}$", sql_text, flags=re.MULTILINE)) == 15)

# Workbook
try:
    wb = load_workbook(os.path.join(ROOT, "Excel_Lab", "Excel_Data_Analysis_Lab.xlsx"),
                       read_only=False, data_only=False)
    add("Excel workbook opens", True, f"sheets={len(wb.sheetnames)}")
    add("Excel required sheets", set(["README", "Raw_Data", "Clean_Data",
                                      "Formulas_Demo", "Pivot_View", "KPI_Dashboard"])
        .issubset(wb.sheetnames))
    add("Excel formulas present", sum(1 for ws in wb.worksheets for row in ws.iter_rows()
                                      for c in row if c.data_type == "f") > 10000)
except Exception as exc:
    add("Excel workbook opens", False, str(exc))
try:
    verification = open(os.path.join(ROOT, "Excel_Lab", "evidence",
                                     "excel_verification.txt")).read()
    add("Excel independent verification 11/11", "11/11 checks passed" in verification)
except Exception as exc:
    add("Excel independent verification 11/11", False, str(exc))

# Images and interactive charts
pngs = sorted([p for p in os.listdir(os.path.join(ROOT, "Data_Visualization_Lab",
                                                    "outputs", "charts"))
               if p.endswith(".png")])
add("8 chart PNGs", len(pngs) == 8, str(len(pngs)))
for name in pngs:
    im = Image.open(os.path.join(ROOT, "Data_Visualization_Lab", "outputs", "charts", name))
    dpi = im.info.get("dpi", (0, 0))[0]
    add(f"chart >=150 DPI: {name}", dpi >= 149, f"dpi={dpi:.1f}")
htmls = [p for p in os.listdir(os.path.join(ROOT, "Data_Visualization_Lab", "outputs",
                                             "interactive")) if p.endswith(".html")]
add("2 interactive Plotly HTML files", len(htmls) == 2, str(len(htmls)))

# Notebook integrity
for rel, min_code in [("Jupyter_Lab/Jupyter_Analytics_Workflow.ipynb", 15),
                      ("Integrated_Project/integrated_business_analytics.ipynb", 7)]:
    try:
        nb = nbformat.read(os.path.join(ROOT, rel), as_version=4)
        code_cells = [c for c in nb.cells if c.cell_type == "code"]
        errors = [o for c in code_cells for o in c.get("outputs", [])
                  if o.get("output_type") == "error"]
        output_cells = sum(bool(c.get("outputs")) for c in code_cells)
        add(f"notebook opens: {rel}", True, f"cells={len(nb.cells)} code={len(code_cells)}")
        add(f"notebook has real outputs: {rel}", output_cells == len(code_cells),
            f"{output_cells}/{len(code_cells)}")
        add(f"notebook zero errors: {rel}", not errors, f"errors={len(errors)}")
        add(f"notebook minimum code cells: {rel}", len(code_cells) >= min_code)
    except Exception as exc:
        add(f"notebook opens: {rel}", False, str(exc))

# Git
repo = os.path.join(ROOT, "Git_GitHub_Lab", "demo_repo")
try:
    log = subprocess.run(["git", "log", "--oneline", "--all"], cwd=repo,
                         capture_output=True, text=True, check=True).stdout
    add("real Git repository", len(log.strip().splitlines()) >= 4,
        f"commits={len(log.strip().splitlines())}")
    branches = subprocess.run(["git", "branch", "--list"], cwd=repo,
                              capture_output=True, text=True, check=True).stdout
    add("Git feature branch exists", "feature/sql-queries" in branches)
except Exception as exc:
    add("real Git repository", False, str(exc))

# Portfolio and assessment
for piece in ["Python_Project", "SQL_Project", "Excel_Project", "PowerBI_Project"]:
    add(f"portfolio README: {piece}", exists(f"Portfolio/{piece}/README.md"))
assessment = open(os.path.join(ROOT, "Assessment", "skills_assessment.md")).read()
for prefix, count in [("A", 10), ("B", 15), ("C", 10), ("D", 5), ("E", 5),
                      ("F", 5), ("G", 5), ("H", 5)]:
    add(f"assessment {prefix} count", sum(f"| {prefix}{i} |" in assessment
                                          for i in range(1, count + 1)) == count,
        str(count))
add("separate assessment answer key", exists("Assessment/answer_key.md"))

# Report
try:
    doc = Document(os.path.join(ROOT, "Report", "Data_Science_Tool_Mastery_Report.docx"))
    h1 = [p.text for p in doc.paragraphs if p.style.name == "Heading 1"]
    add("Word report opens", True,
        f"paragraphs={len(doc.paragraphs)} tables={len(doc.tables)} images={len(doc.inline_shapes)}")
    add("Word report has 15 numbered sections",
        all(any(x.startswith(f"{i}.") for x in h1) for i in range(1, 16)),
        f"headings={len(h1)}")
    add("Word report has captioned images", len(doc.inline_shapes) >= 4)
except Exception as exc:
    add("Word report opens", False, str(exc))

# Root docs and explicit limitation
for rel in ["README.md", "requirements.txt", "environment_check.py",
            "docs/environment_setup.md", "docs/troubleshooting.md",
            "docs/tool_version_inventory.md", "Excel_Lab/pivot_table_guide.md"]:
    add(f"root/support file: {rel}", exists(rel))
readme = open(os.path.join(ROOT, "README.md")).read()
add("README discloses Power BI limitation", "does **not** contain a fabricated `.pbix`" in readme)
add("Power BI M asset", exists("PowerBI_Lab/power_query_m.m"))
add("Power BI DAX asset", exists("PowerBI_Lab/dax_measures.dax"))
add("Power BI model guide", exists("PowerBI_Lab/data_model.md"))

passed = sum(ok for _, ok, _ in checks)
report = ["PROJECT QUALITY ASSURANCE", "=" * 92]
for name, ok, detail in checks:
    report.append(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))
report += ["=" * 92, f"AUTOMATED RESULT: {passed}/{len(checks)} checks passed",
           "", "MANUAL / PLATFORM-DEPENDENT ITEMS:",
           "[MANUAL REQUIRED] Build PowerBI_Business_Analytics.pbix on Windows using the supplied guide.",
           "[MANUAL REQUIRED] Open the .pbix and validate five KPI values; capture genuine screenshots.",
           "[MANUAL OPTIONAL] Create the native Excel PivotTable/PivotChart using pivot_table_guide.md.",
           "[MANUAL REQUIRED] Replace report cover placeholders and add the final GitHub repository URL.",
           "", "No .pbix file or Power BI screenshot is claimed as completed in this package."]
text = "\n".join(report) + "\n"
print(text)
os.makedirs(os.path.join(ROOT, "docs"), exist_ok=True)
open(os.path.join(ROOT, "docs", "qa_results.txt"), "w").write(text)
sys.exit(0 if passed == len(checks) else 1)
