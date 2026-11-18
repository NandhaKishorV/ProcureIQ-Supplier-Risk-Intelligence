PROCUREIQ ENTERPRISE V6 — AI + SQL + POWER BI ADOPTED

Run:
python -m pip install -r requirements.txt
python -m streamlit run app.py

Data sources:
- Excel / CSV
- SQLAlchemy-compatible SQL databases (SQLite, SQL Server, PostgreSQL, MySQL with the appropriate driver)
- Power BI table exports (CSV/XLSX)

Power BI:
- ProcureIQ can ingest Power BI table exports.
- After analysis, use Power BI-ready CSV/XLSX downloads from the Power BI & SQL page.
- The exported model contains the risk score, anomaly score/flag, procurement metrics and source fields for Power BI reporting.
- A .pbix file itself is not treated as a generic data interchange file; use a governed table/export or database source.

SQL:
- Connect to a SQLAlchemy-compatible database with a read-only source query.
- Export the analyzed ProcureIQ model back to a SQL table.
- For SQL Server/PostgreSQL/MySQL, install the appropriate Python DB driver for the chosen connection string.

AI/ML:
- Isolation Forest unsupervised anomaly detection
- Standardized procurement behavior features
- AI anomaly score and anomaly flag
- AI assessment combines ML signals with transparent procurement risk drivers
- Transparent weighted risk score remains separate from the ML layer

Recommended enterprise architecture:
ERP / Procurement System -> SQL Database -> ProcureIQ AI/ML -> ProcureIQ Model Table -> Power BI


SQL SCRIPT FIX (v9): SQL scripts are executed in an in-memory SQLite staging database, preventing Windows file-lock errors during Streamlit reruns.
