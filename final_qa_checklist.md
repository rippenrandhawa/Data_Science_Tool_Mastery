# Final Quality-Assurance Checklist

Automated checks were executed by `build/qa_project.py`. Full evidence is in
`docs/qa_results.txt` (**80/80 automated checks passed**).

| Requirement | Status | Evidence / limitation |
|---|---|---|
| 1. All laboratory folders exist | PASS | Labs 1–9 present |
| 2. Practical exercises have implementations | PASS | Scripts, workbook, notebooks and build assets |
| 3. Python scripts parse and execute | PASS | Syntax checks; executed evidence files |
| 4. SQL runs against supplied database | PASS | 15/15 outputs captured from MariaDB 11.8 |
| 5. Excel formulas and dashboard work | PASS | 11/11 recalculation checks; country selector and charts |
| 6. Power BI project opens | **MANUAL REQUIRED** | No `.pbix` fabricated. Build on Windows using supplied M, DAX, model and guide, then validate five KPIs. |
| 7. Notebooks contain actual outputs | PASS | Jupyter 16/16 output cells; integrated notebook 7/7; zero errors |
| 8. Portfolio pieces documented | PASS | Four GitHub-ready READMEs |
| 9. Root README matches real structure | PASS | Manually reviewed and included in automated path checks |
| 10. Word report opens | PASS | python-docx read; LibreOffice converted to a 10-page PDF |
| 11. Screenshots match implementations | PASS / LIMITED | Four report figures are direct outputs of the executed visualisation lab. Power BI screenshots omitted because dashboard not built here. |
| 12. ZIP complete and healthy | Verified after packaging | `ZipFile.testzip()` result recorded with delivery |

## Manual completion before final employer submission

1. On Windows, build `PowerBI_Business_Analytics.pbix` using the supplied guide.
2. Confirm the five KPI values, save the `.pbix`, and capture genuine dashboard images.
3. Insert those images into the report if the evaluator requires Power BI screenshots.
4. Replace `[Your Name]`, `[Organisation Name]` and the GitHub URL on the report cover.
5. Optionally create the native Excel PivotTable/PivotChart using
   `Excel_Lab/pivot_table_guide.md`; the formula-driven pivot is already complete.

No missing manual item is represented as completed.
