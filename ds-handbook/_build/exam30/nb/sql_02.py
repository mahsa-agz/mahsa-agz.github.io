import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sql_easy_common import start, nrows

# Day 2 SQL: focus aggregation (COUNT, SUM, AVG, GROUP BY, HAVING); review basics.
ex = start(2)

q1 = """SELECT BillingCountry AS country,
       COUNT(*)                 AS invoices,
       ROUND(SUM(Total), 2)     AS revenue,
       ROUND(AVG(Total), 2)     AS avg_invoice
FROM Invoice
GROUP BY BillingCountry
ORDER BY revenue DESC
LIMIT 5"""
ex.q("Revenue by country", minutes=4, level="easy", kind="sql",
     prompt="Finance wants the five billing countries with the most revenue. For each, return `country`, "
            "`invoices` (number of invoices), `revenue` (sum of `Total`) and `avg_invoice` (average `Total`), both "
            "rounded to 2 decimals. Highest revenue first.\n\n"
            "Example: if Chile had 3 invoices of 2, 4 and 6, the row would be `Chile, 3, 12.0, 4.0`.",
     hint1="Signal: 'for each country' plus totals. Pattern: GROUP BY with COUNT, SUM, AVG.",
     hint2="1. FROM Invoice GROUP BY BillingCountry. 2. SELECT the country, COUNT(*), ROUND(SUM(Total), 2), "
           "ROUND(AVG(Total), 2). 3. ORDER BY revenue DESC LIMIT 5.",
     solution=q1,
     why="GROUP BY collapses all invoices of a country into one row; aggregates summarise each group. ORDER BY can "
         "use the SELECT alias because it runs after SELECT. Rounding hides float noise (in floating point, 0.1 + 0.2 gives 0.30000000000000004).",
     complexity="One scan of Invoice (412 rows) and a hash per country.",
     mistakes="Selecting a column that is neither grouped nor aggregated (PostgreSQL rejects it; SQLite silently "
              "picks a random row). Rounding before summing (small errors add up). Using the alias in WHERE "
              "(WHERE runs before SELECT).",
     learn=["sql-aggregation", "sql-query-order"])

q2 = """SELECT g.Name AS genre,
       COUNT(*) AS tracks,
       ROUND(AVG(t.Milliseconds) / 60000.0, 2) AS avg_minutes
FROM Track t
JOIN Genre g ON g.GenreId = t.GenreId
GROUP BY g.Name
HAVING COUNT(*) > 100
ORDER BY tracks DESC"""
ex.q("Big genres only", minutes=5, level="easy", kind="sql",
     prompt="Which genres have more than 100 tracks? Return `genre` (the genre name), `tracks` and `avg_minutes` "
            "(average track length in minutes, 2 decimals), most tracks first.\n\n"
            "The genre name lives in `Genre`, so you need one simple join: "
            "`FROM Track t JOIN Genre g ON g.GenreId = t.GenreId`.\n\n"
            f"Expected: {nrows(ex, q2)} rows.",
     hint1="Signal: a condition on a group total ('more than 100 tracks'). Pattern: GROUP BY with HAVING.",
     hint2="1. Join Track to Genre. 2. GROUP BY the genre name. 3. HAVING COUNT(*) > 100 (not WHERE). "
           "4. AVG(Milliseconds) / 60000.0 for minutes. 5. ORDER BY tracks DESC.",
     solution=q2,
     why="WHERE filters rows before grouping; HAVING filters groups after aggregation. A condition on COUNT(*) can "
         "only live in HAVING.",
     complexity="One scan of Track plus a hash aggregate over 25 genres.",
     mistakes="`WHERE COUNT(*) > 100` is an error. Using the alias `tracks` inside HAVING works in SQLite and MySQL "
              "but not in PostgreSQL; repeat `COUNT(*)` to be portable.",
     learn=["sql-aggregation"])

q3 = """SELECT event_type,
       COUNT(*)                AS n_events,
       COUNT(DISTINCT user_id) AS n_users,
       COUNT(watch_sec)        AS n_with_watch_time
FROM events
GROUP BY event_type
ORDER BY n_events DESC"""
ex.q("Events by type", minutes=4, level="easy", kind="sql",
     prompt="On the made-up `events` table, return one row per `event_type` with `n_events` (rows), `n_users` "
            "(distinct users who did it) and `n_with_watch_time` (rows where `watch_sec` is not NULL). "
            "Most events first.\n\n"
            "Example: a user who liked 5 videos adds 5 to `n_events` for `like` but only 1 to `n_users`.",
     hint1="Signal: three different kinds of 'count'. Pattern: COUNT(*) vs COUNT(DISTINCT col) vs COUNT(col).",
     hint2="1. GROUP BY event_type. 2. COUNT(*) counts rows. 3. COUNT(DISTINCT user_id) counts unique users. "
           "4. COUNT(watch_sec) skips NULLs.",
     solution=q3,
     why="COUNT(*) counts rows, COUNT(col) counts non-NULL values, COUNT(DISTINCT col) counts unique non-NULL "
         "values. Only views have watch time, so the last column is 0 for the other types.",
     complexity="One scan of events.",
     mistakes="Using COUNT(user_id) when the question asks for unique users. Expecting COUNT(watch_sec) to count the "
              "NULL rows. Examiners love this question because the three counts differ.",
     learn=["sql-aggregation"])

q4 = """SELECT user_id,
       COUNT(*) AS views,
       ROUND(SUM(watch_sec) / 60.0, 1) AS watch_minutes
FROM events
WHERE event_type = 'view'
GROUP BY user_id
HAVING COUNT(*) >= 10
ORDER BY watch_minutes DESC"""
ex.q("Heavy viewers", minutes=5, level="easy", kind="sql",
     prompt="A *heavy viewer* has at least 10 `view` events. For each heavy viewer return `user_id`, `views` and "
            "`watch_minutes` (total `watch_sec` of their views divided by 60, one decimal). Most watch time first.\n\n"
            f"Expected: {nrows(ex, q4)} rows.",
     hint1="Signal: filter rows (only views), then filter groups (at least 10). Pattern: WHERE plus GROUP BY plus "
           "HAVING.",
     hint2="1. WHERE event_type = 'view'. 2. GROUP BY user_id. 3. HAVING COUNT(*) >= 10. "
           "4. SUM(watch_sec) / 60.0. 5. ORDER BY watch_minutes DESC.",
     solution=q4,
     why="The row filter (views only) belongs in WHERE so likes are never counted; the group filter belongs in "
         "HAVING. Order of execution: FROM, WHERE, GROUP BY, HAVING, SELECT, ORDER BY.",
     complexity="One scan of events plus a hash per user.",
     mistakes="Putting `event_type = 'view'` in HAVING (error or wrong meaning). Counting all event types as views. "
              "`SUM(watch_sec) / 60` is integer division.",
     learn=["sql-aggregation", "sql-query-order"])

q5 = """SELECT Name,
       COALESCE(Composer, 'Unknown') AS composer,
       ROUND(Milliseconds / 1000.0, 0) AS seconds
FROM Track
WHERE MediaTypeId <> 3
ORDER BY Milliseconds
LIMIT 10"""
ex.q("Shortest audio tracks", minutes=3, level="easy", kind="sql", review=True,
     prompt="List the 10 shortest audio tracks (leave out videos, `MediaTypeId = 3`). Return `Name`, `composer` "
            "(show `Unknown` when `Composer` is NULL) and `seconds` (length in whole seconds). Shortest first.",
     hint1="Signal: sort ascending and keep a few, replace NULLs for display. Pattern: basics with ORDER BY, LIMIT, "
           "COALESCE.",
     hint2="1. WHERE MediaTypeId <> 3. 2. COALESCE(Composer, 'Unknown'). 3. Milliseconds / 1000.0 rounded. "
           "4. ORDER BY Milliseconds LIMIT 10.",
     solution=q5,
     why="ORDER BY ascending is the default. COALESCE only changes what is shown; the row is still there.",
     complexity="One scan and a sort (or a top-10 heap) of Track.",
     mistakes="Ordering by the rounded `seconds` gives unstable ties. Writing `Composer = NULL` instead of COALESCE "
              "or IS NULL.",
     learn=["sql-basics"])

ex.save()
