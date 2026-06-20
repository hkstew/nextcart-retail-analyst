-- =============================================================================
-- NextCart Retail Sales Analysis — SQL Business Queries
-- Database: SQLite (table: sales, loaded from cleaned_sales_data.csv)
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Q1. Monthly revenue & profit trend (for spotting seasonality)
-- -----------------------------------------------------------------------------
SELECT
    strftime('%Y-%m', "Order Date")         AS order_month,
    ROUND(SUM(Sales), 2)                    AS total_sales,
    ROUND(SUM(Profit), 2)                   AS total_profit,
    COUNT(DISTINCT "Order ID")              AS num_orders
FROM sales
GROUP BY order_month
ORDER BY order_month;


-- -----------------------------------------------------------------------------
-- Q2. Top 10 best-selling products by revenue
-- -----------------------------------------------------------------------------
SELECT
    "Product Name",
    Category,
    ROUND(SUM(Sales), 2)        AS total_sales,
    SUM(Quantity)                AS units_sold,
    ROUND(SUM(Profit), 2)        AS total_profit
FROM sales
GROUP BY "Product Name", Category
ORDER BY total_sales DESC
LIMIT 10;


-- -----------------------------------------------------------------------------
-- Q3. Sales & profit margin performance by Region
-- -----------------------------------------------------------------------------
SELECT
    Region,
    ROUND(SUM(Sales), 2)                                   AS total_sales,
    ROUND(SUM(Profit), 2)                                  AS total_profit,
    ROUND(SUM(Profit) * 100.0 / SUM(Sales), 2)             AS profit_margin_pct,
    COUNT(DISTINCT "Order ID")                             AS num_orders
FROM sales
GROUP BY Region
ORDER BY total_sales DESC;


-- -----------------------------------------------------------------------------
-- Q4. Category performance: which categories make money vs. which look big
--     but actually have thin margins (classic BA insight)
-- -----------------------------------------------------------------------------
SELECT
    Category,
    ROUND(SUM(Sales), 2)                        AS total_sales,
    ROUND(SUM(Profit), 2)                       AS total_profit,
    ROUND(SUM(Profit) * 100.0 / SUM(Sales), 2)  AS profit_margin_pct,
    ROUND(AVG(Discount) * 100, 1)               AS avg_discount_pct
FROM sales
GROUP BY Category
ORDER BY total_profit DESC;


-- -----------------------------------------------------------------------------
-- Q5. Customer Segment value: Consumer vs Corporate vs Home Office
-- -----------------------------------------------------------------------------
SELECT
    Segment,
    COUNT(DISTINCT "Customer ID")                        AS num_customers,
    ROUND(SUM(Sales), 2)                                 AS total_sales,
    ROUND(SUM(Sales) / COUNT(DISTINCT "Customer ID"), 2) AS avg_sales_per_customer
FROM sales
GROUP BY Segment
ORDER BY total_sales DESC;


-- -----------------------------------------------------------------------------
-- Q6. Does discounting actually drive more profit, or just erode margin?
-- -----------------------------------------------------------------------------
SELECT
    CASE
        WHEN Discount = 0 THEN 'No Discount'
        WHEN Discount <= 0.10 THEN 'Low (1-10%)'
        ELSE 'High (>10%)'
    END                                            AS discount_band,
    COUNT(*)                                       AS num_orders,
    ROUND(AVG(Sales), 2)                           AS avg_order_value,
    ROUND(SUM(Profit) * 100.0 / SUM(Sales), 2)     AS profit_margin_pct
FROM sales
GROUP BY discount_band
ORDER BY profit_margin_pct DESC;


-- -----------------------------------------------------------------------------
-- Q7. Top 10 customers by lifetime spend (for loyalty / VIP targeting)
-- -----------------------------------------------------------------------------
SELECT
    "Customer ID",
    "Customer Name",
    Segment,
    COUNT(DISTINCT "Order ID")    AS num_orders,
    ROUND(SUM(Sales), 2)          AS lifetime_spend
FROM sales
GROUP BY "Customer ID", "Customer Name", Segment
ORDER BY lifetime_spend DESC
LIMIT 10;


-- -----------------------------------------------------------------------------
-- Q8. Shipping mode usage vs. order value (does faster shipping correlate
--     with bigger baskets?)
-- -----------------------------------------------------------------------------
SELECT
    "Ship Mode",
    COUNT(*)                AS num_orders,
    ROUND(AVG(Sales), 2)    AS avg_order_value
FROM sales
GROUP BY "Ship Mode"
ORDER BY avg_order_value DESC;
