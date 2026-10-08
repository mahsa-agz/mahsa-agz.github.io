import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sql_easy_common import start, nrows

# Day 5 SQL: focus CASE WHEN (buckets, conditional aggregation, custom sort); review aggregation, left-join-nulls.
ex = start(5)

q1 = """SELECT CASE
         WHEN Milliseconds < 3 * 60000 THEN 'short'
         WHEN Milliseconds < 6 * 60000 THEN 'medium'
         ELSE 'long'
       END AS length_bucket,
       COUNT(*) AS tracks
FROM Track
WHERE MediaTypeId <> 3
GROUP BY length_bucket
ORDER BY CASE length_bucket WHEN 'short' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END"""
ex.q("Short, medium, long", minutes=5, level="easy", kind="sql",
     prompt="Put every audio track (`MediaTypeId <> 3`) in a length bucket: `short` (under 3 minutes), `medium` "
            "(3 minutes up to but not including 6) and `long` (6 minutes or more). Return `length_bucket` and "
            "`tracks`, in the order short, medium, long (not alphabetical).\n\n"
            "Example: a track of exactly 3:00 is `medium`.",
     hint1="Signal: turn a number into labels, then count per label. Pattern: CASE WHEN in SELECT and GROUP BY, "
           "plus a CASE in ORDER BY for a custom order.",
     hint2="1. CASE WHEN ms < 180000 THEN 'short' WHEN ms < 360000 THEN 'medium' ELSE 'long' END. 2. GROUP BY that "
           "expression (or its alias). 3. ORDER BY CASE label WHEN 'short' THEN 1 ... END.",
     solution=q1,
     why="CASE checks the branches top to bottom and stops at the first true one, so the second branch does not need "
         "`>= 180000`. A second CASE maps labels to sort keys.",
     complexity="One scan of Track and three groups.",
     mistakes="Overlapping or gapped boundaries (`<= 3` and `>= 3`). Sorting by the label alphabetically (long, medium, "
              "short). Grouping by an alias works in SQLite, MySQL and PostgreSQL but not in SQL Server: repeat the "
              "expression there.",
     learn=["sql-case-when"])

q2 = """SELECT u.platform,
       SUM(CASE WHEN e.event_type = 'view'  THEN 1 ELSE 0 END) AS views,
       SUM(CASE WHEN e.event_type = 'like'  THEN 1 ELSE 0 END) AS likes,
       SUM(CASE WHEN e.event_type = 'share' THEN 1 ELSE 0 END) AS shares,
       ROUND(1.0 * SUM(CASE WHEN e.event_type = 'like' THEN 1 ELSE 0 END)
             / SUM(CASE WHEN e.event_type = 'view' THEN 1 ELSE 0 END), 3) AS likes_per_view
FROM events e
JOIN users u ON u.user_id = e.user_id
GROUP BY u.platform
ORDER BY likes_per_view DESC"""
ex.q("Engagement by platform, one row each", minutes=6, level="easy", kind="sql",
     prompt="Product wants one row per `platform` with the counts side by side: `views`, `likes`, `shares` and "
            "`likes_per_view` (likes divided by views, 3 decimals). Highest likes_per_view first.\n\n"
            "Shape only (made-up numbers): `ios | 40 | 12 | 5 | 0.3`.",
     hint1="Signal: several counts of different event types as columns of one row. Pattern: conditional aggregation, "
           "SUM(CASE WHEN ... THEN 1 ELSE 0 END).",
     hint2="1. events JOIN users for the platform. 2. GROUP BY platform. 3. One SUM(CASE ...) per event type. "
           "4. Ratio: 1.0 * likes / views, rounded.",
     solution=q2,
     why="Conditional aggregation computes many filtered counts in one pass, instead of one query (or one join) per "
         "event type. Multiplying by 1.0 avoids integer division.",
     complexity="One pass over events joined to users.",
     mistakes="Integer division (likes / views gives 0). `COUNT(CASE WHEN ... THEN 1 ELSE 0 END)` counts every row, "
              "because 0 is not NULL; use SUM, or COUNT with no ELSE. PostgreSQL also has "
              "`COUNT(*) FILTER (WHERE event_type = 'like')`.",
     learn=["sql-case-when", "sql-ratios"])

q3 = """SELECT CASE
         WHEN c.Country IN ('USA', 'Canada') THEN 'North America'
         WHEN c.Country IN ('Brazil', 'Argentina', 'Chile') THEN 'South America'
         WHEN c.Country IN ('India', 'Australia') THEN 'Asia Pacific'
         ELSE 'Europe'
       END AS region,
       COUNT(DISTINCT c.CustomerId) AS customers,
       ROUND(SUM(i.Total), 2) AS revenue
FROM Customer c
JOIN Invoice i ON i.CustomerId = c.CustomerId
GROUP BY region
ORDER BY revenue DESC"""
ex.q("Revenue by region", minutes=5, level="easy", kind="sql",
     prompt="Chinook has no region column. Map customer countries to regions: USA and Canada -> `North America`; "
            "Brazil, Argentina, Chile -> `South America`; India, Australia -> `Asia Pacific`; every other country -> "
            "`Europe` (true for this data). Return `region`, `customers` and `revenue` (sum of invoice totals, "
            "2 decimals), highest revenue first.",
     hint1="Signal: a mapping that is not in any table. Pattern: CASE WHEN with IN lists, then GROUP BY the label.",
     hint2="1. Customer JOIN Invoice. 2. CASE WHEN Country IN (...) THEN ... ELSE 'Europe' END AS region. "
           "3. GROUP BY region. 4. COUNT(DISTINCT CustomerId) because the join repeats each customer per invoice.",
     solution=q3,
     why="The join has one row per invoice, so COUNT(*) would count invoices; COUNT(DISTINCT) counts customers. In a "
         "real job you would put the mapping in a small lookup table and join it, so it is reusable and testable.",
     complexity="O(Customer + Invoice).",
     mistakes="A catch-all ELSE hides new countries: check with a query that lists countries in the ELSE branch. "
              "COUNT(*) for customers after the join.",
     learn=["sql-case-when", "sql-joins"])

q4 = """SELECT City, Country, COUNT(*) AS customers
FROM Customer
GROUP BY City, Country
HAVING COUNT(*) >= 2
ORDER BY customers DESC, City"""
ex.q("Cities with several customers", minutes=3, level="easy", kind="sql", review=True,
     prompt="Which cities have at least 2 customers? Return `City`, `Country` and `customers`, most customers first, "
            "then by city.\n\n"
            f"Expected: {nrows(ex, q4)} rows.",
     hint1="Signal: condition on a group count. Pattern: GROUP BY with HAVING.",
     hint2="1. GROUP BY City, Country (two cities in different countries can share a name). "
           "2. HAVING COUNT(*) >= 2. 3. ORDER BY customers DESC, City.",
     solution=q4,
     why="HAVING filters groups after counting. Grouping by City and Country together is the safe key.",
     complexity="One scan of Customer.",
     mistakes="Using WHERE for the count. Grouping by City alone (a Paris in Texas would merge with Paris in France).",
     learn=["sql-aggregation"])

q5 = """SELECT u.user_id, u.signup_date, u.platform
FROM users u
LEFT JOIN events e ON e.user_id = u.user_id
WHERE e.event_id IS NULL
ORDER BY u.user_id"""
ex.q("Signed up, never active", minutes=3, level="easy", kind="sql", review=True,
     prompt="Find users in the made-up `users` table who have **no event at all**. Return `user_id`, `signup_date` "
            "and `platform`.\n\n"
            f"Expected: {nrows(ex, q5)} rows.",
     hint1="Signal: 'no matching rows'. Pattern: anti-join (LEFT JOIN ... WHERE right key IS NULL) or NOT EXISTS.",
     hint2="1. users LEFT JOIN events ON user_id. 2. WHERE e.event_id IS NULL.",
     solution=q5,
     why="Unmatched users get NULLs in all event columns. `NOT EXISTS (SELECT 1 FROM events e WHERE e.user_id = "
         "u.user_id)` is equivalent and often clearer.",
     complexity="O(users + events).",
     mistakes="`WHERE user_id NOT IN (SELECT user_id FROM events)` returns nothing if the subquery ever contains a "
              "NULL. Prefer NOT EXISTS or the LEFT JOIN form.",
     learn=["sql-left-join-nulls"],
     source=("LeetCode 183 Customers Who Never Order (same idea)", "https://leetcode.com/problems/customers-who-never-order/"))

ex.save()
