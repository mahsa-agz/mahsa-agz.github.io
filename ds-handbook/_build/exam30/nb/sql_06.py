import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sql_easy_common import start, nrows, val

# Day 6 SQL: focus subqueries (scalar, IN / EXISTS, derived table, correlated); review CASE WHEN.
ex = start(6)

q1 = """SELECT COUNT(*) AS longer_than_avg,
       (SELECT COUNT(*) FROM Track) AS all_tracks,
       (SELECT ROUND(AVG(Milliseconds) / 60000.0, 2) FROM Track) AS avg_minutes
FROM Track
WHERE Milliseconds > (SELECT AVG(Milliseconds) FROM Track)"""
ex.q("Longer than average", minutes=4, level="easy", kind="sql",
     prompt="How many tracks are longer than the average track? Return one row: `longer_than_avg`, `all_tracks` "
            "(the total number of tracks) and `avg_minutes` (the average length in minutes, 2 decimals).",
     hint1="Signal: compare each row with one number computed from the whole table. Pattern: scalar subquery.",
     hint2="1. The inner query `SELECT AVG(Milliseconds) FROM Track` returns one value. 2. WHERE Milliseconds > "
           "(that subquery). 3. Scalar subqueries can also be columns in SELECT.",
     solution=q1,
     why="You cannot write `WHERE Milliseconds > AVG(Milliseconds)`: aggregates are not allowed in WHERE. A scalar "
         "subquery computes the average first. Long videos pull the mean up, so far fewer than half the tracks "
         "are above it (mean > median for right-skewed data).",
     complexity="Two scans of Track; the subquery is not correlated, so it runs once.",
     mistakes="`WHERE Milliseconds > AVG(Milliseconds)` (error). A subquery that returns several rows where one value "
              "is expected (error in PostgreSQL, silently the first row in SQLite).",
     learn=["sql-subqueries"])

q2 = """SELECT c.CustomerId, c.FirstName, c.LastName, c.Country
FROM Customer c
WHERE c.CustomerId IN (
    SELECT i.CustomerId
    FROM Invoice i
    JOIN InvoiceLine il ON il.InvoiceId = i.InvoiceId
    JOIN Track t ON t.TrackId = il.TrackId
    JOIN Genre g ON g.GenreId = t.GenreId
    WHERE g.Name = 'Jazz')
ORDER BY c.CustomerId"""
ex.q("Jazz buyers", minutes=5, level="easy", kind="sql",
     prompt="List the customers who bought at least one `Jazz` track. Each customer once: `CustomerId`, `FirstName`, "
            "`LastName`, `Country`, by CustomerId.\n\n"
            f"Expected: {nrows(ex, q2)} rows.",
     hint1="Signal: 'at least one' plus 'each customer once'. Pattern: IN (subquery) or EXISTS (a semi-join).",
     hint2="1. Inner query: CustomerIds from Invoice -> InvoiceLine -> Track -> Genre where the genre is Jazz. "
           "2. Outer query: customers WHERE CustomerId IN (inner query).",
     solution=q2,
     why="IN and EXISTS return each outer row at most once, however many jazz tracks a customer bought. A plain JOIN "
         "would repeat the customer once per jazz line and need DISTINCT.",
     complexity="O(InvoiceLine + Track) for the inner query, then a hash lookup per customer.",
     mistakes="Joining everything and forgetting DISTINCT (duplicates). Matching `g.Name LIKE '%Jazz%'` (fine here, "
              "but say which you mean).",
     learn=["sql-subqueries"])

q3 = """SELECT s.CustomerId, s.spend
FROM (SELECT CustomerId, ROUND(SUM(Total), 2) AS spend
      FROM Invoice
      GROUP BY CustomerId) AS s
WHERE s.spend > (SELECT SUM(Total) / COUNT(DISTINCT CustomerId) FROM Invoice)
ORDER BY s.spend DESC"""
ex.q("Above-average spenders", minutes=5, level="easy", kind="sql",
     prompt="Which customers spent more than the **average customer** (total revenue divided by the number of "
            "customers)? Return `CustomerId` and `spend` (2 decimals), highest first.\n\n"
            f"Expected: {nrows(ex, q3)} rows. The average customer spends about "
            f"{val(ex, 'SELECT ROUND(SUM(Total) / COUNT(DISTINCT CustomerId), 2) FROM Invoice')}.",
     hint1="Signal: compare a per-customer total with an average of those totals. Pattern: derived table "
           "(subquery in FROM) plus a scalar subquery.",
     hint2="1. Derived table: spend per customer (GROUP BY CustomerId). 2. Scalar: SUM(Total) / COUNT(DISTINCT "
           "CustomerId). 3. Outer WHERE spend > scalar.",
     solution=q3,
     why="The average customer spend is an average of per-customer sums, not `AVG(Total)` (that is the average "
         "invoice). Defining the grain first (one row per customer) avoids that mix-up. "
         "`HAVING SUM(Total) > (scalar)` without a derived table also works.",
     complexity="Two scans of Invoice.",
     mistakes="Comparing with AVG(Total), the average invoice, which makes every customer 'above average'. "
              "Forgetting the alias on the derived table (required in PostgreSQL and MySQL).",
     learn=["sql-subqueries", "sql-aggregation"])

q4 = """SELECT u.user_id
FROM users u
WHERE EXISTS (SELECT 1
              FROM events e
              JOIN videos v ON v.video_id = e.video_id
              WHERE e.user_id = u.user_id
                AND e.event_type = 'view'
                AND v.category = 'comedy')
  AND NOT EXISTS (SELECT 1
                  FROM events e
                  WHERE e.user_id = u.user_id
                    AND e.event_type = 'share')
ORDER BY u.user_id"""
ex.q("Watched comedy, never shared", minutes=6, level="easy", kind="sql",
     prompt="On the made-up product tables: find users who viewed at least one `comedy` video but have **never** "
            "shared any video. Return `user_id`.\n\n"
            f"Expected: {nrows(ex, q4)} rows.",
     hint1="Signal: 'at least one' and 'never' about related rows. Pattern: correlated EXISTS and NOT EXISTS "
           "subqueries.",
     hint2="1. FROM users u. 2. EXISTS (a comedy view where e.user_id = u.user_id). 3. AND NOT EXISTS (a share where "
           "e.user_id = u.user_id).",
     solution=q4,
     why="A correlated subquery refers to the outer row (`u.user_id`), so it is checked per user. EXISTS stops at the "
         "first match. NOT EXISTS is NULL-safe, unlike NOT IN.",
     complexity="With an index on events(user_id) each check is a short lookup; without one, the optimiser usually "
                "turns EXISTS into a hash semi-join, O(users + events).",
     mistakes="`NOT IN (SELECT user_id FROM events WHERE ...)` breaks if that list contains NULL. Writing the share "
              "condition in the same subquery as the comedy view (that asks for a different thing).",
     learn=["sql-subqueries"])

q5 = """SELECT CASE
         WHEN 1.0 * e.watch_sec / v.duration_sec >= 0.9 THEN 'completed'
         WHEN e.watch_sec < 5 THEN 'skipped'
         ELSE 'partial'
       END AS view_type,
       COUNT(*) AS views
FROM events e
JOIN videos v ON v.video_id = e.video_id
WHERE e.event_type = 'view'
GROUP BY view_type
ORDER BY views DESC"""
ex.q("Completed, partial or skipped", minutes=4, level="easy", kind="sql", review=True,
     prompt="Label each `view` event: `completed` if the user watched at least 90 percent of the video "
            "(`watch_sec / duration_sec >= 0.9`), `skipped` if they watched under 5 seconds, otherwise `partial`. "
            "Return `view_type` and `views`, most first.\n\n"
            "Example: 28 seconds of a 30-second video is `completed`.",
     hint1="Signal: labels from conditions, then counts per label. Pattern: CASE WHEN plus GROUP BY.",
     hint2="1. events JOIN videos for duration_sec. 2. CASE with the completed test first. "
           "3. Use 1.0 * watch_sec / duration_sec. 4. GROUP BY the label.",
     solution=q5,
     why="The first true branch wins, so order the branches on purpose: a 4-second view of a 4-second video counts "
         "as completed, not skipped. Make that choice explicit in an exam.",
     complexity="One pass over events joined to videos.",
     mistakes="Integer division (`watch_sec / duration_sec` is 0 for almost every row). Forgetting the view filter.",
     learn=["sql-case-when"])

ex.save()
