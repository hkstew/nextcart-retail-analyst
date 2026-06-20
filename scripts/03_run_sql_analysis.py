"""
03_run_sql_analysis.py
Loads cleaned_sales_data.csv into a local SQLite database (nextcart.db)
and runs every query in sql/sales_analysis.sql, printing results so they
can be captured into the README as evidence of SQL proficiency.
"""

import sqlite3
import pandas as pd

CLEAN_PATH = "/home/claude/nextcart-retail-analysis/data/cleaned_sales_data.csv"
DB_PATH = "/home/claude/nextcart-retail-analysis/data/nextcart.db"
SQL_PATH = "/home/claude/nextcart-retail-analysis/sql/sales_analysis.sql"

df = pd.read_csv(CLEAN_PATH)
conn = sqlite3.connect(DB_PATH)
df.to_sql("sales", conn, if_exists="replace", index=False)

with open(SQL_PATH) as f:
    sql_text = f.read()

# split into individual queries: each statement ends with ';' and is preceded
# by a '-- Qn. <title>' comment line
import re
blocks = [b.strip() for b in sql_text.split(";") if b.strip()]
pairs = []
for block in blocks:
    title_match = re.search(r"--\s*(Q\d\.[^\n]*)", block)
    title = title_match.group(1).strip() if title_match else "Query"
    # strip all comment lines, keep only SQL
    sql_only = "\n".join(
        line for line in block.splitlines() if not line.strip().startswith("--")
    ).strip()
    if sql_only:
        pairs.append((title, sql_only + ";"))

output_lines = []
for title, sql in pairs:
    sql_clean = sql.strip()
    result = pd.read_sql_query(sql_clean, conn)
    output_lines.append(f"### {title}\n")
    output_lines.append(result.to_markdown(index=False))
    output_lines.append("\n")
    print(f"### {title}")
    print(result.to_string(index=False))
    print()

with open("/home/claude/nextcart-retail-analysis/sql/query_results.md", "w") as f:
    f.write("# SQL Query Results — NextCart Sales Analysis\n\n")
    f.write("\n".join(output_lines))

conn.close()
print("Saved results -> sql/query_results.md")
print("Saved database -> data/nextcart.db")
