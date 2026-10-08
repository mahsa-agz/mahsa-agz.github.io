import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam
from sql_hard_tables import load, put_doc

ex = Exam(23, "sql")
code, doc = load("chinook", "apps", "retail", "movielens")
ex.setup(code, data=True)
put_doc(ex, doc)

ex.q("Typical track length per genre", minutes=5, kind="sql",
     prompt="""Chinook (real). SQLite (like many exam editors) has no `MEDIAN` function. For every genre with at
least 20 tracks return `genre`, `tracks`, `median_min` (median of `Milliseconds / 60000.0`, 2 decimals) and `avg_min`
(2 decimals). Show the 6 genres with the highest median.

Example: lengths 3, 4, 10 have median 4; lengths 3, 4, 5, 10 have median 4.5.

*Follow-up:* for TV Shows the average is far below the median. What does that tell you about the data?""",
     hint1="Signal: 'median' without a MEDIAN function. Pattern: median with ROW_NUMBER and COUNT windows: keep the "
           "middle row (odd count) or the two middle rows (even count) and average them.",
     hint2="1. CTE: `ROW_NUMBER() OVER (PARTITION BY genre ORDER BY ms)` and `COUNT(*) OVER (PARTITION BY genre)`.\n"
           "2. Middle rows: `rn IN ((cnt + 1) / 2, (cnt + 2) / 2)` (integer division: one row if cnt is odd, two if even).\n"
           "3. AVG of those rows per genre; join the plain AVG per genre for comparison.",
     solution="""WITH t AS (
  SELECT g.Name AS genre, t.Milliseconds / 60000.0 AS minutes,
    ROW_NUMBER() OVER (PARTITION BY t.GenreId ORDER BY t.Milliseconds) AS rn,
    COUNT(*) OVER (PARTITION BY t.GenreId) AS cnt
  FROM Track t JOIN Genre g ON g.GenreId = t.GenreId
), med AS (
  SELECT genre, cnt AS tracks, AVG(minutes) AS median_min
  FROM t
  WHERE rn IN ((cnt + 1) / 2, (cnt + 2) / 2)
  GROUP BY genre, cnt
), avgs AS (
  SELECT genre, AVG(minutes) AS avg_min FROM t GROUP BY genre
)
SELECT m.genre, m.tracks, ROUND(m.median_min, 2) AS median_min, ROUND(a.avg_min, 2) AS avg_min
FROM med m JOIN avgs a ON a.genre = m.genre
WHERE m.tracks >= 20
ORDER BY m.median_min DESC
LIMIT 6""",
     why="`(cnt + 1) / 2` and `(cnt + 2) / 2` are the same row when cnt is odd (cnt = 5: 3 and 3) and the two middle "
         "rows when it is even (cnt = 4: 2 and 3), so one formula covers both cases. Follow-up: TV Shows has median "
         "43.03 but mean 35.75: the distribution is skewed LEFT, a group of short items (trailers or short episodes) "
         "pulls the mean down. That is why medians are preferred for skewed metrics like watch time.",
     complexity="One window sort per genre: O(n log n).",
     mistakes="`rn = cnt / 2` only (wrong for odd counts, or picks one of the two middle rows for even counts). "
              "Integer division of Milliseconds by 60000. PostgreSQL has `PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY x)`; "
              "BigQuery has `APPROX_QUANTILES`; say so, then write the portable version.",
     learn=["sql-median-percentiles", "sql-window-ranking"])

ex.q("Order value percentiles, UK versus abroad", minutes=6, kind="sql",
     prompt="""UCI Online Retail (real). An order is one `invoice_no`; its value is `SUM(quantity * unit_price)`. Use
only real sales: `invoice_no` not starting with 'C', `quantity > 0`, `unit_price > 0`. Split orders into `market` =
'UK' (country is United Kingdom) or 'other'. Return per market: `n` orders, `p50`, `p90`, `p99` (nearest-rank method:
the smallest value whose cumulative share is at least p) and `mean`, all values with 2 decimals.

Example (nearest rank): values 10, 20, 30, 40: p50 = 20 (2 of 4 = 50% are <= 20), p90 = 40.

*Follow-up:* the mean is far above the median in both markets. Which number goes on the dashboard, and why?""",
     hint1="Signal: p90 / p99 per group. Pattern: percentiles with CUME_DIST (or ROW_NUMBER / COUNT), then "
           "`MIN(CASE WHEN cume_dist >= p THEN value END)` and a pivot of p50, p90, p99 into columns.",
     hint2="1. CTE `inv`: GROUP BY invoice_no, market: SUM(quantity * unit_price).\n"
           "2. CTE `cd`: `CUME_DIST() OVER (PARTITION BY market ORDER BY value)`.\n"
           "3. Per market: `MIN(CASE WHEN c >= 0.9 THEN value END)` etc.",
     solution="""WITH inv AS (
  SELECT invoice_no,
    CASE WHEN country = 'United Kingdom' THEN 'UK' ELSE 'other' END AS market,
    SUM(quantity * unit_price) AS value
  FROM retail
  WHERE invoice_no NOT LIKE 'C%' AND quantity > 0 AND unit_price > 0
  GROUP BY invoice_no, market
), cd AS (
  SELECT market, value,
    CUME_DIST() OVER (PARTITION BY market ORDER BY value) AS c
  FROM inv
)
SELECT market, COUNT(*) AS n,
  ROUND(MIN(CASE WHEN c >= 0.50 THEN value END), 2) AS p50,
  ROUND(MIN(CASE WHEN c >= 0.90 THEN value END), 2) AS p90,
  ROUND(MIN(CASE WHEN c >= 0.99 THEN value END), 2) AS p99,
  ROUND(AVG(value), 2) AS mean
FROM cd
GROUP BY market
ORDER BY market""",
     why="CUME_DIST is the share of rows with a value less than or equal to the current one, so the first value that "
         "reaches p is the nearest-rank percentile. Ties get the same CUME_DIST, so tied values never split. UK: "
         "p50 300.50, mean 500.87; abroad: p50 424.06, p99 9,341.26. Follow-up: show the median (typical order) and "
         "p90 (big orders) on the dashboard; the mean is pulled up by a few wholesale orders and moves when one huge "
         "order arrives. Report the mean only when you need totals (revenue = mean * orders).",
     complexity="Aggregation, then one window sort per market: O(n log n).",
     mistakes="Grouping by country without the CASE (one row per country). Taking percentiles of LINE values instead "
              "of ORDER values. Using NTILE(100) for p99 (NTILE splits rows into equal buckets and breaks ties). "
              "PostgreSQL: `PERCENTILE_DISC(0.9) WITHIN GROUP (ORDER BY value)` is exactly nearest rank.",
     learn=["sql-median-percentiles", "sql-pivot"])

ex.q("How long from first look to first purchase?", minutes=6, kind="sql", review=True,
     prompt="""Shopping app (made up). For each user take the first `view_item` time and the first `purchase` **after**
it (`app_events`). For users who have both, compute the gap in hours. Return per `platform` (from `app_users`):
`buyers` (users with both events) and `median_hours` (1 decimal).

Example: first view Monday 10:00, purchases Monday 09:00 and Wednesday 10:00: the gap is 48 hours (the Monday 09:00
purchase is before the first view, so it does not count).

*Follow-up:* the average gap is about 2 to 2.5 times the median. Why report the median here?""",
     hint1="Signal: time between two funnel steps, 'median'. Pattern: funnel step pairs (first A, first B after A) "
           "plus a median via ROW_NUMBER / COUNT.",
     hint2="1. `fv`: MIN(event_time) of view_item per user.\n2. `fp`: join purchases with `event_time > view_t`, MIN per user.\n"
           "3. hours = `(julianday(buy_t) - julianday(view_t)) * 24`, join platform.\n"
           "4. Median per platform with `rn IN ((cnt + 1) / 2, (cnt + 2) / 2)`.",
     solution="""WITH fv AS (
  SELECT user_id, MIN(event_time) AS view_t
  FROM app_events WHERE event_name = 'view_item'
  GROUP BY user_id
), fp AS (
  SELECT fv.user_id, fv.view_t, MIN(e.event_time) AS buy_t
  FROM fv
  JOIN app_events e
    ON e.user_id = fv.user_id AND e.event_name = 'purchase' AND e.event_time > fv.view_t
  GROUP BY fv.user_id, fv.view_t
), d AS (
  SELECT u.platform, (julianday(fp.buy_t) - julianday(fp.view_t)) * 24 AS hours
  FROM fp JOIN app_users u ON u.user_id = fp.user_id
), r AS (
  SELECT platform, hours,
    ROW_NUMBER() OVER (PARTITION BY platform ORDER BY hours) AS rn,
    COUNT(*) OVER (PARTITION BY platform) AS cnt
  FROM d
)
SELECT platform, cnt AS buyers, ROUND(AVG(hours), 1) AS median_hours
FROM r
WHERE rn IN ((cnt + 1) / 2, (cnt + 2) / 2)
GROUP BY platform, cnt
ORDER BY platform""",
     why="The join condition `e.event_time > fv.view_t` makes the steps ordered, and MIN picks the first qualifying "
         "purchase. Android buyers convert fastest (median 85.6 hours), web slowest (134.1). Follow-up: the means are "
         "212.5 (android), 230.9 (ios) and 260.2 (web) hours: a long tail of users who buy weeks later pulls the mean "
         "up. The median describes the typical buyer and is robust to that tail.",
     complexity="Two aggregations on events plus a window sort: O(n log n).",
     mistakes="Using the first purchase overall (it can be before the first view: negative gaps). Subtracting text "
              "timestamps directly. In PostgreSQL use `EXTRACT(EPOCH FROM buy_t - view_t) / 3600`.",
     learn=["sql-funnels", "sql-median-percentiles"])

ex.q("How concentrated is the rating activity?", minutes=5, kind="sql",
     prompt="""MovieLens (real). Count ratings per user. Return one row with: `median_n` (median ratings per user),
`p90_n` (nearest-rank p90), `mean_n` (1 decimal) and `top10_share`: the % of ALL ratings made by the 10% of users who
rate most (1 decimal).

Example: 10 users with counts 1, 1, 1, 1, 1, 1, 1, 1, 1, 91: median 1, top 10% (one user) share = 91 / 100 = 91.0%.

*Follow-up:* a PM asks for "the average user". What do you answer?""",
     hint1="Signal: 'median', 'p90' and 'top 10% of users'. Pattern: percentiles with ROW_NUMBER / CUME_DIST, and "
           "NTILE(10) for deciles.",
     hint2="1. `per_user`: COUNT(*) per user_id.\n2. One CTE with ROW_NUMBER, COUNT(*) OVER (), CUME_DIST and "
           "`NTILE(10) OVER (ORDER BY n DESC)`.\n3. Median: AVG over the middle rows (scalar subquery); p90: "
           "`MIN(CASE WHEN cd >= 0.9 THEN n END)`; share: `SUM(CASE WHEN decile = 1 THEN n END) / SUM(n)`.",
     solution="""WITH per_user AS (
  SELECT user_id, COUNT(*) AS n FROM ml_ratings GROUP BY user_id
), r AS (
  SELECT n,
    ROW_NUMBER() OVER (ORDER BY n) AS rn,
    COUNT(*) OVER () AS cnt,
    CUME_DIST() OVER (ORDER BY n) AS cd,
    NTILE(10) OVER (ORDER BY n DESC) AS decile
  FROM per_user
)
SELECT
  (SELECT AVG(n) FROM r WHERE rn IN ((cnt + 1) / 2, (cnt + 2) / 2)) AS median_n,
  MIN(CASE WHEN cd >= 0.9 THEN n END) AS p90_n,
  ROUND(AVG(n), 1) AS mean_n,
  ROUND(100.0 * SUM(CASE WHEN decile = 1 THEN n ELSE 0 END) / SUM(n), 1) AS top10_share
FROM r""",
     why="NTILE(10) over users sorted by activity gives deciles of USERS (61 users each for 610 users), and summing "
         "their ratings gives their share. The typical user has 70.5 ratings, the mean is 165.3, and the top 10% of "
         "users make 47.7% of all ratings. Follow-up: there is no 'average user' in such a skewed distribution: give "
         "the median (70.5), and say that the top decile behaves very differently, so models and metrics should be "
         "checked per segment (heavy versus light users).",
     complexity="One aggregation and one window sort over users.",
     mistakes="NTILE over RATINGS instead of users. Taking the mean as 'typical'. Forgetting that NTILE puts the extra "
              "rows in the first buckets when n is not divisible by 10 (fine here, but say it).",
     learn=["sql-median-percentiles", "sql-window-ranking"])

ex.q("Order count histogram per platform", minutes=4, kind="sql", review=True,
     prompt="""Shopping app (made up). Count **completed** orders per user (`purchases`), keeping users with zero. Return
one row per `platform` with columns `users`, `o0`, `o1`, `o2`, `o3plus` (number of users with 0, 1, 2, 3 or more
completed orders) and `repeat_pct` = users with 2+ orders / users with 1+ orders (1 decimal). Order by platform.""",
     hint1="Signal: buckets as columns. Pattern: pivot with conditional aggregation on a per-user count built with a "
           "LEFT JOIN (status filter in the ON clause).",
     hint2="1. CTE: `app_users u LEFT JOIN purchases p ON p.user_id = u.user_id AND p.status = 'completed'`, "
           "COUNT(p.order_id) per user.\n2. Outer: `SUM(CASE WHEN orders = 0 THEN 1 ELSE 0 END)` etc. per platform.",
     solution="""WITH n AS (
  SELECT u.user_id, u.platform, COUNT(p.order_id) AS orders
  FROM app_users u
  LEFT JOIN purchases p ON p.user_id = u.user_id AND p.status = 'completed'
  GROUP BY u.user_id, u.platform
)
SELECT platform, COUNT(*) AS users,
  SUM(CASE WHEN orders = 0 THEN 1 ELSE 0 END) AS o0,
  SUM(CASE WHEN orders = 1 THEN 1 ELSE 0 END) AS o1,
  SUM(CASE WHEN orders = 2 THEN 1 ELSE 0 END) AS o2,
  SUM(CASE WHEN orders >= 3 THEN 1 ELSE 0 END) AS o3plus,
  ROUND(100.0 * SUM(CASE WHEN orders >= 2 THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN orders >= 1 THEN 1 ELSE 0 END), 0), 1) AS repeat_pct
FROM n
GROUP BY platform
ORDER BY platform""",
     why="The status filter sits in the ON clause, so users whose only orders were refunded still appear with 0. "
         "COUNT(p.order_id) counts only matched rows (COUNT(*) would give 1 to non-buyers). Repeat rates are close "
         "(53.8% to 58.1%), so platforms differ in how many users buy at all, not in loyalty once they buy.",
     complexity="One join and two GROUP BYs: O(users + orders).",
     mistakes="`WHERE p.status = 'completed'` after a LEFT JOIN (drops non-buyers: o0 becomes 0). COUNT(*) instead of "
              "COUNT(p.order_id). Repeat rate over ALL users instead of buyers.",
     learn=["sql-pivot", "sql-left-join-nulls"])

ex.save()
