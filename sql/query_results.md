# SQL Query Results — NextCart Sales Analysis

### Q1. Monthly revenue & profit trend (for spotting seasonality)

| order_month   |   total_sales |   total_profit |   num_orders |
|:--------------|--------------:|---------------:|-------------:|
| 2023-01       |       43573.5 |        12907.2 |           16 |
| 2023-02       |      141756   |        46419.2 |           66 |
| 2023-03       |      302724   |        97228   |          100 |
| 2023-04       |      410074   |       135006   |          138 |
| 2023-05       |      468236   |       151963   |          155 |
| 2023-06       |      562142   |       180149   |          185 |
| 2023-07       |      766712   |       225119   |          210 |
| 2023-08       |      498798   |       163691   |          206 |
| 2023-09       |      690310   |       227523   |          220 |
| 2023-10       |      783874   |       263155   |          254 |
| 2023-11       |      826770   |       269016   |          260 |
| 2023-12       |      678566   |       212335   |          252 |
| 2024-01       |      858602   |       260582   |          284 |
| 2024-02       |      895648   |       281942   |          254 |
| 2024-03       |      785580   |       241909   |          274 |
| 2024-04       |      734463   |       224562   |          241 |
| 2024-05       |      781128   |       261335   |          224 |
| 2024-06       |      673183   |       217263   |          207 |
| 2024-07       |      549920   |       182978   |          173 |
| 2024-08       |      580174   |       188592   |          168 |
| 2024-09       |      475188   |       158568   |          117 |
| 2024-10       |      347210   |        96111.3 |          118 |
| 2024-11       |      178375   |        56787.6 |           55 |
| 2024-12       |       44896   |        15078.3 |           15 |


### Q2. Top 10 best-selling products by revenue

| Product Name   | Category        |      total_sales |   units_sold |     total_profit |
|:---------------|:----------------|-----------------:|-------------:|-----------------:|
| Laptop         | Electronics     |      4.72952e+06 |          266 |      1.49366e+06 |
| Smartphone     | Electronics     |      2.1667e+06  |          256 | 682449           |
| Air Purifier   | Home & Living   |      1.22529e+06 |          254 | 395335           |
| Smart Watch    | Electronics     | 743196           |          220 | 247761           |
| Office Chair   | Office Supplies | 594906           |          216 | 187324           |
| Cookware Set   | Home & Living   | 372519           |          204 | 120880           |
| Sneakers       | Fashion         | 358068           |          233 | 120424           |
| Perfume        | Beauty          | 349107           |          247 | 106380           |
| Bedding Set    | Home & Living   | 323790           |          265 | 103345           |
| Headphones     | Electronics     | 296958           |          238 |  97584           |


### Q3. Sales & profit margin performance by Region

| Region             |   total_sales |     total_profit |   profit_margin_pct |   num_orders |
|:-------------------|--------------:|-----------------:|--------------------:|-------------:|
| Bangkok & Vicinity |   5.1783e+06  |      1.64455e+06 |               31.76 |         1621 |
| Northeastern       |   2.2735e+06  | 716882           |               31.53 |          709 |
| Central            |   2.11592e+06 | 694448           |               32.82 |          763 |
| Northern           |   1.81795e+06 | 601560           |               33.09 |          580 |
| Southern           |   1.69223e+06 | 512776           |               30.3  |          519 |


### Q4. Category performance: which categories make money vs. which look big

| Category        |      total_sales |     total_profit |   profit_margin_pct |   avg_discount_pct |
|:----------------|-----------------:|-----------------:|--------------------:|-------------------:|
| Electronics     |      8.10302e+06 |      2.57426e+06 |               31.77 |                3.6 |
| Home & Living   |      2.09971e+06 | 674844           |               32.14 |                3.9 |
| Beauty          |      1.07336e+06 | 338238           |               31.51 |                4.1 |
| Fashion         | 968668           | 318833           |               32.91 |                3.8 |
| Office Supplies | 833142           | 264047           |               31.69 |                4   |


### Q5. Customer Segment value: Consumer vs Corporate vs Home Office

| Segment     |   num_customers |   total_sales |   avg_sales_per_customer |
|:------------|----------------:|--------------:|-------------------------:|
| Consumer    |             524 |   7.66398e+06 |                  14625.9 |
| Corporate   |             269 |   3.55536e+06 |                  13217   |
| Home Office |             147 |   1.85856e+06 |                  12643.3 |


### Q6. Does discounting actually drive more profit, or just erode margin?

| discount_band   |   num_orders |   avg_order_value |   profit_margin_pct |
|:----------------|-------------:|------------------:|--------------------:|
| No Discount     |         2617 |           3223.07 |               34.39 |
| Low (1-10%)     |         1053 |           3103.69 |               29.91 |
| High (>10%)     |          522 |           2634    |               21.21 |


### Q7. Top 10 customers by lifetime spend (for loyalty / VIP targeting)

| Customer ID   | Customer Name      | Segment     |   num_orders |   lifetime_spend |
|:--------------|:-------------------|:------------|-------------:|-----------------:|
| CUST-0226     | Pim Phromsri       | Consumer    |            8 |          98906.5 |
| CUST-0552     | Chai Chaiyaporn    | Home Office |            6 |          96565   |
| CUST-0920     | Boonmee Chaiyaporn | Consumer    |            7 |          90030   |
| CUST-0189     | Pim Chaiyaporn     | Consumer    |            8 |          84884.5 |
| CUST-0126     | Suda Sukjai        | Consumer    |            5 |          79217.5 |
| CUST-0416     | Siri Saetang       | Consumer    |            6 |          76186.5 |
| CUST-0515     | Anan Saetang       | Consumer    |            7 |          75785.5 |
| CUST-0690     | Wichai Wongsa      | Consumer    |            2 |          74427.5 |
| CUST-0761     | Boonmee Kittisak   | Consumer    |            7 |          72510.5 |
| CUST-0782     | Suda Sukjai        | Consumer    |            9 |          68502.5 |


### Q8. Shipping mode usage vs. order value (does faster shipping correlate

| Ship Mode   |   num_orders |   avg_order_value |
|:------------|-------------:|------------------:|
| Standard    |         2545 |           3298.49 |
| Express     |         1226 |           2856.64 |
| Same Day    |          421 |           2805.22 |

