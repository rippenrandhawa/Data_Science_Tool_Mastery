# Environment Setup — Data Science Tool Mastery

Primary method: **Windows PowerShell**. Linux / macOS equivalents are noted where they
differ. Every command below was executed and verified in a build environment; the
versions recorded in `docs/tool_version_inventory.md` are the ones that produced the
results in this project.

---

## 0. Verify the starting point

```powershell
python --version      # expect 3.11 or newer
git --version
```

If `python` is not recognised, install it from <https://python.org/downloads> and tick
**“Add Python to PATH”** during setup.

---

## 1. Python installation and verification

```powershell
# Install Python 3.13 from python.org (or use the Microsoft Store build).
# Then verify:
python --version
python -m pip --version
python -c "import sys; print(sys.executable)"
```

## 2. Create and activate a virtual environment with `venv`

```powershell
# From the project root (the folder holding README.md)
python -m venv .venv

# Activate (PowerShell)
.\.venv\Scripts\Activate.ps1

# If PowerShell blocks the script, run this once per machine:
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

# Verify activation - the prompt now starts with (.venv) and:
python -c "import sys; print(sys.prefix)"
```

> **Why a venv?** It keeps this project's package versions separate from every other
> Python project on the machine, so `requirements.txt` is the single source of truth.

## 3. Install the required packages

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Verify
python environment_check.py
```

`environment_check.py` prints a full report and writes
`docs/environment_check_report.txt`.

## 4. Install and launch JupyterLab

```powershell
python -m pip install jupyterlab
jupyter lab --version
jupyter lab            # opens http://localhost:8888/lab
```

To run a notebook headlessly (used to produce the evidence in this project):

```powershell
jupyter nbconvert --to notebook --execute --inplace `
    Jupyter_Lab\Jupyter_Analytics_Workflow.ipynb
```

## 5. Configure Visual Studio Code

1. Install from <https://code.visualstudio.com/>.
2. Install the extensions: **Python** (Microsoft), **Jupyter** (Microsoft),
   **MySQL** (Weijan Chen), **Excel Viewer**.
3. Select the interpreter: `Ctrl+Shift+P` → **Python: Select Interpreter** →
   choose `.venv\Scripts\python.exe`.
4. Recommended `settings.json` additions:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/Scripts/python.exe",
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "jupyter.notebookFileRoot": "${workspaceFolder}",
  "files.exclude": { "**/__pycache__": true, "**/.ipynb_checkpoints": true }
}
```

5. Open a notebook and confirm the kernel selector (top right) shows `.venv`.

## 6. MySQL setup and connection

Install **MySQL Community Server 8.x** (<https://dev.mysql.com/downloads/mysql/>) or
**MariaDB** (<https://mariadb.org/download/>), then:

```powershell
# Start the service
net start MySQL80

# Connect as root
mysql -u root -p

# Create the analyst account and the lab database
CREATE USER 'analyst'@'localhost' IDENTIFIED BY 'Analyst@2026';
GRANT ALL PRIVILEGES ON *.* TO 'analyst'@'localhost';
FLUSH PRIVILEGES;
```

Connect from Python (PyMySQL):

```python
import pymysql
conn = pymysql.connect(host="127.0.0.1", port=3306,
                       user="analyst", password="Analyst@2026",
                       database="retail_analytics", charset="utf8mb4")
```

Then build the lab database:

```powershell
python SQL_Lab\run_sql_lab.py
```

> The SQL in this project is standard MySQL/MariaDB SQL. It was developed and
> executed on **MariaDB 11.8**; it also runs unchanged on MySQL 8.

## 7. Git installation and configuration

```powershell
git --version
git config --global user.name  "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
git config --global core.autocrlf true     # Windows line-ending safety
```

## 8. Create the GitHub repository

1. Sign in to <https://github.com> → **New repository** → name it
   `Data_Science_Tool_Mastery`, keep it **Public**, do **not** add a README.
2. Back in PowerShell, from the project root:

```powershell
git init
git add .
git commit -m "Initial commit: tool mastery labs"
git branch -M main
git remote add origin https://github.com/<your-username>/Data_Science_Tool_Mastery.git
git push -u origin main
```

The exact branching / merging sequence used for this project is documented in
`Git_GitHub_Lab/README.md`.

## 9. Power BI Desktop setup

1. Download **Power BI Desktop** from <https://powerbi.microsoft.com/desktop/>
   (Windows only, free).
2. Install and sign in (or skip sign-in to work locally).
3. Follow `PowerBI_Lab/PowerBI_Business_Analytics_BUILD_GUIDE.md` to build the
   dashboard from the supplied Power Query and DAX scripts.

> Power BI cannot be installed on Linux or macOS. On those platforms use
> **Power BI Service** in a browser, or run the Windows build steps in a VM.

## 10. Excel workbook setup

1. Open `Excel_Lab\Excel_Data_Analysis_Lab.xlsx` in **Excel 2019 or newer**
   (XLOOKUP, IFS and TEXTJOIN need a modern version).
2. Enable editing if Excel opens it in Protected View.
3. Use the country dropdown on the **KPI_Dashboard** sheet.
4. To create the native PivotTable and PivotChart, follow
   `Excel_Lab\pivot_table_guide.md`.

---

## Linux / macOS notes (this project's build environment)

| Task | Command |
|---|---|
| Create venv | `python3 -m venv .venv && source .venv/bin/activate` |
| Install packages | `pip install -r requirements.txt` |
| Start MariaDB | `sudo mariadbd --user=mysql --datadir=/var/lib/mysql &` |
| Run SQL lab | `python3 SQL_Lab/run_sql_lab.py` |
| Recalculate Excel | `libreoffice --headless --calc --convert-to xlsx --outdir /tmp file.xlsx` |

The build environment used Debian 13, Python 3.13.18 and MariaDB 11.8.9.
