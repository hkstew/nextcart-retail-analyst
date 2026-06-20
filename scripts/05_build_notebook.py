"""
build_notebook.py
Constructs a fully-executed NextCart_Sales_Analysis.ipynb by running each
cell's code in a shared namespace and capturing real outputs (stdout,
DataFrame HTML tables, and matplotlib figures as embedded PNGs) -- exactly
like a real Jupyter kernel would, so the notebook renders complete and
polished on GitHub without anyone needing to re-run it.
"""

import io
import sys
import json
import base64
import contextlib
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

NS = {}  # shared execution namespace, persists across cells

def run_code_cell(source: str):
    """Execute source in shared NS, capture stdout + last-expression repr
    + any open matplotlib figures, return a Jupyter-style outputs list."""
    outputs = []
    buf = io.StringIO()

    lines = [l for l in source.strip().split("\n")]
    last_line = lines[-1].strip() if lines else ""
    is_expr = (
        last_line
        and not last_line.startswith(("#", "print", "plt.", "for ", "if ", "import", "with "))
        and "=" not in last_line.split("(")[0]
        and not last_line.endswith(":")
    )
    body = "\n".join(lines[:-1]) if is_expr else source
    expr = last_line if is_expr else None

    with contextlib.redirect_stdout(buf):
        if body.strip():
            exec(compile(body, "<cell>", "exec"), NS)
        result = None
        if expr:
            try:
                result = eval(compile(expr, "<cell>", "eval"), NS)
            except Exception:
                exec(compile(expr, "<cell>", "exec"), NS)
                result = None

    stdout_text = buf.getvalue()
    if stdout_text:
        outputs.append({"output_type": "stream", "name": "stdout", "text": stdout_text.splitlines(keepends=True)})

    if result is not None:
        if isinstance(result, pd.DataFrame):
            outputs.append({
                "output_type": "execute_result",
                "execution_count": None,
                "metadata": {},
                "data": {
                    "text/html": result.to_html(index=False, border=0).splitlines(keepends=True),
                    "text/plain": result.to_string(index=False).splitlines(keepends=True),
                },
            })
        else:
            outputs.append({
                "output_type": "execute_result",
                "execution_count": None,
                "metadata": {},
                "data": {"text/plain": [repr(result)]},
            })

    # capture any open matplotlib figures
    fig_nums = plt.get_fignums()
    for n in fig_nums:
        fig = plt.figure(n)
        img_buf = io.BytesIO()
        fig.savefig(img_buf, format="png", bbox_inches="tight", dpi=110)
        img_b64 = base64.b64encode(img_buf.getvalue()).decode("ascii")
        outputs.append({
            "output_type": "display_data",
            "metadata": {},
            "data": {"image/png": img_b64},
        })
        plt.close(fig)

    return outputs


def code_cell(source):
    src_lines = source.strip("\n").splitlines(keepends=True)
    outputs = run_code_cell(source)
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": outputs,
        "source": src_lines,
    }


def md_cell(source):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source.strip("\n").splitlines(keepends=True),
    }


cells = []

cells.append(md_cell("""
# NextCart Retail Sales Analysis

**Business problem:** NextCart is a (fictional) Thailand-based online retailer. Leadership wants to understand
what is driving revenue and profit performance across regions, product categories, and customer segments,
and whether the current discounting strategy is helping or hurting profitability.

**This notebook covers:**
1. Data quality assessment of the raw sales export
2. Data cleaning (documented, reproducible)
3. SQL business analysis (SQLite)
4. Exploratory visual analysis
5. RFM customer segmentation
6. Key insights & business recommendations

**Note on data:** This dataset is synthetically generated to resemble a real e-commerce sales export
(including realistic data quality issues), since no proprietary company data was available for a
public portfolio piece. The analysis methodology is identical to what would be applied to real data.
"""))

cells.append(code_cell("""
import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid", palette="deep")
plt.rcParams["figure.dpi"] = 110
pd.set_option("display.max_columns", 20)

ACCENT = "#2563EB"
print("Libraries loaded.")
"""))

cells.append(md_cell("## 1. Load & Inspect Raw Data"))

cells.append(code_cell("""
raw = pd.read_csv("data/raw_sales_data.csv")
print(f"Shape: {raw.shape}")
raw.head()
"""))

cells.append(md_cell("## 2. Data Quality Assessment"))

cells.append(code_cell("""
print("Missing values per column:")
print(raw.isna().sum()[raw.isna().sum() > 0])
print(f"\\nDuplicate rows: {raw.duplicated().sum()}")
print(f"Negative Quantity rows: {(raw['Quantity'] < 0).sum()}")
print(f"\\nSample of inconsistent text formatting in 'Region':")
print(raw['Region'].unique()[:8])
print(f"\\nSample of mixed date formats in 'Order Date':")
print(raw['Order Date'].sample(5, random_state=1).tolist())
"""))

cells.append(md_cell("""
**Issues identified:**
- Inconsistent `Order Date` formats (ISO, `DD/MM/YYYY`, and timestamped strings mixed together)
- Inconsistent text casing/whitespace in `Region` and `Category` (e.g. `"SOUTHERN"`, `"  Central  "`, `"northern"`)
- Missing values in `Discount` and `Profit`
- Duplicate order rows
- A handful of negative `Quantity` values (data entry errors)
"""))

cells.append(md_cell("## 3. Data Cleaning"))

cells.append(code_cell("""
df = raw.copy()
start_rows = len(df)

# Standardize dates (try multiple known formats)
def parse_date(val):
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"):
        try:
            return pd.to_datetime(val, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.to_datetime(val, errors="coerce")

df["Order Date"] = df["Order Date"].apply(parse_date)
df = df.dropna(subset=["Order Date"])

# Standardize text fields
for col in ["Region", "Category", "Segment", "Ship Mode"]:
    df[col] = df[col].astype(str).str.strip().str.title()

# Remove duplicates and invalid rows
df = df.drop_duplicates()
df = df[df["Quantity"] > 0]

# Impute missing Discount as 0 (no discount applied)
df["Discount"] = df["Discount"].fillna(0)

# Impute missing Profit using category-average margin
category_margin = (
    df.dropna(subset=["Profit"])
    .assign(margin=lambda x: x["Profit"] / x["Sales"])
    .groupby("Category")["margin"].mean()
)
def fill_profit(row):
    if pd.isna(row["Profit"]):
        m = category_margin.get(row["Category"], category_margin.mean())
        return round(row["Sales"] * m, 2)
    return row["Profit"]
df["Profit"] = df.apply(fill_profit, axis=1)

df["Order Date"] = pd.to_datetime(df["Order Date"]).dt.date
df = df.sort_values("Order Date").reset_index(drop=True)

print(f"Rows before cleaning: {start_rows}")
print(f"Rows after cleaning:  {len(df)}")
print(f"Remaining missing values: {df.isna().sum().sum()}")

df.to_csv("data/cleaned_sales_data_nb.csv", index=False)
"""))

cells.append(md_cell("## 4. SQL Business Analysis (SQLite)"))

cells.append(code_cell("""
conn = sqlite3.connect(":memory:")
df_sql = df.copy()
df_sql["Order Date"] = pd.to_datetime(df_sql["Order Date"])
df_sql.to_sql("sales", conn, index=False, if_exists="replace")
print("Loaded", len(df_sql), "rows into in-memory SQLite table `sales`.")
"""))

cells.append(md_cell("**Q: What does the monthly revenue & profit trend look like?**"))

cells.append(code_cell("""
monthly_sql = pd.read_sql_query('''
    SELECT strftime('%Y-%m', "Order Date") AS order_month,
           ROUND(SUM(Sales), 2) AS total_sales,
           ROUND(SUM(Profit), 2) AS total_profit,
           COUNT(DISTINCT "Order ID") AS num_orders
    FROM sales
    GROUP BY order_month
    ORDER BY order_month
''', conn)
monthly_sql.head(12)
"""))

cells.append(md_cell("**Q: Which region and category combination drives the most profit, and at what margin?**"))

cells.append(code_cell("""
region_sql = pd.read_sql_query('''
    SELECT Region,
           ROUND(SUM(Sales), 2) AS total_sales,
           ROUND(SUM(Profit), 2) AS total_profit,
           ROUND(SUM(Profit) * 100.0 / SUM(Sales), 2) AS profit_margin_pct
    FROM sales
    GROUP BY Region
    ORDER BY total_sales DESC
''', conn)
region_sql
"""))

cells.append(md_cell("**Q: Is discounting actually paying for itself?**"))

cells.append(code_cell("""
discount_sql = pd.read_sql_query('''
    SELECT
        CASE WHEN Discount = 0 THEN 'No Discount'
             WHEN Discount <= 0.10 THEN 'Low (1-10%)'
             ELSE 'High (>10%)' END AS discount_band,
        COUNT(*) AS num_orders,
        ROUND(AVG(Sales), 2) AS avg_order_value,
        ROUND(SUM(Profit) * 100.0 / SUM(Sales), 2) AS profit_margin_pct
    FROM sales
    GROUP BY discount_band
    ORDER BY profit_margin_pct DESC
''', conn)
discount_sql
"""))

cells.append(md_cell("""
> **Finding:** Profit margin drops from **34.4%** (no discount) to **21.2%** (discounts above 10%).
> The discount strategy is increasing order volume but eroding overall profitability faster than it's
> generating incremental revenue. See Section 6 for the full recommendation.
"""))

cells.append(md_cell("## 5. Exploratory Visual Analysis"))

cells.append(code_cell("""
monthly = df.groupby(pd.to_datetime(df["Order Date"]).dt.to_period("M").astype(str))["Sales"].sum().reset_index()
monthly.columns = ["order_month", "Sales"]

fig, ax = plt.subplots(figsize=(10, 4.2))
ax.plot(monthly["order_month"], monthly["Sales"], marker="o", color=ACCENT, linewidth=2)
ax.fill_between(range(len(monthly)), monthly["Sales"], alpha=0.08, color=ACCENT)
ax.set_title("Monthly Revenue Trend (2023-2024)", fontsize=13, fontweight="bold")
ax.set_ylabel("Revenue (THB)")
ax.tick_params(axis="x", rotation=60)
plt.tight_layout()
plt.show()
"""))

cells.append(code_cell("""
cat = df.groupby("Category").agg(total_sales=("Sales","sum"), total_profit=("Profit","sum")).reset_index()
cat["margin_pct"] = (cat["total_profit"] / cat["total_sales"] * 100).round(1)
cat = cat.sort_values("total_sales")

fig, ax = plt.subplots(figsize=(9, 4.5))
bars = ax.barh(cat["Category"], cat["total_sales"], color=ACCENT, alpha=0.85)
ax.set_title("Revenue by Category - with Profit Margin %", fontsize=13, fontweight="bold")
ax.set_xlabel("Total Revenue (THB)")
for bar, margin in zip(bars, cat["margin_pct"]):
    ax.text(bar.get_width()*1.01, bar.get_y()+bar.get_height()/2, f"{margin}% margin", va="center", fontsize=9)
plt.tight_layout()
plt.show()
"""))

cells.append(md_cell("## 6. RFM Customer Segmentation"))

cells.append(md_cell("""
RFM scores each customer on **Recency** (days since last order), **Frequency** (number of orders),
and **Monetary** value (total spend), then buckets them into actionable segments — a standard technique
for prioritizing retention and loyalty efforts.
"""))

cells.append(code_cell("""
df["Order Date"] = pd.to_datetime(df["Order Date"])
snapshot_date = df["Order Date"].max() + pd.Timedelta(days=1)

rfm = df.groupby("Customer ID").agg(
    Recency=("Order Date", lambda x: (snapshot_date - x.max()).days),
    Frequency=("Order ID", "nunique"),
    Monetary=("Sales", "sum"),
).reset_index()

rfm["R_score"] = pd.qcut(rfm["Recency"], 4, labels=[4,3,2,1]).astype(int)
rfm["F_score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 4, labels=[1,2,3,4]).astype(int)
rfm["M_score"] = pd.qcut(rfm["Monetary"], 4, labels=[1,2,3,4]).astype(int)
rfm["RFM_total"] = rfm["R_score"] + rfm["F_score"] + rfm["M_score"]

def segment_customer(row):
    if row["RFM_total"] >= 10: return "Champions"
    elif row["RFM_total"] >= 8: return "Loyal Customers"
    elif row["RFM_total"] >= 6: return "Potential Loyalists"
    elif row["RFM_total"] >= 4: return "At Risk"
    return "Lost / Inactive"

rfm["Segment"] = rfm.apply(segment_customer, axis=1)

seg_summary = rfm.groupby("Segment").agg(
    num_customers=("Customer ID","count"),
    avg_monetary=("Monetary","mean")
).round(0).sort_values("avg_monetary", ascending=False).reset_index()
seg_summary
"""))

cells.append(code_cell("""
seg_order = seg_summary.sort_values("num_customers", ascending=False)
colors5 = sns.color_palette("Blues_r", n_colors=len(seg_order))

fig, ax = plt.subplots(figsize=(8, 4.3))
bars = ax.bar(seg_order["Segment"], seg_order["num_customers"], color=colors5)
ax.set_title("Customer Segments - RFM Analysis", fontsize=13, fontweight="bold")
ax.set_ylabel("Number of Customers")
plt.xticks(rotation=20, ha="right")
for bar in bars:
    h = bar.get_height()
    ax.text(bar.get_x()+bar.get_width()/2, h+2, int(h), ha="center", fontweight="bold")
plt.tight_layout()
plt.show()
"""))

cells.append(md_cell("""
## 7. Key Insights & Business Recommendations

**1. Discounting is eroding margin faster than it's driving volume.**
Orders with no discount run a 34.4% margin vs. 21.2% for discounts above 10%. Recommendation: cap
standard discounts at 10% and reserve deeper discounts for clearing aged inventory only, with margin
impact tracked monthly.

**2. Electronics drives revenue, but margin is more evenly spread.**
Electronics is the largest category by revenue, but Home & Living and Fashion carry comparable or
better margins. Recommendation: feature higher-margin categories more prominently in cross-sell and
bundle promotions rather than relying on Electronics alone.

**3. Bangkok & Vicinity is the clear revenue anchor, but margins are consistent nationwide.**
All five regions post profit margins within a tight 30-33% band — regional performance gaps are about
order volume, not regional pricing/cost inefficiency. Recommendation: growth investment should prioritize
expanding order volume in underweighted regions (Southern, Northern) rather than adjusting regional pricing.

**4. ~22% of customers ("Champions" + "Loyal Customers") generate a disproportionate share of revenue.**
Recommendation: launch a tiered loyalty program targeting these ~490 customers, and build a
win-back campaign for the "At Risk" segment (138 customers) before they lapse into "Lost / Inactive."

**5. Revenue softened notably in Q4 2024** relative to the same period in 2023.
Recommendation: this is worth investigating against marketing spend, inventory stockouts, or competitive
activity in the next planning cycle — flagged here as a question for stakeholders, not a conclusion the
data alone can answer.

---
*Full SQL queries: `sql/sales_analysis.sql` · Cleaning log: `data/cleaning_log.txt` · Interactive
dashboard: `dashboard.html`*
"""))

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.12"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

with open("/home/claude/nextcart-retail-analysis/notebooks/NextCart_Sales_Analysis.ipynb", "w") as f:
    json.dump(notebook, f, indent=1)

print("Notebook built successfully.")
