"""Build the formal Data Science Tool Mastery Word report."""

import os
import shutil
from datetime import date

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "Report", "Data_Science_Tool_Mastery_Report.docx")
SCREEN = os.path.join(ROOT, "Screenshots")
CHARTS = os.path.join(ROOT, "Data_Visualization_Lab", "outputs", "charts")

NAVY = "17365D"
BLUE = "2F5597"
LIGHT = "D9EAF7"
GREY = "666666"
WHITE = "FFFFFF"


def shade(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_cell_text(cell, text, bold=False, color=None):
    cell.text = ""
    p = cell.paragraphs[0]
    r = p.add_run(str(text))
    r.bold = bold
    if color:
        r.font.color.rgb = RGBColor.from_string(color)
    r.font.size = Pt(9)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def table(doc, headers, rows, widths=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        shade(t.rows[0].cells[i], NAVY)
        set_cell_text(t.rows[0].cells[i], h, True, WHITE)
    for ridx, row in enumerate(rows):
        cells = t.add_row().cells
        for i, value in enumerate(row):
            set_cell_text(cells[i], value)
            if ridx % 2:
                shade(cells[i], "F3F6F9")
    t.autofit = True
    doc.add_paragraph()
    return t


def add_page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "1"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    for element in (begin, instr, separate, text, end):
        run._r.append(element)


def add_caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    r.italic = True
    r.font.size = Pt(9)
    r.font.color.rgb = RGBColor.from_string(GREY)


def picture(doc, filename, caption):
    path = os.path.join(CHARTS, filename)
    if os.path.exists(path):
        doc.add_picture(path, width=Inches(6.25))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_caption(doc, caption)


def bullet(doc, text, level=0):
    doc.add_paragraph(text, style="List Bullet" if level == 0 else "List Bullet 2")


def heading(doc, number, title):
    doc.add_heading(f"{number}. {title}", level=1)


def build():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    os.makedirs(SCREEN, exist_ok=True)
    for f in ["01_monthly_revenue_trend.png", "02_revenue_by_country.png",
              "06_correlation_heatmap.png", "08_top_products_revenue.png"]:
        shutil.copy2(os.path.join(CHARTS, f), os.path.join(SCREEN, f))

    doc = Document()
    sec = doc.sections[0]
    sec.top_margin = Inches(.7)
    sec.bottom_margin = Inches(.7)
    sec.left_margin = Inches(.8)
    sec.right_margin = Inches(.8)
    sec.header_distance = Inches(.3)
    sec.footer_distance = Inches(.35)

    styles = doc.styles
    styles["Normal"].font.name = "Aptos"
    styles["Normal"].font.size = Pt(10)
    styles["Normal"].paragraph_format.space_after = Pt(6)
    for name, size, colour in [("Title", 30, NAVY), ("Heading 1", 19, NAVY),
                                ("Heading 2", 14, BLUE), ("Heading 3", 11, BLUE)]:
        styles[name].font.name = "Aptos Display"
        styles[name].font.size = Pt(size)
        styles[name].font.color.rgb = RGBColor.from_string(colour)
        styles[name].font.bold = True

    header = sec.header.paragraphs[0]
    header.text = "DATA SCIENCE TOOL MASTERY  |  DATA ANALYST INTERNSHIP — TASK 4"
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    header.runs[0].font.size = Pt(8)
    header.runs[0].font.color.rgb = RGBColor.from_string(GREY)
    add_page_number(sec.footer.paragraphs[0])

    # Cover
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.space_after = Pt(18)
    r = p.add_run("DATA SCIENCE\nTOOL MASTERY")
    r.bold = True
    r.font.name = "Aptos Display"
    r.font.size = Pt(34)
    r.font.color.rgb = RGBColor.from_string(NAVY)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("A practical Data Analyst skills portfolio")
    r.font.size = Pt(17)
    r.font.color.rgb = RGBColor.from_string(BLUE)
    doc.add_paragraph("\n")
    table(doc, ["Submission detail", "Value"], [
        ("Task", "Data Analyst Internship — Task 4"),
        ("Prepared by", "[Your Name]"),
        ("Internship / organisation", "[Organisation Name]"),
        ("Specialisation", "Data Analytics (Data Science progression)"),
        ("Dataset", "UCI Online Retail — real transaction data"),
        ("Submission date", "21 November 2026"),
        ("Repository", "[Insert GitHub repository URL]"),
    ])
    p = doc.add_paragraph("WORKING IMPLEMENTATIONS  •  GENUINE OUTPUTS  •  REPRODUCIBLE EVIDENCE")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.runs[0].bold = True
    p.runs[0].font.color.rgb = RGBColor.from_string(NAVY)
    doc.add_page_break()

    # TOC (manual, stable)
    doc.add_heading("Contents", level=1)
    for i, title in enumerate([
        "Cover Page", "Executive Summary", "Project Introduction", "Learning Objectives",
        "Tools and Technologies", "Environment Setup", "Individual Laboratory Exercises",
        "Practical Implementations", "Screenshots and Outputs", "Integrated Business Project",
        "Portfolio Pieces", "Skills Demonstrated", "Challenges and Solutions", "Conclusion",
        "References"], 1):
        doc.add_paragraph(f"{i}. {title}")
    doc.add_page_break()

    heading(doc, 1, "Cover Page")
    doc.add_paragraph("The preceding page is the formal cover page. The prepared-by, organisation and repository fields are editable placeholders for the candidate to complete before submission.")

    heading(doc, 2, "Executive Summary")
    doc.add_paragraph("This project demonstrates practical proficiency with the core tools expected of a Data Analyst: Python, NumPy, pandas, SQL/MySQL, Excel, statistics, visualisation, Power BI, Jupyter and Git. Every completed claim is supported by an executable implementation or captured output. A consistent extract of the real UCI Online Retail dataset is reused across tools so that the workflow resembles professional analytics rather than disconnected tutorials.")
    table(doc, ["Outcome", "Verified result"], [
        ("Shared dataset", "12,177 lines; 500 invoices; GBP 239,642.62 revenue"),
        ("Python", "6 exercises executed; CSV, Excel and JSON evidence"),
        ("SQL", "15/15 queries executed against MariaDB 11.8"),
        ("Excel", "6 sheets; dashboard; independent formula verification 11/11"),
        ("Visualisation", "8 PNGs at 200 DPI; 2 interactive HTML files"),
        ("Statistics", "10 exercises with reasoning and outputs"),
        ("Jupyter", "Two executed notebooks; 0 cell errors"),
        ("Git", "Real repository with branch, merge and annotated tag"),
        ("Machine learning", "5 exercises; optional Data Science extension"),
        ("Power BI", "Complete M/DAX/model package; manual Windows assembly disclosed"),
    ])
    doc.add_paragraph("The preferred Indian e-commerce scenario was evaluated, but no sufficiently trustworthy public transaction source with customer, order and time dimensions was available without presenting unverified or synthetic data as real. The documented UCI source was chosen to protect the evidence standard.")

    heading(doc, 3, "Project Introduction")
    doc.add_paragraph("The business scenario is an online retailer asking three recurring questions: where does revenue come from, which customers and products matter most, and how should activity be monitored? A seeded 500-invoice extract was created from the UCI source. Duplicates were removed, cancellations and non-product codes were flagged, and relational tables were built for customers, products, orders and order items.")
    table(doc, ["Dataset metric", "Value"], [
        ("Source rows", "541,909"), ("Duplicate rows removed", "5,268"),
        ("Project sample", "12,177 transaction lines"), ("Invoices", "500"),
        ("Registered customers", "394"), ("Distinct products", "2,497"),
        ("Revenue", "GBP 239,642.62"), ("Period", "1 Dec 2010 – 8 Dec 2011")])

    heading(doc, 4, "Learning Objectives")
    for item in [
        "Use Python, NumPy and pandas to load, clean, transform and aggregate business data.",
        "Design a relational database and answer 15 progressively harder questions with SQL.",
        "Build and independently verify an Excel analytical dashboard.",
        "Choose and interpret static, statistical and interactive visualisations.",
        "Apply descriptive statistics, confidence intervals, tests, correlation and regression.",
        "Document an end-to-end analysis in an executed notebook.",
        "Use genuine Git history rather than describing version control theoretically.",
        "Understand introductory machine learning without overstating it as analyst mastery.",
    ]: bullet(doc, item)

    heading(doc, 5, "Tools and Technologies")
    table(doc, ["Category", "Tools", "Status"], [
        ("Programming", "Python 3.13, NumPy 2.3, pandas 2.2", "Core analyst"),
        ("Database", "MariaDB 11.8 / MySQL SQL, PyMySQL", "Core analyst"),
        ("Visualisation", "Matplotlib, Seaborn, Plotly", "Core analyst"),
        ("Spreadsheet", "Excel, openpyxl, LibreOffice verification", "Core analyst"),
        ("Business intelligence", "Power BI, Power Query M, DAX", "Core BI"),
        ("Statistics", "SciPy", "Core analyst"),
        ("Workflow", "JupyterLab, VS Code instructions, Git/GitHub", "Core professional"),
        ("Machine learning", "scikit-learn", "Optional DS extension"),
    ])

    heading(doc, 6, "Environment Setup")
    doc.add_paragraph("Windows PowerShell is the primary setup path. The project includes a pinned requirements file, a verification script, installation instructions, troubleshooting guidance and a tool inventory. The verified build used Python 3.13.18, MariaDB 11.8.9 and LibreOffice Calc 25.2.3.")
    doc.add_paragraph("Primary commands:")
    p = doc.add_paragraph(style="Intense Quote")
    p.add_run("python -m venv .venv\n.\\.venv\\Scripts\\Activate.ps1\npython -m pip install -r requirements.txt\npython environment_check.py")
    doc.add_paragraph("The environment checker verifies packages, external tools, database connectivity and required project files, then writes a text report to docs/environment_check_report.txt.")

    heading(doc, 7, "Individual Laboratory Exercises")
    table(doc, ["Lab", "Scope", "Evidence"], [
        ("1 Python", "6 exercises: structures, I/O, NumPy, pandas, cleaning", "Executed text + CSV/XLSX/JSON"),
        ("2 SQL", "Schema, keys, inserts and 15 analytical queries", "15 captured result sets"),
        ("3 Excel", "Formulas, data validation, pivots, dashboard", "Workbook + 11/11 verifier"),
        ("4 Visualisation", "bar, line, histogram, box, scatter, heatmap, interactive", "8 PNG + 2 HTML"),
        ("5 Statistics", "10 exercises from central tendency to A/B reasoning", "Executed text evidence"),
        ("6 Power BI", "Power Query, relationships, DAX and report design", "M/DAX/model/build guide"),
        ("7 Jupyter", "Combined documented analytical workflow", "27-cell executed notebook"),
        ("8 Git/GitHub", "init, stage, commit, branch, merge, tag", "Real .git history"),
        ("9 ML", "preprocessing, regression, classification, trees", "Executed evidence"),
    ])

    heading(doc, 8, "Practical Implementations")
    doc.add_heading("8.1 Python and pandas", level=2)
    doc.add_paragraph("The Python lab reads both CSV and Excel files, compares standard-library and pandas I/O, audits data quality, flags outliers and exports summaries. The top 20% of registered customers generate 59.7% of registered revenue.")
    doc.add_heading("8.2 SQL database", level=2)
    doc.add_paragraph("Four normalised tables enforce primary and foreign keys. The query set progresses from SELECT/WHERE to CTEs and window functions. SQL revenue is lower than the flat-file figure because the relational model intentionally excludes 2,698 guest lines without customer IDs; this difference is documented rather than hidden.")
    doc.add_heading("8.3 Excel", level=2)
    doc.add_paragraph("The workbook contains Raw_Data, Clean_Data, Formulas_Demo, Pivot_View, KPI_Dashboard and README sheets. Nine KPI formulas and three charts respond to the country selector. Headless recalculation was compared with pandas: 11 of 11 checks passed.")
    doc.add_heading("8.4 Statistics and ML", level=2)
    doc.add_paragraph("Line revenue is strongly right-skewed (skewness 35.12), so median and IQR are preferred. A Welch test identifies a UK/overseas difference but cannot establish causation. The optional ML lab reports a majority baseline, confusion matrix and train/test gap rather than accuracy alone.")
    table(doc, ["ML model", "Verified result"], [
        ("Linear regression", "RMSE 57.36; MAE 12.18; R² 0.6374"),
        ("Logistic regression", "Precision 0.7850; Recall 0.4773; F1 0.5936"),
        ("Majority baseline", "Accuracy 0.9257; zero positive recall"),
        ("Decision tree depth 4", "5-fold CV F1 0.8740 ± 0.0494"),
    ])

    heading(doc, 9, "Screenshots and Outputs")
    picture(doc, "01_monthly_revenue_trend.png", "Figure 1. Monthly revenue trend generated by the executed visualisation lab (200 DPI).")
    picture(doc, "02_revenue_by_country.png", "Figure 2. Revenue by country, showing the concentration in the United Kingdom (200 DPI).")
    picture(doc, "06_correlation_heatmap.png", "Figure 3. Spearman correlation heatmap from the real sample (200 DPI).")
    picture(doc, "08_top_products_revenue.png", "Figure 4. Top products by revenue from the executed visualisation lab (200 DPI).")
    doc.add_paragraph("Excel evidence is the workbook itself plus the independent recalculation report. Power BI screenshots are intentionally omitted because no interactive report was built in this Linux environment; including invented screenshots would violate the project standard.")

    heading(doc, 10, "Integrated Business Project")
    doc.add_paragraph("The integrated notebook connects ten stages without artificial duplication. pandas is used for data understanding, SQL for governed aggregation, Excel for stakeholder delivery, Python visualisation for communication, Power BI assets for self-service exploration, Jupyter for reproducibility and Git for change history.")
    table(doc, ["Finding", "Computed value", "Business implication"], [
        ("UK concentration", "81.98% of revenue", "Protect base; diversify markets"),
        ("Customer concentration", "Top 20% = 59.7%", "Prioritise retention"),
        ("Peak month", "Jan 2011; GBP 35,715.76", "Investigate seasonality before scaling"),
        ("Guest data gap", "2,698 lines", "Encourage account registration"),
        ("Right-skewed values", "Median GBP 10.50; mean GBP 19.68", "Use robust summaries"),
    ])

    heading(doc, 11, "Portfolio Pieces")
    table(doc, ["Piece", "Deliverable", "Portfolio value"], [
        ("Python Data Analysis", "Script, notebook, evidence, charts", "Shows cleaning, analysis and communication"),
        ("SQL Business Intelligence", "Schema, loader, 15 queries, outputs", "Shows relational thinking and advanced SQL"),
        ("Excel Analytics Dashboard", "Functional .xlsx + verifier", "Shows stakeholder-ready spreadsheet work"),
        ("Power BI Dashboard Build", "M, DAX, star schema, guide", "Shows model and measure design; manual build disclosed"),
    ])

    heading(doc, 12, "Skills Demonstrated")
    doc.add_paragraph("The assessment contains 60 practical tasks: 10 Python, 15 SQL, 10 Excel, and five each for visualisation, statistics, Power BI, Git/GitHub and machine learning. Each task specifies difficulty, expected outcome and evaluation criteria. The answer key is separate. No automatic mastery label is assigned.")
    table(doc, ["Skill", "Practical evidence"], [
        ("Data cleaning", "Flags, dtypes, duplicates, quality counts"),
        ("Business querying", "15 SQL result sets"),
        ("Spreadsheet modelling", "11/11 verified KPIs"),
        ("Visual communication", "8 report-grade figures + 2 interactive charts"),
        ("Statistical reasoning", "Assumptions, intervals, tests and limitations"),
        ("Reproducibility", "Fixed seed, relative paths, pinned packages, notebooks"),
        ("Collaboration", "Real commit, branch, merge and tag history"),
    ])

    heading(doc, 13, "Challenges and Solutions")
    table(doc, ["Challenge", "Solution and evidence"], [
        ("Reliable native Excel PivotTable authoring", "Used a verified formula-driven pivot and supplied the two-minute native PivotTable guide."),
        ("Excel modern functions showed #NAME?", "Stored functions with the OOXML _xlfn prefix; recalculated the file in LibreOffice."),
        ("Distinct invoice formula divided by zero", "Added a transparent First Line of Invoice helper and validated its total equals 500."),
        ("MySQL unavailable initially", "Installed and ran MariaDB; created a real database and executed all 15 queries."),
        ("Power BI Desktop unavailable on Linux", "Delivered real M/DAX/schema assets and disclosed the manual Windows build; no fake .pbix or screenshots."),
        ("Preferred Indian source quality", "Selected a documented real UCI dataset rather than label suspicious synthetic data as real."),
        ("Class imbalance in ML", "Reported a majority baseline, precision, recall, F1, AUC and a confusion matrix."),
    ])

    heading(doc, 14, "Conclusion")
    doc.add_paragraph("The project meets its main objective: it demonstrates practical Data Analyst capability through working artefacts rather than theory. The implementation shows that the tools are complementary: Python prepares and tests, SQL governs and aggregates, Excel communicates, visualisation explains, Power BI structures self-service reporting, Jupyter documents and Git preserves the history. The optional machine-learning extension is evaluated honestly and is not used to overstate proficiency.")
    doc.add_paragraph("The only material manual completion item is the Power BI Desktop report. It requires Windows, and the exact build and validation steps are supplied. This exception is visible in the README, lab documentation and quality-assurance checklist.")

    heading(doc, 15, "References")
    refs = [
        "Chen, D., Sain, S. L., & Guo, K. (2012). Data mining for the online retail industry: A case study of RFM model-based customer segmentation using data mining. Journal of Database Marketing & Customer Strategy Management, 19, 197–208.",
        "UCI Machine Learning Repository. (2015). Online Retail [Dataset 352]. https://doi.org/10.24432/C5BW33",
        "pandas Development Team. pandas documentation. https://pandas.pydata.org/docs/",
        "NumPy Developers. NumPy documentation. https://numpy.org/doc/",
        "SciPy Community. SciPy documentation. https://docs.scipy.org/doc/scipy/",
        "MySQL. MySQL 8.0 Reference Manual. https://dev.mysql.com/doc/",
        "Microsoft. Power BI documentation. https://learn.microsoft.com/power-bi/",
        "scikit-learn Developers. scikit-learn User Guide. https://scikit-learn.org/stable/user_guide.html",
        "Git Project. Git documentation. https://git-scm.com/doc",
    ]
    for ref in refs:
        doc.add_paragraph(ref, style="List Number")

    # Document properties
    props = doc.core_properties
    props.title = "Data Science Tool Mastery Report"
    props.subject = "Data Analyst Internship Task 4"
    props.author = "[Your Name]"
    props.keywords = "Data Analytics, Python, SQL, Excel, Power BI, Portfolio"

    doc.save(OUT)
    print(f"report written: {OUT}")
    print(f"paragraphs: {len(doc.paragraphs)} | tables: {len(doc.tables)} | images: 4")


if __name__ == "__main__":
    build()
