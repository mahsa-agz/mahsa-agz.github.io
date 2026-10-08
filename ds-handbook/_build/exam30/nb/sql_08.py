import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sql_easy_common import start, nrows

# Day 8 SQL: focus CTEs (WITH, several steps, reuse); review subqueries. First medium questions.
ex = start(8)

q1 = """WITH spend AS (
    SELECT CustomerId, SUM(Total) AS spend
    FROM Invoice
    GROUP BY CustomerId
)
SELECT CASE WHEN spend >= 45 THEN 'high'
            WHEN spend >= 40 THEN 'mid'
            ELSE 'low' END AS tier,
       COUNT(*) AS customers,
       ROUND(AVG(spend), 2) AS avg_spend
FROM spend
GROUP BY tier
ORDER BY avg_spend DESC"""
ex.q("Customer tiers", minutes=5, level="easy", kind="sql",
     prompt="Give each customer a tier from their total spend (sum of `Invoice.Total`): `high` if 45 or more, `mid` "
            "if 40 up to 45, else `low`. Return `tier`, `customers` and `avg_spend` (2 decimals), highest tier "
            "first.\n\n"
            "Write it with a CTE: step 1 computes spend per customer, step 2 buckets and counts.",
     hint1="Signal: aggregate, then aggregate again on the result. Pattern: CTE (WITH) as a named first step.",
     hint2="1. WITH spend AS (SELECT CustomerId, SUM(Total) AS spend FROM Invoice GROUP BY CustomerId). "
           "2. SELECT CASE ... END AS tier, COUNT(*), AVG(spend) FROM spend GROUP BY tier.",
     solution=q1,
     why="You cannot nest aggregates (`COUNT(SUM(...))`), so you need two levels. A CTE names the first level and "
         "reads top to bottom, which examiners find easier to follow than a nested subquery.",
     complexity="One scan of Invoice, then 59 rows.",
     mistakes="Bucketing invoices instead of customers (CASE on Total, not on the sum). Overlapping thresholds.",
     learn=["sql-cte", "sql-case-when"])

q2 = """WITH per_user AS (
    SELECT user_id,
           SUM(CASE WHEN event_type = 'view' THEN 1 ELSE 0 END) AS views,
           SUM(CASE WHEN event_type = 'like' THEN 1 ELSE 0 END) AS likes
    FROM events
    GROUP BY user_id
)
SELECT user_id, views, likes,
       ROUND(1.0 * likes / views, 3) AS like_rate
FROM per_user
WHERE views >= 5
ORDER BY like_rate DESC, user_id"""
ex.q("Who likes what they watch?", minutes=6, level="medium", kind="sql",
     prompt="On the made-up product tables: for users with at least 5 views, compute `like_rate` = likes / views "
            "(3 decimals). Return `user_id`, `views`, `likes`, `like_rate`, highest rate first (ties by user_id).\n\n"
            f"Expected: {nrows(ex, q2)} rows.\n\n"
            "Follow-up: what changes if the events table can contain exact duplicate rows (the same event logged twice)?",
     hint1="Signal: per-user counts, then a filter and a ratio on those counts. Pattern: CTE with conditional "
           "aggregation, then a simple outer query.",
     hint2="1. CTE per_user: GROUP BY user_id with SUM(CASE ...) for views and likes. 2. Outer: WHERE views >= 5, "
           "ratio 1.0 * likes / views, ORDER BY.",
     solution=q2,
     why="The CTE gives one clean row per user; the filter and ratio are then trivial. Follow-up: add a first CTE "
         "`dedup AS (SELECT DISTINCT user_id, video_id, event_type, event_time FROM events)` and read from it; "
         "event_id differs between copies, so leave it out of the DISTINCT. Chaining CTEs this way is the habit "
         "examiners look for.",
     complexity="One scan of events.",
     mistakes="Integer division. Filtering `views >= 5` inside the CTE with WHERE (WHERE runs before grouping, it would "
              "need HAVING there). Dividing by zero if you drop the filter: guard with NULLIF(views, 0).",
     learn=["sql-cte", "sql-ratios"])

q3 = """WITH country_rev AS (
    SELECT BillingCountry AS country, SUM(Total) AS revenue
    FROM Invoice
    GROUP BY BillingCountry
),
total AS (
    SELECT SUM(revenue) AS all_revenue FROM country_rev
)
SELECT c.country,
       ROUND(c.revenue, 2) AS revenue,
       ROUND(100.0 * c.revenue / t.all_revenue, 1) AS pct_of_total
FROM country_rev c
CROSS JOIN total t
ORDER BY c.revenue DESC
LIMIT 5"""
ex.q("Share of revenue", minutes=6, level="medium", kind="sql",
     prompt="For the five biggest billing countries return `country`, `revenue` (2 decimals) and `pct_of_total` "
            "(percent of all revenue, 1 decimal). Biggest first.\n\n"
            "Example: if total revenue were 2000 and USA had 500, USA would show 25.0.",
     hint1="Signal: each row needs a number computed over all rows. Pattern: two CTEs (per group and total) and a "
           "CROSS JOIN of the one-row total.",
     hint2="1. CTE country_rev: revenue per country. 2. CTE total: SUM(revenue) FROM country_rev (one row). "
           "3. SELECT ... FROM country_rev CROSS JOIN total. 4. 100.0 * revenue / all_revenue.",
     solution=q3,
     why="A one-row CTE joined to every row is the classic way to divide by a grand total. A later CTE can read an "
         "earlier one. With window functions you can also write `SUM(revenue) OVER ()` (day 13).",
     complexity="One scan of Invoice, then 24 country rows.",
     mistakes="Taking LIMIT 5 before computing the total (the total would only cover 5 countries). "
              "Using 100 instead of 100.0 (integer division in PostgreSQL when both sides are integers).",
     learn=["sql-cte", "sql-ratios"])

q4 = """WITH video_stats AS (
    SELECT v.video_id, v.creator_id,
           COUNT(e.event_id) AS views,
           COALESCE(SUM(e.watch_sec), 0) AS watch_sec
    FROM videos v
    LEFT JOIN events e ON e.video_id = v.video_id AND e.event_type = 'view'
    GROUP BY v.video_id, v.creator_id
),
creator_stats AS (
    SELECT creator_id,
           COUNT(*) AS videos,
           SUM(views) AS views,
           ROUND(SUM(watch_sec) / 60.0, 1) AS watch_minutes
    FROM video_stats
    GROUP BY creator_id
)
SELECT c.creator_id, COALESCE(u.country, 'unknown') AS country,
       c.videos, c.views, c.watch_minutes
FROM creator_stats c
JOIN users u ON u.user_id = c.creator_id
ORDER BY c.views DESC, c.creator_id"""
ex.q("Creator scoreboard", minutes=7, level="medium", kind="sql",
     prompt="On the made-up product tables, build a creator scoreboard. For every creator (a user who uploaded at "
            "least one video) return `creator_id`, `country` (`unknown` if NULL), `videos` (uploaded), `views` "
            "(view events on their videos, 0 if none) and `watch_minutes` (1 decimal). Most views first, ties by "
            "creator_id.\n\n"
            f"Expected: {nrows(ex, q4)} rows.",
     hint1="Signal: stats at two grains (video, then creator) plus a label from a third table. Pattern: chained CTEs, "
           "LEFT JOIN to keep videos with no views.",
     hint2="1. CTE video_stats: videos LEFT JOIN events (views only, in ON), one row per video with views and "
           "watch_sec. 2. CTE creator_stats: GROUP BY creator_id from video_stats. 3. Join users for the country.",
     solution=q4,
     why="Aggregating per video first stops the fan-out: if you join events directly and count videos, a video with "
         "30 views counts 30 times. Each CTE has one clear grain, which makes the query easy to debug step by step.",
     complexity="O(videos + events + users).",
     mistakes="`COUNT(*)` of videos after joining events (counts views, not videos). Filtering views in WHERE, which "
              "drops videos without views and their creators' video counts.",
     learn=["sql-cte", "sql-left-join-nulls"])

q5 = """SELECT al.Title AS album, COUNT(*) AS tracks
FROM Album al
JOIN Track t ON t.AlbumId = al.AlbumId
GROUP BY al.AlbumId, al.Title
HAVING COUNT(*) > (SELECT AVG(n)
                   FROM (SELECT COUNT(*) AS n FROM Track GROUP BY AlbumId) AS per_album) * 2
ORDER BY tracks DESC, album"""
ex.q("Unusually long albums", minutes=5, level="easy", kind="sql", review=True,
     prompt="Which albums have more than **twice** the average number of tracks per album? Return `album` (title) "
            "and `tracks`, most tracks first (ties by title).\n\n"
            f"Expected: {nrows(ex, q5)} rows.",
     hint1="Signal: compare a group count with an average of group counts. Pattern: subquery over a derived table "
           "inside HAVING.",
     hint2="1. Inner derived table: COUNT(*) per AlbumId. 2. AVG of those counts (scalar). 3. Outer: GROUP BY album, "
           "HAVING COUNT(*) > 2 * (scalar).",
     solution=q5,
     why="The average album size is an average of counts, so it needs its own GROUP BY inside a subquery. "
         "The same thing as a CTE: `WITH per_album AS (...) SELECT ... HAVING COUNT(*) > 2 * (SELECT AVG(n) FROM "
         "per_album)`.",
     complexity="Two scans of Track.",
     mistakes="Using AVG(COUNT(*)) directly (nested aggregates are not allowed). Dividing total tracks by total "
              "albums including albums without tracks (here every album has tracks, but check).",
     learn=["sql-subqueries", "sql-cte"])

ex.save()
