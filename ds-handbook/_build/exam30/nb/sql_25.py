import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam
from sql_hard_tables import load, put_doc

TT = ("DataLemur TikTok SQL questions (inspiration, own wording and data)",
      "https://datalemur.com/blog/tiktok-sql-interview-questions")

EXTRA = '''# Made-up signup verification tables (tiny on purpose: check the answer by hand).
db.executescript("""
CREATE TABLE tt_signups (user_id INTEGER, signup_time TEXT, country TEXT);
INSERT INTO tt_signups VALUES
(1, '2024-05-01 10:00:00', 'US'), (2, '2024-05-01 11:30:00', 'US'), (3, '2024-05-01 23:50:00', 'KR'),
(4, '2024-05-02 08:00:00', 'KR'), (5, '2024-05-02 09:15:00', 'BR'), (6, '2024-05-02 20:00:00', 'US'),
(7, '2024-05-03 07:45:00', 'KR'), (8, '2024-05-03 12:00:00', 'BR'), (9, '2024-05-03 18:30:00', 'US'),
(10, '2024-05-04 06:10:00', 'KR');
CREATE TABLE tt_texts (text_id INTEGER, user_id INTEGER, sent_at TEXT, status TEXT);
INSERT INTO tt_texts VALUES
(101, 1, '2024-05-01 10:00:05', 'confirmed'),
(102, 2, '2024-05-01 11:30:04', 'not_confirmed'), (103, 2, '2024-05-01 15:00:00', 'confirmed'),
(104, 3, '2024-05-01 23:50:03', 'not_confirmed'), (105, 3, '2024-05-02 23:00:00', 'confirmed'),
(106, 4, '2024-05-02 08:00:02', 'not_confirmed'), (107, 4, '2024-05-03 09:00:00', 'confirmed'),
(108, 5, '2024-05-02 09:15:03', 'confirmed'), (109, 5, '2024-05-02 09:20:00', 'confirmed'),
(110, 7, '2024-05-03 07:45:02', 'not_confirmed'), (115, 7, '2024-05-03 20:00:00', 'confirmed'),
(111, 8, '2024-05-03 12:00:03', 'confirmed'),
(112, 9, '2024-05-03 18:30:02', 'not_confirmed'), (113, 9, '2024-05-05 10:00:00', 'confirmed'),
(114, 10, '2024-05-04 06:10:01', 'confirmed');
""")'''

SMALL = """**Made-up signup tables (tiny):** `tt_signups` (`user_id`, `signup_time`, `country`): one row per new account.
`tt_texts` (`text_id`, `user_id`, `sent_at`, `status` = confirmed / not_confirmed): one row per verification SMS; a
user can get several texts, and `sent_at` of a confirmed text is the moment the user confirmed."""

INTRO = ("**Company style: TikTok.** Short-video data: watch time, completion, sessions, follows, activation. TikTok "
         "SQL rounds are usually 2 to 3 queries in 30 to 45 minutes with follow-up questions on the metric definition, "
         "so say your definition out loud before you write the query.")

ex = Exam(25, "sql", intro=INTRO)
code, doc = load("tiktok", extra=EXTRA)
ex.setup(code, data=True)
put_doc(ex, doc, SMALL)

ex.q("Activation within 24 hours", minutes=6, kind="sql", source=TT,
     prompt="""A new account is **activated** if the user confirms a verification text within 24 hours of
`signup_time` (any of their texts counts). Return the activation rate per `country` and one extra row with country
'ALL' for the total: `country`, `signups`, `activated`, `pct` (1 decimal). Country rows first (highest pct first),
then 'ALL'.

Edge cases in the data: a user who got two texts and confirmed the second; a user who confirmed twice; a user who never
got a text; a user who confirmed 23 hours later but on the next calendar day.

*Follow-up:* product wants "confirmed on the day after signup" instead. What changes, and why is that metric worse?""",
     hint1="Signal: an activation rate where users can have 0, 1 or many texts. Pattern: ratio with LEFT JOIN + "
           "COUNT(DISTINCT CASE ...), and UNION ALL for the total row.",
     hint2="1. `tt_signups s LEFT JOIN tt_texts t ON t.user_id = s.user_id`.\n"
           "2. activated = `COUNT(DISTINCT CASE WHEN t.status = 'confirmed' AND t.sent_at <= datetime(s.signup_time, '+24 hours') THEN s.user_id END)`.\n"
           "3. Put the per-country query and an 'ALL' query (no GROUP BY) in a CTE with UNION ALL; sort with a CASE.",
     solution="""WITH j AS (
  SELECT s.user_id, s.country,
    CASE WHEN t.status = 'confirmed'
          AND t.sent_at <= datetime(s.signup_time, '+24 hours') THEN s.user_id END AS ok_user
  FROM tt_signups s
  LEFT JOIN tt_texts t ON t.user_id = s.user_id
), rates AS (
  SELECT country, COUNT(DISTINCT user_id) AS signups, COUNT(DISTINCT ok_user) AS activated
  FROM j GROUP BY country
  UNION ALL
  SELECT 'ALL', COUNT(DISTINCT user_id), COUNT(DISTINCT ok_user) FROM j
)
SELECT country, signups, activated,
  ROUND(100.0 * activated / signups, 1) AS pct
FROM rates
ORDER BY CASE WHEN country = 'ALL' THEN 1 ELSE 0 END, pct DESC""",
     why="The LEFT JOIN keeps user 6 (no text) in the denominator; COUNT(DISTINCT ...) counts user 5 (two "
         "confirmations) and user 2 (two texts) once; the 24 hour test on timestamps accepts user 3 (23 h 10 min, next "
         "calendar day) and rejects user 4 (25 h) and user 9 (about 40 h). Result: BR 100.0, KR 75.0, US 50.0, ALL "
         "70.0. Follow-up: a calendar-day definition depends on the signup hour (a 23:50 signup has 10 minutes on day "
         "0) and on the time zone, so it is unfair across users; a fixed 24 hour window is the same for everyone.",
     complexity="One join and two small aggregations.",
     mistakes="Inner join (user 6 disappears: rate too high). Counting texts instead of users. `date(sent_at) = "
              "date(signup_time)` (rejects user 3). PostgreSQL: `t.sent_at <= s.signup_time + interval '24 hours'`.",
     learn=["sql-ratios", "sql-left-join-nulls", "sql-dates"])

ex.q("Most watched-through creators per category", minutes=6, kind="sql", source=TT,
     prompt="""Completion of one view = `watch_s / duration_s`, **capped at 1** (a looping video can be watched longer
than it lasts). A creator's completion rate is the average over all views of all their videos. Among creators with at
least 200 views, return the **top 2 per category** (the creator's category in `tt_creators`): `category`,
`creator_id`, `views`, `pct` (completion in %, 1 decimal), ordered by category then rank.

Example: a 30 s video watched 45 s (a loop) counts as 1.0, not 1.5.

*Follow-up:* why cap at 1 instead of using raw watch time?""",
     hint1="Signal: average of a per-row ratio, then 'top 2 per group'. Pattern: ratios (cap with MIN(x, 1.0) or CASE) "
           "plus top-N per group with RANK / ROW_NUMBER.",
     hint2="1. Per view: `MIN(1.0 * watch_s / duration_s, 1.0)` (scalar MIN in SQLite; LEAST in PostgreSQL).\n"
           "2. GROUP BY creator with HAVING COUNT(*) >= 200.\n3. `RANK() OVER (PARTITION BY category ORDER BY avg DESC)`; keep <= 2.",
     solution="""WITH v AS (
  SELECT vd.creator_id,
    CASE WHEN w.watch_s >= vd.duration_s THEN 1.0
         ELSE 1.0 * w.watch_s / vd.duration_s END AS completion
  FROM tt_views w
  JOIN tt_videos vd ON vd.video_id = w.video_id
), c AS (
  SELECT cr.category, v.creator_id, COUNT(*) AS views, AVG(v.completion) AS avg_completion
  FROM v JOIN tt_creators cr ON cr.creator_id = v.creator_id
  GROUP BY cr.category, v.creator_id
  HAVING COUNT(*) >= 200
), r AS (
  SELECT *, RANK() OVER (PARTITION BY category ORDER BY avg_completion DESC) AS rk
  FROM c
)
SELECT category, creator_id, views, ROUND(100 * avg_completion, 1) AS pct
FROM r
WHERE rk <= 2
ORDER BY category, rk""",
     why="Capping happens per view BEFORE averaging. The CASE form works in every dialect. The HAVING filter runs "
         "before ranking, so a creator with 20 perfect views cannot win. Comedy creator 25 leads overall with 69.5%. "
         "Follow-up: without the cap 8% of views (the loops) count up to 3 times; the average becomes 72.1% instead "
         "of 63.2%, and creators of short looping videos win by construction. Watch time is a separate metric (total "
         "attention); completion should measure 'did people finish it'.",
     complexity="One join, one aggregation, one window over 40 creators.",
     mistakes="AVG(watch_s) / AVG(duration_s) (a ratio of averages, a different metric). Ranking before the 200 view "
              "filter. Integer division (`watch_s / duration_s` is 0 for most views).",
     learn=["sql-ratios", "sql-top-n"])

ex.q("Viewing sessions", minutes=8, kind="sql", source=TT,
     prompt="""A viewer's views belong to the same **session** until there is a break of more than 30 minutes between the
END of one view (`view_time + watch_s` seconds) and the START of the next. Return one row: `sessions`, `viewers`,
`per_viewer` (sessions per viewer), `avg_videos` (videos per session), `avg_min` (session length in minutes, from
first start to last end), all with 2 decimals (avg_min with 1), plus `max_videos`.

Example: views at 20:00 (60 s), 20:05 (30 s), 21:10 (10 s): the gap 20:05:30 to 21:10 is 64.5 minutes, so 2 sessions.

*Follow-up:* the events arrive as a stream. How would the job that builds sessions work?""",
     hint1="Signal: 'a break of more than N minutes starts a new one'. Pattern: sessionization = gaps and islands with "
           "LAG (flag a new session) plus a running SUM of the flags (session number).",
     hint2="1. `LAG(datetime(view_time, '+' || watch_s || ' seconds'))` per viewer = end of the previous view.\n"
           "2. new_session = 1 if no previous view or the gap > 30 minutes.\n"
           "3. `SUM(new_session) OVER (PARTITION BY viewer_id ORDER BY view_time ROWS UNBOUNDED PRECEDING)` = session id.\n"
           "4. GROUP BY viewer, session; then one summary row.",
     solution="""WITH v AS (
  SELECT viewer_id, view_id, view_time, watch_s,
    datetime(view_time, '+' || watch_s || ' seconds') AS end_time,
    LAG(datetime(view_time, '+' || watch_s || ' seconds'))
      OVER (PARTITION BY viewer_id ORDER BY view_time, view_id) AS prev_end
  FROM tt_views
), flagged AS (
  SELECT *,
    CASE WHEN prev_end IS NULL
           OR (julianday(view_time) - julianday(prev_end)) * 1440 > 30 THEN 1 ELSE 0 END AS new_session
  FROM v
), numbered AS (
  SELECT *,
    SUM(new_session) OVER (PARTITION BY viewer_id ORDER BY view_time, view_id
                           ROWS UNBOUNDED PRECEDING) AS session_id
  FROM flagged
), sessions AS (
  SELECT viewer_id, session_id, COUNT(*) AS videos,
    (julianday(MAX(end_time)) - julianday(MIN(view_time))) * 1440 AS minutes
  FROM numbered
  GROUP BY viewer_id, session_id
)
SELECT COUNT(*) AS sessions,
  COUNT(DISTINCT viewer_id) AS viewers,
  ROUND(1.0 * COUNT(*) / COUNT(DISTINCT viewer_id), 2) AS per_viewer,
  ROUND(AVG(videos), 2) AS avg_videos,
  ROUND(AVG(minutes), 1) AS avg_min,
  MAX(videos) AS max_videos
FROM sessions""",
     why="The gap is measured from the END of the previous view, otherwise one long video would split a session. The "
         "flag-then-running-sum trick turns 'new session starts here' into a session number that GROUP BY can use. "
         "4,843 sessions from 1,183 viewers, about 7 videos and 6.3 minutes each. Follow-up: in streaming, keep per "
         "viewer state (last end time, current session id); close a session when 30 minutes pass with no event "
         "(a timer / watermark), and handle late events by re-opening within an allowed lateness.",
     complexity="One sort per viewer for LAG and the running sum: O(n log n).",
     mistakes="Gap from the previous START. `ORDER BY view_time` alone when two views share a timestamp (add view_id "
              "for a stable order). Default window frame RANGE in the running sum (ties get the same total). "
              "PostgreSQL: `view_time + watch_s * interval '1 second'`.",
     learn=["sql-gaps-islands", "sql-running-totals", "sql-lag-lead"])

ex.q("Do new viewers come back?", minutes=6, kind="sql", review=True,
     prompt="""A viewer's day 0 is the date of their first view. Group viewers by the **week** (Monday start) of day 0.
For each cohort week return `viewers`, `d1_pct` (viewed on day 1) and `w1_pct` (viewed on ANY day from day 1 to day 7),
1 decimal. Data ends on 2024-05-31, so keep only viewers whose day 7 is inside the data (day 0 on or before 2024-05-24).

*Follow-up:* `w1_pct` is about 5 times `d1_pct`. Which one would you put in a weekly business review, and why?""",
     hint1="Signal: 'cohort', 'came back on day N / within N days'. Pattern: retention: first date per user, join "
           "activity, MAX(CASE ...) per user as 0/1 flags, then AVG per cohort.",
     hint2="1. `first`: MIN(date(view_time)) per viewer.\n2. Join all views; per viewer: "
           "`MAX(CASE WHEN date(view_time) = date(d0, '+1 day') THEN 1 ELSE 0 END)` and the same with BETWEEN +1 and +7 days.\n"
           "3. Filter `d0 <= '2024-05-24'`; group by `date(d0, 'weekday 0', '-6 days')`.",
     solution="""WITH first AS (
  SELECT viewer_id, MIN(date(view_time)) AS d0
  FROM tt_views GROUP BY viewer_id
), flags AS (
  SELECT f.viewer_id, f.d0,
    date(f.d0, 'weekday 0', '-6 days') AS cohort_week,
    MAX(CASE WHEN date(v.view_time) = date(f.d0, '+1 day') THEN 1 ELSE 0 END) AS d1,
    MAX(CASE WHEN date(v.view_time) BETWEEN date(f.d0, '+1 day') AND date(f.d0, '+7 days')
             THEN 1 ELSE 0 END) AS w1
  FROM first f
  JOIN tt_views v ON v.viewer_id = f.viewer_id
  WHERE f.d0 <= '2024-05-24'
  GROUP BY f.viewer_id, f.d0
)
SELECT cohort_week, COUNT(*) AS viewers,
  ROUND(100.0 * AVG(d1), 1) AS d1_pct,
  ROUND(100.0 * AVG(w1), 1) AS w1_pct
FROM flags
GROUP BY cohort_week
ORDER BY cohort_week""",
     why="One row per viewer with 0/1 flags makes AVG a rate and avoids double counting viewers with many views. The "
         "observability filter removes viewers whose 7 day window is cut by the end of the data (they would look "
         "churned). The first cohort is the week of 2024-04-29 (May 1 is a Wednesday). Follow-up: w1 (about 60% to "
         "66%) is stable and less sensitive to the weekday of day 0, so it is better for a weekly review; d1 (8% to "
         "16%) is noisy but reacts faster, so it is a good early warning in experiments.",
     complexity="One join of views to first dates and one GROUP BY per viewer.",
     mistakes="Counting day 0 as a return. Keeping recent cohorts with incomplete windows. COUNT(*) after the join "
              "(counts views, not viewers).",
     learn=["sql-retention", "sql-dates"])

ex.q("Creators who turn viewers into followers", minutes=6, kind="sql", review=True, source=TT,
     prompt="""Follow rate of a creator = follows received / **distinct** viewers of their videos. For creators with at
least 100 distinct viewers, return `category`, `creator_id`, `viewers`, `follows`, `pct` (follow rate in %, 2
decimals), `cat_avg` (the average follow rate of qualifying creators in the same category, %, 2 decimals) and `idx` =
creator rate / category average (2 decimals). Show the top 5 by `idx`.

*Follow-up:* why compare with the category average instead of ranking raw follow rates?""",
     hint1="Signal: a rate per creator compared with its group. Pattern: ratios, pre-aggregated per creator, then a "
           "window AVG OVER (PARTITION BY category).",
     hint2="1. `uv`: COUNT(DISTINCT viewer_id) per creator (views join videos).\n2. `f`: follows per creator.\n"
           "3. LEFT JOIN f (creators with 0 follows), HAVING / WHERE viewers >= 100.\n"
           "4. `AVG(rate) OVER (PARTITION BY category)` and rate / that.",
     solution="""WITH uv AS (
  SELECT vd.creator_id, COUNT(DISTINCT w.viewer_id) AS viewers
  FROM tt_views w JOIN tt_videos vd ON vd.video_id = w.video_id
  GROUP BY vd.creator_id
), f AS (
  SELECT creator_id, COUNT(*) AS follows FROM tt_follows GROUP BY creator_id
), x AS (
  SELECT c.category, uv.creator_id, uv.viewers, COALESCE(f.follows, 0) AS follows,
    1.0 * COALESCE(f.follows, 0) / uv.viewers AS rate
  FROM uv
  JOIN tt_creators c ON c.creator_id = uv.creator_id
  LEFT JOIN f ON f.creator_id = uv.creator_id
  WHERE uv.viewers >= 100
)
SELECT category, creator_id, viewers, follows,
  ROUND(100 * rate, 2) AS pct,
  ROUND(100 * AVG(rate) OVER (PARTITION BY category), 2) AS cat_avg,
  ROUND(rate / AVG(rate) OVER (PARTITION BY category), 2) AS idx
FROM x
ORDER BY idx DESC
LIMIT 5""",
     why="Views and follows are aggregated separately and then joined (joining raw views to raw follows would multiply "
         "rows). The window AVG keeps every creator row while adding the category benchmark. Food creator 16 converts "
         "7.96% of viewers, 2.57 times the food average. Follow-up: categories have different natural follow rates "
         "(food 3.10% versus education 2.03% on average), so raw ranking mostly ranks categories; the index finds "
         "creators who beat their peers.",
     complexity="Two aggregations and one window over about 40 rows.",
     mistakes="Denominator = views (a viewer who watches 20 videos counts 20 times). Joining views to follows before "
              "aggregating. Average of the category computed before the 100 viewer filter (a different benchmark; say which you use).",
     learn=["sql-ratios", "sql-window-ranking"])

ex.save()
