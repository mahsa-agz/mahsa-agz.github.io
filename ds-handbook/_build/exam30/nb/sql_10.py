import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sql_easy_common import start, nrows

# Day 10 SQL: focus window ranking (ROW_NUMBER, RANK, DENSE_RANK, NTILE, PARTITION BY); review dates.
ex = start(10)

q1 = """WITH genre_units AS (
    SELECT g.Name AS genre, SUM(il.Quantity) AS units
    FROM InvoiceLine il
    JOIN Track t ON t.TrackId = il.TrackId
    JOIN Genre g ON g.GenreId = t.GenreId
    GROUP BY g.Name
)
SELECT genre, units,
       ROW_NUMBER() OVER (ORDER BY units DESC) AS row_num,
       RANK()       OVER (ORDER BY units DESC) AS rnk,
       DENSE_RANK() OVER (ORDER BY units DESC) AS dense_rnk
FROM genre_units
ORDER BY units DESC, genre"""
ex.q("Three ways to rank genres", minutes=5, level="easy", kind="sql",
     prompt="Rank genres by units sold (sum of `InvoiceLine.Quantity`). Return `genre`, `units` and three ranks side "
            "by side: `row_num` (ROW_NUMBER), `rnk` (RANK) and `dense_rnk` (DENSE_RANK). Order by units descending, "
            "then genre.\n\n"
            "Look at the tied rows (for example the two genres with 41 units) and explain the difference out loud.",
     hint1="Signal: 'rank' with ties. Pattern: window ranking functions with OVER (ORDER BY ...).",
     hint2="1. CTE: units per genre. 2. ROW_NUMBER() / RANK() / DENSE_RANK() OVER (ORDER BY units DESC). "
           "3. Final ORDER BY units DESC, genre.",
     solution=q1,
     why="ROW_NUMBER gives unique numbers (ties broken arbitrarily), RANK gives ties the same number and then skips "
         "(1, 2, 2, 4), DENSE_RANK gives ties the same number without gaps (1, 2, 2, 3). Window functions keep every "
         "row, unlike GROUP BY.",
     complexity="Aggregation O(InvoiceLine), then a sort of 24 genre rows.",
     mistakes="Using ROW_NUMBER when the question says 'all items tied for first'. Expecting the window ORDER BY to "
              "sort the output (add a final ORDER BY). Window functions need SQLite 3.25 or later (Colab has it).",
     learn=["sql-window-ranking"])

q2 = """WITH spend AS (
    SELECT c.CustomerId, c.FirstName || ' ' || c.LastName AS customer, c.Country,
           ROUND(SUM(i.Total), 2) AS spend
    FROM Customer c
    JOIN Invoice i ON i.CustomerId = c.CustomerId
    GROUP BY c.CustomerId, customer, c.Country
)
SELECT Country, customer, spend,
       RANK() OVER (PARTITION BY Country ORDER BY spend DESC) AS rank_in_country
FROM spend
WHERE Country IN (SELECT Country FROM Customer GROUP BY Country HAVING COUNT(*) >= 4)
ORDER BY Country, rank_in_country, customer"""
ex.q("Best customers within each country", minutes=6, level="medium", kind="sql",
     prompt="For countries with at least 4 customers, rank customers by total spend **within their country** (1 = "
            "biggest spender, ties share a rank). Return `Country`, `customer` (full name), `spend` (2 decimals) and "
            "`rank_in_country`, ordered by country, rank, name.\n\n"
            f"Expected: {nrows(ex, q2)} rows.\n\n"
            "Follow-up: how would you keep only the top 2 per country?",
     hint1="Signal: 'within each country'. Pattern: RANK() OVER (PARTITION BY country ORDER BY spend DESC).",
     hint2="1. CTE: spend per customer with country. 2. RANK() OVER (PARTITION BY Country ORDER BY spend DESC). "
           "3. Filter countries with a subquery (HAVING COUNT(*) >= 4).",
     solution=q2,
     why="PARTITION BY restarts the ranking for each country, like a GROUP BY that keeps the rows. Follow-up: wrap "
         "this in another CTE and filter `WHERE rank_in_country <= 2`; you cannot filter a window function in the "
         "same SELECT's WHERE, because WHERE runs before windows (that is tomorrow's top-N topic).",
     complexity="O(Invoice) to aggregate, then a sort per partition.",
     mistakes="`WHERE rank_in_country <= 2` in the same query (error). Ranking before aggregating (ranks invoices, not "
              "customers).",
     learn=["sql-window-ranking", "sql-top-n"])

q3 = """WITH video_views AS (
    SELECT v.category, v.video_id, COUNT(e.event_id) AS views
    FROM videos v
    LEFT JOIN events e ON e.video_id = v.video_id AND e.event_type = 'view'
    GROUP BY v.category, v.video_id
)
SELECT category, video_id, views,
       DENSE_RANK() OVER (PARTITION BY category ORDER BY views DESC) AS rank_in_category
FROM video_views
ORDER BY category, rank_in_category, video_id"""
ex.q("Top videos per category", minutes=5, level="easy", kind="sql",
     prompt="On the made-up product tables: rank every video within its `category` by number of views (videos with "
            "no views count 0). Ties share a rank and the next rank has no gap. Return `category`, `video_id`, "
            "`views`, `rank_in_category`, ordered by category, rank, video_id.\n\n"
            f"Expected: {nrows(ex, q3)} rows (every video).",
     hint1="Signal: rank inside groups, ties without gaps. Pattern: DENSE_RANK() OVER (PARTITION BY category ...).",
     hint2="1. CTE: views per video with a LEFT JOIN (views filter in ON). 2. DENSE_RANK() OVER (PARTITION BY "
           "category ORDER BY views DESC).",
     solution=q3,
     why="The LEFT JOIN keeps videos with 0 views so they get a rank too. DENSE_RANK matches 'no gap after ties'.",
     complexity="O(videos + events), then a sort per category.",
     mistakes="Inner join (dead videos lose their rank). RANK instead of DENSE_RANK (gaps).",
     learn=["sql-window-ranking", "sql-left-join-nulls"])

q4 = """WITH spend AS (
    SELECT CustomerId, SUM(Total) AS spend
    FROM Invoice
    GROUP BY CustomerId
),
q AS (
    SELECT CustomerId, spend, NTILE(4) OVER (ORDER BY spend DESC) AS quartile
    FROM spend
)
SELECT quartile,
       COUNT(*) AS customers,
       ROUND(MIN(spend), 2) AS min_spend,
       ROUND(MAX(spend), 2) AS max_spend,
       ROUND(SUM(spend), 2) AS revenue
FROM q
GROUP BY quartile
ORDER BY quartile"""
ex.q("Spend quartiles", minutes=6, level="medium", kind="sql",
     prompt="Split customers into 4 equal-size groups by total spend (quartile 1 = top spenders). For each quartile "
            "return `customers`, `min_spend`, `max_spend` and `revenue` (all 2 decimals).\n\n"
            "Follow-up: 59 customers do not split evenly into 4. Which quartiles get the extra customers?",
     hint1="Signal: 'equal-size buckets by rank'. Pattern: NTILE(4) OVER (ORDER BY spend DESC).",
     hint2="1. CTE spend per customer. 2. CTE with NTILE(4) OVER (ORDER BY spend DESC). 3. GROUP BY quartile with "
           "COUNT, MIN, MAX, SUM.",
     solution=q4,
     why="NTILE deals rows into n buckets in order; when the count does not divide evenly, the first buckets get one "
         "extra row (here 15, 15, 15, 14). Ties can land in different buckets, which matters when many customers "
         "spend the same amount, as here.",
     complexity="O(Invoice) plus a sort of 59 rows.",
     mistakes="Confusing NTILE (equal counts) with value ranges (equal widths). Forgetting DESC, which makes "
              "quartile 1 the lowest spenders.",
     learn=["sql-window-ranking", "sql-median-percentiles"])

q5 = """SELECT DATE(signup_date, '-6 days', 'weekday 1') AS week_start,
       COUNT(*) AS new_users
FROM users
GROUP BY week_start
ORDER BY week_start"""
ex.q("Signups per week", minutes=4, level="easy", kind="sql", review=True,
     prompt="On the made-up `users` table: count new users per signup week, where a week starts on **Monday**. "
            "Return `week_start` (the Monday, `YYYY-MM-DD`) and `new_users`, in time order.\n\n"
            "Example: 2024-03-04 is a Monday, so a signup on Wednesday 2024-03-06 belongs to week_start 2024-03-04.",
     hint1="Signal: 'per week'. Pattern: truncate a date to the start of its week, then GROUP BY.",
     hint2="1. SQLite: DATE(d, '-6 days', 'weekday 1') = the Monday on or before d ('weekday 1' moves forward to the "
           "next Monday, so go back 6 days first). 2. GROUP BY week_start.",
     solution=q5,
     why="Truncating to the week start gives one label per week. PostgreSQL: `DATE_TRUNC('week', signup_date)` "
         "(weeks start on Monday there). `strftime('%W')` gives a week number, but labels like `10` are harder to "
         "read and break across years.",
     complexity="One scan of users.",
     mistakes="`DATE(d, 'weekday 1')` alone gives the NEXT Monday for any non-Monday. Week numbers without the year.",
     learn=["sql-dates"])

ex.save()
