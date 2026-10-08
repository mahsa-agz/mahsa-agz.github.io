import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam
from sql_hard_tables import load, put_doc

TT = ("DataLemur TikTok SQL questions (inspiration)", "https://datalemur.com/blog/tiktok-sql-interview-questions")
GG = ("DataLemur Google SQL questions (inspiration)", "https://datalemur.com/blog/google-sql-interview-questions")
SS = ("DataLemur Samsung SQL questions (inspiration)", "https://datalemur.com/blog/samsung-sql-interview-questions")

INTRO = """**Mock exam rules (30 minutes, one timer for the whole notebook).**

- This is a company-style round: TikTok, Google and Samsung flavoured questions, mixed. Start one 30 minute timer.
- About 5 minutes a query. Before each query say your metric definition in one sentence (examiners grade that).
- No hints or solutions until the timer rings. Then grade: 1 point correct, 0.5 for right logic with a small slip.
  5 or more is exam ready. Put every miss in the mistake log; day 30 and the redo days bring them back.
- After grading, answer each follow-up out loud in under a minute."""

ex = Exam(28, "sql", intro=INTRO)
code, doc = load("tiktok", "search", "device", "movielens", "retail")
ex.setup(code, data=True)
put_doc(ex, doc)

ex.q("Fastest start per category", minutes=5, kind="sql", review=True, source=TT,
     prompt="""TikTok style. For each video count the views in its **first 24 hours** after `posted_at` (videos with no
views count 0). Return the video with the most first-day views in each category (`tt_videos.category`): `category`,
`video_id`, `creator_id`, `views_24h`, ordered by `views_24h` descending. Ties: show all tied videos.

*Follow-up:* why measure the first 24 hours instead of total views?""",
     hint1="Signal: a time window relative to each row's own start, then top 1 per group. Pattern: LEFT JOIN with the "
           "window in the ON clause, then RANK per category.",
     hint2="1. `tt_videos v LEFT JOIN tt_views w ON w.video_id = v.video_id AND w.view_time < datetime(v.posted_at, '+24 hours')`.\n"
           "2. COUNT(w.view_id) per video.\n3. `RANK() OVER (PARTITION BY category ORDER BY views_24h DESC)`, keep 1.",
     solution="""WITH first_day AS (
  SELECT v.video_id, v.category, v.creator_id, COUNT(w.view_id) AS views_24h
  FROM tt_videos v
  LEFT JOIN tt_views w
    ON w.video_id = v.video_id
   AND w.view_time < datetime(v.posted_at, '+24 hours')
  GROUP BY v.video_id, v.category, v.creator_id
), r AS (
  SELECT *, RANK() OVER (PARTITION BY category ORDER BY views_24h DESC) AS rk
  FROM first_day
)
SELECT category, video_id, creator_id, views_24h
FROM r
WHERE rk = 1
ORDER BY views_24h DESC""",
     why="The window condition belongs in the ON clause: in WHERE it would remove videos without early views. RANK "
         "keeps ties as asked. Food video 1108 by creator 16 gets 397 views on day one. Follow-up: total views favour "
         "old videos (more time to collect views); a fixed window compares videos posted on different days fairly, "
         "and early velocity is what a recommender uses to decide whether to push a video wider.",
     complexity="One join (views filtered per video) and one window over about 300 videos.",
     mistakes="COUNT(*) after a LEFT JOIN (a video with no views counts 1). Window measured from the first VIEW, not the post time.",
     learn=["sql-top-n", "sql-dates"])

ex.q("How much do people click on the top results?", minutes=4, kind="sql", source=GG,
     prompt="""Google style. For each result `position` in `clicks` return `clicks`, `pct` (share of all clicks) and
`cum_pct` (share of clicks at this position or higher up), 1 decimal, ordered by position.

Example: positions 1, 2, 3 with 60, 30, 10 clicks: cum_pct = 60.0, 90.0, 100.0.""",
     hint1="Signal: 'share' and 'this position or above'. Pattern: running total with SUM OVER (ORDER BY position) "
           "divided by the grand total SUM OVER ().",
     hint2="1. CTE: COUNT(*) per position.\n2. `n / SUM(n) OVER ()` and `SUM(n) OVER (ORDER BY position ROWS UNBOUNDED PRECEDING) / SUM(n) OVER ()`.",
     solution="""WITH p AS (
  SELECT position, COUNT(*) AS clicks FROM clicks GROUP BY position
)
SELECT position, clicks,
  ROUND(100.0 * clicks / SUM(clicks) OVER (), 1) AS pct,
  ROUND(100.0 * SUM(clicks) OVER (ORDER BY position ROWS UNBOUNDED PRECEDING)
        / SUM(clicks) OVER (), 1) AS cum_pct
FROM p
ORDER BY position""",
     why="Window functions run on the grouped rows, so one SELECT gives both the share and the cumulative share. "
         "60.0% of clicks go to position 1 and 91.5% to the top 3, which is why ranking metrics weight the top heavily.",
     complexity="One aggregation, one window over 5 rows.",
     mistakes="Integer division (`clicks / SUM(...)` = 0). Cumulating in the wrong direction (ORDER BY position DESC).",
     learn=["sql-running-totals", "sql-ratios"])

ex.q("Firmware adoption curve by series", minutes=5, kind="sql", review=True, source=SS,
     prompt="""Samsung style. The devices that received firmware 6.0 are the active fleet. Per `series` (S / A / Z) return
`devices`, and the % of them that had installed 6.1 **before** 2024-05-08 (`by_may7`), before 2024-05-15 (`by_may14`),
at any time (`ever`), and never (`never`), 1 decimal. Order by series.

*Follow-up:* product wants to compare crash rates of updated and not-updated phones to judge 6.1. What is the problem?""",
     hint1="Signal: shares at several cut-off dates as columns. Pattern: LEFT JOIN to the first install time, then a "
           "pivot with conditional aggregation.",
     hint2="1. `base`: DISTINCT device_id, series for version 6.0.\n2. `up`: MIN(installed_at) of 6.1 per device.\n"
           "3. `base LEFT JOIN up`; `100.0 * SUM(CASE WHEN up_t < '2024-05-08' THEN 1 ELSE 0 END) / COUNT(*)` etc.",
     solution="""WITH base AS (
  SELECT DISTINCT f.device_id, d.series
  FROM firmware_updates f JOIN devices d ON d.device_id = f.device_id
  WHERE f.version = '6.0'
), up AS (
  SELECT device_id, MIN(installed_at) AS up_t
  FROM firmware_updates WHERE version = '6.1'
  GROUP BY device_id
)
SELECT b.series, COUNT(*) AS devices,
  ROUND(100.0 * SUM(CASE WHEN u.up_t < '2024-05-08' THEN 1 ELSE 0 END) / COUNT(*), 1) AS by_may7,
  ROUND(100.0 * SUM(CASE WHEN u.up_t < '2024-05-15' THEN 1 ELSE 0 END) / COUNT(*), 1) AS by_may14,
  ROUND(100.0 * SUM(CASE WHEN u.up_t IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS ever,
  ROUND(100.0 * SUM(CASE WHEN u.up_t IS NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS never
FROM base b
LEFT JOIN up u ON u.device_id = b.device_id
GROUP BY b.series
ORDER BY b.series""",
     why="The LEFT JOIN keeps devices that never updated (up_t NULL), which is the 'never' column (about 21% to 23%). "
         "Text timestamps compare correctly with `<` because the format is fixed width. Adoption is almost the same "
         "across series (about 44% by May 14). Follow-up: updaters self-select (heavier users, newer phones, Wi-Fi "
         "users), so their crash rate differs for reasons other than the firmware. Compare each device with itself "
         "before and after (as on day 27) and use the never-updated devices as a calendar control.",
     complexity="Two small aggregations and one join.",
     mistakes="Inner join (never-updated devices vanish, 'ever' becomes 100%). Using `<=` with a date string against a "
              "timestamp (`'2024-05-07 10:00' <= '2024-05-07'` is false).",
     learn=["sql-pivot", "sql-left-join-nulls"])

ex.q("The most divisive movies", minutes=5, kind="sql",
     prompt="""MovieLens (real). Among movies with at least 50 ratings, find the 5 with the **highest variance** of
ratings (the most divisive). Return `title`, `n`, `avg_rating` (2 decimals) and `var` (population variance, 2
decimals), highest variance first. Your SQL engine has no STDDEV or SQRT function.

Example: ratings 1 and 5: mean 3, variance = ((1-3)^2 + (5-3)^2) / 2 = 4.

*Follow-up:* why is a high-variance movie interesting for a recommender?""",
     hint1="Signal: spread without STDDEV. Pattern: aggregation with the identity `var = AVG(x * x) - AVG(x) * AVG(x)`.",
     hint2="1. Join ratings to movies, GROUP BY movie, HAVING COUNT(*) >= 50.\n2. var = `AVG(rating * rating) - AVG(rating) * AVG(rating)`.\n3. ORDER BY var DESC LIMIT 5.",
     solution="""SELECT m.title, COUNT(*) AS n,
  ROUND(AVG(r.rating), 2) AS avg_rating,
  ROUND(AVG(r.rating * r.rating) - AVG(r.rating) * AVG(r.rating), 2) AS var
FROM ml_ratings r
JOIN ml_movies m ON m.movie_id = r.movie_id
GROUP BY r.movie_id, m.title
HAVING COUNT(*) >= 50
ORDER BY var DESC
LIMIT 5""",
     why="`E[x^2] - E[x]^2` is the population variance, computable in one pass with plain aggregates (the sample "
         "variance multiplies by n / (n - 1)). The Blair Witch Project tops the list (variance 1.86, so the standard "
         "deviation is about 1.36). The 50 rating minimum stops movies with 2 ratings (1 and 5) from winning. "
         "Follow-up: the average hides that some users love and others hate the movie; a personalised model can "
         "separate the two groups, while a popularity ranking by average would treat it as mediocre.",
     complexity="One join and one GROUP BY.",
     mistakes="Ranking by the range MAX - MIN (almost always 0.5 to 5). Forgetting the minimum count. Integer math "
              "(not an issue here, ratings are real numbers). PostgreSQL has `VAR_POP` and `STDDEV_SAMP`.",
     learn=["sql-aggregation", "sql-median-percentiles"])

ex.q("Quick second orders at a real shop", minutes=6, kind="sql", review=True,
     prompt="""UCI Online Retail (real). An order is one `invoice_no` (real sales only: customer known, not 'C', quantity
> 0); its time is the earliest `invoice_date` of its lines. For customers whose **first** order was before
2011-11-01, compute the % who placed a second order within 30 days of the first. Return per first-order month:
`first_month`, `customers`, `pct_30d` (1 decimal).

*Follow-up:* why the cut-off at 2011-11-01?""",
     hint1="Signal: 'first order' and 'the next order within N days'. Pattern: ROW_NUMBER to find the first order and "
           "LEAD for the next one (retention of buyers).",
     hint2="1. `orders`: GROUP BY customer_id, invoice_no with MIN(invoice_date).\n"
           "2. `ROW_NUMBER()` and `LEAD(t)` per customer ordered by t, invoice_no.\n"
           "3. Keep rn = 1 and t < '2011-11-01'; flag next_t - t <= 30 days; AVG per month.",
     solution="""WITH orders AS (
  SELECT customer_id, invoice_no, MIN(invoice_date) AS t
  FROM retail
  WHERE customer_id IS NOT NULL AND invoice_no NOT LIKE 'C%' AND quantity > 0
  GROUP BY customer_id, invoice_no
), seq AS (
  SELECT customer_id, t,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY t, invoice_no) AS rn,
    LEAD(t) OVER (PARTITION BY customer_id ORDER BY t, invoice_no) AS next_t
  FROM orders
)
SELECT substr(t, 1, 7) AS first_month, COUNT(*) AS customers,
  ROUND(100.0 * AVG(CASE WHEN next_t IS NOT NULL
                          AND julianday(next_t) - julianday(t) <= 30 THEN 1 ELSE 0 END), 1) AS pct_30d
FROM seq
WHERE rn = 1 AND t < '2011-11-01'
GROUP BY substr(t, 1, 7)
ORDER BY first_month""",
     why="Orders are built first (one row per invoice), so a 30 line invoice is one order. LEAD on the first row gives "
         "the second order. December 2010 looks best (35.0%) because it mixes in old loyal customers who bought "
         "before the data starts; later months sit around 15% to 24%. Follow-up: the data ends on 2011-12-09; a "
         "customer whose first order was on 2011-11-20 had only 19 days to come back, so recent months would look "
         "worse for no real reason (right censoring).",
     complexity="Aggregation to orders, then one window sort per customer.",
     mistakes="Working on invoice LINES (the 'next line' is usually the same invoice: gap 0). Ignoring the censoring cut-off. "
              "Counting cancellations as orders.",
     learn=["sql-retention", "sql-lag-lead"])

ex.q("Longest 10k-step streak (after cleaning)", minutes=6, kind="sql", review=True, source=SS,
     prompt="""Samsung Health style. `health_steps` has several syncs per day (cumulative counts) and duplicate uploads;
the day's value is the latest sync. A **10k day** is a day with at least 10,000 steps. For each user find their
longest run of consecutive 10k days and return the top 5 runs overall: `user_id`, `start_date`, `end_date`, `days`
(longest first, then user_id). A user can appear twice if they have two long runs.

*Follow-up:* what goes wrong if you skip the cleaning step?""",
     hint1="Signal: dirty snapshots, then 'consecutive days'. Pattern: dedup with ROW_NUMBER (latest sync), then gaps "
           "and islands (date minus row number).",
     hint2="1. `final`: rn = 1 of `ROW_NUMBER() OVER (PARTITION BY user_id, step_date ORDER BY synced_at DESC, steps DESC)`.\n"
           "2. `good`: 10k days with `julianday(step_date) - ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY step_date)`.\n"
           "3. GROUP BY user, group key: MIN, MAX, COUNT; ORDER BY days DESC, user_id LIMIT 5.",
     solution="""WITH ranked AS (
  SELECT user_id, step_date, steps,
    ROW_NUMBER() OVER (PARTITION BY user_id, step_date ORDER BY synced_at DESC, steps DESC) AS rn
  FROM health_steps
), good AS (
  SELECT user_id, step_date,
    julianday(step_date) - ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY step_date) AS grp
  FROM ranked
  WHERE rn = 1 AND steps >= 10000
)
SELECT user_id, MIN(step_date) AS start_date, MAX(step_date) AS end_date, COUNT(*) AS days
FROM good
GROUP BY user_id, grp
ORDER BY days DESC, user_id
LIMIT 5""",
     why="The 10k filter is applied to the cleaned daily value, BEFORE numbering the rows, so only 10k days take part "
         "in the date minus row number trick. User 31 has the longest run (11 days, June 4 to 14) and also a 9 day run "
         "later. Follow-up: on the raw table a day has several rows, so the row number grows faster than the date and "
         "streaks break apart, and early syncs below 10k make the day look like a gap; with the raw rows, user 60 "
         "even looks like the best walker because its duplicate rows stretch one streak to 20 rows.",
     complexity="Two window sorts: O(n log n).",
     mistakes="Filtering 10k on the raw syncs (an early sync of 4,000 on a 12,000 day). Running ROW_NUMBER before the "
              "10k filter (then non-10k days fill the gaps).",
     learn=["sql-gaps-islands", "sql-dedup-cleaning"])

ex.save()
