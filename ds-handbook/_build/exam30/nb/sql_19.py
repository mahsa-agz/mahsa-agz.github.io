import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
from sql_mid_data import build_setup

ex = Exam(19, "sql")
build_setup(ex, "app", "movielens")

STREAK_CTE = """WITH grp AS (
    SELECT user_id, activity_date,
           julianday(activity_date)
             - ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY activity_date) AS island
    FROM daily_activity
), streaks AS (
    SELECT user_id, MIN(activity_date) AS start_date, MAX(activity_date) AS end_date, COUNT(*) AS days
    FROM grp
    GROUP BY user_id, island
)"""

# ---------------------------------------------------------------- Q1 longest streak
ex.q("The most loyal users", minutes=7, kind="sql",
     prompt="""Shopping app (made up). A **streak** is a run of consecutive calendar days on which a user has a
`daily_activity` row. For every user find their **longest streak** (ties: the earliest one). Return the **5 users**
with the longest streaks: `user_id`, `start_date`, `end_date`, `longest_streak` (days), longest first, then user_id.

Example: active on Jan 3, 4, 5, 7, 8 gives streaks of 3 (Jan 3 to 5) and 2 (Jan 7 to 8); the longest is 3.

Follow-up: what if a user can have two rows on the same day?""",
     hint1="Signal: \"consecutive days\" = gaps and islands. Pattern: date minus ROW_NUMBER is constant inside a run "
           "of consecutive dates; group by that difference.",
     hint2="1. CTE grp: `julianday(activity_date) - ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY activity_date)`.\n"
           "2. CTE streaks: group by user and that value: MIN, MAX, COUNT.\n"
           "3. ROW_NUMBER per user by days DESC, start_date; keep 1; order and LIMIT 5.",
     solution=STREAK_CTE + """, ranked AS (
    SELECT user_id, start_date, end_date, days,
           ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY days DESC, start_date) AS rn
    FROM streaks
)
SELECT user_id, start_date, end_date, days AS longest_streak
FROM ranked
WHERE rn = 1
ORDER BY longest_streak DESC, user_id
LIMIT 5""",
     why="Within a run of consecutive dates, both the date and the row number go up by 1 each row, so their "
         "difference stays the same; a gap in dates increases the difference and starts a new island. Example: "
         "Jan 3, 4, 5, 7, 8 with row numbers 1 to 5 give differences Jan 2, Jan 2, Jan 2, Jan 3, Jan 3. The top "
         "user was active 62 days in a row. Follow-up: duplicates per day break the trick (the row number grows "
         "but the date does not). Deduplicate first (`SELECT DISTINCT user_id, activity_date`) or use DENSE_RANK "
         "instead of ROW_NUMBER. PostgreSQL: `activity_date - ROW_NUMBER() OVER (...)::int` gives a date.",
     complexity="One window sort per user, then two group bys; linear after sorting.",
     mistakes="Partitioning ROW_NUMBER by something other than the user. Forgetting duplicates per day. Using "
              "LAG(date) = date - 1 alone (finds the joints, but you still need a running sum to label the runs).",
     learn=["sql-gaps-islands", "sql-window-ranking"])

# ---------------------------------------------------------------- Q2 current streak
ex.q("Who is on a streak right now?", minutes=6, kind="sql",
     prompt="""Shopping app. The **current streak** of a user is the streak that includes the **last date in the
data** (2024-03-31; do not hard-code it). Per `platform` return `active_on_last_day`, `streak_7plus` (users whose
current streak is at least 7 days), `avg_current_streak` (1 decimal) and `max_current`.

Example: a user active Mar 29, 30, 31 has a current streak of 3; a user last active on Mar 30 has none.""",
     hint1="Pattern: same islands as Q1, then keep only the island whose end date equals the overall last date.",
     hint2="1. Reuse the grp / streaks CTEs.\n2. `WHERE end_date = (SELECT MAX(activity_date) FROM daily_activity)`.\n"
           "3. Join app_users for platform; conditional SUM for 7+.",
     solution=STREAK_CTE + """
SELECT u.platform,
       COUNT(*)                                     AS active_on_last_day,
       SUM(CASE WHEN s.days >= 7 THEN 1 ELSE 0 END) AS streak_7plus,
       ROUND(AVG(s.days), 1)                        AS avg_current_streak,
       MAX(s.days)                                  AS max_current
FROM streaks s
JOIN app_users u ON u.user_id = s.user_id
WHERE s.end_date = (SELECT MAX(activity_date) FROM daily_activity)
GROUP BY u.platform
ORDER BY u.platform""",
     why="Each user has at most one island that ends on the last date, so the filter returns one row per user active "
         "that day (115 users, the DAU of March 31). A scalar subquery for the last date keeps the query correct "
         "when new data arrives. Web has only 11 users here, so its average (11.0) is driven by one long streak: "
         "always show the count next to an average.",
     complexity="Same as Q1 plus a small join.",
     mistakes="Hard-coding the date. Using `end_date >= today - 1` and counting users whose streak just broke. "
              "Reporting the web average without its tiny base.",
     learn=["sql-gaps-islands", "sql-subqueries"])

# ---------------------------------------------------------------- Q3 sessionization (MovieLens)
ex.q("Rating sessions", minutes=8, kind="sql",
     prompt="""MovieLens (real). A **rating session** of a user is a run of ratings where each rating comes at most
**30 minutes** after the previous one of the same user; a longer gap (or the first rating) starts a new session.

Return one summary row: `users`, `sessions`, `avg_ratings_per_session` (1 decimal), `single_rating_sessions` and
`biggest_session` (most ratings in one session).

Example: a user rates at 10:00, 10:10, 10:50, 10:55: two sessions (2 and 2 ratings), because 10:10 to 10:50 is 40
minutes.

Follow-up: `biggest_session` is over 1,000 ratings. Is that a real human session?""",
     hint1="Signal: \"a new group starts when the gap is larger than X\". Pattern: islands by flag + running sum: "
           "LAG to compute the gap, flag 1 when a session starts, cumulative SUM of the flag = session number.",
     hint2="1. CTE r: `new_session = 1` when LAG(rated_at) is NULL or the gap in minutes is > 30 "
           "(`(julianday(a) - julianday(b)) * 24 * 60`).\n"
           "2. CTE s: `SUM(new_session) OVER (PARTITION BY user_id ORDER BY rated_at ROWS UNBOUNDED PRECEDING)`.\n"
           "3. Group by user and session number, then summarise.",
     solution="""WITH r AS (
    SELECT user_id, rated_at,
           CASE WHEN LAG(rated_at) OVER w IS NULL
                  OR (julianday(rated_at) - julianday(LAG(rated_at) OVER w)) * 24 * 60 > 30
                THEN 1 ELSE 0 END AS new_session
    FROM ml_ratings
    WINDOW w AS (PARTITION BY user_id ORDER BY rated_at)
), s AS (
    SELECT user_id, rated_at,
           SUM(new_session) OVER (PARTITION BY user_id ORDER BY rated_at ROWS UNBOUNDED PRECEDING) AS session_no
    FROM r
), per_session AS (
    SELECT user_id, session_no, COUNT(*) AS ratings
    FROM s
    GROUP BY user_id, session_no
)
SELECT COUNT(DISTINCT user_id)                              AS users,
       COUNT(*)                                             AS sessions,
       ROUND(AVG(ratings), 1)                               AS avg_ratings_per_session,
       SUM(CASE WHEN ratings = 1 THEN 1 ELSE 0 END)         AS single_rating_sessions,
       MAX(ratings)                                         AS biggest_session
FROM per_session""",
     why="When the islands are defined by a threshold on gaps (not by consecutive integers), the date minus row "
         "number trick does not work; the flag plus running sum does, and it is the standard sessionization "
         "query. Say `ROWS UNBOUNDED PRECEDING` explicitly: with the default RANGE "
         "frame, rows with the same timestamp share one running sum (harmless here, surprising elsewhere). Follow-up: many MovieLens ratings share the same second (bulk imports "
         "of old ratings when a user joins), so huge \"sessions\" are an artefact of how the data was collected. "
         "In product logs you would also cap session length or split on app background events.",
     complexity="Two window passes per user over 100,836 ratings, then group bys.",
     mistakes="Running SUM without PARTITION BY user (session numbers leak across users). Comparing a gap in "
              "days with 30 (wrong units). Forgetting the first rating of each user: its LAG is NULL, and "
              "`NULL > 30` is not true, so without the IS NULL test it would not start a session.",
     learn=["sql-gaps-islands", "sql-lag-lead", "sql-running-totals"])

# ---------------------------------------------------------------- Q4 review: gaps with LEAD
ex.q("Long breaks and comebacks", minutes=5, kind="sql", review=True,
     prompt="""Shopping app. A **comeback** is a pair of consecutive active days of the same user that are **more
than 14 days apart** (the user was away and came back). Per `platform` return `comebacks`, `users_with_comeback`,
`avg_gap_days` (1 decimal) and `max_gap`.

Example: active on Jan 2, Jan 20, Jan 22 gives one comeback with a gap of 18 days.""",
     hint1="Pattern: gaps (not islands): LEAD gives each active day the next active day of the same user; filter "
           "where the difference is > 14.",
     hint2="1. CTE: `LEAD(activity_date) OVER (PARTITION BY user_id ORDER BY activity_date) AS next_date`.\n"
           "2. Gap = `julianday(next_date) - julianday(activity_date)`; keep > 14; group by platform.",
     solution="""WITH nxt AS (
    SELECT d.user_id, u.platform, d.activity_date,
           LEAD(d.activity_date) OVER (PARTITION BY d.user_id ORDER BY d.activity_date) AS next_date
    FROM daily_activity d
    JOIN app_users u ON u.user_id = d.user_id
)
SELECT platform,
       COUNT(*)                AS comebacks,
       COUNT(DISTINCT user_id) AS users_with_comeback,
       ROUND(AVG(julianday(next_date) - julianday(activity_date)), 1) AS avg_gap_days,
       MAX(julianday(next_date) - julianday(activity_date))           AS max_gap
FROM nxt
WHERE julianday(next_date) - julianday(activity_date) > 14
GROUP BY platform
ORDER BY platform""",
     why="Gaps are the space between islands; LEAD exposes each gap on one row. The last active day of every user "
         "has a NULL next_date, and the WHERE comparison with NULL is not true, so it drops out automatically. "
         "Gaps average about a month. Users who left and never came back are not comebacks; a churn analysis "
         "would look at the gap from the last active day to the end of the data instead.",
     complexity="One window sort over 17,223 rows.",
     mistakes="LAG and LEAD mixed up (both work if used consistently). Forgetting PARTITION BY user. Counting "
              "users instead of gaps when the question asks for comebacks.",
     learn=["sql-lag-lead", "sql-gaps-islands"])

# ---------------------------------------------------------------- Q5 review: ratio on top of islands
ex.q("How much activity comes from streaks?", minutes=5, kind="sql", review=True,
     prompt="""Shopping app. Label each active day with the length of the streak it belongs to. Per `platform` return
`active_days`, `days_in_streak3` (active days that belong to a streak of 3 or more days) and `pct_in_streak3`
(1 decimal).

Example: a user with streaks of 1, 4 and 2 days has 7 active days, 4 of them in a 3+ streak (57.1%).""",
     hint1="Pattern: islands, but instead of collapsing each island to one row, attach its size to every row with "
           "`COUNT(*) OVER (PARTITION BY user_id, island)`; then a conditional ratio.",
     hint2="1. grp CTE as in Q1.\n2. `COUNT(*) OVER (PARTITION BY user_id, island) AS streak_len`.\n"
           "3. Join platform; `SUM(CASE WHEN streak_len >= 3 ...) / COUNT(*)`.",
     solution="""WITH grp AS (
    SELECT user_id, activity_date,
           julianday(activity_date)
             - ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY activity_date) AS island
    FROM daily_activity
), sized AS (
    SELECT user_id, COUNT(*) OVER (PARTITION BY user_id, island) AS streak_len
    FROM grp
)
SELECT u.platform,
       COUNT(*) AS active_days,
       SUM(CASE WHEN s.streak_len >= 3 THEN 1 ELSE 0 END) AS days_in_streak3,
       ROUND(100.0 * SUM(CASE WHEN s.streak_len >= 3 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_in_streak3
FROM sized s
JOIN app_users u ON u.user_id = s.user_id
GROUP BY u.platform
ORDER BY u.platform""",
     why="A window COUNT over the island keeps every day as a row but tells it how big its island is, so the "
         "ratio is over days (the denominator the question asks for). iOS has the most streaky usage (79.5% of "
         "its active days are in 3+ day streaks), web the least (67.1%). Habit-forming products track this kind "
         "of metric (share of usage from habitual users).",
     complexity="Two window passes, one join, one group by.",
     mistakes="Collapsing islands first and then dividing islands by days (mixed units). Computing the ratio "
              "per user and averaging (average of ratios, see day 18).",
     learn=["sql-gaps-islands", "sql-ratios"])

ex.save()
