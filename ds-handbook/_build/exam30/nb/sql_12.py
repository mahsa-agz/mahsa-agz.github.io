import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
from sql_mid_data import build_setup

ex = Exam(12, "sql")
build_setup(ex, "product", "app", "northwind", "retail")

# ---------------------------------------------------------------- Q1 month over month (real retail)
ex.q("Month over month at the gift shop", minutes=6, kind="sql",
     prompt="""Online Retail (real). Net revenue of a line is `quantity * unit_price` (cancellations have negative
quantity, so they subtract). For every month, return `month` ('YYYY-MM'), `revenue`, `prev_revenue`, `mom_pct`
(percent change versus the previous month, 1 decimal) and `next_pct` (percent change from this month to the next one).
Round money to whole units.

Example of the logic: if November is 1,461,756 and December is 433,668, December's `mom_pct` is -70.3.

Then answer: the CEO sees `-70.3` for December 2011 and panics. What do you check before anybody panics?""",
     hint1="Signal: \"compare a row with the previous / next row\". Pattern: LAG and LEAD over `ORDER BY month` "
           "on a monthly aggregate.",
     hint2="1. CTE: `strftime('%Y-%m', invoice_date)` and SUM(quantity * unit_price) per month.\n"
           "2. `LAG(revenue) OVER (ORDER BY month)` for the previous month, LEAD for the next one.\n"
           "3. Percent change = `100.0 * (revenue - prev) / prev`. The first month has no previous value (NULL).",
     solution="""WITH monthly AS (
    SELECT strftime('%Y-%m', invoice_date) AS month,
           SUM(quantity * unit_price)     AS revenue
    FROM retail
    GROUP BY strftime('%Y-%m', invoice_date)
)
SELECT month,
       ROUND(revenue, 0)                              AS revenue,
       ROUND(LAG(revenue) OVER (ORDER BY month), 0)   AS prev_revenue,
       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month))
             / LAG(revenue) OVER (ORDER BY month), 1) AS mom_pct,
       ROUND(100.0 * (LEAD(revenue) OVER (ORDER BY month) - revenue) / revenue, 1) AS next_pct
FROM monthly
ORDER BY month""",
     why="LAG reads a value from the previous row of the window order, LEAD from the next row, without a self join. "
         "The first month has no previous row, so its mom_pct is NULL (and the last month has no next_pct). "
         "December 2011: the data ends on 2011-12-09, so the month is only 9 days long. Always check the date "
         "range before comparing periods: compare equal windows (Dec 1 to 9 versus Nov 1 to 9), or revenue per "
         "day, or the same month last year. November is also a seasonal peak (Christmas orders). "
         "PostgreSQL: `to_char(invoice_date, 'YYYY-MM')` or `date_trunc('month', invoice_date)`.",
     complexity="One group by over 541,909 lines, then a window over 13 rows.",
     mistakes="Integer division when computing the percentage (use 100.0). Ordering the window by revenue "
              "instead of month. Forgetting that a missing month (no rows) makes LAG jump two months back: build a "
              "calendar of months if months can be empty. Panicking about a partial period.",
     learn=["sql-lag-lead", "sql-dates"])

# ---------------------------------------------------------------- Q2 LEAD for the next action (short-video product tables)
ex.q("Did the viewer like it right away?", minutes=7, kind="sql",
     prompt="""Short-video tables (made up). A **quick like** is a view whose **very next event by the same user**
is a `like` on the **same video**, at most **60 seconds** later.

For each video `category`, return `views`, `quick_likes` and `quick_like_rate` (3 decimals), highest rate first.

Example: user 9 views video 107 at 12:41:59 and likes video 107 at 12:42:16 (17 s later), so that view counts as a
quick like. If the user's next event were a view of another video, it would not count, even if a like came later.

Follow-up: two events of the same user can have the same `event_time`. How do you make "next event" well defined?""",
     hint1="Signal: \"the next event of the same user\". Pattern: LEAD over `PARTITION BY user_id ORDER BY "
           "event_time`, then a conditional count.",
     hint2="1. CTE: join events to videos; add `LEAD(event_type)`, `LEAD(video_id)` and `LEAD(event_time)` over "
           "`(PARTITION BY e.user_id ORDER BY e.event_time, e.event_id)`.\n"
           "2. Keep rows with event_type = 'view'.\n"
           "3. `SUM(CASE WHEN next_type = 'like' AND next_video = video_id AND seconds <= 60 THEN 1 ELSE 0 END)`; "
           "seconds in SQLite: `(julianday(t2) - julianday(t1)) * 86400`.",
     solution="""WITH seq AS (
    SELECT e.event_id, e.user_id, e.video_id, e.event_type, e.event_time, v.category,
           LEAD(e.event_type) OVER w AS next_type,
           LEAD(e.video_id)   OVER w AS next_video,
           LEAD(e.event_time) OVER w AS next_time
    FROM events e
    JOIN videos v ON v.video_id = e.video_id
    WINDOW w AS (PARTITION BY e.user_id ORDER BY e.event_time, e.event_id)
), flagged AS (
    SELECT category,
           CASE WHEN next_type = 'like' AND next_video = video_id
                 AND (julianday(next_time) - julianday(event_time)) * 86400 <= 60
                THEN 1 ELSE 0 END AS quick_like
    FROM seq
    WHERE event_type = 'view'
)
SELECT category,
       COUNT(*) AS views,
       SUM(quick_like) AS quick_likes,
       ROUND(1.0 * SUM(quick_like) / COUNT(*), 3) AS quick_like_rate
FROM flagged
GROUP BY category
ORDER BY quick_like_rate DESC""",
     why="LEAD looks one row ahead inside the user's own timeline, so \"next event\" is exactly what the question "
         "means; a self join with `MIN(event_time) > t` would also work but is longer and slower. The LEAD must be "
         "computed before filtering to views: if you filter first, the like rows are gone and LEAD sees the next "
         "view instead. Adding `event_id` to the ORDER BY breaks ties when two events share a timestamp, so the "
         "result is deterministic. The named `WINDOW w` clause works in SQLite and PostgreSQL. PostgreSQL seconds: "
         "`EXTRACT(EPOCH FROM next_time - event_time)`.",
     complexity="One sort of events per user for the window, then one group by.",
     mistakes="Filtering `WHERE event_type = 'view'` in the same SELECT as the LEAD (WHERE runs first). Forgetting "
              "`PARTITION BY user_id`, which compares with another user's event. Not checking that the like is on "
              "the same video. Integer division in the rate.",
     learn=["sql-lag-lead", "sql-case-when", "sql-ratios"])

# ---------------------------------------------------------------- Q3 time between purchases (real retail)
ex.q("How long until customers come back?", minutes=7, kind="sql",
     prompt="""Online Retail (real). The marketing team wants to time its reminder emails. For each customer, look at
the **days on which they bought** (ignore rows without `customer_id` and cancellation invoices, whose number starts
with 'C'). The **gap** is the number of days between two consecutive buying days of the same customer.

Per `country`, return `repeat_customers` (customers with at least one gap), `n_gaps`, `avg_gap_days` (1 decimal)
and `min_gap`. Keep countries with at least 10 repeat customers, shortest average gap first.

Example: a customer who bought on 2011-01-10, 2011-01-10 (two invoices) and 2011-02-09 has one gap of 30 days, not
two gaps (0 and 30).""",
     hint1="Signal: \"days between consecutive purchases of the same customer\". Pattern: LAG over "
           "`PARTITION BY customer ORDER BY day`, after removing duplicates per day.",
     hint2="1. CTE: `SELECT DISTINCT customer_id, country, substr(invoice_date, 1, 10) AS buy_day` with the filters.\n"
           "2. Gap = `julianday(buy_day) - julianday(LAG(buy_day) OVER (PARTITION BY customer_id ORDER BY buy_day))`.\n"
           "3. Outer query: drop NULL gaps (first purchase), group by country, HAVING COUNT(DISTINCT customer_id) >= 10.",
     solution="""WITH buy_days AS (
    SELECT DISTINCT customer_id, country, substr(invoice_date, 1, 10) AS buy_day
    FROM retail
    WHERE customer_id IS NOT NULL
      AND invoice_no NOT LIKE 'C%'
), gaps AS (
    SELECT country, customer_id, buy_day,
           julianday(buy_day)
             - julianday(LAG(buy_day) OVER (PARTITION BY customer_id ORDER BY buy_day)) AS gap_days
    FROM buy_days
)
SELECT country,
       COUNT(DISTINCT customer_id) AS repeat_customers,
       COUNT(*)                    AS n_gaps,
       ROUND(AVG(gap_days), 1)     AS avg_gap_days,
       MIN(gap_days)               AS min_gap
FROM gaps
WHERE gap_days IS NOT NULL
GROUP BY country
HAVING COUNT(DISTINCT customer_id) >= 10
ORDER BY avg_gap_days""",
     why="DISTINCT per day first, otherwise several invoices on the same day create gaps of 0 that pull the average "
         "down. LAG gives the previous buying day of the same customer; the first day of each customer has no "
         "previous day (NULL) and is dropped. Germany and France come back a bit faster than the United Kingdom "
         "on average (about 42 to 46 days), so a reminder around day 35 to 40 is a reasonable first test. "
         "The median gap would be more robust than the mean (gaps are skewed). PostgreSQL: dates subtract "
         "directly, `buy_day - LAG(buy_day) OVER (...)` gives an integer number of days.",
     complexity="DISTINCT and a window sort over about 400k purchase lines, then a small group by.",
     mistakes="Partitioning by country instead of customer (mixes customers). Forgetting the DISTINCT per day. "
              "Keeping the NULL first gaps in COUNT(*). A few customers appear with two countries; partitioning "
              "by customer_id still gives correct gaps, but they are then counted in both countries.",
     learn=["sql-lag-lead", "sql-dates", "sql-dedup-cleaning"])

# ---------------------------------------------------------------- Q4 strictly increasing sequence (app tables)
ex.q("Customers who always spend more", minutes=6, kind="sql",
     prompt="""Shopping app (made up). Find users with **at least 3 orders** (any status) where **every order is
larger than the order before it** (by `order_time`). Return `user_id`, `n_orders`, `first_amount`, `last_amount`,
users with more orders first, then by user_id.

Example: amounts 10.50, 18.00, 24.56 qualify; 10.50, 18.00, 18.00 do not (equal is not larger); 30, 12, 40 do not.""",
     hint1="Signal: \"each row compared with the previous row of the same user\". Pattern: LAG per user, then a "
           "group-level check that no row breaks the rule (count of violations = 0).",
     hint2="1. CTE: `LAG(amount) OVER (PARTITION BY user_id ORDER BY order_time, order_id)` and "
           "`COUNT(*) OVER (PARTITION BY user_id)`.\n"
           "2. Group by user; HAVING the number of rows with `prev_amount IS NOT NULL AND amount <= prev_amount` is 0.\n"
           "3. first and last amount: MIN and MAX work here because the sequence is increasing.",
     solution="""WITH p AS (
    SELECT user_id, order_id, order_time, amount,
           LAG(amount) OVER (PARTITION BY user_id ORDER BY order_time, order_id) AS prev_amount,
           COUNT(*)    OVER (PARTITION BY user_id)                                AS n_orders
    FROM purchases
)
SELECT user_id,
       n_orders,
       ROUND(MIN(amount), 2) AS first_amount,
       ROUND(MAX(amount), 2) AS last_amount
FROM p
WHERE n_orders >= 3
GROUP BY user_id, n_orders
HAVING SUM(CASE WHEN prev_amount IS NOT NULL AND amount <= prev_amount THEN 1 ELSE 0 END) = 0
ORDER BY n_orders DESC, user_id""",
     why="\"All rows satisfy X\" is easiest as \"no row violates X\": count the violations with a CASE inside SUM "
         "and require 0. LAG gives each order its previous amount; the first order has NULL and is not a "
         "violation. The COUNT window adds the order count to every row without collapsing them. Because the "
         "amounts are strictly increasing for the users that pass, MIN is the first and MAX the last amount; in "
         "general you would use `FIRST_VALUE` / `LAST_VALUE` (with a full frame) instead.",
     complexity="One window sort of purchases per user, one group by.",
     mistakes="Comparing with `<` instead of `<=` (equal amounts would pass). Ordering the window by amount instead "
              "of time. Using `LAST_VALUE(amount) OVER (ORDER BY ...)` with the default frame, which stops at the "
              "current row and returns the current amount.",
     learn=["sql-lag-lead", "sql-case-when"])

# ---------------------------------------------------------------- Q5 review top-n (real Northwind)
ex.q("Two best products in every category, 2022", minutes=5, kind="sql", review=True,
     prompt="""Northwind (real schema, enlarged dates). For orders placed in **2022**, return the **2 products with
the highest revenue in each category**. Revenue of a line is `unit_price * quantity * (1 - discount)`.
Keep ties (two products with exactly the same revenue both stay).

Return `category_name`, `dr`, `product_name`, `revenue` (rounded to whole units), ordered by category and dr.""",
     hint1="Signal: top 2 per category, ties kept. Pattern: aggregate, DENSE_RANK per category, filter in an outer "
           "query.",
     hint2="1. Join nw_order_details, nw_orders (for the date), nw_products, nw_categories.\n"
           "2. Filter `order_date >= '2022-01-01' AND order_date < '2023-01-01'`, group by category and product.\n"
           "3. `DENSE_RANK() OVER (PARTITION BY category_name ORDER BY revenue DESC)`, keep dr <= 2.",
     solution="""WITH rev AS (
    SELECT c.category_name, p.product_name,
           SUM(d.unit_price * d.quantity * (1 - d.discount)) AS revenue
    FROM nw_order_details d
    JOIN nw_orders o     ON o.order_id = d.order_id
    JOIN nw_products p   ON p.product_id = d.product_id
    JOIN nw_categories c ON c.category_id = p.category_id
    WHERE o.order_date >= '2022-01-01' AND o.order_date < '2023-01-01'
    GROUP BY c.category_name, p.product_name
), ranked AS (
    SELECT category_name, product_name, revenue,
           DENSE_RANK() OVER (PARTITION BY category_name ORDER BY revenue DESC) AS dr
    FROM rev
)
SELECT category_name, dr, product_name, ROUND(revenue, 0) AS revenue
FROM ranked
WHERE dr <= 2
ORDER BY category_name, dr""",
     why="Same template as day 11: aggregate, rank inside the partition, filter outside. The date filter goes into "
         "WHERE before the GROUP BY, so only 2022 lines are summed. DENSE_RANK keeps ties; with ROW_NUMBER you "
         "would need a tie breaker.",
     complexity="A join over the order lines of one year, a group by, one small window.",
     mistakes="Ranking by unit price or quantity instead of revenue. Forgetting the discount. Filtering on the "
              "year with `strftime('%Y', order_date) = '2022'` works but cannot use an index on order_date.",
     learn=["sql-top-n", "sql-joins"])

ex.save()
