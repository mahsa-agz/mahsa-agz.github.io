import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
from sql_mid_data import build_setup

ex = Exam(20, "sql")
build_setup(ex, "app", "ab", "gplay")

# ---------------------------------------------------------------- Q1 exact duplicates
ex.q("Retries in the event pipeline", minutes=5, kind="sql",
     prompt="""Shopping app. `app_events_raw` is the event log as received from the phones. When the network
fails, the app **retries** and the same event arrives twice: same `user_id`, `event_time` and `event_name`, but a new
`raw_id` and a later `received_at`.

Return one summary row: `raw_rows`, `unique_events` (keep one row per user, time and event name: the one received
first), `copies_removed`, `events_with_copies` and `max_copies` (most rows for one event).

Example: rows (7, 10:00:00, view_item, received 10:00:05) and (7, 10:00:00, view_item, received 10:03:00) are one
event; keep the first.""",
     hint1="Signal: \"same business key, several rows, keep one\". Pattern: ROW_NUMBER over `PARTITION BY` the "
           "business key, ordered by the tie rule; keep rn = 1.",
     hint2="1. `ROW_NUMBER() OVER (PARTITION BY user_id, event_time, event_name ORDER BY received_at, raw_id) AS rn`.\n"
           "2. `COUNT(*) OVER (same partition) AS copies`.\n3. Summarise with conditional sums: rn = 1, rn > 1, "
           "rn = 1 AND copies > 1.",
     solution="""WITH ranked AS (
    SELECT raw_id, user_id, event_time, event_name, received_at,
           ROW_NUMBER() OVER (PARTITION BY user_id, event_time, event_name
                              ORDER BY received_at, raw_id) AS rn,
           COUNT(*)     OVER (PARTITION BY user_id, event_time, event_name) AS copies
    FROM app_events_raw
)
SELECT COUNT(*)                                           AS raw_rows,
       SUM(CASE WHEN rn = 1 THEN 1 ELSE 0 END)            AS unique_events,
       SUM(CASE WHEN rn > 1 THEN 1 ELSE 0 END)            AS copies_removed,
       SUM(CASE WHEN rn = 1 AND copies > 1 THEN 1 ELSE 0 END) AS events_with_copies,
       MAX(copies)                                        AS max_copies
FROM ranked""",
     why="ROW_NUMBER keeps exactly one row per key and lets you choose which (first received, then lowest raw_id "
         "as a final tie breaker); `SELECT DISTINCT` would also work here, but only when every column is "
         "identical, and it cannot choose between rows that differ in a non-key column such as received_at. "
         "795 of 20,082 rows are retries. Always say the business key out loud: here it is (user, time, event), "
         "not raw_id, which is unique by construction. PostgreSQL also has `DISTINCT ON (key) ... ORDER BY key, "
         "received_at`.",
     complexity="One window sort over 20,082 rows.",
     mistakes="Partitioning by raw_id (nothing is a duplicate). `GROUP BY` the key with `MIN(received_at)` and then "
              "losing the other columns. No tie breaker, so the kept row changes between runs.",
     learn=["sql-dedup-cleaning", "sql-window-ranking"])

# ---------------------------------------------------------------- Q2 near duplicates (double taps)
ex.q("Double taps", minutes=7, kind="sql",
     prompt="""After removing the retries from Q1, some events are still doubled: a user taps twice and the app logs
the **same `event_name`** for the **same user** again **1 to 3 seconds** later. Drop every event that comes at most
**3 seconds** after the previous kept-or-not event of the same user and event name.

Return `after_exact` (rows after Q1), `after_double_taps` and `reference_clean_table` (row count of the clean table
`app_events`, which should match if your cleaning is right).

Example: view_item at 10:00:00 and 10:00:02 by user 7: keep 10:00:00 only. A view_item at 10:00:30 stays.

Follow-up: why is `(julianday(t2) - julianday(t1)) * 86400 > 3` risky for this test?""",
     hint1="Signal: duplicates defined by \"close in time\", not by equal keys. Pattern: LAG per (user, event_name) "
           "ordered by time, drop rows whose gap is at most 3 seconds. It is the same gap logic as sessionization "
           "(day 19).",
     hint2="1. CTE exact: Q1's ROW_NUMBER, keep rn = 1.\n2. CTE lagged: `LAG(event_time) OVER (PARTITION BY "
           "user_id, event_name ORDER BY event_time, raw_id)`.\n3. Keep rows where prev is NULL or the gap in whole "
           "seconds > 3: `strftime('%s', event_time) - strftime('%s', prev_time)`.",
     solution="""WITH exact AS (
    SELECT raw_id, user_id, event_time, event_name,
           ROW_NUMBER() OVER (PARTITION BY user_id, event_time, event_name
                              ORDER BY received_at, raw_id) AS rn
    FROM app_events_raw
), lagged AS (
    SELECT raw_id, user_id, event_time, event_name,
           LAG(event_time) OVER (PARTITION BY user_id, event_name ORDER BY event_time, raw_id) AS prev_time
    FROM exact
    WHERE rn = 1
), clean AS (
    SELECT *
    FROM lagged
    WHERE prev_time IS NULL
       OR strftime('%s', event_time) - strftime('%s', prev_time) > 3
)
SELECT (SELECT COUNT(*) FROM exact WHERE rn = 1) AS after_exact,
       COUNT(*)                                  AS after_double_taps,
       (SELECT COUNT(*) FROM app_events)         AS reference_clean_table
FROM clean""",
     why="Cleaning in two passes: exact copies first (cheap and safe), then near copies with a rule you can explain "
         "(same user, same event, at most 3 s apart). The result matches the clean table exactly (19,094 rows), "
         "which is the check you would run in an exam if a reference exists, or by sampling rows by hand if "
         "not. Follow-up: julianday is a floating-point day number, so a gap of exactly 3 seconds can come out as "
         "3.0000001 and pass `> 3`. On this data that version keeps 29 double taps. Compare integer seconds "
         "(`strftime('%s', ...)`), or in PostgreSQL `EXTRACT(EPOCH FROM t2 - t1)` on real timestamps. Note: "
         "comparing with the previous raw event (not the previous kept one) means a burst of taps 2 s apart for "
         "10 s collapses to one event; say which rule you chose.",
     complexity="Two window sorts over about 20k rows.",
     mistakes="Partitioning only by user (a view followed by a cart 2 s later is not a duplicate). Floating-point "
              "seconds. Doing the near-duplicate pass before the exact pass (works, but harder to reason about).",
     learn=["sql-dedup-cleaning", "sql-lag-lead", "sql-gaps-islands"])

# ---------------------------------------------------------------- Q3 dedup a real experiment log
ex.q("One row per user in the experiment", minutes=6, kind="sql",
     prompt="""`ab_data` (real) has 294,478 rows but fewer users: some users appear twice. Clean it in this order:
1. drop rows where group and page disagree (`(grp = 'treatment') <> (landing_page = 'new_page')`);
2. keep each user's **first** remaining row by `timestamp`.

Per `grp` return `users`, `conversions` and `conv_pct` (3 decimals).

Example: a user with rows (treatment, new_page, 09:00, converted 0) and (treatment, new_page, 11:00, converted 1)
keeps the 09:00 row: their exposure starts at the first visit.

Follow-up: why first visit and not "converted if any row converted"?""",
     hint1="Pattern: filter, then ROW_NUMBER per user ordered by time, keep rn = 1, then aggregate.",
     hint2="1. CTE: `ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY timestamp)` over the consistent rows.\n"
           "2. Outer: WHERE rn = 1, group by grp: COUNT(*), SUM(converted), AVG(converted).",
     solution="""WITH clean AS (
    SELECT user_id, timestamp, grp, converted,
           ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY timestamp) AS rn
    FROM ab_data
    WHERE (grp = 'treatment') = (landing_page = 'new_page')
)
SELECT grp,
       COUNT(*) AS users,
       SUM(converted) AS conversions,
       ROUND(100.0 * AVG(converted), 3) AS conv_pct
FROM clean
WHERE rn = 1
GROUP BY grp""",
     why="The order matters: dedup after removing inconsistent rows, otherwise a user's first row could be a bad "
         "one and the user would disappear. The text timestamp ('2017-01-21 22:11:48.556739') sorts correctly as "
         "text because it is zero padded. Result: 145,274 control and 145,310 treatment users, 12.039% versus "
         "11.881%. Follow-up: the experiment unit is the user and the metric should be defined once per user; "
         "\"any row converted\" is also a valid per-user metric, but it gives users with two visits two chances, "
         "and two visits can be a consequence of the treatment. Decide the rule before looking at the results.",
     complexity="One window sort over about 290k rows.",
     mistakes="Deduplicating before removing mismatches. `GROUP BY user_id` with `MAX(converted)` without "
              "thinking about the definition. Ordering by user_id instead of timestamp inside the partition.",
     learn=["sql-dedup-cleaning", "stats-ab-pitfalls"])

# ---------------------------------------------------------------- Q4 messy real listing data
ex.q("The same app listed many times", minutes=7, kind="sql",
     prompt="""`play_apps` (real scrape of Google Play) lists some apps several times (scraped at different moments,
sometimes under two categories), and `reviews` is **text**. Clean it:
1. keep only rows whose `reviews` is made of digits only (one shifted row has '3.0M');
2. keep **one row per app**: the one with the most reviews (as an integer); ties: the row that comes first in the
   table (`rowid`).

Return `raw_rows`, `bad_reviews_rows`, `distinct_apps`, `clean_rows`, and `dup_apps` (apps that had more than one
valid row).

Example: '8 Ball Pool' appears 7 times with reviews from 14,184,910 to 14,201,891; keep the 14,201,891 row.""",
     hint1="Pattern: validate the type first (GLOB for digits), then ROW_NUMBER per app ordered by the integer value "
           "DESC, keep rn = 1.",
     hint2="1. CTE typed: `WHERE reviews GLOB '[0-9]*' AND reviews NOT GLOB '*[^0-9]*'`, "
           "`CAST(reviews AS INTEGER)`.\n2. CTE dedup: `ROW_NUMBER() OVER (PARTITION BY app ORDER BY reviews DESC, "
           "rid)` and `COUNT(*) OVER (PARTITION BY app)`.\n3. One summary SELECT with scalar subqueries or "
           "conditional sums.",
     solution="""WITH typed AS (
    SELECT rowid AS rid, app, category, CAST(reviews AS INTEGER) AS reviews
    FROM play_apps
    WHERE reviews GLOB '[0-9]*' AND reviews NOT GLOB '*[^0-9]*'
), dedup AS (
    SELECT rid, app, category, reviews,
           ROW_NUMBER() OVER (PARTITION BY app ORDER BY reviews DESC, rid) AS rn,
           COUNT(*)     OVER (PARTITION BY app)                            AS n_rows
    FROM typed
)
SELECT (SELECT COUNT(*) FROM play_apps)                AS raw_rows,
       (SELECT COUNT(*) FROM play_apps) - (SELECT COUNT(*) FROM typed) AS bad_reviews_rows,
       (SELECT COUNT(DISTINCT app) FROM play_apps)     AS distinct_apps,
       SUM(CASE WHEN rn = 1 THEN 1 ELSE 0 END)         AS clean_rows,
       SUM(CASE WHEN rn = 1 AND n_rows > 1 THEN 1 ELSE 0 END) AS dup_apps
FROM dedup""",
     why="Type validation comes first: `CAST('3.0M' AS INTEGER)` silently returns 3 in SQLite (PostgreSQL would "
         "raise an error), so a bad row could win or lose a ranking for the wrong reason. The two GLOBs mean "
         "\"starts with a digit and contains no non-digit\". Then ROW_NUMBER per app keeps the most recent-looking "
         "snapshot (most reviews). More than a thousand rows are duplicates. Keeping one row per app on the app "
         "name alone also merges listings that sit in two categories; if category matters, decide which one wins "
         "and say it. PostgreSQL: `reviews ~ '^[0-9]+$'`.",
     complexity="One window sort over about 10.8k rows.",
     mistakes="CAST without validation. `SELECT DISTINCT *` (rows differ in reviews, so nothing is removed). "
              "Keeping the first row instead of the most complete one.",
     learn=["sql-dedup-cleaning", "sql-window-ranking"])

# ---------------------------------------------------------------- Q5 review: top-n on the cleaned data
ex.q("Top apps per category after cleaning", minutes=5, kind="sql", review=True,
     prompt="""Using the cleaning rules of Q4 (digits-only reviews, one row per app with the most reviews), return
the **3 apps with the most reviews** in each of the categories `GAME`, `SOCIAL` and `COMMUNICATION` (ties share a
rank). Return `category`, `rank_in_cat`, `app`, `reviews`.

Why must the dedup happen before the ranking?""",
     hint1="Pattern: dedup CTE (Q4), then DENSE_RANK per category, filter rank <= 3.",
     hint2="1. Reuse typed and dedup CTEs, keep rn = 1.\n2. `DENSE_RANK() OVER (PARTITION BY category ORDER BY "
           "reviews DESC)`.\n3. Filter the three categories and rank <= 3 in an outer query.",
     solution="""WITH typed AS (
    SELECT rowid AS rid, app, category, CAST(reviews AS INTEGER) AS reviews
    FROM play_apps
    WHERE reviews GLOB '[0-9]*' AND reviews NOT GLOB '*[^0-9]*'
), dedup AS (
    SELECT rid, app, category, reviews,
           ROW_NUMBER() OVER (PARTITION BY app ORDER BY reviews DESC, rid) AS rn
    FROM typed
), ranked AS (
    SELECT category, app, reviews,
           DENSE_RANK() OVER (PARTITION BY category ORDER BY reviews DESC) AS rank_in_cat
    FROM dedup
    WHERE rn = 1 AND category IN ('GAME', 'SOCIAL', 'COMMUNICATION')
)
SELECT category, rank_in_cat, app, reviews
FROM ranked
WHERE rank_in_cat <= 3
ORDER BY category, rank_in_cat, app""",
     why="Without the dedup, an app listed 4 times would take several of the top 3 places in its category "
         "(Clash of Clans or Subway Surfers several times). Dedup first, rank second, filter last. The WHERE on "
         "category runs before the window, which is fine here because the ranking is per category anyway. "
         "Facebook leads SOCIAL, WhatsApp leads COMMUNICATION and Clash of Clans leads GAME.",
     complexity="Two window sorts over about 10.8k rows.",
     mistakes="Ranking raw rows. Ranking the text column (as text, '9' > '10'). Using ROW_NUMBER for \"ties share a "
              "rank\".",
     learn=["sql-top-n", "sql-dedup-cleaning"])

ex.save()
