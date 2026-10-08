import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
from sql_mid_data import build_setup

ex = Exam(11, "sql")
build_setup(ex, "chinook", "app", "movielens")

# ---------------------------------------------------------------- Q1 top-n per group with ties (Chinook)
ex.q("Best artists inside the biggest genres", minutes=6, kind="sql",
     prompt="""The music store wants a slide: for each of its **4 genres with the most revenue**, the **3 artists**
with the most revenue in that genre. Revenue of an invoice line is `UnitPrice * Quantity`.

If two artists tie for third place, show both (a slide that hides one of two equal artists is wrong).

Return `genre`, `artist`, `revenue` (rounded to 2 decimals), `rnk`, ordered by genre, rank, artist.
Example of the shape: `Rock | U2 | 90.09 | 1`.

Follow-up to answer out loud: what changes if the business says "exactly 3 rows per genre, break ties by artist
name"?""",
     hint1="Signal: \"top K inside each group\". Pattern: rank inside a window `PARTITION BY genre ORDER BY revenue DESC`, "
           "then filter rank <= 3 in an outer query. Ties kept means RANK (or DENSE_RANK), not ROW_NUMBER.",
     hint2="1. CTE 1: genre revenue, keep the top 4 with ORDER BY ... LIMIT 4.\n"
           "2. CTE 2: revenue per (genre, artist) for those genres: InvoiceLine, Track, Genre, Album, Artist.\n"
           "3. CTE 3: `RANK() OVER (PARTITION BY genre ORDER BY revenue DESC)`.\n"
           "4. Outer query: `WHERE rnk <= 3`. You cannot filter a window function in WHERE of the same SELECT.",
     solution="""WITH genre_rev AS (
    SELECT g.Name AS genre, SUM(il.UnitPrice * il.Quantity) AS rev
    FROM InvoiceLine il
    JOIN Track t ON t.TrackId = il.TrackId
    JOIN Genre g ON g.GenreId = t.GenreId
    GROUP BY g.Name
    ORDER BY rev DESC
    LIMIT 4
), artist_rev AS (
    SELECT g.Name AS genre, ar.Name AS artist, ROUND(SUM(il.UnitPrice * il.Quantity), 2) AS revenue
    FROM InvoiceLine il
    JOIN Track t   ON t.TrackId = il.TrackId
    JOIN Genre g   ON g.GenreId = t.GenreId
    JOIN Album al  ON al.AlbumId = t.AlbumId
    JOIN Artist ar ON ar.ArtistId = al.ArtistId
    WHERE g.Name IN (SELECT genre FROM genre_rev)
    GROUP BY g.Name, ar.Name
), ranked AS (
    SELECT genre, artist, revenue,
           RANK() OVER (PARTITION BY genre ORDER BY revenue DESC) AS rnk
    FROM artist_rev
)
SELECT genre, artist, revenue, rnk
FROM ranked
WHERE rnk <= 3
ORDER BY genre, rnk, artist""",
     why="The window ranks artists separately inside each genre. RANK gives tied artists the same number, so "
         "Faith No More and Green Day both get 2 in Alternative & Punk, and two Metal artists share rank 3, which "
         "is why Metal has 4 rows. With RANK the next rank after a tie is skipped (1, 2, 2, 4); DENSE_RANK would "
         "not skip (1, 2, 2, 3) and could return even more rows. For \"exactly 3 rows\" use "
         "`ROW_NUMBER() OVER (PARTITION BY genre ORDER BY revenue DESC, artist)`: the extra sort key makes the "
         "result deterministic.",
     complexity="One pass over InvoiceLine for the joins and group by, then a sort per genre for the window.",
     mistakes="Filtering `WHERE RANK() OVER (...) <= 3` (not allowed: windows are computed after WHERE). "
              "Using ROW_NUMBER without a tie breaker, so the result changes between runs. Ranking over the whole "
              "table and forgetting PARTITION BY. Grouping by artist only, which merges an artist across genres.",
     learn=["sql-top-n", "sql-window-ranking", "sql-cte"])

# ---------------------------------------------------------------- Q2 Nth highest with NULL (Chinook)
ex.q("Runner-up customer in every country", minutes=6, kind="sql",
     prompt="""For **every** country in `Customer`, find the customer with the **second highest total spend**
(sum of their invoice totals). Return `country`, `second_customer`, `second_spend` (2 decimals).

Rules:
- A country with only one customer must still appear, with NULL in the other two columns.
- "Second highest" means the second highest **distinct** amount. If three customers spent 40, 40 and 37, the
  runner-up is the one with 37. If several customers share the second amount, show all of them.

Example: in a country with spends 43.62, 43.62, 43.62 (all equal) there is no second amount, so you return NULL.

This is the per-group version of the classic "second highest salary" question.""",
     source=("LeetCode 176 (Second Highest Salary), same idea", "https://leetcode.com/problems/second-highest-salary/"),
     hint1="Signal: \"Nth highest, and show NULL when it does not exist\". Pattern: DENSE_RANK per country "
           "(distinct amounts) plus a LEFT JOIN from the full list of countries.",
     hint2="1. CTE: spend per customer (Customer join Invoice, group by customer).\n"
           "2. CTE: `DENSE_RANK() OVER (PARTITION BY country ORDER BY spend DESC) AS dr`.\n"
           "3. Start from `SELECT DISTINCT Country FROM Customer` and LEFT JOIN the ranked rows "
           "`ON country matches AND dr = 2`. Put `dr = 2` in the ON clause, not in WHERE.",
     solution="""WITH spend AS (
    SELECT c.Country AS country, c.FirstName || ' ' || c.LastName AS customer, SUM(i.Total) AS spend
    FROM Customer c
    JOIN Invoice i ON i.CustomerId = c.CustomerId
    GROUP BY c.CustomerId, c.Country, c.FirstName, c.LastName
), ranked AS (
    SELECT country, customer, spend,
           DENSE_RANK() OVER (PARTITION BY country ORDER BY spend DESC) AS dr
    FROM spend
)
SELECT c.country, r.customer AS second_customer, ROUND(r.spend, 2) AS second_spend
FROM (SELECT DISTINCT Country AS country FROM Customer) AS c
LEFT JOIN ranked AS r
       ON r.country = c.country AND r.dr = 2
ORDER BY c.country""",
     why="DENSE_RANK numbers distinct amounts 1, 2, 3 without gaps, so `dr = 2` is exactly \"the second distinct "
         "amount\" and returns every customer who has it (Brazil shows 4 tied customers). Countries with one "
         "customer, or where everybody spent the same (the United Kingdom has 3 customers with equal spend), have "
         "no `dr = 2` row, and the LEFT JOIN keeps them with NULL. With RANK, ties at the top would push the "
         "next amount to rank 3 and you would wrongly get NULL; with ROW_NUMBER you would return a tied first-place "
         "customer as \"second\".",
     complexity="Group by over invoices, one sorted window per country.",
     mistakes="Writing `WHERE r.dr = 2` after the LEFT JOIN: it removes the NULL rows and turns the LEFT JOIN into "
              "an inner join. Using `LIMIT 1 OFFSET 1`, which only works for one group and ignores ties. "
              "Using `Invoice.BillingCountry` instead of the customer's country (they can differ in real data).",
     learn=["sql-top-n", "sql-left-join-nulls", "sql-window-ranking"])

# ---------------------------------------------------------------- Q3 top-2 per group, deterministic (app tables)
ex.q("Top spenders per country in March", minutes=5, kind="sql",
     prompt="""Using the made-up shopping app: for each `country`, return the **2 users** with the highest
**completed** purchase amount in **March 2024** (`purchases.status = 'completed'`, refunds do not count).
Exactly 2 rows per country: if two users have the same spend, the one whose first March order came earlier wins.

Return `country`, `rn` (1 or 2), `user_id`, `spend` (2 decimals), ordered by country and rn.

Follow-ups: (a) Why is the date filter written as `order_time >= '2024-03-01' AND order_time < '2024-04-01'`
and not `BETWEEN '2024-03-01' AND '2024-03-31'`? (b) What would you change for "top 2 per country per week"?""",
     hint1="Signal: \"top 2 per country, exactly 2 rows\". Pattern: ROW_NUMBER over a partition with an explicit "
           "tie breaker, then filter rn <= 2.",
     hint2="1. CTE: join purchases to app_users, filter completed and March, group by country and user: "
           "`SUM(amount)` and `MIN(order_time)`.\n"
           "2. `ROW_NUMBER() OVER (PARTITION BY country ORDER BY spend DESC, first_order)`.\n"
           "3. Keep rn <= 2.",
     solution="""WITH march AS (
    SELECT u.country, p.user_id, SUM(p.amount) AS spend, MIN(p.order_time) AS first_order
    FROM purchases p
    JOIN app_users u ON u.user_id = p.user_id
    WHERE p.status = 'completed'
      AND p.order_time >= '2024-03-01' AND p.order_time < '2024-04-01'
    GROUP BY u.country, p.user_id
), ranked AS (
    SELECT country, user_id, ROUND(spend, 2) AS spend,
           ROW_NUMBER() OVER (PARTITION BY country ORDER BY spend DESC, first_order) AS rn
    FROM march
)
SELECT country, rn, user_id, spend
FROM ranked
WHERE rn <= 2
ORDER BY country, rn""",
     why="ROW_NUMBER always gives 1, 2, 3 with no ties, so each country returns exactly 2 rows; the second sort key "
         "(first order time) decides ties in a way the business can explain. (a) `order_time` has a time part: "
         "`BETWEEN '2024-03-01' AND '2024-03-31'` compares text and drops every order on March 31 after 00:00:00. "
         "A half-open range `>= start AND < next start` is always correct, also in PostgreSQL with timestamps. "
         "(b) Add the week to the GROUP BY and to the PARTITION BY: `PARTITION BY country, week`.",
     complexity="Filter and group by on purchases, then one window sort per country.",
     mistakes="Ranking before filtering March (ranks lifetime spend). Forgetting the status filter. "
              "Partitioning by user instead of country. Using RANK when the spec says exactly 2 rows.",
     learn=["sql-top-n", "sql-dates"])

# ---------------------------------------------------------------- Q4 top-n with a minimum sample size (MovieLens)
ex.q("Best movies of each decade, fairly", minutes=7, kind="sql",
     prompt="""MovieLens (real ratings). The year of a movie is in its title, e.g. `Toy Story (1995)`.
For each **decade from 1970 on**, return the **3 movies with the highest average rating**, counting only movies with
**at least 50 ratings** (otherwise a movie rated once with 5 stars wins). Ties on the average: more ratings first.

Return `decade` (1970, 1980, ...), `rn`, `title`, `avg_rating` (2 decimals), `n_ratings`.

Hints on the data: a few titles have no year or trailing spaces; skip titles that do not end with `(YYYY)` after
trimming. In SQLite, `substr(s, -5, 4)` takes 4 characters starting 5 from the end.

Follow-up: the product manager does not like a hard cutoff of 50. What would you propose instead?""",
     hint1="Signal: \"top 3 per decade\" plus \"only if enough data\". Pattern: aggregate per movie with HAVING "
           "(minimum count), then ROW_NUMBER per decade.",
     hint2="1. CTE per movie: decade = `CAST(substr(trim(title), -5, 4) AS INTEGER) / 10 * 10`, COUNT(*), AVG(rating); "
           "WHERE trimmed title LIKE '%(____)'; HAVING COUNT(*) >= 50.\n"
           "2. `ROW_NUMBER() OVER (PARTITION BY decade ORDER BY avg_rating DESC, n_ratings DESC)`.\n"
           "3. Keep rn <= 3 and decade >= 1970.",
     solution="""WITH movie_stats AS (
    SELECT m.movie_id, m.title,
           CAST(substr(trim(m.title), -5, 4) AS INTEGER) / 10 * 10 AS decade,
           COUNT(*) AS n_ratings,
           AVG(r.rating) AS avg_rating
    FROM ml_movies m
    JOIN ml_ratings r ON r.movie_id = m.movie_id
    WHERE trim(m.title) LIKE '%(____)'
    GROUP BY m.movie_id, m.title
    HAVING COUNT(*) >= 50
), ranked AS (
    SELECT decade, title, n_ratings, ROUND(avg_rating, 2) AS avg_rating,
           ROW_NUMBER() OVER (PARTITION BY decade ORDER BY avg_rating DESC, n_ratings DESC) AS rn
    FROM movie_stats
)
SELECT decade, rn, title, avg_rating, n_ratings
FROM ranked
WHERE rn <= 3 AND decade >= 1970
ORDER BY decade, rn""",
     why="HAVING filters groups after aggregation, so the minimum count is applied per movie before ranking. "
         "Integer division `year / 10 * 10` turns 1994 into 1990. The result is sensible: The Godfather leads the "
         "1970s and The Shawshank Redemption the 1990s. Follow-up: a hard cutoff throws away information. A "
         "Bayesian (shrunk) average, `(n * avg + m * global_avg) / (n + m)` with m around 30 to 50, pulls movies "
         "with few ratings toward the global mean, so they can rank but need more evidence to reach the top. "
         "Dialects: PostgreSQL has `substring(title from '\\((\\d{4})\\)\\s*$')` for a regex extract, and integer "
         "division also truncates there.",
     complexity="One group by over 100k ratings, then a small sort per decade.",
     mistakes="Putting the count condition in WHERE (aggregates are not allowed there). Using AVG on an integer "
              "column in PostgreSQL is fine, but `SUM(x) / COUNT(*)` on integers truncates. Taking the first 4 "
              "digits in the title instead of the last ones (titles like '1984 (1984)').",
     learn=["sql-top-n", "sql-aggregation", "sql-window-ranking"])

# ---------------------------------------------------------------- Q5 review: left join nulls + ranking (Chinook)
ex.q("Every employee on the sales board", minutes=5, kind="sql", review=True,
     prompt="""Make a leaderboard of **all 8 employees**: `EmployeeId`, `employee` (first and last name),
`Title`, `customers` (customers they support), `revenue` (sum of those customers' invoice totals, 2 decimals) and
`revenue_rank` (1 = most revenue, ties share a rank and the next rank does not skip).

Employees who support no customers must appear with 0 customers and 0.00 revenue (not NULL). Example row:
`1 | Andrew Adams | General Manager | 0 | 0.0 | 4`.""",
     hint1="Signal: \"all employees, even without customers\" plus a ranking without gaps. Pattern: LEFT JOIN chain "
           "with COALESCE, then DENSE_RANK over the aggregated value.",
     hint2="1. Employee LEFT JOIN Customer ON SupportRepId, LEFT JOIN Invoice ON CustomerId.\n"
           "2. Group by employee; `COUNT(DISTINCT c.CustomerId)` and `COALESCE(SUM(i.Total), 0)`.\n"
           "3. `DENSE_RANK() OVER (ORDER BY COALESCE(SUM(i.Total), 0) DESC)`: a window can use an aggregate "
           "in the same SELECT, because windows run after GROUP BY.",
     solution="""SELECT e.EmployeeId,
       e.FirstName || ' ' || e.LastName AS employee,
       e.Title,
       COUNT(DISTINCT c.CustomerId)          AS customers,
       ROUND(COALESCE(SUM(i.Total), 0), 2)   AS revenue,
       DENSE_RANK() OVER (ORDER BY COALESCE(SUM(i.Total), 0) DESC) AS revenue_rank
FROM Employee e
LEFT JOIN Customer c ON c.SupportRepId = e.EmployeeId
LEFT JOIN Invoice  i ON i.CustomerId = c.CustomerId
GROUP BY e.EmployeeId, e.FirstName, e.LastName, e.Title
ORDER BY revenue_rank, e.EmployeeId""",
     why="Only the 3 sales support agents have customers; the 5 others survive because every join is a LEFT JOIN. "
         "`COUNT(DISTINCT c.CustomerId)` counts customers, not invoices (the invoice join repeats each customer "
         "once per invoice), and COUNT ignores NULLs so it gives 0. SUM over no rows is NULL, hence COALESCE. "
         "DENSE_RANK gives the 5 employees with 0 revenue rank 4, right after rank 3.",
     complexity="One pass over the joined rows (8 employees, 59 customers, 412 invoices).",
     mistakes="`COUNT(*)` (gives 1 for an employee with no customers, because the LEFT JOIN row exists). "
              "`COUNT(c.CustomerId)` without DISTINCT (counts invoices). An inner JOIN to Invoice after the LEFT "
              "JOIN to Customer, which drops the employees again.",
     learn=["sql-left-join-nulls", "sql-window-ranking"])

ex.save()
