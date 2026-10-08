import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam
from sql_hard_tables import load, put_doc

INTRO = """**Light day: a short final check (about 20 minutes), then rest.**

- Three mixed questions, no timer pressure. If one feels slow, that is fine: note it, do not grind.
- Then redo the 2 or 3 SQL items from your mistake log that you missed most often (the handbook Plan tab lists them).
- Finish with the checklist at the bottom of this notebook. Sleep matters more than one more query."""

ex = Exam(30, "sql", title="Day 30: SQL final check", intro=INTRO)
code, doc = load("chinook", "tiktok")
ex.setup(code, data=True)
put_doc(ex, doc)

ex.q("Top customer in each country, ties included", minutes=5, kind="sql",
     prompt="""Chinook (real). For countries with at least 3 customers, return the customer(s) with the highest total
spend (`SUM(Invoice.Total)`): `Country`, `customer` (first + last name), `total` (2 decimals). If several customers
tie for first place, show all of them. Order by total descending.""",
     hint1="Signal: 'highest per country' and 'show all ties'. Pattern: top-N per group with RANK (not ROW_NUMBER), "
           "plus a COUNT window for the group size filter.",
     hint2="1. `spend`: SUM(Total) per country and customer.\n2. `RANK() OVER (PARTITION BY Country ORDER BY total DESC)` "
           "and `COUNT(*) OVER (PARTITION BY Country)`.\n3. Keep rank 1 and count >= 3.",
     solution="""WITH spend AS (
  SELECT c.Country, c.CustomerId, c.FirstName || ' ' || c.LastName AS customer,
         SUM(i.Total) AS total
  FROM Customer c
  JOIN Invoice i ON i.CustomerId = c.CustomerId
  GROUP BY c.Country, c.CustomerId, c.FirstName, c.LastName
), r AS (
  SELECT *,
    RANK() OVER (PARTITION BY Country ORDER BY total DESC) AS rk,
    COUNT(*) OVER (PARTITION BY Country) AS n_customers
  FROM spend
)
SELECT Country, customer, ROUND(total, 2) AS total
FROM r
WHERE rk = 1 AND n_customers >= 3
ORDER BY total DESC""",
     why="RANK gives every tied customer rank 1, so the United Kingdom returns three customers at 37.62; ROW_NUMBER "
         "would silently pick one. The group-size filter is a window COUNT, computed before the rank filter, so it "
         "counts all customers of the country, not just the winners.",
     complexity="One join, one aggregation, two windows over 59 customers.",
     mistakes="ROW_NUMBER (drops ties). `WHERE n_customers >= 3` inside the same SELECT that defines it (not allowed: "
              "filter in the outer query). Grouping by name only (two customers with the same name merge).",
     learn=["sql-top-n", "sql-window-ranking"])

ex.q("Find the bugs", minutes=6, kind="text",
     prompt="""A teammate wrote this query for "conversion rate per country = users with a completed order / all users",
but the numbers look too high. Find **three** bugs and say how to fix each one.

```sql
SELECT u.country,
  COUNT(*) AS users,
  COUNT(p.order_id) / COUNT(*) * 100 AS conversion_pct
FROM users u
LEFT JOIN orders p ON p.user_id = u.user_id
WHERE p.status = 'completed'
GROUP BY u.country;
```""",
     hint1="Signal: a rate built from a LEFT JOIN. Check three things: where the filter sits, what COUNT counts after the "
           "join, and the data type of the division.",
     hint2="1. What does `WHERE p.status = ...` do to users without orders?\n2. A user with 3 orders: how many rows?\n"
           "3. What is `7 / 10` in integer arithmetic?",
     solution="""**Bug 1: the filter is in WHERE.** For users without orders `p.status` is NULL, so WHERE removes them and
the LEFT JOIN becomes an inner join: only buyers remain, and the rate is close to 100%. Fix: move it into the join,
`LEFT JOIN orders p ON p.user_id = u.user_id AND p.status = 'completed'`.

**Bug 2: rows are orders, not users.** A user with 3 orders gives 3 rows, so `COUNT(*)` counts orders and
`COUNT(p.order_id)` counts orders too. Fix: `COUNT(DISTINCT u.user_id)` for users and
`COUNT(DISTINCT p.user_id)` for converted users.

**Bug 3: integer division.** In PostgreSQL and SQLite, `7 / 10` is 0, so the rate is 0 or 100 (and multiplying by 100
after dividing is too late). Fix: `100.0 * COUNT(DISTINCT p.user_id) / COUNT(DISTINCT u.user_id)`.

Fixed query:

```sql
SELECT u.country,
  COUNT(DISTINCT u.user_id) AS users,
  ROUND(100.0 * COUNT(DISTINCT p.user_id) / COUNT(DISTINCT u.user_id), 1) AS conversion_pct
FROM users u
LEFT JOIN orders p ON p.user_id = u.user_id AND p.status = 'completed'
GROUP BY u.country;
```

Bonus: users with a NULL country form their own group; say whether you keep it or label it 'unknown' with COALESCE.""",
     why="These three bugs (WHERE after LEFT JOIN, fan-out after a join, integer division) cause most wrong ratios in "
         "SQL exams. Checking for them is the 30 second review to do before you say 'done'.",
     learn=["sql-left-join-nulls", "sql-ratios", "sql-exam-approach"])

ex.q("Whose fans are they?", minutes=7, kind="sql", review=True,
     source=("DataLemur TikTok SQL questions (inspiration)", "https://datalemur.com/blog/tiktok-sql-interview-questions"),
     prompt="""Short-video app (made up). A viewer's **favourite creator** is the creator whose videos they watched for the
most seconds in total (ties: the lower `creator_id`). Return the 5 creators who are the favourite of the most viewers:
`creator_id`, `fans`, `pct` (% of all viewers, 1 decimal). Order by fans descending, then creator_id.

*Follow-up:* one creator is the favourite of a third of all viewers. Is that a problem for the platform?""",
     hint1="Signal: 'the top one per viewer', then count those. Pattern: top-N per group (ROW_NUMBER with a tiebreaker), "
           "then an aggregation over the winners.",
     hint2="1. `w`: SUM(watch_s) per viewer and creator (views join videos).\n"
           "2. `ROW_NUMBER() OVER (PARTITION BY viewer_id ORDER BY secs DESC, creator_id)`, keep 1.\n"
           "3. COUNT per creator; divide by `(SELECT COUNT(DISTINCT viewer_id) FROM tt_views)`.",
     solution="""WITH w AS (
  SELECT x.viewer_id, v.creator_id, SUM(x.watch_s) AS secs
  FROM tt_views x
  JOIN tt_videos v ON v.video_id = x.video_id
  GROUP BY x.viewer_id, v.creator_id
), top AS (
  SELECT viewer_id, creator_id,
    ROW_NUMBER() OVER (PARTITION BY viewer_id ORDER BY secs DESC, creator_id) AS rn
  FROM w
)
SELECT creator_id, COUNT(*) AS fans,
  ROUND(100.0 * COUNT(*) / (SELECT COUNT(DISTINCT viewer_id) FROM tt_views), 1) AS pct
FROM top
WHERE rn = 1
GROUP BY creator_id
ORDER BY fans DESC, creator_id
LIMIT 5""",
     why="Here ROW_NUMBER is right (the task defines a tiebreaker and wants exactly one favourite per viewer). Creator "
         "16 is the favourite of 401 viewers (33.9%). Follow-up: heavy concentration means the feed may over-expose "
         "one creator (a popularity feedback loop); new creators get little exposure and viewers may tire. Look at "
         "diversity metrics (share of watch time from the top creator per viewer) and at exploration in ranking.",
     complexity="One join and aggregation, one window over (viewer, creator) pairs.",
     mistakes="Favourite by number of views instead of seconds (the task says seconds). RANK without a tiebreaker "
              "(a viewer can then have two favourites and is counted twice).",
     learn=["sql-top-n", "sql-aggregation"])

ex.text("""---
## Checklist for the day before the exam

**SQL, 10 minutes of recall (say it, do not code it):**
- Query order: FROM, JOIN, WHERE, GROUP BY, HAVING, window functions, SELECT, DISTINCT, ORDER BY, LIMIT.
- The 6 shapes you met most: top-N per group (ROW_NUMBER / RANK), running totals (SUM OVER, ROWS frame),
  LAG/LEAD comparisons, gaps and islands (date minus ROW_NUMBER), retention / funnels (LEFT JOIN + CASE flags),
  median / percentiles (ROW_NUMBER and COUNT, or CUME_DIST).
- The 3 bugs from Q2: filter of a LEFT JOIN in WHERE, fan-out after a join, integer division.
- Dialect notes: PostgreSQL has `DATE_TRUNC`, `INTERVAL`, `FILTER (WHERE ...)`, `PERCENTILE_CONT`; SQLite does not.

**In the exam:**
- Restate the question, ask about the grain (one row = ?), duplicates, NULLs and time zone.
- Say the plan in 2 sentences, write CTEs with clear names, run a sanity check (row counts, a known user).
- When done, offer one follow-up yourself: "if the table had duplicates I would ...", "at scale I would ...".

**Logistics:**
- Test the editor or shared doc link, camera, microphone; have water and paper ready.
- Prepare 2 questions for the examiner about the team's data and metrics.
- Stop studying early in the evening. Sleep is part of the preparation.""")

ex.save()
