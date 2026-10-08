import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam
from sql_hard_tables import load, put_doc

GG = ("DataLemur Google SQL questions (inspiration, own wording and data)",
      "https://datalemur.com/blog/google-sql-interview-questions")

EXTRA = '''# Made-up small tables for classic Google-style questions.
db.executescript("""
CREATE TABLE search_freq (searches_per_week INTEGER, num_users INTEGER);
INSERT INTO search_freq VALUES (0, 120), (1, 260), (2, 120), (3, 230), (4, 140), (5, 60), (7, 40), (10, 20), (20, 10);
CREATE TABLE ad_budgets (advertiser_id INTEGER, budget REAL);
INSERT INTO ad_budgets VALUES (1, 1000), (2, 500), (3, 2000), (4, 300);
CREATE TABLE ad_spend (advertiser_id INTEGER, spend_date TEXT, spend REAL);
INSERT INTO ad_spend VALUES
(1, '2024-06-03', 220), (1, '2024-06-04', 310), (1, '2024-06-05', 180), (1, '2024-06-06', 400), (1, '2024-06-07', 90),
(2, '2024-06-03', 150), (2, '2024-06-04', 150), (2, '2024-06-05', 200), (2, '2024-06-06', 120),
(3, '2024-06-03', 300), (3, '2024-06-05', 450), (3, '2024-06-06', 500), (3, '2024-06-07', 380),
(4, '2024-06-04', 120), (4, '2024-06-04', 90), (4, '2024-06-06', 150);
""")'''

SMALL = """**Made-up small tables:** `search_freq` (`searches_per_week`, `num_users`): a compressed histogram, e.g. the row
(2, 120) means 120 users searched exactly 2 times. `ad_budgets` (`advertiser_id`, `budget`) and `ad_spend`
(`advertiser_id`, `spend_date`, `spend`): one row per spend record; a day can have several records."""

INTRO = ("**Company style: Google.** Search, ads and Play Store data. Google SQL rounds like clean definitions "
         "(what is a 'good click'?), compressed tables, and edge cases such as ties and duplicates. Say how you would "
         "validate the result.")

ex = Exam(26, "sql", intro=INTRO)
code, doc = load("search", "play", extra=EXTRA)
ex.setup(code, data=True)
put_doc(ex, doc, SMALL)

ex.q("Median from a compressed histogram", minutes=6, kind="sql", source=GG,
     prompt="""`search_freq` stores how many users searched N times last week (one row per N) instead of one row per
user. Return the **median** searches per week (1 decimal) without expanding the table into one row per user.

Example: rows (1, 2), (5, 1), (9, 1) mean the values 1, 1, 5, 9: the median is (1 + 5) / 2 = 3.0.

*Follow-up:* how would you get p90 with the same idea?""",
     hint1="Signal: a frequency table (value, count) and a percentile. Pattern: running totals of the counts give each "
           "value's position range; the median is the value whose range contains the middle position(s).",
     hint2="1. `SUM(num_users) OVER (ORDER BY searches_per_week ROWS UNBOUNDED PRECEDING)` = last position of each value.\n"
           "2. First position = that minus num_users plus 1; n = SUM(num_users) OVER ().\n"
           "3. Middle positions are `(n + 1) / 2` and `(n + 2) / 2` (integer division). AVG the values whose range contains either.",
     solution="""WITH c AS (
  SELECT searches_per_week AS x, num_users,
    SUM(num_users) OVER (ORDER BY searches_per_week ROWS UNBOUNDED PRECEDING) AS last_pos,
    SUM(num_users) OVER () AS n
  FROM search_freq
), r AS (
  SELECT x, last_pos - num_users + 1 AS first_pos, last_pos, n FROM c
)
SELECT ROUND(AVG(x), 1) AS median
FROM r
WHERE (n + 1) / 2 BETWEEN first_pos AND last_pos
   OR (n + 2) / 2 BETWEEN first_pos AND last_pos""",
     why="There are 1,000 users, so the median averages positions 500 and 501. The running total reaches exactly 500 "
         "at value 2 (120 + 260 + 120), so position 500 is a 2 and position 501 is a 3: median 2.5. Many solutions "
         "return 2 or 3 because they only look for the first value whose running share passes 50%. The same range "
         "logic works for odd n (both expressions give the same position). Follow-up: p90 (nearest rank) is the "
         "value whose range contains position `CEIL(0.9 * n)` = 900: value 5 (positions 871 to 930).",
     complexity="One window over the distinct values: O(k log k) for k rows, no matter how many users.",
     mistakes="Expanding with a recursive CTE (works, but n rows; mention it as the slow alternative). Default RANGE "
              "frame (fine here because values are unique, but say ROWS). Picking only one middle value.",
     learn=["sql-median-percentiles", "sql-running-totals"])

ex.q("Queries where users do not find what they need", minutes=6, kind="sql", source=GG,
     prompt="""A search has a **good click** if any of its clicks has `dwell_s > 30`. For every exact `query` text with at
least 200 searches return `searches`, `ctr_pct` (searches with any click), `good_pct` (searches with a good click) and
`pos1_pct` (searches with a click on position 1), all in % with 1 decimal. Show the 5 queries with the lowest `good_pct`.

*Follow-up:* CTR is above 60% for all of them. Why is good-click rate the better quality metric?""",
     hint1="Signal: rates per query where a search can have 0, 1 or many clicks. Pattern: ratios: collapse to one row "
           "per search with MAX(CASE ...) flags, then AVG the flags per query.",
     hint2="1. `searches LEFT JOIN clicks`, GROUP BY search: `MAX(CASE WHEN c.dwell_s > 30 THEN 1 ELSE 0 END)` etc.\n"
           "2. GROUP BY query HAVING COUNT(*) >= 200: `100.0 * AVG(flag)`.\n3. ORDER BY good_pct LIMIT 5.",
     solution="""WITH per_search AS (
  SELECT s.search_id, s.query,
    MAX(CASE WHEN c.search_id IS NOT NULL THEN 1 ELSE 0 END) AS any_click,
    MAX(CASE WHEN c.dwell_s > 30 THEN 1 ELSE 0 END) AS good_click,
    MAX(CASE WHEN c.position = 1 THEN 1 ELSE 0 END) AS pos1_click
  FROM searches s
  LEFT JOIN clicks c ON c.search_id = s.search_id
  GROUP BY s.search_id, s.query
)
SELECT query, COUNT(*) AS searches,
  ROUND(100.0 * AVG(any_click), 1) AS ctr_pct,
  ROUND(100.0 * AVG(good_click), 1) AS good_pct,
  ROUND(100.0 * AVG(pos1_click), 1) AS pos1_pct
FROM per_search
GROUP BY query
HAVING COUNT(*) >= 200
ORDER BY good_pct
LIMIT 5""",
     why="Collapsing to one row per search first is the key step: after the LEFT JOIN a search with two clicks has "
         "two rows, and averaging those rows would weight it twice. 'nba scores' has 62.7% CTR but only 25.9% good "
         "clicks. Follow-up: a short click followed by a quick return (pogo-sticking) is a click, but a failure; "
         "good-click (long dwell) rate tracks satisfaction, so queries with high CTR but low good-click rate are the "
         "ones to send to the ranking team.",
     complexity="One join and two GROUP BYs: O(searches + clicks).",
     mistakes="AVG over the joined rows (multi-click searches count twice). `COUNT(c.search_id) / COUNT(*)` (clicks per "
              "search, not a rate). Filtering `WHERE dwell_s > 30` before the join (drops searches without good clicks "
              "from the denominator).",
     learn=["sql-ratios", "sql-left-join-nulls"])

ex.q("How often do users rephrase?", minutes=7, kind="sql", source=GG,
     prompt="""A search is **abandoned and rephrased** if it has no good click (`dwell_s > 30`) AND the same user runs
their next search within 120 seconds. Return per `device`: `searches` and `reform_pct` (% of all searches that were
abandoned and rephrased, 1 decimal). Order by device.

Example: user 7 searches 'weather' at 10:00:00, short click (5 s dwell), searches 'weather 2024' at 10:00:40: the
first search counts. The second search counts only if it is also followed within 120 s.""",
     hint1="Signal: compare each search with the user's NEXT search. Pattern: LEAD over the user's searches, after "
           "collapsing clicks to one row per search.",
     hint2="1. One row per search: MAX(CASE good click) from the LEFT JOIN, GROUP BY search.\n"
           "2. In the same SELECT (windows run after GROUP BY): `LEAD(search_time) OVER (PARTITION BY user_id ORDER BY search_time, search_id)`.\n"
           "3. Flag = no good click AND next time - this time <= 120 s; AVG per device.",
     solution="""WITH g AS (
  SELECT s.search_id, s.user_id, s.device, s.search_time,
    MAX(CASE WHEN c.dwell_s > 30 THEN 1 ELSE 0 END) AS good_click,
    LEAD(s.search_time) OVER (PARTITION BY s.user_id ORDER BY s.search_time, s.search_id) AS next_time
  FROM searches s
  LEFT JOIN clicks c ON c.search_id = s.search_id
  GROUP BY s.search_id, s.user_id, s.device, s.search_time
)
SELECT device, COUNT(*) AS searches,
  ROUND(100.0 * AVG(CASE WHEN good_click = 0
      AND (julianday(next_time) - julianday(search_time)) * 86400 <= 120
    THEN 1 ELSE 0 END), 1) AS reform_pct
FROM g
GROUP BY device
ORDER BY device""",
     why="Window functions are evaluated after GROUP BY, so LEAD here walks over one row per search, not one per "
         "click. When there is no next search, `next_time` is NULL, the comparison is NULL, and the CASE gives 0. "
         "About 18% to 20% of searches on every device end in a quick rephrase; that is a direct 'search failed' "
         "signal used as a guardrail metric in ranking experiments.",
     complexity="One join, one GROUP BY, one window sort per user: O(n log n).",
     mistakes="LEAD over the raw joined rows (the 'next' row can be another click of the same search). Partitioning by "
              "query instead of user (a rephrase changes the query text). Not ordering by a tiebreaker (search_id) "
              "when two searches share a second.",
     learn=["sql-lag-lead", "sql-ratios"])

ex.q("Top apps per category on Google Play", minutes=5, kind="sql", review=True,
     prompt="""Google Play (real, scraped). Some apps appear several times in the same category (scraped twice, with
slightly different review counts). Keep one row per (app, category): the one with the most reviews. Then return the
**top 3 apps per category** by `installs`, breaking ties by `reviews`, for the categories COMMUNICATION, GAME and
PHOTOGRAPHY: `category`, `rn`, `app`, `installs`, `reviews`.

*Follow-up:* `installs` is a bucket (1,000,000,000+ means "at least a billion"). What does that do to a top-N by installs?""",
     hint1="Signal: duplicates, then 'top 3 per group' with ties. Pattern: dedup with ROW_NUMBER, then top-N per group "
           "with a second ROW_NUMBER and a tiebreaker.",
     hint2="1. `ROW_NUMBER() OVER (PARTITION BY app, category ORDER BY reviews DESC)`, keep 1.\n"
           "2. `ROW_NUMBER() OVER (PARTITION BY category ORDER BY installs DESC, reviews DESC)`, keep <= 3.\n"
           "3. Filter the 3 categories at the end (or before ranking: same result here).",
     solution="""WITH one AS (
  SELECT app, category, installs, reviews,
    ROW_NUMBER() OVER (PARTITION BY app, category ORDER BY reviews DESC) AS dup
  FROM play_apps
), ranked AS (
  SELECT app, category, installs, reviews,
    ROW_NUMBER() OVER (PARTITION BY category ORDER BY installs DESC, reviews DESC) AS rn
  FROM one
  WHERE dup = 1
)
SELECT category, rn, app, installs, reviews
FROM ranked
WHERE category IN ('COMMUNICATION', 'GAME', 'PHOTOGRAPHY') AND rn <= 3
ORDER BY category, rn""",
     why="Without the dedup step, WhatsApp Messenger takes ranks 1, 2 and 3 of COMMUNICATION (three scraped copies), "
         "and the same happens to Subway Surfers and Google Photos. 10,840 rows hold only 9,744 distinct (app, "
         "category) pairs. Follow-up: many apps share the top bucket (three COMMUNICATION apps have 1,000,000,000), "
         "so the order inside a bucket comes from the tiebreaker (reviews). Say that the ranking is coarse, and use "
         "RANK or DENSE_RANK if ties should share a place.",
     complexity="Two window sorts: O(n log n).",
     mistakes="SELECT DISTINCT (the copies differ in reviews, so they are not exact duplicates). RANK without a "
              "tiebreaker (returns 4+ rows when the 3rd place is tied, which may or may not be what is asked: say it).",
     learn=["sql-top-n", "sql-dedup-cleaning"])

ex.q("When did each advertiser hit the budget?", minutes=6, kind="sql", review=True, source=GG,
     prompt="""Each advertiser has a total `budget` (`ad_budgets`). Spend arrives as records in `ad_spend` (a day can have
several records). For **every** advertiser return `advertiser_id`, `budget`, `reached_on` (the first day the
cumulative spend is >= budget), `cum_spend` on that day and `over_by` (cum_spend - budget). Advertisers who never
reach the budget get NULLs. Order by advertiser.

Example: budget 500, daily spend 150, 150, 200: cumulative 150, 300, 500: reached on day 3, over_by 0.""",
     hint1="Signal: 'first day the cumulative total crosses X'. Pattern: running total with SUM OVER (ORDER BY day), "
           "then MIN(day) where the total >= budget, LEFT JOINed back to all advertisers.",
     hint2="1. `daily`: SUM(spend) per advertiser and day (several records per day).\n"
           "2. `run`: `SUM(spend) OVER (PARTITION BY advertiser_id ORDER BY spend_date ROWS UNBOUNDED PRECEDING)`.\n"
           "3. `hit`: MIN(spend_date) WHERE cum >= budget.\n4. `ad_budgets LEFT JOIN hit LEFT JOIN run` on the hit day.",
     solution="""WITH daily AS (
  SELECT advertiser_id, spend_date, SUM(spend) AS spend
  FROM ad_spend
  GROUP BY advertiser_id, spend_date
), run AS (
  SELECT advertiser_id, spend_date,
    SUM(spend) OVER (PARTITION BY advertiser_id ORDER BY spend_date
                     ROWS UNBOUNDED PRECEDING) AS cum
  FROM daily
), hit AS (
  SELECT r.advertiser_id, MIN(r.spend_date) AS reached_on
  FROM run r
  JOIN ad_budgets b ON b.advertiser_id = r.advertiser_id
  WHERE r.cum >= b.budget
  GROUP BY r.advertiser_id
)
SELECT b.advertiser_id, b.budget, h.reached_on,
  r.cum AS cum_spend, r.cum - b.budget AS over_by
FROM ad_budgets b
LEFT JOIN hit h ON h.advertiser_id = b.advertiser_id
LEFT JOIN run r ON r.advertiser_id = b.advertiser_id AND r.spend_date = h.reached_on
ORDER BY b.advertiser_id""",
     why="Aggregating to one row per day first makes the running total and the join on the hit day unique (advertiser 4 "
         "has two records on 2024-06-04). Advertiser 2 reaches exactly 500 on 2024-06-05 (over_by 0, so `>=` matters); "
         "advertiser 3 spends 1,630 of 2,000 and correctly gets NULLs thanks to the LEFT JOINs. In production this is "
         "the query behind 'pacing' alerts: the over_by column is money the advertiser did not want to spend.",
     complexity="One aggregation and one window sort per advertiser.",
     mistakes="Running total over raw records joined back by date (duplicate rows for advertiser 4). `>` instead of "
              "`>=`. Inner joins that drop advertiser 3. RANGE frame with duplicate dates (both records of a day get "
              "the day's total, which hides the order inside the day).",
     learn=["sql-running-totals", "sql-left-join-nulls"])

ex.save()
