# Tool and Version Inventory

Versions below were detected in the build/verification environment on 21 November
2026. `requirements.txt` pins the Python stack.

| Category | Tool | Version used | Role | Analyst priority |
|---|---|---:|---|---|
| Language | Python | 3.13.18 | automation and analysis | Essential |
| Arrays | NumPy | 2.3.5 | vectorised numerical operations | Essential |
| Data frames | pandas | 2.2.3 | cleaning and aggregation | Essential |
| Statistics | SciPy | 1.17.1 | distributions and hypothesis tests | Essential |
| Static charts | Matplotlib | 3.11.2 | controlled report graphics | Essential |
| Statistical charts | Seaborn | 0.13.2 | distributions and heatmaps | Essential |
| Interactive charts | Plotly | 6.0.1 | browser-based exploration | Useful |
| Machine learning | scikit-learn | 1.6.1 | optional predictive extension | Optional DS |
| Excel automation | openpyxl | 3.1.5 | workbook construction | Useful |
| Notebooks | JupyterLab | 4.6.6 | documented interactive workflow | Essential |
| Database | MariaDB | 11.8.9 | MySQL-compatible SQL engine | Essential |
| Python DB driver | PyMySQL | 2.2.8 | database connection | Essential |
| Version control | Git | 2.47.3 | history and collaboration | Essential |
| Spreadsheet verification | LibreOffice Calc | 25.2.3 | headless formula recalculation | Build/QA |
| Report generation | python-docx | 1.1.2 | Word report construction | Build/QA |
| IDE | VS Code | Manual Windows install | development environment | Essential |
| Spreadsheet GUI | Microsoft Excel | 2019+ recommended | formulas, pivots, dashboard | Essential |
| BI platform | Power BI Desktop | Current Windows release | semantic model and dashboard | Essential BI |

## Essential vs optional

**Core Data Analyst:** Excel, SQL/MySQL, Python/pandas/NumPy, visualisation,
statistics, Jupyter, Git/GitHub and Power BI.

**Optional Data Science extension:** scikit-learn preprocessing, regression,
classification, tree models, cross-validation and model evaluation. These are not
claimed as core analyst mastery merely because Lab 9 was completed.
