import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
from sql_mid_data import build_setup

ex = Exam(15, "sql")
build_setup(ex, "chinook", "app", "movielens")

# ---------------------------------------------------------------- Q1 org chart (Chinook)
ex.q("Who reports to whom", minutes=5, kind="sql",
     prompt="""Chinook `Employee` has a `ReportsTo` column with the id of each person's manager (NULL for the top
boss). Return all 8 employees with `EmployeeId`, `employee` (full name), `manager` (full name, NULL for the boss),
`skip_manager` (the manager's manager) and `direct_reports` (how many people report to this employee, 0 if nobody).

Example row: `3 | Jane Peacock | Nancy Edwards | Andrew Adams | 0`.

Follow-up: how would you list everybody under Andrew Adams at any depth?""",
     hint1="Signal: a table that points at itself (`ReportsTo` -> `EmployeeId`). Pattern: self join with aliases; "
           "LEFT JOIN so the boss (NULL manager) stays.",
     hint2="1. `Employee e LEFT JOIN Employee m ON m.EmployeeId = e.ReportsTo` (manager).\n"
           "2. `LEFT JOIN Employee mm ON mm.EmployeeId = m.ReportsTo` (skip level).\n"
           "3. `LEFT JOIN Employee r ON r.ReportsTo = e.EmployeeId` and COUNT(r.EmployeeId), grouped by employee.",
     solution="""SELECT e.EmployeeId,
       e.FirstName || ' ' || e.LastName   AS employee,
       m.FirstName || ' ' || m.LastName   AS manager,
       mm.FirstName || ' ' || mm.LastName AS skip_manager,
       COUNT(r.EmployeeId)                AS direct_reports
FROM Employee e
LEFT JOIN Employee m  ON m.EmployeeId  = e.ReportsTo     -- my manager
LEFT JOIN Employee mm ON mm.EmployeeId = m.ReportsTo     -- my manager's manager
LEFT JOIN Employee r  ON r.ReportsTo   = e.EmployeeId    -- people who report to me
GROUP BY e.EmployeeId, e.FirstName, e.LastName, m.FirstName, m.LastName, mm.FirstName, mm.LastName
ORDER BY e.EmployeeId""",
     why="Each alias is a separate copy of the same table playing a different role (me, my manager, my skip "
         "manager, my reports); the join condition says which role. LEFT JOIN keeps Andrew Adams, whose ReportsTo "
         "is NULL, and also keeps people without reports. `COUNT(r.EmployeeId)` counts only matched rows, so it "
         "gives 0, while `COUNT(*)` would give 1. In SQLite `'a' || NULL` is NULL, so the boss gets a NULL manager "
         "name, as asked. Follow-up: any depth needs a recursive CTE (day 24).",
     complexity="8 rows; in general one index lookup per join on the id columns.",
     mistakes="Swapping the direction (`m.ReportsTo = e.EmployeeId` finds reports, not the manager). Inner joins "
              "that drop the boss. `COUNT(*)` for direct reports.",
     learn=["sql-self-join", "sql-left-join-nulls", "sql-recursive-cte"])

# ---------------------------------------------------------------- Q2 pairs in the same basket (Chinook)
ex.q("Genres bought in the same order", minutes=6, kind="sql",
     prompt="""Chinook. Two genres are **bought together** when both appear on the same invoice. Return the
**8 genre pairs** that appear together on the most invoices: `genre_a`, `genre_b`, `invoices`, most first (ties:
alphabetical). List each pair once, with `genre_a` alphabetically before `genre_b`.

Example: an invoice with 3 Rock tracks, 1 Jazz track and 2 Latin tracks adds 1 to (Jazz, Latin), (Jazz, Rock) and
(Latin, Rock). It does not add 3 to anything.

Follow-up: Rock appears in most top pairs simply because it is the biggest genre. How would you measure
"surprisingly often together"?""",
     hint1="Signal: \"pairs that occur together in the same basket\". Pattern: self join of a (basket, item) table "
           "on the basket id, with `a.item < b.item` to avoid duplicates and self pairs.",
     hint2="1. CTE: `SELECT DISTINCT InvoiceId, genre` (one row per genre per invoice).\n"
           "2. Join the CTE to itself `ON a.InvoiceId = b.InvoiceId AND a.genre < b.genre`.\n"
           "3. Group by the pair, COUNT(*), order, LIMIT 8.",
     solution="""WITH inv_genre AS (
    SELECT DISTINCT il.InvoiceId, g.Name AS genre
    FROM InvoiceLine il
    JOIN Track t ON t.TrackId = il.TrackId
    JOIN Genre g ON g.GenreId = t.GenreId
)
SELECT a.genre AS genre_a, b.genre AS genre_b, COUNT(*) AS invoices
FROM inv_genre a
JOIN inv_genre b
  ON a.InvoiceId = b.InvoiceId
 AND a.genre < b.genre
GROUP BY a.genre, b.genre
ORDER BY invoices DESC, genre_a, genre_b
LIMIT 8""",
     why="The DISTINCT step turns lines into one row per (invoice, genre), so 3 Rock tracks count once. The "
         "condition `a.genre < b.genre` removes (Rock, Rock) and keeps only one of (Jazz, Rock) / (Rock, Jazz); "
         "`<>` would list every pair twice. Follow-up: use lift = `P(A and B) / (P(A) * P(B))` with P = share of "
         "invoices. Lift above 1 means more often together than chance. Big genres get high counts but not "
         "necessarily high lift.",
     complexity="The self join is quadratic in the number of genres per invoice (small here). On big baskets, "
                "restrict to frequent items first.",
     mistakes="Joining raw invoice lines (inflated counts). `a.genre <> b.genre` (double counting). Forgetting the "
              "invoice condition, which pairs every row with every row (a cross join).",
     learn=["sql-self-join", "sql-dedup-cleaning"])

# ---------------------------------------------------------------- Q3 referrals (app)
ex.q("Do buyers bring buyers?", minutes=7, kind="sql",
     prompt="""Shopping app (made up). `app_users.referred_by` holds the user_id of the person who invited this user.
Growth asks: **are friends invited by buyers more likely to buy?** A buyer is a user with at least one completed order.

Return one row per `referrer_type` ('buyer' or 'non_buyer'): `referred_users`, `referred_buyers`, `pct_bought`
(1 decimal) and `pct_same_platform` (share of invited friends on the same platform as their referrer, 1 decimal).

Then say in one sentence whether you would tell Growth "buyers bring buyers".""",
     hint1="Signal: a column that points to another row of the same table (`referred_by`). Pattern: self join "
           "friend -> referrer, plus LEFT JOINs to a buyer list for both sides.",
     hint2="1. CTE buyers: DISTINCT user_id with a completed order.\n"
           "2. `app_users f JOIN app_users r ON r.user_id = f.referred_by`.\n"
           "3. LEFT JOIN buyers twice (once for r, once for f); CASE to label and flag; group by referrer type.",
     solution="""WITH buyers AS (
    SELECT DISTINCT user_id FROM purchases WHERE status = 'completed'
), pairs AS (
    SELECT f.user_id AS friend_id,
           r.user_id AS referrer_id,
           CASE WHEN rb.user_id IS NOT NULL THEN 'buyer' ELSE 'non_buyer' END AS referrer_type,
           CASE WHEN fb.user_id IS NOT NULL THEN 1 ELSE 0 END AS friend_bought,
           CASE WHEN f.platform = r.platform THEN 1 ELSE 0 END AS same_platform
    FROM app_users f
    JOIN app_users r     ON r.user_id = f.referred_by
    LEFT JOIN buyers rb  ON rb.user_id = r.user_id
    LEFT JOIN buyers fb  ON fb.user_id = f.user_id
)
SELECT referrer_type,
       COUNT(*)                            AS referred_users,
       SUM(friend_bought)                  AS referred_buyers,
       ROUND(100.0 * AVG(friend_bought), 1) AS pct_bought,
       ROUND(100.0 * AVG(same_platform), 1) AS pct_same_platform
FROM pairs
GROUP BY referrer_type""",
     why="The self join puts each invited friend next to their referrer, so attributes of both can be compared on "
         "one row. 30.8% of friends of buyers bought versus 24.7% of friends of non-buyers, but with only 65 "
         "friends in the buyer group the gap is within noise (a two-proportion test would not be significant), "
         "and it is correlation, not causation. Tell Growth: \"a small, uncertain difference; not enough to target "
         "referral rewards at buyers yet\". AVG of a 0/1 flag is a rate, a handy trick.",
     complexity="Index lookups on user_id for each join; linear in the number of referred users.",
     mistakes="Joining in the wrong direction (`r.referred_by = f.user_id` finds who referred the referrer). "
              "Inner joins to buyers (drops non-buyers). Over-reading a small difference.",
     learn=["sql-self-join", "sql-ratios", "stats-hypothesis-tests"])

# ---------------------------------------------------------------- Q4 co-liked movies (MovieLens)
ex.q("Fans of both", minutes=7, kind="sql",
     prompt="""MovieLens (real). Take the **15 most rated movies** (ties by movie_id). A user **likes** a movie if
they rated it 4 or more. Which **5 pairs** of these movies have the most users who like **both**?

Return `movie_a`, `movie_b` (titles, each pair once), `fans_of_both`, most first.

Example: if user 1 likes Pulp Fiction, Forrest Gump and Fight Club, they add 1 to three pairs.

Follow-up: why restrict to the top 15 first? What would happen on all 9,742 movies?""",
     hint1="Signal: \"pairs of items that share users\". Pattern: self join of (user, movie) on user_id with "
           "`a.movie_id < b.movie_id`, after filtering both the movies and the likes.",
     hint2="1. CTE top: 15 movie_ids by COUNT(*) DESC.\n2. CTE liked: ratings >= 4 on those movies.\n"
           "3. Self join liked on user_id with a.movie_id < b.movie_id, group by the pair, join titles, LIMIT 5.",
     solution="""WITH top AS (
    SELECT movie_id
    FROM ml_ratings
    GROUP BY movie_id
    ORDER BY COUNT(*) DESC, movie_id
    LIMIT 15
), liked AS (
    SELECT r.user_id, r.movie_id
    FROM ml_ratings r
    JOIN top t ON t.movie_id = r.movie_id
    WHERE r.rating >= 4
)
SELECT ma.title AS movie_a, mb.title AS movie_b, COUNT(*) AS fans_of_both
FROM liked a
JOIN liked b     ON a.user_id = b.user_id AND a.movie_id < b.movie_id
JOIN ml_movies ma ON ma.movie_id = a.movie_id
JOIN ml_movies mb ON mb.movie_id = b.movie_id
GROUP BY a.movie_id, b.movie_id, ma.title, mb.title
ORDER BY fans_of_both DESC, movie_a
LIMIT 5""",
     why="This is item-to-item co-occurrence, the simplest \"people who liked X also liked Y\" recommender. "
         "Filtering before the self join keeps it small: a user who likes k of the 15 movies creates k(k-1)/2 "
         "pairs. On the full table, heavy users with thousands of ratings would create millions of pairs, so in "
         "production you limit items, sample users, or compute it in a batch job (or with embeddings). Raw "
         "co-counts favour popular movies; cosine similarity or lift normalises for popularity.",
     complexity="Quadratic in likes per user for the self join; 2,860 liked rows here.",
     mistakes="Self joining before filtering (slow). `a.movie_id <> b.movie_id` (each pair twice). Grouping by "
              "title only (two movies can share a title).",
     learn=["sql-self-join", "sql-top-n", "ai-recommenders"])

# ---------------------------------------------------------------- Q5 review: running ratio (app)
ex.q("Referral share of the user base, week by week", minutes=5, kind="sql", review=True,
     prompt="""Shopping app. Weeks start on Monday (`date(d, 'weekday 0', '-6 days')`). For each signup week return
`week_start`, `signups`, `referral_signups`, `cum_users`, `cum_referral` (both cumulative since launch) and
`cum_referral_pct` = cum_referral / cum_users in percent (1 decimal).

Example: weeks with (signups, referral) = (100, 20) then (300, 30) give cumulative shares 20.0 and 12.5.
The average of the weekly rates (20% and 10%) would wrongly say 15.""",
     hint1="Pattern: two running totals, then divide them. Never average weekly ratios to get a cumulative ratio.",
     hint2="1. CTE weekly: COUNT(*) and SUM(CASE WHEN channel = 'referral' ...) per week.\n"
           "2. `SUM(x) OVER (ORDER BY week_start ROWS UNBOUNDED PRECEDING)` for both; divide with 100.0.",
     solution="""WITH weekly AS (
    SELECT date(signup_date, 'weekday 0', '-6 days') AS week_start,
           COUNT(*) AS signups,
           SUM(CASE WHEN channel = 'referral' THEN 1 ELSE 0 END) AS referral_signups
    FROM app_users
    GROUP BY date(signup_date, 'weekday 0', '-6 days')
)
SELECT week_start, signups, referral_signups,
       SUM(signups)          OVER w AS cum_users,
       SUM(referral_signups) OVER w AS cum_referral,
       ROUND(100.0 * SUM(referral_signups) OVER w / SUM(signups) OVER w, 1) AS cum_referral_pct
FROM weekly
WINDOW w AS (ORDER BY week_start ROWS UNBOUNDED PRECEDING)
ORDER BY week_start""",
     why="A ratio of running totals weights every user equally; an average of weekly ratios weights every week "
         "equally, which is wrong when week sizes differ (the last week is half size). The share is stable around "
         "15% to 17%, and the final cumulative value (227 of 1,500) equals the overall referral share.",
     complexity="One group by and windows over 9 rows.",
     mistakes="`AVG(weekly_pct) OVER (...)` (average of ratios). Integer division. Forgetting the frame and "
              "relying on the default (fine here because weeks are unique, risky otherwise).",
     learn=["sql-running-totals", "sql-ratios"])

ex.save()
