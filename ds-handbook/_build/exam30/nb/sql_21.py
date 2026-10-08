import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam
from sql_hard_tables import load, put_doc

INTRO = """**Mock exam rules (30 minutes, one timer for the whole notebook).**

- Start one 30 minute timer, then work through Q1 to Q6 in any order. That is about 5 minutes a query: exam pace.
- Do not open any hint or solution until the timer rings. When it rings, stop, then grade yourself with the solutions.
- Score: 1 point for a correct result, 0.5 if the logic is right but a detail is wrong (rounding, a missing filter).
  5 or more is exam ready. Every question you missed goes into the mistake log.
- Topics are mixed on purpose (dedup, funnels, retention, self-joins, ratios, streaks). Part of the test is spotting which one."""

ex = Exam(21, "sql", intro=INTRO)
code, doc = load("apps", "chinook")
ex.setup(code, data=True)
put_doc(ex, doc)

ex.q("Clean the raw event stream", minutes=5, kind="sql",
     prompt="""`app_events_raw` is the log as the apps send it. Two kinds of junk are in it:
- **retries**: an exact copy of an event (same `user_id`, `event_time`, `event_name`), only `raw_id` and `received_at` differ;
- **double taps**: the same user fires the same event again 1 to 3 seconds later.

Rule: drop exact copies, then drop an event if the same user had the same `event_name` **5 seconds or less** before it.
Return one row per `event_name`: `raw_rows`, `clean_rows`, `removed`, ordered by `raw_rows` descending.

Example: user 7 sends `view_item` at 10:00:00 (twice, a retry) and again at 10:00:02 (a tap). Clean result: 1 row.

*Follow-up (say it out loud):* how would you check that your rule did not delete real events?""",
     hint1="Signal: 'copies' and 'within N seconds of the previous one'. Pattern: dedup-cleaning. SELECT DISTINCT for "
           "exact copies, then LAG over (user, event) ordered by time for near copies.",
     hint2="1. CTE `exact`: SELECT DISTINCT user_id, event_time, event_name.\n"
           "2. CTE `flagged`: add `LAG(event_time) OVER (PARTITION BY user_id, event_name ORDER BY event_time)`.\n"
           "3. Keep rows where the previous time is NULL or more than 5 seconds earlier "
           "(`(julianday(t) - julianday(prev)) * 86400 > 5`).\n4. Count raw and clean rows per event and join them.",
     solution="""WITH exact AS (
  SELECT DISTINCT user_id, event_time, event_name
  FROM app_events_raw
), flagged AS (
  SELECT *,
    LAG(event_time) OVER (PARTITION BY user_id, event_name ORDER BY event_time) AS prev_time
  FROM exact
), clean AS (
  SELECT * FROM flagged
  WHERE prev_time IS NULL
     OR (julianday(event_time) - julianday(prev_time)) * 86400 > 5
)
SELECT r.event_name, r.raw_rows, c.clean_rows, r.raw_rows - c.clean_rows AS removed
FROM (SELECT event_name, COUNT(*) AS raw_rows FROM app_events_raw GROUP BY event_name) r
JOIN (SELECT event_name, COUNT(*) AS clean_rows FROM clean GROUP BY event_name) c
  ON c.event_name = r.event_name
ORDER BY r.raw_rows DESC""",
     why="Retries are identical on the business columns, so DISTINCT on those columns (not on `raw_id`) removes them. "
         "Double taps differ by a few seconds, so only a comparison with the previous event of the same user and type "
         "finds them: that is LAG with the right PARTITION BY. Follow-up answer: the clean counts (11,003 views, 4,638 "
         "carts, 2,439 checkouts, 1,014 purchases) match the trusted `app_events` table exactly, which is the check "
         "you describe: compare with a trusted source, and look at the gap distribution (real repeats are 15 s or more apart).",
     complexity="One sort per (user, event) partition: O(n log n).",
     mistakes="DISTINCT on all columns (raw_id makes every row unique, nothing is removed). Comparing with the previous "
              "event of ANY type (a view then a cart 2 s later is real). In PostgreSQL write "
              "`event_time - prev_time <= interval '5 seconds'`; julianday is SQLite only.",
     learn=["sql-dedup-cleaning", "sql-lag-lead"])

ex.q("Ordered checkout funnel by platform", minutes=6, kind="sql",
     prompt="""Users who signed up in **January 2024** (`app_users`). For each user look at their first 7 days
(signup day plus the next 6, i.e. `event_time < signup_date + 7 days`). The funnel is
`view_item -> add_to_cart -> checkout -> purchase`, and **order matters**: a step only counts if it happens after the
user's first time at the previous step (an `add_to_cart` before any `view_item` does not count).

Return per `platform`: `users`, `viewed`, `carted`, `checked_out`, `purchased`, `pct_purchase` (purchased / users, 1 decimal).

Example: a user with cart 09:00, view 09:05, purchase 09:20 and no checkout counts as viewed only.""",
     hint1="Signal: 'order matters' and 'first time at the previous step'. Pattern: funnels with chained CTEs: each step "
           "joins events that happen after the previous step's time.",
     hint2="1. CTE `u`: January signups.\n2. `s1`: first view per user inside the window.\n"
           "3. `s2`: first cart with `event_time > s1.t`, joined from s1 (so only viewers can reach it). Same for s3, s4.\n"
           "4. `u LEFT JOIN s1 ... s4`, GROUP BY platform, COUNT(sN.user_id).",
     solution="""WITH u AS (
  SELECT user_id, platform, signup_date, date(signup_date, '+7 days') AS window_end
  FROM app_users
  WHERE signup_date >= '2024-01-01' AND signup_date < '2024-02-01'
), s1 AS (
  SELECT u.user_id, MIN(e.event_time) AS t
  FROM u JOIN app_events e ON e.user_id = u.user_id
  WHERE e.event_name = 'view_item' AND e.event_time < u.window_end
  GROUP BY u.user_id
), s2 AS (
  SELECT s1.user_id, MIN(e.event_time) AS t
  FROM s1 JOIN u ON u.user_id = s1.user_id
  JOIN app_events e ON e.user_id = s1.user_id
  WHERE e.event_name = 'add_to_cart' AND e.event_time > s1.t AND e.event_time < u.window_end
  GROUP BY s1.user_id
), s3 AS (
  SELECT s2.user_id, MIN(e.event_time) AS t
  FROM s2 JOIN u ON u.user_id = s2.user_id
  JOIN app_events e ON e.user_id = s2.user_id
  WHERE e.event_name = 'checkout' AND e.event_time > s2.t AND e.event_time < u.window_end
  GROUP BY s2.user_id
), s4 AS (
  SELECT s3.user_id, MIN(e.event_time) AS t
  FROM s3 JOIN u ON u.user_id = s3.user_id
  JOIN app_events e ON e.user_id = s3.user_id
  WHERE e.event_name = 'purchase' AND e.event_time > s3.t AND e.event_time < u.window_end
  GROUP BY s3.user_id
)
SELECT u.platform, COUNT(*) AS users,
  COUNT(s1.user_id) AS viewed, COUNT(s2.user_id) AS carted,
  COUNT(s3.user_id) AS checked_out, COUNT(s4.user_id) AS purchased,
  ROUND(100.0 * COUNT(s4.user_id) / COUNT(*), 1) AS pct_purchase
FROM u
LEFT JOIN s1 ON s1.user_id = u.user_id
LEFT JOIN s2 ON s2.user_id = u.user_id
LEFT JOIN s3 ON s3.user_id = u.user_id
LEFT JOIN s4 ON s4.user_id = u.user_id
GROUP BY u.platform
ORDER BY u.platform""",
     why="Each step CTE starts from the users who passed the previous step and only looks at later events, so the "
         "funnel is monotone (viewed >= carted >= checked_out >= purchased) by construction. LEFT JOIN from `u` keeps "
         "users who never viewed, so the denominator is all signups. iOS converts best (17.0%), web worst (11.1%).",
     complexity="Each step is a join on user_id plus a MIN: about O(events) with an index on (user_id, event_name, event_time).",
     mistakes="Counting users who did each event at any time (not ordered, not monotone). Using `MIN(CASE ...)` per step "
              "and comparing first times: the first cart can be before the first view while a later cart is valid. "
              "Forgetting the 7 day window or using `<=` on a date string against a timestamp.",
     learn=["sql-funnels", "sql-cte"])

ex.q("Day 1 and day 7 retention by signup week", minutes=5, kind="sql", review=True,
     prompt="""Group users by signup week (weeks start on **Monday**). For each cohort week return `users`,
`d1_pct` (share active exactly 1 day after signup) and `d7_pct` (active exactly 7 days after signup), in percent with 1
decimal, using `daily_activity`. Order by cohort week.

Example: signup 2024-01-03 (a Wednesday) belongs to cohort week 2024-01-01; day 7 is 2024-01-10.

*Follow-up:* the last cohort looks worse. Is it a real drop?""",
     hint1="Signal: 'cohort', 'active N days after signup'. Pattern: retention: cohort CTE + LEFT JOIN activity on the exact day.",
     hint2="1. Week start in SQLite: `date(d, 'weekday 0', '-6 days')` (next Sunday, back 6 days = Monday).\n"
           "2. LEFT JOIN `daily_activity` twice, with `activity_date = date(signup_date, '+1 day')` and `'+7 days'`.\n"
           "3. COUNT(d1.user_id) / COUNT(*) per cohort, times 100.0.",
     solution="""WITH cohort AS (
  SELECT user_id, signup_date,
    date(signup_date, 'weekday 0', '-6 days') AS cohort_week
  FROM app_users
)
SELECT c.cohort_week, COUNT(*) AS users,
  ROUND(100.0 * COUNT(d1.user_id) / COUNT(*), 1) AS d1_pct,
  ROUND(100.0 * COUNT(d7.user_id) / COUNT(*), 1) AS d7_pct
FROM cohort c
LEFT JOIN daily_activity d1
  ON d1.user_id = c.user_id AND d1.activity_date = date(c.signup_date, '+1 day')
LEFT JOIN daily_activity d7
  ON d7.user_id = c.user_id AND d7.activity_date = date(c.signup_date, '+7 days')
GROUP BY c.cohort_week
ORDER BY c.cohort_week""",
     why="The day condition sits in the JOIN, not in WHERE, so retained-or-not users all stay in the denominator. "
         "`daily_activity` has one row per user and day, so the joins cannot multiply rows. Follow-up: the last cohort "
         "(2024-02-26, 97 users, d7 22.7%) is a partial week (Monday to Thursday, signups stop on 2024-02-29) and small, "
         "so it is noisy; also check day of week effects before calling it a drop.",
     complexity="Two equality joins on (user_id, date): O(n) with an index.",
     mistakes="Putting `d7.activity_date = ...` in WHERE (turns the LEFT JOIN into an inner join: 100% retention). "
              "Counting activity on day 1 to 7 (that is rolling retention, a different metric). PostgreSQL: "
              "`date_trunc('week', signup_date)` gives the Monday.",
     learn=["sql-retention", "sql-dates"])

ex.q("Genres bought together (with lift)", minutes=6, kind="sql",
     prompt="""Chinook (real). Two genres are "bought together" when both appear on the same invoice. For every pair of
genres (each pair once) with at least 10 shared invoices, return `genre_1`, `genre_2`, `both_inv` and
`lift = P(both) / (P(g1) * P(g2))`, where P is a share of all invoices. Show the top 5 by lift (ties: more shared
invoices first), lift rounded to 2 decimals.

Example: 412 invoices, Rock on 100, Jazz on 50, both on 20: lift = (20/412) / ((100/412) * (50/412)) = 1.65.

*Follow-up:* why not rank by `both_inv` alone?""",
     hint1="Signal: 'pairs on the same invoice'. Pattern: self-join of (invoice, genre) on invoice_id with "
           "`a.genre < b.genre`, then a ratio with per-genre counts.",
     hint2="1. CTE `inv_genre`: DISTINCT (InvoiceId, GenreId) from InvoiceLine join Track.\n"
           "2. `pairs`: self-join on InvoiceId with `a.GenreId < b.GenreId`, COUNT(*).\n"
           "3. `single`: invoices per genre; `n`: total invoices.\n"
           "4. lift = `1.0 * both * total / (inv1 * inv2)`; filter both >= 10; ORDER BY lift DESC.",
     solution="""WITH inv_genre AS (
  SELECT DISTINCT il.InvoiceId, t.GenreId
  FROM InvoiceLine il JOIN Track t ON t.TrackId = il.TrackId
), n AS (
  SELECT COUNT(DISTINCT InvoiceId) AS total FROM inv_genre
), single AS (
  SELECT GenreId, COUNT(*) AS inv FROM inv_genre GROUP BY GenreId
), pairs AS (
  SELECT a.GenreId AS g1, b.GenreId AS g2, COUNT(*) AS both_inv
  FROM inv_genre a
  JOIN inv_genre b ON a.InvoiceId = b.InvoiceId AND a.GenreId < b.GenreId
  GROUP BY a.GenreId, b.GenreId
)
SELECT ga.Name AS genre_1, gb.Name AS genre_2, p.both_inv,
  ROUND(1.0 * p.both_inv * n.total / (s1.inv * s2.inv), 2) AS lift
FROM pairs p
CROSS JOIN n
JOIN single s1 ON s1.GenreId = p.g1
JOIN single s2 ON s2.GenreId = p.g2
JOIN Genre ga ON ga.GenreId = p.g1
JOIN Genre gb ON gb.GenreId = p.g2
WHERE p.both_inv >= 10
ORDER BY lift DESC, p.both_inv DESC
LIMIT 5""",
     why="DISTINCT first makes one row per (invoice, genre), so an invoice with 5 Rock tracks counts once. "
         "`a.GenreId < b.GenreId` keeps each pair once and drops self pairs. Follow-up: raw co-occurrence is dominated "
         "by popular genres (Rock appears with everything); lift divides by what chance alone predicts. TV Shows + "
         "Drama has lift 15.49 (people buy TV episodes together); Rock + Alternative & Punk has the most shared "
         "invoices (54) but a lift of only 1.11, so it is mostly popularity. The minimum count guards against tiny noisy pairs.",
     complexity="Self-join per invoice: O(sum of k^2) where k = genres per invoice (small).",
     mistakes="Self-joining InvoiceLine without DISTINCT (counts track pairs, not invoices). Using `<>` instead of `<` "
              "(each pair twice). Integer division in the lift (multiply by 1.0 first).",
     learn=["sql-self-join", "sql-ratios"])

ex.q("Which acquisition channel brings valuable users?", minutes=5, kind="sql",
     prompt="""Per `channel` in `app_users` return:
- `users`: signed-up users;
- `buyer_pct`: % of users with at least one **completed** purchase;
- `net_rev_per_user`: completed revenue divided by ALL users of the channel (2 decimals);
- `refund_pct`: refunded orders / all orders of the channel (1 decimal; NULL if no orders).

Order by `net_rev_per_user` descending. Users with no purchase must count in the denominators.""",
     hint1="Signal: per-group ratios with different denominators. Pattern: ratios with LEFT JOIN + conditional "
           "aggregation (CASE inside SUM / COUNT DISTINCT), and NULLIF for a safe division.",
     hint2="1. `app_users u LEFT JOIN purchases p`.\n2. users = COUNT(DISTINCT u.user_id) (the join repeats users).\n"
           "3. buyers = COUNT(DISTINCT CASE WHEN p.status = 'completed' THEN u.user_id END).\n"
           "4. revenue = SUM(CASE ... THEN amount ELSE 0 END); refunds over `NULLIF(COUNT(p.order_id), 0)`.",
     solution="""SELECT u.channel,
  COUNT(DISTINCT u.user_id) AS users,
  ROUND(100.0 * COUNT(DISTINCT CASE WHEN p.status = 'completed' THEN u.user_id END)
        / COUNT(DISTINCT u.user_id), 1) AS buyer_pct,
  ROUND(SUM(CASE WHEN p.status = 'completed' THEN p.amount ELSE 0 END)
        / COUNT(DISTINCT u.user_id), 2) AS net_rev_per_user,
  ROUND(100.0 * SUM(CASE WHEN p.status = 'refunded' THEN 1 ELSE 0 END)
        / NULLIF(COUNT(p.order_id), 0), 1) AS refund_pct
FROM app_users u
LEFT JOIN purchases p ON p.user_id = u.user_id
GROUP BY u.channel
ORDER BY net_rev_per_user DESC""",
     why="After the LEFT JOIN a user appears once per order, so user counts need DISTINCT while order counts must "
         "not. Referral users bring the most net revenue per signup (29.08) and paid social the least (20.97), even "
         "though buyer rates are close (25.4% to 28.3%), so the gap is in order value, not conversion.",
     complexity="One join and one GROUP BY: O(users + orders).",
     mistakes="Revenue per BUYER instead of per user (changes the ranking). COUNT(*) as the user count (counts orders). "
              "`100 * a / b` with integers. Including refunded amounts in revenue.",
     learn=["sql-ratios", "sql-case-when"])

ex.q("Longest daily streak", minutes=5, kind="sql",
     prompt="""Using `daily_activity` (one row per user per active day), find each user's **longest run of consecutive
active days**. Return the top 5 users: `user_id`, `start_date`, `end_date`, `days`, ordered by `days` descending then
`user_id`. If a user has two runs of the same length, show the earlier one.

Example: active on Jan 3, 4, 5, 7, 8: runs are 3 days (Jan 3 to 5) and 2 days; the longest is 3.

*Follow-up:* how many users ever had a streak of 7 days or more? (Change one line.)""",
     hint1="Signal: 'consecutive days'. Pattern: gaps and islands: day number minus ROW_NUMBER is constant inside a run.",
     hint2="1. `julianday(activity_date) - ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY activity_date)` = group key.\n"
           "2. GROUP BY user_id, key: MIN date, MAX date, COUNT.\n"
           "3. ROW_NUMBER over runs per user ordered by days DESC, start_date; keep rn = 1; top 5.",
     solution="""WITH g AS (
  SELECT user_id, activity_date,
    julianday(activity_date)
      - ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY activity_date) AS grp
  FROM daily_activity
), streaks AS (
  SELECT user_id, MIN(activity_date) AS start_date, MAX(activity_date) AS end_date,
         COUNT(*) AS days
  FROM g
  GROUP BY user_id, grp
), ranked AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY days DESC, start_date) AS rn
  FROM streaks
)
SELECT user_id, start_date, end_date, days
FROM ranked
WHERE rn = 1
ORDER BY days DESC, user_id
LIMIT 5""",
     why="Inside a run the date grows by 1 and the row number grows by 1, so their difference stays constant; a gap "
         "changes it. That turns 'consecutive' into a plain GROUP BY. Follow-up: replace the final SELECT with "
         "`SELECT COUNT(DISTINCT user_id) FROM streaks WHERE days >= 7`: 384 users.",
     complexity="One window sort per user: O(n log n).",
     mistakes="Using ROW_NUMBER when a user can have two rows on the same day (then dedup first or use DENSE_RANK). "
              "Subtracting a row number from a date string (convert to a day number first). In PostgreSQL: "
              "`activity_date - ROW_NUMBER() OVER (...) * INTERVAL '1 day'`.",
     learn=["sql-gaps-islands", "sql-window-ranking"])

ex.save()
