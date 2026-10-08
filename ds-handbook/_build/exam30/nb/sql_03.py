import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sql_easy_common import start, nrows

# Day 3 SQL: focus joins (INNER JOIN over 2 to 4 tables, join keys, row multiplication); review aggregation.
ex = start(3)

q1 = """SELECT al.Title AS album, t.Name AS track
FROM Artist ar
JOIN Album al ON al.ArtistId = ar.ArtistId
JOIN Track t  ON t.AlbumId  = al.AlbumId
WHERE ar.Name = 'Queen'
ORDER BY al.Title, t.TrackId"""
ex.q("Every Queen track", minutes=4, level="easy", kind="sql",
     prompt="List every track by the artist named `Queen`. Return `album` (album title) and `track` (track name), "
            "ordered by album title and then by `TrackId` (the order on the album).\n\n"
            "The chain is Artist -> Album -> Track.\n\n"
            f"Expected: {nrows(ex, q1)} rows.",
     hint1="Signal: the filter is in one table (Artist) and the output in others (Album, Track). Pattern: a chain of "
           "INNER JOINs on the key columns.",
     hint2="1. FROM Artist ar. 2. JOIN Album al ON al.ArtistId = ar.ArtistId. 3. JOIN Track t ON t.AlbumId = "
           "al.AlbumId. 4. WHERE ar.Name = 'Queen'. 5. ORDER BY al.Title, t.TrackId.",
     solution=q1,
     why="Each JOIN adds the matching rows of the next table along a foreign key. Table aliases keep the query short "
         "and remove ambiguity: both Album and Track have columns named like `Title`/`Name`.",
     complexity="With indexes on the keys this is a few lookups; without them each join is a hash join, "
                "O(rows of both tables).",
     mistakes="Joining on the wrong key (for example `t.AlbumId = ar.ArtistId`), which silently returns nonsense. "
              "Selecting `Name` without an alias prefix when two tables have that column.",
     learn=["sql-joins"])

q2 = """SELECT g.Name AS genre,
       ROUND(SUM(il.UnitPrice * il.Quantity), 2) AS revenue,
       SUM(il.Quantity) AS units
FROM InvoiceLine il
JOIN Track t ON t.TrackId = il.TrackId
JOIN Genre g ON g.GenreId = t.GenreId
GROUP BY g.Name
ORDER BY revenue DESC
LIMIT 5"""
ex.q("Which genres make money?", minutes=5, level="easy", kind="sql",
     prompt="Return the five genres with the highest sales revenue: `genre`, `revenue` (sum of "
            "`UnitPrice * Quantity` from `InvoiceLine`, 2 decimals) and `units` (tracks sold). Highest revenue first.\n\n"
            "Tip: revenue is in InvoiceLine, the genre is two joins away.",
     hint1="Signal: the measure is in one table and the label two tables away. Pattern: join first, then GROUP BY.",
     hint2="1. FROM InvoiceLine il. 2. JOIN Track t ON t.TrackId = il.TrackId. 3. JOIN Genre g ON g.GenreId = "
           "t.GenreId. 4. GROUP BY g.Name with SUM(il.UnitPrice * il.Quantity). 5. ORDER BY revenue DESC LIMIT 5.",
     solution=q2,
     why="Start from the table whose grain matches the measure (one row per sold line), then join the labels. "
         "Every InvoiceLine has exactly one Track and one Genre, so the join does not duplicate revenue.",
     complexity="O(InvoiceLine + Track + Genre) with hash joins.",
     mistakes="Using `Track.UnitPrice` instead of the price actually paid (`InvoiceLine.UnitPrice`). Joining "
              "Invoice too and summing `Invoice.Total`, which counts each invoice once per line (fan-out).",
     learn=["sql-joins", "sql-aggregation"])

q3 = """SELECT e.FirstName || ' ' || e.LastName AS rep,
       COUNT(*) AS customers
FROM Customer c
JOIN Employee e ON e.EmployeeId = c.SupportRepId
GROUP BY e.EmployeeId, rep
ORDER BY customers DESC"""
ex.q("Support rep workload", minutes=4, level="easy", kind="sql",
     prompt="Each customer has a support rep (`Customer.SupportRepId` points to `Employee.EmployeeId`). Return `rep` "
            "(first and last name in one string, like `Jane Peacock`) and `customers` (how many customers they "
            "support), most customers first.\n\n"
            f"Expected: {nrows(ex, q3)} rows.",
     hint1="Signal: two tables linked by an id with a different name. Pattern: INNER JOIN on SupportRepId = "
           "EmployeeId, then GROUP BY.",
     hint2="1. FROM Customer c JOIN Employee e ON e.EmployeeId = c.SupportRepId. 2. Build the name with `||`. "
           "3. GROUP BY e.EmployeeId (and the name). 4. COUNT(*).",
     solution=q3,
     why="The join key names do not have to match; the meaning does. Grouping by the id as well as the name keeps two "
         "employees with the same name apart.",
     complexity="O(Customer + Employee).",
     mistakes="Joining `c.CustomerId = e.EmployeeId` because both are 'ids'. String concatenation is `||` in SQLite "
              "and PostgreSQL, `CONCAT()` in MySQL. Only employees with customers appear: an INNER JOIN drops the "
              "others (tomorrow's topic).",
     learn=["sql-joins"])

q4 = """SELECT v.category,
       COUNT(*) AS views,
       ROUND(SUM(e.watch_sec) / 60.0, 1) AS watch_minutes,
       ROUND(AVG(e.watch_sec), 1) AS avg_watch_sec
FROM events e
JOIN videos v ON v.video_id = e.video_id
WHERE e.event_type = 'view'
GROUP BY v.category
ORDER BY watch_minutes DESC"""
ex.q("Watch time by category", minutes=5, level="easy", kind="sql",
     prompt="On the made-up product tables: for each video `category`, return `views` (number of view events), "
            "`watch_minutes` (total watch time in minutes, 1 decimal) and `avg_watch_sec` (average seconds per view, "
            "1 decimal). Most watch time first.",
     hint1="Signal: the event is in `events`, the label in `videos`. Pattern: INNER JOIN on video_id, then GROUP BY.",
     hint2="1. FROM events e JOIN videos v ON v.video_id = e.video_id. 2. WHERE e.event_type = 'view'. "
           "3. GROUP BY v.category. 4. COUNT(*), SUM(e.watch_sec) / 60.0, AVG(e.watch_sec).",
     solution=q4,
     why="One event row joins to exactly one video, so counts stay correct. Categories with no views simply do not "
         "appear in an inner join.",
     complexity="O(events + videos).",
     mistakes="Grouping by `e.video_id` instead of the category. Forgetting the view filter, which counts likes as "
              "views (their watch_sec is NULL, so SUM is fine but COUNT(*) is not).",
     learn=["sql-joins"])

q5 = """SELECT platform,
       COUNT(*)                  AS users,
       COUNT(country)            AS known_country,
       COUNT(*) - COUNT(country) AS unknown_country
FROM users
GROUP BY platform
ORDER BY users DESC"""
ex.q("Users per platform", minutes=3, level="easy", kind="sql", review=True,
     prompt="For each `platform` in the made-up `users` table, return `users`, `known_country` (users with a "
            "country) and `unknown_country` (users whose country is NULL). Most users first.",
     hint1="Signal: count rows and count non-NULL values in the same group. Pattern: COUNT(*) vs COUNT(col).",
     hint2="1. GROUP BY platform. 2. COUNT(*) for all users. 3. COUNT(country) skips NULLs. 4. Subtract for unknown.",
     solution=q5,
     why="COUNT(col) ignores NULLs, so the difference with COUNT(*) is the number of NULLs. "
         "`SUM(CASE WHEN country IS NULL THEN 1 ELSE 0 END)` is the explicit alternative.",
     complexity="One scan of users.",
     mistakes="`COUNT(country = NULL)` or `WHERE country = NULL`: comparisons with NULL are never true.",
     learn=["sql-aggregation"])

ex.save()
