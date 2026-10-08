import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sql_easy_common import start, nrows

# Day 1 SQL: focus basics (SELECT, WHERE, ORDER BY, LIMIT, DISTINCT, LIKE, IN, IS NULL, COALESCE). No review yet.
ex = start(1)

q1 = """SELECT Name,
       ROUND(Milliseconds / 60000.0, 1) AS minutes
FROM Track
WHERE Milliseconds > 10 * 60 * 1000
  AND MediaTypeId <> 3
ORDER BY Milliseconds DESC
LIMIT 5"""
ex.q("The longest songs", minutes=4, level="easy", kind="sql",
     prompt="The music team wants the five longest **audio** tracks that run more than 10 minutes. "
            "Video tracks have `MediaTypeId = 3`; leave them out.\n\n"
            "Return `Name` and `minutes` (the length in minutes, one decimal), longest first.\n\n"
            "Example of the shape: a 12-minute track gives `minutes = 12.0`.",
     hint1="Signal: filter rows, sort, keep the first few. Pattern: plain SELECT with WHERE, ORDER BY and LIMIT.",
     hint2="1. FROM Track. 2. WHERE length over 600000 ms and MediaTypeId <> 3. 3. Compute minutes as "
           "`Milliseconds / 60000.0` (note the .0). 4. ORDER BY Milliseconds DESC, LIMIT 5.",
     solution=q1,
     why="WHERE runs before SELECT and ORDER BY, so we filter on the raw column. Sorting by the raw Milliseconds "
         "avoids ties created by rounding. Dividing by 60000.0 forces decimal division.",
     complexity="One scan of Track (3,503 rows) plus a sort of the matching rows.",
     mistakes="`Milliseconds / 60000` is integer division in SQLite and PostgreSQL (12.9 becomes 12). "
              "Forgetting to exclude videos. Using `TOP 5` (SQL Server) instead of `LIMIT 5`.",
     learn=["sql-basics", "sql-query-order"])

q2 = """SELECT DISTINCT Country
FROM Customer
ORDER BY Country"""
ex.q("Where do our customers live?", minutes=3, level="easy", kind="sql",
     prompt="List every country that has at least one customer, each country once, in alphabetical order. "
            "Return one column, `Country`.\n\n"
            f"Expected: {nrows(ex, q2)} rows, starting with Argentina.",
     hint1="Signal: 'each once'. Pattern: SELECT DISTINCT.",
     hint2="1. SELECT DISTINCT Country FROM Customer. 2. ORDER BY Country.",
     solution=q2,
     why="DISTINCT removes duplicate rows of the selected columns. It is applied after SELECT, so it works on "
         "Country only. `GROUP BY Country` gives the same result and is the usual choice when you also need counts.",
     complexity="One scan plus a sort or hash on 59 rows.",
     mistakes="`SELECT DISTINCT Country, City` is distinct on the pair, not on Country. Forgetting ORDER BY: SQL "
              "has no guaranteed row order without it.",
     learn=["sql-basics"])

q3 = """SELECT FirstName, LastName, Country, Email
FROM Customer
WHERE Country IN ('USA', 'Canada')
  AND (Email LIKE '%@gmail.com' OR Email LIKE '%@yahoo.com')
ORDER BY Country, LastName"""
ex.q("North American webmail users", minutes=5, level="easy", kind="sql",
     prompt="Find customers in the USA or Canada whose email address is a Gmail or Yahoo address "
            "(it ends with `@gmail.com` or `@yahoo.com`).\n\n"
            "Return `FirstName`, `LastName`, `Country`, `Email`, sorted by country, then last name.\n\n"
            f"Expected: {nrows(ex, q3)} rows. A customer in France with a Gmail address must NOT appear.",
     hint1="Signal: a list of allowed values plus a text pattern. Pattern: IN and LIKE, with brackets around the OR.",
     hint2="1. `Country IN ('USA', 'Canada')`. 2. `Email LIKE '%@gmail.com' OR Email LIKE '%@yahoo.com'` inside "
           "brackets. 3. Join the two with AND. 4. ORDER BY Country, LastName.",
     solution=q3,
     why="AND binds tighter than OR. Without the brackets the condition becomes `(country AND gmail) OR yahoo`, "
         "which lets Yahoo users from any country through. `%` matches any run of characters.",
     complexity="One scan of Customer.",
     mistakes="Missing brackets around the OR. `LIKE '%gmail%'` would also match `gmail.com.br`. In PostgreSQL LIKE "
              "is case sensitive (use ILIKE for case-insensitive); in SQLite LIKE ignores case for ASCII letters.",
     learn=["sql-basics", "cheat-sql"])

q4 = """SELECT event_id, user_id, video_id, watch_sec
FROM events
WHERE event_type = 'view'
  AND watch_sec < 5
ORDER BY watch_sec, event_id"""
ex.q("Quick skips", minutes=4, level="easy", kind="sql",
     prompt="Product question on the made-up `events` table. A *quick skip* is a `view` event watched for less than "
            "5 seconds. List all quick skips with `event_id`, `user_id`, `video_id`, `watch_sec`, shortest first "
            "(ties by event_id).\n\n"
            f"Expected: {nrows(ex, q4)} rows.",
     hint1="Signal: keep only some event rows. Pattern: WHERE with two conditions.",
     hint2="1. FROM events. 2. WHERE event_type = 'view' AND watch_sec < 5. 3. ORDER BY watch_sec, event_id.",
     solution=q4,
     why="Only views have a watch time. Filtering on event_type makes the intent clear even though `watch_sec < 5` "
         "is already false for the NULL rows (a comparison with NULL is never true).",
     complexity="One scan of events.",
     mistakes="Writing `watch_sec <= 5` (the definition says less than 5). Expecting `watch_sec < 5` to return the "
              "like/share rows whose watch_sec is NULL: it does not, NULL compared to anything is unknown.",
     learn=["sql-basics"])

q5 = """SELECT user_id, COALESCE(country, 'unknown') AS country, platform
FROM users
WHERE country <> 'US' OR country IS NULL
ORDER BY user_id"""
ex.q("Everyone outside the US", minutes=5, level="easy", kind="sql",
     prompt="Marketing will send a campaign to every user who is **not known to be** in the US. Users with an "
            "unknown country (NULL) must be included.\n\n"
            "Return `user_id`, `country` (show `unknown` instead of NULL) and `platform`, by user_id.\n\n"
            f"Expected: {nrows(ex, q5)} rows, including users 7 and 16 whose country is NULL.",
     hint1="Signal: 'not equal' on a column that has NULLs. Pattern: three-valued logic, IS NULL and COALESCE.",
     hint2="1. `country <> 'US'` alone drops NULL rows, because NULL <> 'US' is unknown. 2. Add "
           "`OR country IS NULL`. 3. In SELECT, `COALESCE(country, 'unknown')` replaces NULL for display.",
     solution=q5,
     why="SQL has three truth values. WHERE keeps only rows where the condition is TRUE, so a NULL country fails "
         "both `= 'US'` and `<> 'US'`. COALESCE returns its first non-NULL argument.",
     complexity="One scan of users.",
     mistakes="`country != 'US'` alone (loses users 7 and 16). Writing `country = NULL` (always unknown, use IS NULL). "
              "Putting COALESCE in WHERE as well is fine but slower on big tables because an index on country "
              "cannot be used.",
     learn=["sql-basics", "sql-left-join-nulls"])

ex.save()
