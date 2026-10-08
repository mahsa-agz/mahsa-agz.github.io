import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
from sql_mid_data import build_setup

ex = Exam(13, "sql")
build_setup(ex, "app", "northwind", "retail")

# ---------------------------------------------------------------- Q1 YTD and share of year (Northwind)
ex.q("Year to date, month by month", minutes=6, kind="sql",
     prompt="""Northwind (real schema). For **2021 and 2022**, return one row per month with `month` ('YYYY-MM'),
`revenue` (that month), `ytd` (revenue from January of the same year up to and including this month) and
`pct_of_year` (ytd as a percent of the full year's revenue, 1 decimal). Round money to whole units.
Revenue of a line is `unit_price * quantity * (1 - discount)`.

Example: if January is 100 and February 80 in a year that totals 1,000, then February has `ytd = 180` and
`pct_of_year = 18.0`. January of the next year starts again from its own revenue.""",
     hint1="Signal: \"cumulative from the start of the year, restart every year\". Pattern: running total "
           "`SUM(...) OVER (PARTITION BY year ORDER BY month)`, plus a plain `SUM(...) OVER (PARTITION BY year)` "
           "for the total.",
     hint2="1. CTE monthly: year, month, revenue (join orders and order details, filter the two years).\n"
           "2. `SUM(revenue) OVER (PARTITION BY yr ORDER BY month ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)`.\n"
           "3. Divide by `SUM(revenue) OVER (PARTITION BY yr)` (no ORDER BY = whole partition).",
     solution="""WITH monthly AS (
    SELECT substr(o.order_date, 1, 4) AS yr,
           substr(o.order_date, 1, 7) AS month,
           SUM(d.unit_price * d.quantity * (1 - d.discount)) AS revenue
    FROM nw_orders o
    JOIN nw_order_details d ON d.order_id = o.order_id
    WHERE o.order_date >= '2021-01-01' AND o.order_date < '2023-01-01'
    GROUP BY substr(o.order_date, 1, 4), substr(o.order_date, 1, 7)
)
SELECT month,
       ROUND(revenue, 0) AS revenue,
       ROUND(SUM(revenue) OVER (PARTITION BY yr ORDER BY month
                                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 0) AS ytd,
       ROUND(100.0 * SUM(revenue) OVER (PARTITION BY yr ORDER BY month
                                        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
             / SUM(revenue) OVER (PARTITION BY yr), 1) AS pct_of_year
FROM monthly
ORDER BY month""",
     why="With ORDER BY inside OVER, SUM becomes cumulative; PARTITION BY yr restarts it every January. Without "
         "ORDER BY, the same SUM covers the whole partition, which gives the yearly total on every row. 2021 "
         "reaches 81.2% of its revenue by October, 2022 reaches 82.3%. Writing the frame "
         "`ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` explicitly matters: the default frame is RANGE, "
         "which treats rows with the same ORDER BY value as one block (no difference here because months are "
         "unique, but it bites when the order key has duplicates).",
     complexity="Join and group by over the order lines of two years, then windows over 24 rows.",
     mistakes="Forgetting PARTITION BY yr (ytd keeps growing into the next year). Using the default RANGE frame "
              "with duplicate order keys (all tied rows get the same running total). Dividing by the running "
              "total instead of the year total.",
     learn=["sql-running-totals", "sql-dates"])

# ---------------------------------------------------------------- Q2 rolling 7-day average (app)
ex.q("A smoother DAU line for March", minutes=6, kind="sql",
     prompt="""Shopping app (made up). Daily active users (DAU) = number of users with a row in `daily_activity`
that day. The dashboard for **March 2024** needs `activity_date`, `dau`, `dau_7d` (average DAU of this day and the
6 days before, 1 decimal) and `n_days` (how many days went into the average).

Important: the 7-day average on 2024-03-01 must use Feb 24 to Mar 1, so `n_days` must be 7 on every March row.

Follow-up: what breaks if some dates have no activity rows at all, and how do you fix it?""",
     hint1="Signal: \"average of the last 7 days on every row\". Pattern: moving window "
           "`AVG(...) OVER (ORDER BY day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)`. Trap: when is the March "
           "filter applied?",
     hint2="1. CTE dau: COUNT(*) per activity_date over ALL dates.\n"
           "2. CTE smooth: add the moving AVG and a moving COUNT(*) with the same frame.\n"
           "3. Only now filter `activity_date >= '2024-03-01'` in the outer query.",
     solution="""WITH dau AS (
    SELECT activity_date, COUNT(*) AS dau
    FROM daily_activity
    GROUP BY activity_date
), smooth AS (
    SELECT activity_date, dau,
           ROUND(AVG(dau) OVER (ORDER BY activity_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 1) AS dau_7d,
           COUNT(*) OVER (ORDER BY activity_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)             AS n_days
    FROM dau
)
SELECT activity_date, dau, dau_7d, n_days
FROM smooth
WHERE activity_date >= '2024-03-01' AND activity_date < '2024-04-01'
ORDER BY activity_date""",
     why="WHERE runs before window functions. If you put the March filter in the same SELECT as the AVG, the "
         "window only sees March rows and the first 6 days average fewer than 7 days (n_days 1, 2, ... 6). "
         "Computing the window in a CTE and filtering outside keeps February in the frame. The smooth line shows "
         "DAU falling through March (signups stopped at the end of February). Follow-up: ROWS counts rows, not "
         "days. If a date has no rows, the frame reaches 8 or more calendar days back. Fix: build a calendar "
         "(recursive CTE or `generate_series` in PostgreSQL), LEFT JOIN the counts and COALESCE to 0, or in "
         "PostgreSQL use `RANGE BETWEEN INTERVAL '6 days' PRECEDING AND CURRENT ROW` on a date column.",
     complexity="One group by, then a window over 91 daily rows.",
     mistakes="Filtering the month before computing the window. `ROWS BETWEEN 7 PRECEDING` (that is 8 days). "
              "Averaging user-level rows instead of daily counts. Assuming no gaps in the dates.",
     learn=["sql-running-totals", "sql-query-order", "sql-dates"])

# ---------------------------------------------------------------- Q3 first time the running total crosses a threshold (retail)
ex.q("Joining the 1,000 club", minutes=7, kind="sql",
     prompt="""Online Retail (real). A customer joins the **1,000 club** on the first day their **cumulative net
spend** (all their lines up to and including that day, `quantity * unit_price`, cancellations included as negative)
reaches **1,000 or more**. Ignore rows without `customer_id`.

Return, per month ('YYYY-MM'), `new_1000_club` (customers who joined that month) and `club_size` (members so far,
cumulative over months).

Example: a customer with daily spend 600 (Jan 5), -200 (Jan 9, a return), 700 (Feb 2) reaches 600, 400, 1,100,
so they join on Feb 2. Note that a return can push a customer back below 1,000; they still joined on the first day.""",
     hint1="Signal: \"the first day a cumulative sum crosses a threshold\". Pattern: running total per customer, "
           "then MIN(day) where the running total >= 1000; a second running total over months.",
     hint2="1. CTE daily: spend per customer per day.\n"
           "2. CTE cum: `SUM(spend) OVER (PARTITION BY customer_id ORDER BY day ROWS UNBOUNDED PRECEDING)`.\n"
           "3. CTE firsts: `MIN(day)` per customer WHERE cum_spend >= 1000.\n"
           "4. Group firsts by month; `SUM(COUNT(*)) OVER (ORDER BY month)` for club_size.",
     solution="""WITH daily AS (
    SELECT customer_id, substr(invoice_date, 1, 10) AS day, SUM(quantity * unit_price) AS spend
    FROM retail
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id, substr(invoice_date, 1, 10)
), cum AS (
    SELECT customer_id, day,
           SUM(spend) OVER (PARTITION BY customer_id ORDER BY day ROWS UNBOUNDED PRECEDING) AS cum_spend
    FROM daily
), firsts AS (
    SELECT customer_id, MIN(day) AS joined_day
    FROM cum
    WHERE cum_spend >= 1000
    GROUP BY customer_id
)
SELECT substr(joined_day, 1, 7) AS month,
       COUNT(*) AS new_1000_club,
       SUM(COUNT(*)) OVER (ORDER BY substr(joined_day, 1, 7)) AS club_size
FROM firsts
GROUP BY substr(joined_day, 1, 7)
ORDER BY month""",
     why="Aggregate to one row per customer and day first, so the running total moves once per day. "
         "`ROWS UNBOUNDED PRECEDING` is short for `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`. Taking "
         "MIN(day) among the rows that pass the threshold gives the first crossing even if the customer later "
         "drops below. `SUM(COUNT(*)) OVER (...)` is a window over an aggregate: GROUP BY runs first, then the "
         "window adds up the monthly counts. December 2011 is small because the data ends on 2011-12-09.",
     complexity="Group by over the lines, one window sort per customer, then small group bys.",
     mistakes="Running the window over raw lines (several rows per day; you still get the right first day, but "
              "work on 400k rows instead of about 18k). Using `MAX` instead of `MIN` for the crossing day. "
              "Forgetting that people who returned items can drop back below the threshold (they must not be "
              "counted twice).",
     learn=["sql-running-totals", "sql-cte"])

# ---------------------------------------------------------------- Q4 Pareto share (app)
ex.q("How concentrated is revenue?", minutes=7, kind="sql",
     prompt="""Shopping app (made up). Sort buyers by their **completed** revenue, largest first (ties: smaller
user_id first). What is the **smallest number of buyers** whose combined revenue is at least **80%** of all
completed revenue?

Return one row: `buyers_for_80pct`, `n_buyers` (users with at least one completed order), `pct_of_buyers`
(1 decimal) and `n_users` (all users in app_users).

Example: revenues 50, 30, 10, 10 (total 100). Cumulative shares are 50%, 80%, 90%, 100%, so 2 buyers out of 4
(50.0%) make 80% of revenue.

Follow-up: a PM says "half of our buyers make 80% of revenue, so revenue is not concentrated". What else would you
show?""",
     hint1="Signal: \"cumulative share of a total, sorted\". Pattern: running total over `ORDER BY revenue DESC` "
           "divided by the grand total `SUM(revenue) OVER ()`; the answer is the first row that reaches 0.8.",
     hint2="1. CTE: revenue per user (completed only).\n"
           "2. CTE: ROW_NUMBER by revenue desc, `COUNT(*) OVER ()`, and cum_share = running SUM / `SUM(...) OVER ()`.\n"
           "3. `MIN(rnk) WHERE cum_share >= 0.8`.",
     solution="""WITH spend AS (
    SELECT user_id, SUM(amount) AS revenue
    FROM purchases
    WHERE status = 'completed'
    GROUP BY user_id
), cum AS (
    SELECT user_id, revenue,
           ROW_NUMBER() OVER (ORDER BY revenue DESC, user_id) AS rnk,
           COUNT(*) OVER () AS n_buyers,
           SUM(revenue) OVER (ORDER BY revenue DESC, user_id ROWS UNBOUNDED PRECEDING)
             / SUM(revenue) OVER () AS cum_share
    FROM spend
)
SELECT MIN(rnk) AS buyers_for_80pct,
       MAX(n_buyers) AS n_buyers,
       ROUND(100.0 * MIN(rnk) / MAX(n_buyers), 1) AS pct_of_buyers,
       (SELECT COUNT(*) FROM app_users) AS n_users
FROM cum
WHERE cum_share >= 0.8""",
     why="`SUM(...) OVER ()` with an empty window is the grand total on every row, so the ratio is the cumulative "
         "share. The tie breaker in both ORDER BYs keeps ROW_NUMBER and the running sum in the same order. "
         "About half of the 403 buyers make 80% of revenue, which is less concentrated than the classic 80/20. "
         "Follow-up: the base matters. Only 403 of 1,500 users buy at all, so relative to all users about 13.5% "
         "make 80% of revenue. Show both, plus a Lorenz curve or the top 10% share, and how it changes over time.",
     complexity="Group by, then windows over about 400 rows.",
     mistakes="Running sum without the tie breaker (equal revenues get the same RANGE sum and the count jumps). "
              "Using `> 0.8` and missing the row that is exactly 80%. Including refunded orders.",
     learn=["sql-running-totals", "sql-ratios"])

# ---------------------------------------------------------------- Q5 review: weekly growth with LAG (app)
ex.q("Week over week signups", minutes=5, kind="sql", review=True,
     prompt="""Shopping app (made up). Weeks start on **Monday**. Return `week_start`, `signups`, `prev_week` and
`wow_pct` (week over week percent change, 1 decimal) for every signup week.

In SQLite, the Monday of the week of date d is `date(d, 'weekday 0', '-6 days')` (move forward to Sunday, then
back 6 days). Example: 2024-01-03 (a Wednesday) belongs to week 2024-01-01.

Then explain the last row.""",
     hint1="Signal: \"this week versus last week\". Pattern: truncate dates to the week, aggregate, then LAG.",
     hint2="1. CTE weekly: week_start and COUNT(*).\n2. `LAG(signups) OVER (ORDER BY week_start)`.\n"
           "3. Percent change with 100.0 to avoid integer division.",
     solution="""WITH weekly AS (
    SELECT date(signup_date, 'weekday 0', '-6 days') AS week_start,
           COUNT(*) AS signups
    FROM app_users
    GROUP BY date(signup_date, 'weekday 0', '-6 days')
)
SELECT week_start,
       signups,
       LAG(signups) OVER (ORDER BY week_start) AS prev_week,
       ROUND(100.0 * (signups - LAG(signups) OVER (ORDER BY week_start))
             / LAG(signups) OVER (ORDER BY week_start), 1) AS wow_pct
FROM weekly
ORDER BY week_start""",
     why="Truncating to the week start makes a stable group key; LAG then compares neighbouring weeks. The last "
         "week (2024-02-26) shows -37.8%, but signups in the data stop on 2024-02-29, so that week has only 4 "
         "days. Same lesson as the partial month on day 12: compare complete periods or per-day rates. "
         "PostgreSQL: `date_trunc('week', signup_date)` (weeks start on Monday there too).",
     complexity="One group by and a window over 9 rows.",
     mistakes="Using `strftime('%W')` without the year (weeks of different years merge). Weeks starting on "
              "Sunday by accident. Reading the partial last week as a real drop.",
     learn=["sql-lag-lead", "sql-dates"])

ex.save()
