import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam
from sql_hard_tables import load, put_doc

EXTRA = '''# Made-up dashboard export in WIDE format (one column per platform), built from the app tables above.
db.executescript("""
CREATE TABLE platform_dau AS
SELECT d.activity_date AS day,
  SUM(CASE WHEN u.platform = 'ios' THEN 1 ELSE 0 END) AS ios,
  SUM(CASE WHEN u.platform = 'android' THEN 1 ELSE 0 END) AS android,
  SUM(CASE WHEN u.platform = 'web' THEN 1 ELSE 0 END) AS web
FROM daily_activity d JOIN app_users u ON u.user_id = d.user_id
GROUP BY d.activity_date
ORDER BY d.activity_date;
""")'''

SMALL = """**Made-up wide table:** `platform_dau`: one row per day (2024-01-01 to 2024-03-31), columns `day`, `ios`,
`android`, `web` = daily active users per platform (a dashboard export)."""

ex = Exam(22, "sql")
code, doc = load("chinook", "apps", "retail", "movielens", "northwind", extra=EXTRA)
ex.setup(code, data=True)
put_doc(ex, doc, SMALL)

ex.q("Revenue by country and year, side by side", minutes=4, kind="sql",
     prompt="""Chinook (real). Finance wants one row per billing country and one column per year: `y2009` ... `y2013`
(revenue = sum of `Invoice.Total`, 2 decimals) plus `total`. Show only the 6 countries with the highest total,
highest first.

Example row shape: `USA | 103.95 | 102.98 | ... | 523.06`.

*Follow-up:* the years are not known in advance (new data arrives every year). What do you do?""",
     hint1="Signal: 'one column per year'. Pattern: pivot with conditional aggregation: `SUM(CASE WHEN year = ... THEN x ELSE 0 END)`.",
     hint2="1. GROUP BY BillingCountry.\n2. One `SUM(CASE WHEN strftime('%Y', InvoiceDate) = '2009' THEN Total ELSE 0 END)` per year.\n"
           "3. SUM(Total) AS total; ORDER BY total DESC LIMIT 6.",
     solution="""SELECT BillingCountry AS country,
  ROUND(SUM(CASE WHEN strftime('%Y', InvoiceDate) = '2009' THEN Total ELSE 0 END), 2) AS y2009,
  ROUND(SUM(CASE WHEN strftime('%Y', InvoiceDate) = '2010' THEN Total ELSE 0 END), 2) AS y2010,
  ROUND(SUM(CASE WHEN strftime('%Y', InvoiceDate) = '2011' THEN Total ELSE 0 END), 2) AS y2011,
  ROUND(SUM(CASE WHEN strftime('%Y', InvoiceDate) = '2012' THEN Total ELSE 0 END), 2) AS y2012,
  ROUND(SUM(CASE WHEN strftime('%Y', InvoiceDate) = '2013' THEN Total ELSE 0 END), 2) AS y2013,
  ROUND(SUM(Total), 2) AS total
FROM Invoice
GROUP BY BillingCountry
ORDER BY total DESC
LIMIT 6""",
     why="Every invoice row goes into exactly one CASE bucket, so the year columns add up to `total` (USA: 523.06). "
         "`ELSE 0` makes an empty year show 0 instead of NULL. Follow-up: SQL needs the column list at write time. "
         "Options: generate the query text in Python from `SELECT DISTINCT year`; PostgreSQL `crosstab` (tablefunc "
         "extension); or keep the result LONG (country, year, revenue) and pivot in pandas or the BI tool. In an "
         "exam, say the long format is the better storage format and the pivot is a presentation step.",
     complexity="One scan and one GROUP BY: O(n).",
     mistakes="`COUNT(CASE ... THEN Total END)` (counts, not sums). Forgetting ELSE 0 (NULL cells). Filtering a year "
              "in WHERE (drops the other columns). PostgreSQL: `SUM(Total) FILTER (WHERE EXTRACT(year FROM InvoiceDate) = 2009)`.",
     learn=["sql-pivot", "sql-case-when"])

ex.q("Monthly retention matrix for a real shop", minutes=7, kind="sql", review=True,
     prompt="""UCI Online Retail (real). A customer's **cohort** is the month of their first purchase. For each cohort
return `customers` and `m1`, `m2`, `m3`: the % of the cohort that bought again 1, 2 and 3 calendar months later
(1 decimal). Only real purchases: `customer_id` not NULL, `invoice_no` not starting with 'C', `quantity > 0`.
A cell that cannot be observed yet (the month is after the last month in the data) must be **NULL, not 0**.

Example: first purchase in 2011-03; m1 = bought in 2011-04, m2 = 2011-05.

*Follow-up:* the data ends on 2011-12-09. Which cells are biased even though they are not NULL?""",
     hint1="Signal: 'cohort' and 'k months later' as columns. Pattern: retention plus pivot: month index difference, "
           "then `COUNT(DISTINCT CASE WHEN k = 1 THEN customer_id END)`.",
     hint2="1. CTE `orders`: DISTINCT customer, month text, month index `year * 12 + month`.\n"
           "2. `firsts`: MIN(month), MIN(index) per customer.\n3. Join back: k = index - first index.\n"
           "4. Per cohort: COUNT DISTINCT for k = 1, 2, 3 over cohort size.\n"
           "5. Wrap each in `CASE WHEN first_index + k <= last_index THEN ... END` (last_index = MAX over all orders).",
     solution="""WITH orders AS (
  SELECT DISTINCT customer_id, substr(invoice_date, 1, 7) AS month,
    CAST(substr(invoice_date, 1, 4) AS INTEGER) * 12
      + CAST(substr(invoice_date, 6, 2) AS INTEGER) AS m
  FROM retail
  WHERE customer_id IS NOT NULL AND invoice_no NOT LIKE 'C%' AND quantity > 0
), firsts AS (
  SELECT customer_id, MIN(month) AS cohort, MIN(m) AS c
  FROM orders GROUP BY customer_id
), j AS (
  SELECT f.cohort, f.c, f.customer_id, o.m - f.c AS k
  FROM firsts f JOIN orders o ON o.customer_id = f.customer_id
), last AS (
  SELECT MAX(m) AS last_m FROM orders
)
SELECT cohort,
  COUNT(DISTINCT customer_id) AS customers,
  CASE WHEN c + 1 <= last_m THEN ROUND(100.0 * COUNT(DISTINCT CASE WHEN k = 1 THEN customer_id END)
       / COUNT(DISTINCT customer_id), 1) END AS m1,
  CASE WHEN c + 2 <= last_m THEN ROUND(100.0 * COUNT(DISTINCT CASE WHEN k = 2 THEN customer_id END)
       / COUNT(DISTINCT customer_id), 1) END AS m2,
  CASE WHEN c + 3 <= last_m THEN ROUND(100.0 * COUNT(DISTINCT CASE WHEN k = 3 THEN customer_id END)
       / COUNT(DISTINCT customer_id), 1) END AS m3
FROM j CROSS JOIN last
GROUP BY cohort, c, last_m
ORDER BY cohort""",
     why="A month index (`year * 12 + month`) makes 'k months later' a subtraction that works across the year boundary "
         "(2010-12 to 2011-01 is k = 1). The k = 0 rows keep every customer in the cohort size. The CASE on "
         "`c + k <= last_m` separates 'nobody came back' (0) from 'we cannot know yet' (NULL): 2011-10 has m3 NULL, "
         "2011-11 has m2 and m3 NULL. The first cohort (2010-12) is much stickier (m1 36.6%) because it holds all the "
         "loyal customers who bought before the data starts. Follow-up: every cell that lands in 2011-12 only has 9 "
         "days of data (2011-09 m3 = 11.4%, 2011-10 m2 = 11.5%, 2011-11 m1 = 11.1%), so they look low for no real reason.",
     complexity="A DISTINCT and a self-join on customer_id: O(n log n).",
     mistakes="Subtracting month numbers without the year (December to January gives -11). Showing 0 for future months. "
              "Keeping cancellations ('C' invoices) as purchases. Using the first INVOICE line instead of the first month "
              "(a customer with two invoices in month 0 counts once, which DISTINCT on month handles).",
     learn=["sql-retention", "sql-pivot", "sql-dates"])

ex.q("Unpivot a wide dashboard table", minutes=5, kind="sql",
     prompt="""`platform_dau` (made up) is wide: `day | ios | android | web`. Turn it into a long table
`(day, platform, dau)` and use it to find, for each platform, its **peak day** (highest DAU; ties: earliest day), the
DAU on that day and `share_pct`: that platform's share of the day's total DAU across all three platforms (1 decimal).
Order by `dau` descending.

Example: on 2024-01-01 the wide row `12 | 12 | 6` becomes three long rows; ios share that day = 12 / 30 = 40.0%.""",
     hint1="Signal: columns that are really values of one variable. Pattern: unpivot with UNION ALL, then window "
           "functions (a ranking per platform and a SUM per day).",
     hint2="1. CTE `long`: three SELECTs (`'ios' AS platform, ios AS dau`), glued with UNION ALL.\n"
           "2. In one CTE: `SUM(dau) OVER (PARTITION BY day)` and `ROW_NUMBER() OVER (PARTITION BY platform ORDER BY dau DESC, day)`.\n"
           "3. Keep rn = 1.",
     solution="""WITH long AS (
  SELECT day, 'ios' AS platform, ios AS dau FROM platform_dau
  UNION ALL
  SELECT day, 'android', android FROM platform_dau
  UNION ALL
  SELECT day, 'web', web FROM platform_dau
), ranked AS (
  SELECT day, platform, dau,
    SUM(dau) OVER (PARTITION BY day) AS day_total,
    ROW_NUMBER() OVER (PARTITION BY platform ORDER BY dau DESC, day) AS rn
  FROM long
)
SELECT platform, day AS peak_day, dau, ROUND(100.0 * dau / day_total, 1) AS share_pct
FROM ranked
WHERE rn = 1
ORDER BY dau DESC""",
     why="Once the data is long, 'per platform' is just PARTITION BY platform, and adding a fourth platform needs no "
         "query change. The day total is computed in the same CTE as the rank, BEFORE the `rn = 1` filter; computed "
         "after the filter it would only see one row per day. Android peaks on 2024-02-24 with 147 users (51.8% of that day).",
     complexity="O(n) to unpivot (3 rows per day) plus window sorts.",
     mistakes="UNION instead of UNION ALL (removes rows that happen to be equal). Taking the share after filtering rn = 1. "
              "PostgreSQL has a shorter form: `CROSS JOIN LATERAL (VALUES ('ios', ios), ('android', android), ('web', web)) v(platform, dau)`.",
     learn=["sql-pivot", "sql-window-ranking"])

ex.q("Genre share of ratings by year", minutes=5, kind="sql",
     prompt="""MovieLens (real). For the years 2015 to 2018 (by `rated_at`), build a table with one row per genre and
columns `p2015`, `p2016`, `p2017`, `p2018`: the % of **all ratings of that year** that went to a movie of that genre
(1 decimal). Show the 6 genres with the highest `p2018`.

Example: 2018 has 6,418 ratings; if 2,000 of them are for Comedy movies, Comedy's p2018 = 31.2.

*Follow-up:* the column for 2018 adds up to far more than 100%. Bug or not?""",
     hint1="Signal: rows = genre, columns = year, cell = share of the column total. Pattern: pivot with conditional "
           "aggregation, divided by a per-year denominator.",
     hint2="1. CTE `r`: ratings joined to `ml_movie_genres`, with `yr = strftime('%Y', rated_at)`, from 2015 on.\n"
           "2. CTE `tot`: ratings per year from `ml_ratings` (NOT from the join).\n"
           "3. Per genre: `100.0 * SUM(CASE WHEN yr = '2018' THEN 1 ELSE 0 END) / (SELECT n FROM tot WHERE yr = '2018')`.",
     solution="""WITH r AS (
  SELECT g.genre, strftime('%Y', r.rated_at) AS yr
  FROM ml_ratings r
  JOIN ml_movie_genres g ON g.movie_id = r.movie_id
  WHERE r.rated_at >= '2015-01-01'
), tot AS (
  SELECT strftime('%Y', rated_at) AS yr, COUNT(*) AS n
  FROM ml_ratings
  WHERE rated_at >= '2015-01-01'
  GROUP BY strftime('%Y', rated_at)
)
SELECT genre,
  ROUND(100.0 * SUM(CASE WHEN yr = '2015' THEN 1 ELSE 0 END) / (SELECT n FROM tot WHERE yr = '2015'), 1) AS p2015,
  ROUND(100.0 * SUM(CASE WHEN yr = '2016' THEN 1 ELSE 0 END) / (SELECT n FROM tot WHERE yr = '2016'), 1) AS p2016,
  ROUND(100.0 * SUM(CASE WHEN yr = '2017' THEN 1 ELSE 0 END) / (SELECT n FROM tot WHERE yr = '2017'), 1) AS p2017,
  ROUND(100.0 * SUM(CASE WHEN yr = '2018' THEN 1 ELSE 0 END) / (SELECT n FROM tot WHERE yr = '2018'), 1) AS p2018
FROM r
GROUP BY genre
ORDER BY p2018 DESC
LIMIT 6""",
     why="The denominator must be the number of RATINGS per year, counted before the genre join; counting after the "
         "join would count a 3 genre movie three times. Follow-up: not a bug. A movie has several genres, so a "
         "rating is counted once in every genre column; the shares are 'percent of ratings that touch this genre', "
         "and they can sum above 100. Comedy leads 2018 with 40.4% while Drama falls from 44.0% (2015) to 34.2% (2018).",
     complexity="Join of ratings to genres (about 2.2 rows per rating) and one GROUP BY.",
     mistakes="Dividing by the joined row count. Integer division. Filtering `yr = '2018'` in WHERE, which empties the other columns.",
     learn=["sql-pivot", "sql-ratios"])

ex.q("This year versus last year, per category", minutes=5, kind="sql",
     prompt="""Northwind (real). Revenue = `unit_price * quantity * (1 - discount)`. The data stops on 2023-10-28, so
compare the same window in both years: **January to September**. Return per category `rev_2022`, `rev_2023`
(rounded to whole numbers) and `growth_pct = (rev_2023 / rev_2022 - 1) * 100` (1 decimal), ordered by growth descending.

*Follow-up:* why not compare full-year 2022 with all of 2023?""",
     hint1="Signal: two periods as two columns, then a ratio. Pattern: pivot by period with conditional sums, then "
           "compute growth in an outer query (or repeat the expressions).",
     hint2="1. Join orders, items, products, categories; WHERE order_date in 2022 or 2023 (Jan to Sep).\n"
           "2. `SUM(CASE WHEN order_date >= '2022-01-01' AND order_date < '2022-10-01' THEN rev ELSE 0 END)` and the same for 2023.\n"
           "3. Outer SELECT: growth from the two columns.",
     solution="""WITH lines AS (
  SELECT c.category, o.order_date,
    i.unit_price * i.quantity * (1 - i.discount) AS revenue
  FROM nw_orders o
  JOIN nw_order_items i ON i.order_id = o.order_id
  JOIN nw_products p ON p.product_id = i.product_id
  JOIN nw_categories c ON c.category_id = p.category_id
  WHERE (o.order_date >= '2022-01-01' AND o.order_date < '2022-10-01')
     OR (o.order_date >= '2023-01-01' AND o.order_date < '2023-10-01')
), by_cat AS (
  SELECT category,
    SUM(CASE WHEN order_date < '2023-01-01' THEN revenue ELSE 0 END) AS rev_2022,
    SUM(CASE WHEN order_date >= '2023-01-01' THEN revenue ELSE 0 END) AS rev_2023
  FROM lines
  GROUP BY category
)
SELECT category, ROUND(rev_2022) AS rev_2022, ROUND(rev_2023) AS rev_2023,
  ROUND((rev_2023 / rev_2022 - 1) * 100, 1) AS growth_pct
FROM by_cat
ORDER BY growth_pct DESC""",
     why="Filtering both windows in WHERE first keeps the scan small; the CASE then splits the rows into the two "
         "columns. Growth is computed from the UNROUNDED sums in the outer query. Every category grows 1% to 6%; "
         "Seafood grows most. Follow-up: 2023 is incomplete (no data after 2023-10-28), so a full-year comparison "
         "shows a fake drop of about 17% (39.7 million versus 33.1 million); like-for-like windows (or year to date) are the rule.",
     complexity="One join over about 600k item lines, filtered by date first.",
     mistakes="Comparing a partial year with a full year. Growth from rounded values. Forgetting the discount. "
              "Dividing by a zero baseline for a new category (guard with NULLIF).",
     learn=["sql-pivot", "sql-dates", "sql-ratios"])

ex.save()
