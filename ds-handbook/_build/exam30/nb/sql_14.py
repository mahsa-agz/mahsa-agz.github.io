import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
from sql_mid_data import build_setup

INTRO = """**Mock exam rules.** Set **one timer for 30 minutes** for the whole notebook (6 questions, about 5 minutes
each). Work as in a real exam: say the grain of each table and your plan out loud before typing. Do not open any
hint or solution until the timer rings. Then mark each question: solved in time, solved late, or not solved, and
put the last two in the mistake log.

Topics are mixed on purpose (CTEs, dates, ranking, top N, LAG / LEAD, running totals). Recognising which tool a
question needs is part of the test."""

ex = Exam(14, "sql", intro=INTRO)
build_setup(ex, "chinook", "app", "movielens")

# ---------------------------------------------------------------- Q1 cte + dates
ex.q("New or returning buyers?", minutes=5, kind="sql",
     prompt="""Shopping app. Using **completed** orders only, for each month ('YYYY-MM') return `new_buyers`
(users whose first completed order is in that month), `returning_buyers` (users who bought this month and whose first
completed order was in an earlier month) and `buyers` (all distinct buyers that month).

Example: a user with completed orders on Jan 20, Feb 3 and Feb 18 counts as new in January and once as returning in
February.""",
     hint1="Pattern: CTE with each user's first order date (a `MIN(...) OVER (PARTITION BY user_id)` or a separate "
           "group by), then conditional COUNT(DISTINCT CASE ...) per month.",
     hint2="1. CTE: user_id, month of the order, `MIN(order_time) OVER (PARTITION BY user_id) AS first_order`.\n"
           "2. Per month: `COUNT(DISTINCT CASE WHEN first month = month THEN user_id END)` and the same with `<`.",
     solution="""WITH orders AS (
    SELECT user_id,
           substr(order_time, 1, 7) AS month,
           MIN(order_time) OVER (PARTITION BY user_id) AS first_order
    FROM purchases
    WHERE status = 'completed'
)
SELECT month,
       COUNT(DISTINCT CASE WHEN substr(first_order, 1, 7) = month THEN user_id END) AS new_buyers,
       COUNT(DISTINCT CASE WHEN substr(first_order, 1, 7) < month THEN user_id END) AS returning_buyers,
       COUNT(DISTINCT user_id) AS buyers
FROM orders
GROUP BY month
ORDER BY month""",
     why="The window MIN attaches the first order date to every order row without a join. COUNT(DISTINCT CASE ...) "
         "counts a user once per month even with several orders (CASE without ELSE gives NULL, which COUNT "
         "ignores). new + returning = buyers in every month, a quick sanity check. 'YYYY-MM' strings compare "
         "correctly as text because they are zero padded.",
     complexity="One window sort over purchases plus one group by.",
     mistakes="COUNT without DISTINCT (counts orders). Computing the first order over all statuses while counting "
              "only completed ones (inconsistent definitions). Comparing full timestamps to months.",
     learn=["sql-cte", "sql-dates", "sql-case-when"])

# ---------------------------------------------------------------- Q2 window-ranking: NTILE
ex.q("Buyer quartiles", minutes=5, kind="sql",
     prompt="""Shopping app. Split all buyers (users with completed revenue) into **4 equal-size groups by completed
revenue**, quartile 1 = biggest spenders (ties: smaller user_id first). Per quartile return `buyers`, `min_rev`,
`max_rev`, `revenue` and `pct_revenue` (share of all completed revenue, 1 decimal).

Example: with 8 buyers, quartile 1 holds the 2 largest, quartile 4 the 2 smallest. If the count does not divide by 4,
the first groups get one extra buyer.""",
     hint1="Pattern: NTILE(4) over the revenue order, then a group by on the bucket.",
     hint2="1. CTE spend per user.\n2. `NTILE(4) OVER (ORDER BY revenue DESC, user_id)`.\n"
           "3. Group by quartile; divide by the total from a scalar subquery.",
     solution="""WITH spend AS (
    SELECT user_id, SUM(amount) AS revenue
    FROM purchases
    WHERE status = 'completed'
    GROUP BY user_id
), q AS (
    SELECT user_id, revenue, NTILE(4) OVER (ORDER BY revenue DESC, user_id) AS quartile
    FROM spend
)
SELECT quartile,
       COUNT(*) AS buyers,
       ROUND(MIN(revenue), 2) AS min_rev,
       ROUND(MAX(revenue), 2) AS max_rev,
       ROUND(SUM(revenue), 2) AS revenue,
       ROUND(100.0 * SUM(revenue) / (SELECT SUM(revenue) FROM spend), 1) AS pct_revenue
FROM q
GROUP BY quartile
ORDER BY quartile""",
     why="NTILE(n) deals rows into n buckets of (almost) equal size in window order; with 403 buyers the first 3 "
         "buckets get 101 and the last 100. The top quartile brings 55.3% of revenue. NTILE splits by row count, "
         "not by value: equal revenues can land in different buckets, so use PERCENT_RANK or fixed thresholds if "
         "the business wants value cutoffs.",
     complexity="Group by plus one window sort over about 400 rows.",
     mistakes="Forgetting DESC (quartile 1 becomes the smallest spenders). Dividing by the quartile total instead "
              "of the grand total.",
     learn=["sql-window-ranking", "sql-ratios"])

# ---------------------------------------------------------------- Q3 top-n
ex.q("Favourite genre of each country", minutes=5, kind="sql",
     prompt="""Chinook. For every customer country, return the genre with the **most units sold** (sum of
`InvoiceLine.Quantity`). If genres tie for first place, return all of them.

Return `country`, `genre`, `units`, ordered by country and genre. Use the customer's country.""",
     hint1="Pattern: top 1 per group with ties: aggregate per (country, genre), RANK per country, keep rank 1.",
     hint2="1. Join Customer, Invoice, InvoiceLine, Track, Genre; group by country and genre.\n"
           "2. `RANK() OVER (PARTITION BY country ORDER BY units DESC)`; outer filter `= 1`.",
     solution="""WITH units AS (
    SELECT c.Country AS country, g.Name AS genre, SUM(il.Quantity) AS units
    FROM Customer c
    JOIN Invoice i      ON i.CustomerId = c.CustomerId
    JOIN InvoiceLine il ON il.InvoiceId = i.InvoiceId
    JOIN Track t        ON t.TrackId = il.TrackId
    JOIN Genre g        ON g.GenreId = t.GenreId
    GROUP BY c.Country, g.Name
), ranked AS (
    SELECT country, genre, units, RANK() OVER (PARTITION BY country ORDER BY units DESC) AS rk
    FROM units
)
SELECT country, genre, units
FROM ranked
WHERE rk = 1
ORDER BY country, genre""",
     why="RANK keeps ties, so Argentina returns two genres (Alternative & Punk and Rock, 9 units each). Rock wins "
         "almost everywhere; Sweden prefers Latin. A `GROUP BY country` with `MAX(units)` gives the number but not "
         "the genre, which is why the window is the standard tool.",
     complexity="Joins over 2,240 invoice lines, a group by and a small window.",
     mistakes="ROW_NUMBER (drops one of the tied genres at random). Selecting `genre` next to `MAX(units)` in a "
              "plain GROUP BY (SQLite allows it and returns an arbitrary genre on ties; PostgreSQL rejects it).",
     learn=["sql-top-n", "sql-window-ranking"])

# ---------------------------------------------------------------- Q4 lag-lead
ex.q("Time to the second order", minutes=5, kind="sql",
     prompt="""Shopping app, all orders (any status). For each `platform`: `buyers` (users with at least one order),
`repeat_buyers` (users with a second order), `pct_repeat` (1 decimal) and `avg_days_to_2nd` (average days from the
first to the second order, 1 decimal, fractional days allowed).

Example: a user ordering on Jan 3 10:00 and Jan 5 22:00 has 2.5 days to the second order.""",
     hint1="Pattern: LEAD (the next order of the same user) on the user's first row, found with ROW_NUMBER.",
     hint2="1. CTE: ROW_NUMBER and `LEAD(order_time)` over `(PARTITION BY user_id ORDER BY order_time, order_id)`, "
           "join app_users for platform.\n2. Keep n = 1; repeat = next_time IS NOT NULL; days with julianday.",
     solution="""WITH o AS (
    SELECT p.user_id, u.platform, p.order_time,
           ROW_NUMBER() OVER w        AS n,
           LEAD(p.order_time) OVER w  AS next_time
    FROM purchases p
    JOIN app_users u ON u.user_id = p.user_id
    WINDOW w AS (PARTITION BY p.user_id ORDER BY p.order_time, p.order_id)
)
SELECT platform,
       COUNT(*) AS buyers,
       SUM(CASE WHEN next_time IS NOT NULL THEN 1 ELSE 0 END) AS repeat_buyers,
       ROUND(100.0 * SUM(CASE WHEN next_time IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_repeat,
       ROUND(AVG(julianday(next_time) - julianday(order_time)), 1) AS avg_days_to_2nd
FROM o
WHERE n = 1
GROUP BY platform
ORDER BY platform""",
     why="On the first order row (n = 1), LEAD gives the second order time, or NULL for one-time buyers. AVG skips "
         "NULLs, so the average covers repeat buyers only, which is what we want. Repeat rates are close across "
         "platforms (about 54% to 60%). PostgreSQL: `EXTRACT(EPOCH FROM next_time - order_time) / 86400`.",
     complexity="One window sort over purchases, then a group by.",
     mistakes="Taking `MAX - MIN` of order times (that is first to last, not first to second). Counting one-time "
              "buyers as 0 days in the average.",
     learn=["sql-lag-lead", "sql-dates"])

# ---------------------------------------------------------------- Q5 running totals
ex.q("Growth of the rater base", minutes=5, kind="sql",
     prompt="""MovieLens (real). A user is a **new rater** in the year of their first rating. Return `yr`,
`new_raters` and `total_raters` (cumulative number of raters up to that year).

Example: 97 new raters in 1996 and 27 in 1997 give totals of 97 and 124.""",
     hint1="Pattern: first event per user (MIN), count per year, then a running SUM over years.",
     hint2="1. CTE: `MIN(substr(rated_at, 1, 4))` per user.\n2. Group by year; `SUM(COUNT(*)) OVER (ORDER BY yr "
           "ROWS UNBOUNDED PRECEDING)`.",
     solution="""WITH firsts AS (
    SELECT user_id, MIN(substr(rated_at, 1, 4)) AS yr
    FROM ml_ratings
    GROUP BY user_id
)
SELECT yr,
       COUNT(*) AS new_raters,
       SUM(COUNT(*)) OVER (ORDER BY yr ROWS UNBOUNDED PRECEDING) AS total_raters
FROM firsts
GROUP BY yr
ORDER BY yr""",
     why="Each user is counted once, in their first year, so the running total ends at 610 (all users). Counting "
         "distinct users per year and summing would count returning users many times.",
     complexity="Group by over 100k ratings, then a window over 23 rows.",
     mistakes="`COUNT(DISTINCT user_id)` per year of any rating (active raters, not new raters). Forgetting the "
              "ORDER BY in the window (every row shows the grand total).",
     learn=["sql-running-totals", "sql-aggregation"])

# ---------------------------------------------------------------- Q6 combined
ex.q("Peak day per platform, with context", minutes=5, kind="sql",
     prompt="""Shopping app. For each `platform`, find the **day with the highest DAU** (users of that platform in
`daily_activity`; ties: earliest day) and show the platform's **7-day average DAU** ending on that day.

Return `platform`, `peak_day`, `peak_dau`, `dau_7d` (1 decimal).""",
     hint1="Pattern: daily counts per platform, a moving average per platform, then top 1 per platform. The moving "
           "average must be computed before you keep only the peak row.",
     hint2="1. CTE dau: platform, day, COUNT(*).\n2. CTE: `AVG(dau) OVER (PARTITION BY platform ORDER BY day ROWS "
           "BETWEEN 6 PRECEDING AND CURRENT ROW)`.\n3. CTE: `ROW_NUMBER() OVER (PARTITION BY platform ORDER BY dau "
           "DESC, day)`; keep 1.",
     solution="""WITH dau AS (
    SELECT u.platform, d.activity_date, COUNT(*) AS dau
    FROM daily_activity d
    JOIN app_users u ON u.user_id = d.user_id
    GROUP BY u.platform, d.activity_date
), smooth AS (
    SELECT platform, activity_date, dau,
           AVG(dau) OVER (PARTITION BY platform ORDER BY activity_date
                          ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS dau_7d
    FROM dau
), ranked AS (
    SELECT platform, activity_date, dau, dau_7d,
           ROW_NUMBER() OVER (PARTITION BY platform ORDER BY dau DESC, activity_date) AS rn
    FROM smooth
)
SELECT platform, activity_date AS peak_day, dau AS peak_dau, ROUND(dau_7d, 1) AS dau_7d
FROM ranked
WHERE rn = 1
ORDER BY platform""",
     why="Three steps, each one CTE: count, smooth, rank. The order matters: if you filtered to the peak row "
         "first, the moving average would only see one row. The peak is clearly above the 7-day average on every "
         "platform (for example android 147 versus 135.4), so a single day is a noisy summary; dashboards should "
         "show the smoothed line next to the raw one.",
     complexity="Group by, two window sorts per platform over 91 days.",
     mistakes="Partitioning the moving average by day instead of platform. Using MAX(dau) in a group by and "
              "losing the date. Ranking before smoothing.",
     learn=["sql-running-totals", "sql-top-n", "sql-cte"])

ex.save()
