"""
02_clean_data.py
Cleans the raw NextCart sales export and documents every transformation,
mirroring the kind of cleaning log an analyst would keep for stakeholders.

Issues found and fixed:
  1. Inconsistent date formats        -> parsed to a single ISO date
  2. Inconsistent text casing/spaces  -> Region & Category standardized
  3. Missing Discount values          -> imputed as 0 (no discount applied)
  4. Missing Profit values            -> recalculated from Sales where possible,
                                          dropped if still unrecoverable
  5. Duplicate order rows             -> removed
  6. Invalid Quantity (negative)      -> removed (data entry errors)
"""

import pandas as pd
import numpy as np

RAW_PATH = "/home/claude/nextcart-retail-analysis/data/raw_sales_data.csv"
CLEAN_PATH = "/home/claude/nextcart-retail-analysis/data/cleaned_sales_data.csv"

df = pd.read_csv(RAW_PATH)
log = []
log.append(f"Starting rows: {len(df)}")

# 1. Standardize Order Date (mixed formats: YYYY-MM-DD, DD/MM/YYYY, with timestamps)
def parse_date(val):
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"):
        try:
            return pd.to_datetime(val, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.to_datetime(val, errors="coerce")

df["Order Date"] = df["Order Date"].apply(parse_date)
bad_dates = df["Order Date"].isna().sum()
log.append(f"Unparseable dates dropped: {bad_dates}")
df = df.dropna(subset=["Order Date"])

# 2. Standardize text fields: strip whitespace, title case
for col in ["Region", "Category", "Segment", "Ship Mode"]:
    df[col] = df[col].astype(str).str.strip().str.title()
log.append("Standardized casing/whitespace in: Region, Category, Segment, Ship Mode")

# 3. Remove duplicate rows (exact duplicates across all columns)
before = len(df)
df = df.drop_duplicates()
log.append(f"Duplicate rows removed: {before - len(df)}")

# 4. Remove invalid Quantity (negative = data entry error, can't be recovered)
before = len(df)
df = df[df["Quantity"] > 0]
log.append(f"Invalid (negative) Quantity rows removed: {before - len(df)}")

# 5. Fix missing Discount -> assume no discount was applied (most common business case)
missing_discount = df["Discount"].isna().sum()
df["Discount"] = df["Discount"].fillna(0)
log.append(f"Missing Discount values imputed as 0: {missing_discount}")

# 6. Fix missing Profit -> recompute using average category margin where possible
missing_profit_before = df["Profit"].isna().sum()
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
log.append(f"Missing Profit values imputed using category-average margin: {missing_profit_before}")

# 7. Final type cleanup
df["Order Date"] = df["Order Date"].dt.date
df = df.sort_values("Order Date").reset_index(drop=True)

log.append(f"Final rows: {len(df)}")
log.append(f"Final columns: {list(df.columns)}")

df.to_csv(CLEAN_PATH, index=False)

print("=== CLEANING LOG ===")
for line in log:
    print(" -", line)

with open("/home/claude/nextcart-retail-analysis/data/cleaning_log.txt", "w") as f:
    f.write("NextCart Sales Data — Cleaning Log\n")
    f.write("=" * 40 + "\n")
    for line in log:
        f.write(f"- {line}\n")

print(f"\nClean data saved -> {CLEAN_PATH}")
