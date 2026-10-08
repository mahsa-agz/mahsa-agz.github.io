import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sql_easy_common import start, nrows

# Day 7 SQL: mock exam over days 1 to 6 (basics, aggregation, joins, left-join-nulls, case-when, subqueries).
INTRO = ("**Mock exam rules.** Set one timer for **30 minutes** for the whole notebook. Work in order, but skip a "
         "question after 7 minutes and come back. Do not open any hint or solution until the timer ends. "
         "Then grade yourself: a question counts as solved only if the result matches exactly (columns, rows, "
         "order). Put every miss in the mistake log.")
ex = start(7, intro=INTRO)

q1 = """SELECT FirstName, LastName, Title, DATE(HireDate) AS hired
FROM Employee
WHERE HireDate >= '2003-01-01'
ORDER BY HireDate, LastName"""
ex.q("Newer employees", minutes=3, level="easy", kind="sql",
     prompt="List employees hired on or after 1 January 2003. Return `FirstName`, `LastName`, `Title` and `hired` "
            "(the date only, `YYYY-MM-DD`), earliest hire first (ties by last name).\n\n"
            f"Expected: {nrows(ex, q1)} rows.",
     hint1="Signal: a simple filter and sort. Pattern: basics (WHERE on an ISO date string, ORDER BY).",
     hint2="1. WHERE HireDate >= '2003-01-01'. 2. DATE(HireDate) drops the time part. 3. ORDER BY HireDate, LastName.",
     solution=q1,
     why="SQLite stores these dates as ISO text (`2003-05-03 00:00:00`), and ISO strings sort like dates, so a "
         "string comparison is correct. In PostgreSQL the column would be a timestamp and the same literal works.",
     complexity="One scan of Employee.",
     mistakes="Comparing with '1/1/2003' (not ISO, string order breaks). `>` instead of `>=` (misses a hire on the day).",
     learn=["sql-basics"])

q2 = """SELECT Composer, COUNT(*) AS tracks
FROM Track
WHERE Composer IS NOT NULL
GROUP BY Composer
ORDER BY tracks DESC, Composer
LIMIT 5"""
ex.q("Most prolific composers", minutes=4, level="easy", kind="sql",
     prompt="Return the 5 composers with the most tracks: `Composer` and `tracks`, most first (ties by name). "
            "Tracks with no composer (NULL) must not count as a composer.",
     hint1="Signal: count per value, keep the top few. Pattern: GROUP BY, ORDER BY the count, LIMIT; filter NULL "
           "first.",
     hint2="1. WHERE Composer IS NOT NULL. 2. GROUP BY Composer. 3. ORDER BY COUNT(*) DESC, Composer. 4. LIMIT 5.",
     solution=q2,
     why="GROUP BY puts all NULLs into one group, which would be the 'top composer' here. Filtering them in WHERE "
         "removes that fake group.",
     complexity="One scan of Track plus a hash per composer.",
     mistakes="Forgetting the NULL filter (a NULL row on top). Note the data quirk: `Composer` is free text, so "
              "'Jagger/Richards' and 'Keith Richards/Mick Jagger' are different groups.",
     learn=["sql-aggregation"])

q3 = """SELECT e.FirstName || ' ' || e.LastName AS rep,
       COUNT(i.InvoiceId) AS invoices,
       ROUND(SUM(i.Total), 2) AS revenue
FROM Employee e
JOIN Customer c ON c.SupportRepId = e.EmployeeId
JOIN Invoice i  ON i.CustomerId = c.CustomerId
GROUP BY e.EmployeeId, rep
ORDER BY revenue DESC"""
ex.q("Revenue per support rep", minutes=5, level="easy", kind="sql",
     prompt="Credit each invoice to the support rep of its customer. Return `rep` (full name), `invoices` and "
            "`revenue` (2 decimals), highest revenue first.",
     hint1="Signal: a chain Employee -> Customer -> Invoice. Pattern: INNER JOINs, then GROUP BY the employee.",
     hint2="1. Employee e JOIN Customer c ON c.SupportRepId = e.EmployeeId. 2. JOIN Invoice i ON i.CustomerId = "
           "c.CustomerId. 3. GROUP BY e.EmployeeId. 4. COUNT and SUM.",
     solution=q3,
     why="Each invoice has one customer and each customer one rep, so the joins do not duplicate invoices.",
     complexity="O(Employee + Customer + Invoice).",
     mistakes="Joining Customer to Employee on EmployeeId = CustomerId. Grouping by name only.",
     learn=["sql-joins"])

q4 = """SELECT v.category,
       COUNT(DISTINCT v.video_id) AS videos,
       COUNT(DISTINCT v.video_id) - COUNT(DISTINCT e.video_id) AS videos_without_views
FROM videos v
LEFT JOIN events e
       ON e.video_id = v.video_id
      AND e.event_type = 'view'
GROUP BY v.category
ORDER BY videos_without_views DESC, v.category"""
ex.q("Categories with dead videos", minutes=5, level="easy", kind="sql",
     prompt="On the made-up product tables: for each `category`, return `videos` (number of videos) and "
            "`videos_without_views` (videos with no view event at all). Most dead videos first, then by category. "
            "Every category must appear, even with 0.",
     hint1="Signal: 'with no view' plus every category kept. Pattern: LEFT JOIN with the filter in ON, then counts "
           "that ignore NULL.",
     hint2="1. videos LEFT JOIN events ON video_id AND event_type = 'view'. 2. GROUP BY category. "
           "3. COUNT(DISTINCT v.video_id) all videos; COUNT(DISTINCT e.video_id) videos that matched. 4. Subtract.",
     solution=q4,
     why="The join creates many rows per watched video, so plain COUNT(*) is useless; COUNT(DISTINCT) brings it back "
         "to videos. COUNT(DISTINCT e.video_id) ignores the NULL from unmatched videos.",
     complexity="O(videos + events).",
     mistakes="Putting `event_type = 'view'` in WHERE (dead videos disappear). COUNT(*) instead of COUNT(DISTINCT).",
     learn=["sql-left-join-nulls"])

q5 = """SELECT COALESCE(u.country, 'unknown') AS country,
       COUNT(*) AS users,
       SUM(CASE WHEN a.user_id IS NOT NULL THEN 1 ELSE 0 END) AS active_users
FROM users u
LEFT JOIN (SELECT DISTINCT user_id FROM events) a ON a.user_id = u.user_id
GROUP BY COALESCE(u.country, 'unknown')
ORDER BY users DESC, country"""
ex.q("Active users by country", minutes=5, level="easy", kind="sql",
     prompt="On the made-up product tables: for each country (show `unknown` for NULL), return `users` (all users) "
            "and `active_users` (users with at least one event). Most users first, then by country.",
     hint1="Signal: a flag per user (active or not) counted per group. Pattern: LEFT JOIN to the distinct active "
           "users, then SUM(CASE WHEN ...).",
     hint2="1. Derived table: SELECT DISTINCT user_id FROM events. 2. users LEFT JOIN it. 3. GROUP BY "
           "COALESCE(country, 'unknown'). 4. COUNT(*) and SUM(CASE WHEN a.user_id IS NOT NULL THEN 1 ELSE 0 END).",
     solution=q5,
     why="Deduplicating events first keeps one row per user, so COUNT(*) still counts users. The CASE turns "
         "'matched or not' into 1 or 0.",
     complexity="O(users + events).",
     mistakes="Joining raw events (each user repeated per event, so `users` is inflated). Grouping by `country` and "
              "showing COALESCE: that works, but group by the same expression you show to avoid surprises.",
     learn=["sql-case-when", "sql-left-join-nulls"])

q6 = """SELECT c.CustomerId, c.FirstName, c.LastName, c.Country
FROM Customer c
WHERE NOT EXISTS (
    SELECT 1
    FROM Invoice i
    JOIN InvoiceLine il ON il.InvoiceId = i.InvoiceId
    JOIN Track t ON t.TrackId = il.TrackId
    JOIN Genre g ON g.GenreId = t.GenreId
    WHERE i.CustomerId = c.CustomerId
      AND g.Name = 'Metal')
ORDER BY c.CustomerId"""
ex.q("Customers who never bought Metal", minutes=8, level="easy", kind="sql",
     prompt="Metal is the third best-selling genre. Which customers have **never** bought a Metal track? Return "
            f"`CustomerId`, `FirstName`, `LastName`, `Country`, by CustomerId. Expected: {nrows(ex, q6)} rows.\n\n"
            "Follow-up to answer out loud: why can `NOT IN` be dangerous here?",
     hint1="Signal: 'never' about related rows several joins away. Pattern: NOT EXISTS with a correlated subquery.",
     hint2="1. Outer: FROM Customer c. 2. Inner: Invoice -> InvoiceLine -> Track -> Genre, WHERE i.CustomerId = "
           "c.CustomerId AND g.Name = 'Metal'. 3. WHERE NOT EXISTS (inner).",
     solution=q6,
     why="NOT EXISTS is true when the inner query finds no row for this customer. Follow-up: `CustomerId NOT IN "
         "(subquery)` returns no rows at all if the subquery yields a NULL, because `x NOT IN (1, NULL)` is unknown. "
         "Here the ids are never NULL, but NOT EXISTS is safe by design.",
     complexity="Hash anti-join: O(Customer + InvoiceLine).",
     mistakes="`WHERE g.Name <> 'Metal'` after a join: that finds customers who bought something that is not Metal, "
              "which is a different (much bigger) set.",
     learn=["sql-subqueries"])

ex.save()
