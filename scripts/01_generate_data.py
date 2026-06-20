"""
01_generate_data.py
Generates a synthetic but realistic retail sales dataset for "NextCart" -
a fictional Thailand-based e-commerce retailer.

The dataset intentionally includes common real-world data quality issues
(missing values, duplicates, inconsistent text formatting, mixed date formats)
so that the cleaning notebook has genuine problems to solve.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

N_ORDERS = 4200

# ---- Reference data -------------------------------------------------------
regions = ["Bangkok & Vicinity", "Central", "Northern", "Northeastern", "Southern"]
region_weights = [0.40, 0.18, 0.14, 0.16, 0.12]

segments = ["Consumer", "Corporate", "Home Office"]
segment_weights = [0.55, 0.30, 0.15]

categories = {
    "Electronics": ["Smartphone", "Laptop", "Headphones", "Smart Watch", "Power Bank"],
    "Fashion": ["T-Shirt", "Jeans", "Sneakers", "Backpack", "Sunglasses"],
    "Home & Living": ["Desk Lamp", "Storage Box", "Cookware Set", "Bedding Set", "Air Purifier"],
    "Beauty": ["Skincare Set", "Perfume", "Makeup Kit", "Hair Dryer", "Sunscreen"],
    "Office Supplies": ["Notebook Set", "Printer Ink", "Office Chair", "Desk Organizer", "Stapler"],
}

ship_modes = ["Standard", "Express", "Same Day"]
ship_weights = [0.60, 0.30, 0.10]

first_names = ["Somchai", "Suda", "Anan", "Pim", "Krit", "Nattaya", "Wichai", "Aom",
               "Decha", "Mali", "Theerapat", "Kanya", "Surasak", "Napat", "Orawan",
               "Chai", "Ploy", "Nopporn", "Siri", "Boonmee"]
last_names = ["Srisuk", "Boonmee", "Chaiyaporn", "Wongsa", "Thongdee", "Saetang",
              "Phromsri", "Charoen", "Ruangrit", "Kittisak", "Sukjai", "Intharak"]

base_price = {
    "Smartphone": 8900, "Laptop": 18500, "Headphones": 1290, "Smart Watch": 3490, "Power Bank": 690,
    "T-Shirt": 290, "Jeans": 790, "Sneakers": 1590, "Backpack": 990, "Sunglasses": 590,
    "Desk Lamp": 450, "Storage Box": 350, "Cookware Set": 1890, "Bedding Set": 1290, "Air Purifier": 4990,
    "Skincare Set": 1190, "Perfume": 1490, "Makeup Kit": 890, "Hair Dryer": 690, "Sunscreen": 350,
    "Notebook Set": 120, "Printer Ink": 590, "Office Chair": 2890, "Desk Organizer": 290, "Stapler": 90,
}

start_date = datetime(2023, 1, 1)
end_date = datetime(2024, 12, 31)
date_range_days = (end_date - start_date).days

rows = []
n_customers = 950
customer_ids = [f"CUST-{str(i).zfill(4)}" for i in range(1, n_customers + 1)]
customer_names = {cid: f"{random.choice(first_names)} {random.choice(last_names)}" for cid in customer_ids}
customer_segment = {cid: np.random.choice(segments, p=segment_weights) for cid in customer_ids}

for i in range(1, N_ORDERS + 1):
    order_id = f"NC-{str(i).zfill(5)}"
    customer_id = random.choice(customer_ids)

    # mild seasonality: more orders mid-year and Nov-Dec (sales season)
    day_offset = int(np.random.beta(2, 2) * date_range_days)
    order_date = start_date + timedelta(days=day_offset)

    region = np.random.choice(regions, p=region_weights)
    category = random.choice(list(categories.keys()))
    product = random.choice(categories[category])
    unit_price = base_price[product]

    quantity = np.random.choice([1, 1, 1, 2, 2, 3, 4], p=[0.35, 0.2, 0.15, 0.12, 0.08, 0.06, 0.04])
    discount = np.random.choice([0, 0, 0.05, 0.10, 0.15, 0.20], p=[0.45, 0.15, 0.15, 0.12, 0.08, 0.05])

    sales = round(unit_price * quantity * (1 - discount), 2)
    cost_ratio = np.random.uniform(0.55, 0.75)
    profit = round(sales - (unit_price * quantity * cost_ratio), 2)

    ship_mode = np.random.choice(ship_modes, p=ship_weights)

    rows.append({
        "Order ID": order_id,
        "Order Date": order_date,
        "Customer ID": customer_id,
        "Customer Name": customer_names[customer_id],
        "Segment": customer_segment[customer_id],
        "Region": region,
        "Category": category,
        "Product Name": product,
        "Quantity": quantity,
        "Discount": discount,
        "Sales": sales,
        "Profit": profit,
        "Ship Mode": ship_mode,
    })

df = pd.DataFrame(rows)

# ---------------------------------------------------------------------------
# Inject realistic data quality issues
# ---------------------------------------------------------------------------

# 1. Mixed date formats (simulate manual exports from different systems)
def messy_date(d, idx):
    if idx % 7 == 0:
        return d.strftime("%d/%m/%Y")
    elif idx % 11 == 0:
        return d.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return d.strftime("%Y-%m-%d")

df["Order Date"] = [messy_date(d, i) for i, d in enumerate(df["Order Date"])]

# 2. Missing values in Discount and Profit (~4%)
missing_idx = df.sample(frac=0.04, random_state=1).index
df.loc[missing_idx, "Discount"] = np.nan
missing_idx2 = df.sample(frac=0.03, random_state=2).index
df.loc[missing_idx2, "Profit"] = np.nan

# 3. Inconsistent text casing / whitespace in Region and Category
def mess_text(val, idx):
    if idx % 13 == 0:
        return f"  {val.upper()}  "
    elif idx % 17 == 0:
        return val.lower()
    return val

df["Region"] = [mess_text(v, i) for i, v in enumerate(df["Region"])]
df["Category"] = [mess_text(v, i) for i, v in enumerate(df["Category"])]

# 4. Duplicate rows (~1.5%)
dupes = df.sample(frac=0.015, random_state=3)
df = pd.concat([df, dupes], ignore_index=True)

# 5. A few negative/invalid Quantity values (data entry errors)
err_idx = df.sample(n=8, random_state=4).index
df.loc[err_idx, "Quantity"] = -1

# 6. Shuffle rows so it looks like a raw export, not generated in order
df = df.sample(frac=1, random_state=5).reset_index(drop=True)

df.to_csv("/home/claude/nextcart-retail-analysis/data/raw_sales_data.csv", index=False)
print(f"Generated {len(df)} rows -> data/raw_sales_data.csv")
print(df.head(10).to_string())
print("\nMissing values per column:")
print(df.isna().sum())
print(f"\nDuplicate rows: {df.duplicated().sum()}")
