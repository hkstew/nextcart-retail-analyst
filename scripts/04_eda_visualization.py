"""
04_eda_visualization.py
Exploratory analysis + chart generation for the NextCart portfolio project.
Produces publication-ready PNG charts saved to /images for use in the README.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid", palette="deep")
plt.rcParams["figure.dpi"] = 130
plt.rcParams["font.size"] = 10

DATA_PATH = "/home/claude/nextcart-retail-analysis/data/cleaned_sales_data.csv"
IMG_DIR = "/home/claude/nextcart-retail-analysis/images"

df = pd.read_csv(DATA_PATH, parse_dates=["Order Date"])
df["order_month"] = df["Order Date"].dt.to_period("M").astype(str)

ACCENT = "#2563EB"

# ---------------------------------------------------------------------------
# Chart 1: Monthly revenue trend
# ---------------------------------------------------------------------------
monthly = df.groupby("order_month")["Sales"].sum().reset_index()
fig, ax = plt.subplots(figsize=(10, 4.5))
ax.plot(monthly["order_month"], monthly["Sales"], marker="o", color=ACCENT, linewidth=2)
ax.fill_between(range(len(monthly)), monthly["Sales"], alpha=0.08, color=ACCENT)
ax.set_title("Monthly Revenue Trend (2023–2024)", fontsize=13, fontweight="bold")
ax.set_xlabel("")
ax.set_ylabel("Revenue (THB)")
ax.tick_params(axis="x", rotation=60)
plt.tight_layout()
plt.savefig(f"{IMG_DIR}/01_monthly_revenue_trend.png")
plt.close()

# ---------------------------------------------------------------------------
# Chart 2: Revenue & profit margin by category
# ---------------------------------------------------------------------------
cat = df.groupby("Category").agg(total_sales=("Sales", "sum"), total_profit=("Profit", "sum")).reset_index()
cat["margin_pct"] = (cat["total_profit"] / cat["total_sales"] * 100).round(1)
cat = cat.sort_values("total_sales", ascending=True)

fig, ax1 = plt.subplots(figsize=(9, 5))
bars = ax1.barh(cat["Category"], cat["total_sales"], color=ACCENT, alpha=0.85)
ax1.set_xlabel("Total Revenue (THB)")
ax1.set_title("Revenue by Category — with Profit Margin %", fontsize=13, fontweight="bold")
for bar, margin in zip(bars, cat["margin_pct"]):
    ax1.text(bar.get_width() * 1.01, bar.get_y() + bar.get_height()/2,
              f"{margin}% margin", va="center", fontsize=9, color="#444")
plt.tight_layout()
plt.savefig(f"{IMG_DIR}/02_category_revenue_margin.png")
plt.close()

# ---------------------------------------------------------------------------
# Chart 3: Discount band vs profit margin (key insight chart)
# ---------------------------------------------------------------------------
def band(d):
    if d == 0:
        return "No Discount"
    elif d <= 0.10:
        return "Low (1-10%)"
    return "High (>10%)"

df["discount_band"] = df["Discount"].apply(band)
band_order = ["No Discount", "Low (1-10%)", "High (>10%)"]
band_stats = df.groupby("discount_band").apply(
    lambda x: pd.Series({"margin_pct": x["Profit"].sum() / x["Sales"].sum() * 100})
).reindex(band_order).reset_index()

fig, ax = plt.subplots(figsize=(7, 4.5))
colors = ["#16A34A", "#F59E0B", "#DC2626"]
bars = ax.bar(band_stats["discount_band"], band_stats["margin_pct"], color=colors)
ax.set_ylabel("Profit Margin (%)")
ax.set_title("Heavier Discounts Erode Profit Margin", fontsize=13, fontweight="bold")
for bar in bars:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, h + 0.5, f"{h:.1f}%", ha="center", fontweight="bold")
plt.tight_layout()
plt.savefig(f"{IMG_DIR}/03_discount_vs_margin.png")
plt.close()

# ---------------------------------------------------------------------------
# Chart 4: Regional performance
# ---------------------------------------------------------------------------
reg = df.groupby("Region")["Sales"].sum().sort_values(ascending=False).reset_index()
fig, ax = plt.subplots(figsize=(8, 4.5))
sns.barplot(data=reg, x="Sales", y="Region", ax=ax, color=ACCENT)
ax.set_title("Total Revenue by Region", fontsize=13, fontweight="bold")
ax.set_xlabel("Revenue (THB)")
plt.tight_layout()
plt.savefig(f"{IMG_DIR}/04_regional_revenue.png")
plt.close()

print("Saved 4 charts to /images")

# ---------------------------------------------------------------------------
# RFM Customer Segmentation
# ---------------------------------------------------------------------------
snapshot_date = df["Order Date"].max() + pd.Timedelta(days=1)

rfm = df.groupby("Customer ID").agg(
    Recency=("Order Date", lambda x: (snapshot_date - x.max()).days),
    Frequency=("Order ID", "nunique"),
    Monetary=("Sales", "sum"),
).reset_index()

rfm["R_score"] = pd.qcut(rfm["Recency"], 4, labels=[4, 3, 2, 1]).astype(int)
rfm["F_score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
rfm["M_score"] = pd.qcut(rfm["Monetary"], 4, labels=[1, 2, 3, 4]).astype(int)
rfm["RFM_total"] = rfm["R_score"] + rfm["F_score"] + rfm["M_score"]

def segment_customer(row):
    if row["RFM_total"] >= 10:
        return "Champions"
    elif row["RFM_total"] >= 8:
        return "Loyal Customers"
    elif row["RFM_total"] >= 6:
        return "Potential Loyalists"
    elif row["RFM_total"] >= 4:
        return "At Risk"
    else:
        return "Lost / Inactive"

rfm["Segment"] = rfm.apply(segment_customer, axis=1)
rfm.to_csv("/home/claude/nextcart-retail-analysis/data/rfm_segments.csv", index=False)

seg_summary = rfm.groupby("Segment").agg(
    num_customers=("Customer ID", "count"),
    avg_monetary=("Monetary", "mean"),
).sort_values("avg_monetary", ascending=False).reset_index()
print("\n=== RFM Segment Summary ===")
print(seg_summary.to_string(index=False))

# Chart 5: RFM segment distribution
fig, ax = plt.subplots(figsize=(8, 4.5))
seg_order = seg_summary.sort_values("num_customers", ascending=False)
colors5 = sns.color_palette("Blues_r", n_colors=len(seg_order))
bars = ax.bar(seg_order["Segment"], seg_order["num_customers"], color=colors5)
ax.set_title("Customer Segments — RFM Analysis", fontsize=13, fontweight="bold")
ax.set_ylabel("Number of Customers")
plt.xticks(rotation=20, ha="right")
for bar in bars:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, h + 2, int(h), ha="center", fontweight="bold")
plt.tight_layout()
plt.savefig(f"{IMG_DIR}/05_rfm_segments.png")
plt.close()

seg_summary.to_csv("/home/claude/nextcart-retail-analysis/data/rfm_segment_summary.csv", index=False)
print("\nSaved RFM segments -> data/rfm_segments.csv")
print("Saved chart 5 -> images/05_rfm_segments.png")
