# Troubleshooting Guide

| Symptom | Likely cause | Resolution |
|---|---|---|
| `python` is not recognised | Python not on PATH | Reinstall from python.org and select **Add Python to PATH**, or use `py` on Windows. |
| `Activate.ps1 cannot be loaded` | PowerShell execution policy | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then activate again. |
| `ModuleNotFoundError` | Wrong interpreter / venv | Activate `.venv`; run `python -m pip install -r requirements.txt`; select the same interpreter in VS Code. |
| Jupyter kernel is missing | `ipykernel` not registered | `python -m ipykernel install --user --name tool-mastery`. |
| Notebook uses stale values | Cells run out of order | Kernel → Restart Kernel and Run All Cells. |
| `Can't connect to MySQL server` | Service stopped or wrong port | Windows: `net start MySQL80`; verify `mysql -h 127.0.0.1 -P 3306 -u analyst -p`. |
| MySQL access denied | Account/host mismatch | Recreate `'analyst'@'localhost'`; check `DB_USER`, `DB_PASSWORD`, and host. |
| SQL foreign-key load fails | Tables loaded in wrong order | Load customers/products, then orders, then order_items; use `run_sql_lab.py`. |
| Excel shows `#NAME?` | Old Excel / modern function prefix | Use Excel 2019+; formulas in the supplied workbook include `_xlfn.` where required. |
| Excel KPI does not change | Formula calculation set to manual | Formulas → Calculation Options → Automatic, then `Ctrl+Alt+F9`. |
| PivotTable source is wrong | Selected a range instead of table | Set source to Excel Table `tblRaw`; refresh. |
| Plotly HTML is blank in the workspace preview | Sandboxed preview blocks external network | The files are self-contained; download/open in a normal browser. |
| Matplotlib has no display | Headless machine | The scripts use the non-interactive `Agg` backend and save PNGs. |
| Power BI cannot be installed | Non-Windows OS | Use Windows 10/11 or a Windows VM; follow the supplied build guide. |
| Power BI measure is blank | Date table not marked or relationship inactive | Mark `dim_date`; check relationship direction and active status. |
| `git push` asks for a password | GitHub stopped password auth | Use a Personal Access Token or Git Credential Manager. |
| Large files rejected by GitHub | File over 100 MB | Use Git LFS or release assets; do not commit raw source workbooks. |
| Re-running Git lab says repository exists | Demo repo already built | The delivered repo is complete; inspect it instead of rebuilding. |

## Clean rebuild order

```powershell
python build\prepare_data.py
python Python_Lab\python_lab.py
python SQL_Lab\run_sql_lab.py
python Excel_Lab\build_excel.py
python Excel_Lab\verify_excel.py
python Data_Visualization_Lab\visualization_lab.py
python Statistics_Lab\statistics_lab.py
python Machine_Learning_Lab\ml_lab.py
python environment_check.py
```

The Power BI `.pbix` and native Excel PivotTable require the manual GUI steps described
in their build guides.
