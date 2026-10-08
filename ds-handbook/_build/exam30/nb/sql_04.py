import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sql_easy_common import start, nrows, val

# Day 4 SQL: focus LEFT JOIN and NULLs (anti-join, counting zeros, ON vs WHERE); review joins.
ex = start(4)

q1 = """SELECT ar.ArtistId, ar.Name
FROM Artist ar
LEFT JOIN Album al ON al.ArtistId = ar.ArtistId
WHERE al.AlbumId IS NULL
ORDER BY ar.ArtistId"""
ex.q("Artists without albums", minutes=4, level="easy", kind="sql",
     prompt="Some artists in the catalogue have no album at all. Return their `ArtistId` and `Name`, by ArtistId.\n\n"
            f"Expected: {nrows(ex, q1)} rows (out of 275 artists).",
     hint1="Signal: 'has no matching row in the other table'. Pattern: anti-join (LEFT JOIN, then keep rows where the "
           "right side IS NULL).",
     hint2="1. FROM Artist ar LEFT JOIN Album al ON al.ArtistId = ar.ArtistId. 2. Artists with no album get NULL in "
           "every Album column. 3. WHERE al.AlbumId IS NULL.",
     solution=q1,
     why="A LEFT JOIN keeps every left row; when there is no match, the right columns are NULL. Testing the right "
         "table's primary key for NULL is safe because a real key is never NULL. "
         "`WHERE NOT EXISTS (SELECT 1 FROM Album al WHERE al.ArtistId = ar.ArtistId)` is equivalent.",
     complexity="O(Artist + Album) with a hash join.",
     mistakes="Testing a nullable right column (for example a column that can be NULL even when the row exists). "
              "Using an INNER JOIN, which can never return unmatched rows.",
     learn=["sql-left-join-nulls"],
     source=("LeetCode 183 Customers Who Never Order (same pattern)", "https://leetcode.com/problems/customers-who-never-order/"))

q2_simple = """SELECT m.Name AS media_type,
       COUNT(*) AS never_sold
FROM Track t
JOIN MediaType m ON m.MediaTypeId = t.MediaTypeId
LEFT JOIN InvoiceLine il ON il.TrackId = t.TrackId
WHERE il.InvoiceLineId IS NULL
GROUP BY m.Name
ORDER BY never_sold DESC"""
ex.q("Tracks nobody bought", minutes=5, level="easy", kind="sql",
     prompt="How many tracks of each media type have **never** been sold (no row in `InvoiceLine`)? Return "
            "`media_type` (the name from `MediaType`) and `never_sold`, highest first.\n\n"
            f"Expected: {nrows(ex, q2_simple)} rows; together they add up to {val(ex, 'SELECT COUNT(*) FROM Track WHERE TrackId NOT IN (SELECT TrackId FROM InvoiceLine)')} unsold tracks.",
     hint1="Signal: 'never sold' means no matching row. Pattern: LEFT JOIN anti-join, then GROUP BY.",
     hint2="1. FROM Track t JOIN MediaType m (every track has a type). 2. LEFT JOIN InvoiceLine il ON il.TrackId = "
           "t.TrackId. 3. WHERE il.InvoiceLineId IS NULL. 4. GROUP BY m.Name, COUNT(*).",
     solution=q2_simple,
     why="The anti-join keeps exactly one row per unsold track (there is no line to multiply it), so COUNT(*) counts "
         "tracks. Follow-up: to also show sold tracks per type, count the anti-join flag with CASE instead of "
         "filtering, but deduplicate InvoiceLine first, because a track sold twice would otherwise be counted twice.",
     complexity="O(Track + InvoiceLine).",
     mistakes="Adding a condition on `il` in WHERE other than IS NULL (turns the LEFT JOIN back into an inner join). "
              "Counting `il.TrackId` (always NULL here, so the count is 0).",
     learn=["sql-left-join-nulls", "sql-joins"])

q3 = """SELECT u.user_id,
       COUNT(e.event_id) AS views
FROM users u
LEFT JOIN events e
       ON e.user_id = u.user_id
      AND e.event_type = 'view'
GROUP BY u.user_id
ORDER BY views, u.user_id"""
ex.q("Views per user, zeros included", minutes=5, level="easy", kind="sql",
     prompt="Return **every** user in the made-up `users` table with `views` = their number of `view` events. "
            "Users with no views must appear with 0. Order by views, then user_id.\n\n"
            f"Expected: {nrows(ex, q3)} rows (all users), and users 4, 11 and 19 have 0.",
     hint1="Signal: 'every user, zeros included'. Pattern: LEFT JOIN with the filter in the ON clause, and "
           "COUNT(right_column).",
     hint2="1. FROM users u LEFT JOIN events e ON e.user_id = u.user_id AND e.event_type = 'view'. 2. GROUP BY "
           "u.user_id. 3. COUNT(e.event_id), not COUNT(*).",
     solution=q3,
     why="A filter on the right table in WHERE removes the NULL rows created by the LEFT JOIN, so users without views "
         "vanish. In ON it only restricts which events match. COUNT(*) would count the NULL row as 1; "
         "COUNT(e.event_id) counts 0.",
     complexity="O(users + events).",
     mistakes="`WHERE e.event_type = 'view'` (silently becomes an inner join). `COUNT(*)` (gives 1 instead of 0). "
              "This is one of the most common exam traps.",
     learn=["sql-left-join-nulls"])

q4 = """SELECT e.EmployeeId,
       e.FirstName || ' ' || e.LastName AS employee,
       e.Title,
       COUNT(c.CustomerId) AS customers
FROM Employee e
LEFT JOIN Customer c ON c.SupportRepId = e.EmployeeId
GROUP BY e.EmployeeId, employee, e.Title
ORDER BY customers DESC, e.EmployeeId"""
ex.q("All employees and their customers", minutes=4, level="easy", kind="sql",
     prompt="HR wants a list of **all** employees with the number of customers each supports (0 if none). Return "
            "`EmployeeId`, `employee` (full name), `Title` and `customers`. Most customers first, then by id.\n\n"
            f"Expected: {nrows(ex, q4)} rows.",
     hint1="Signal: 'all employees' (the table that must stay complete) and a count from another table. Pattern: "
           "LEFT JOIN from Employee, COUNT of a right-side column.",
     hint2="1. FROM Employee e LEFT JOIN Customer c ON c.SupportRepId = e.EmployeeId. 2. GROUP BY the employee "
           "columns. 3. COUNT(c.CustomerId).",
     solution=q4,
     why="The table that must be complete goes on the left. Managers and IT staff have no customers, so they get "
         "one NULL row from the join and COUNT(c.CustomerId) turns it into 0.",
     complexity="O(Employee + Customer).",
     mistakes="Starting FROM Customer (then employees without customers can never appear). COUNT(*) gives 1 for them. "
              "RIGHT JOIN works in PostgreSQL but only in SQLite 3.39 and later; prefer swapping the tables.",
     learn=["sql-left-join-nulls"])

q5 = """SELECT c.CustomerId,
       c.FirstName || ' ' || c.LastName AS customer,
       c.Country,
       e.LastName AS rep,
       ROUND(SUM(i.Total), 2) AS spend
FROM Customer c
JOIN Invoice i  ON i.CustomerId = c.CustomerId
JOIN Employee e ON e.EmployeeId = c.SupportRepId
GROUP BY c.CustomerId, customer, c.Country, rep
ORDER BY spend DESC
LIMIT 5"""
ex.q("Top customers and their rep", minutes=5, level="easy", kind="sql", review=True,
     prompt="Return the top 5 customers by total spend (sum of `Invoice.Total`): `CustomerId`, `customer` (full "
            "name), `Country`, `rep` (support rep's last name) and `spend` (2 decimals). Highest spend first.",
     hint1="Signal: data from three tables, one row per customer. Pattern: INNER JOIN chain plus GROUP BY.",
     hint2="1. Customer JOIN Invoice ON CustomerId. 2. JOIN Employee ON EmployeeId = SupportRepId. 3. GROUP BY the "
           "customer columns and rep. 4. SUM(i.Total), ORDER BY DESC, LIMIT 5.",
     solution=q5,
     why="Joining Employee adds one rep per customer, so it does not multiply invoices. Grouping by the id keeps "
         "customers with the same name apart.",
     complexity="O(Customer + Invoice + Employee).",
     mistakes="Joining InvoiceLine as well and still summing Invoice.Total (each invoice counted once per line). "
              "Ties at rank 5: LIMIT cuts arbitrarily; say so in an exam.",
     learn=["sql-joins"])

ex.save()
