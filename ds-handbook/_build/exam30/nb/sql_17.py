import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
from sql_mid_data import build_setup

ex = Exam(17, "sql")
build_setup(ex, "app", "ab")

# ---------------------------------------------------------------- Q1 simple funnel
ex.q("The shopping funnel at a glance", minutes=5, kind="sql",
     prompt="""Shopping app (made up). The funnel steps are, in order: 1 `view_item`, 2 `add_to_cart`, 3 `checkout`,
4 `purchase`. For each step return `step_no`, `step`, `users` (distinct users who did that event at least once, at any
time), `pct_of_first` (users as a percent of step 1) and `pct_of_prev` (percent of the previous step), 1 decimal.

Example shape: `2 | add_to_cart | 1091 | 79.1 | 79.1`.

Follow-up: this version ignores order and timing. Name two ways it can overstate conversion.""",
     hint1="Signal: \"how many users reach each step\". Pattern: a small step table (to fix the order and keep empty "
           "steps), COUNT(DISTINCT user_id) per step, then FIRST_VALUE / LAG for the percentages.",
     hint2="1. CTE steps with `SELECT 1 AS step_no, 'view_item' AS step UNION ALL ...`.\n"
           "2. LEFT JOIN app_events on event_name, `COUNT(DISTINCT e.user_id)` per step.\n"
           "3. `FIRST_VALUE(users) OVER (ORDER BY step_no)` and `LAG(users) OVER (ORDER BY step_no)`.",
     solution="""WITH steps AS (
    SELECT 1 AS step_no, 'view_item' AS step
    UNION ALL SELECT 2, 'add_to_cart'
    UNION ALL SELECT 3, 'checkout'
    UNION ALL SELECT 4, 'purchase'
), reached AS (
    SELECT s.step_no, s.step, COUNT(DISTINCT e.user_id) AS users
    FROM steps s
    LEFT JOIN app_events e ON e.event_name = s.step
    GROUP BY s.step_no, s.step
)
SELECT step_no, step, users,
       ROUND(100.0 * users / FIRST_VALUE(users) OVER (ORDER BY step_no), 1) AS pct_of_first,
       ROUND(100.0 * users / LAG(users) OVER (ORDER BY step_no), 1)         AS pct_of_prev
FROM reached
ORDER BY step_no""",
     why="The step table gives the funnel a fixed order (alphabetical order would be wrong) and, with a LEFT JOIN, "
         "shows a step with 0 users instead of hiding it. The biggest drop is checkout to purchase (48.3%). "
         "Follow-up: (1) a user can add to cart without viewing first (from a wishlist), or purchase months after "
         "an unrelated view, and still counts; (2) there is no time window, so old users have had more time to "
         "convert than new ones. Q2 and Q3 fix both.",
     complexity="One pass over app_events with a group by on 4 steps.",
     mistakes="Counting events instead of distinct users (a user with 5 carts counts 5 times). Ordering steps "
              "alphabetically. Integer division.",
     learn=["sql-funnels", "sql-lag-lead"])

# ---------------------------------------------------------------- Q2 ordered funnel per platform
ex.q("A funnel that respects the order", minutes=8, kind="sql",
     prompt="""Shopping app. Now a user only counts for a step if they did it **after** the previous step:
- viewed: has a `view_item` (take their first view time);
- carted: has an `add_to_cart` **after** that first view (take the first such cart time);
- checked_out: a `checkout` after that cart time; purchased: a `purchase` after that checkout time.

Per `platform` (all users, also those who never viewed) return `viewed`, `carted`, `checked_out`, `purchased` and
`view_to_purchase_pct` (purchased / viewed, 1 decimal).

Example: a user with add_to_cart at 09:00, view_item at 09:05 and nothing else counts as viewed but not carted.""",
     hint1="Signal: \"step B must happen after step A\". Pattern: a chain of CTEs, each taking the first time of a "
           "step that is later than the previous step's time (join + MIN), then LEFT JOIN all to users.",
     hint2="1. v: MIN(event_time) of view_item per user.\n"
           "2. c: join app_events to v on user, `event_name = 'add_to_cart' AND e.event_time > v.t`, MIN per user.\n"
           "3. k from c, p from k the same way.\n"
           "4. app_users LEFT JOIN v, c, k, p; COUNT(x.user_id) per platform.",
     solution="""WITH v AS (
    SELECT user_id, MIN(event_time) AS t
    FROM app_events WHERE event_name = 'view_item'
    GROUP BY user_id
), c AS (
    SELECT e.user_id, MIN(e.event_time) AS t
    FROM app_events e JOIN v ON v.user_id = e.user_id
    WHERE e.event_name = 'add_to_cart' AND e.event_time > v.t
    GROUP BY e.user_id
), k AS (
    SELECT e.user_id, MIN(e.event_time) AS t
    FROM app_events e JOIN c ON c.user_id = e.user_id
    WHERE e.event_name = 'checkout' AND e.event_time > c.t
    GROUP BY e.user_id
), p AS (
    SELECT e.user_id, MIN(e.event_time) AS t
    FROM app_events e JOIN k ON k.user_id = e.user_id
    WHERE e.event_name = 'purchase' AND e.event_time > k.t
    GROUP BY e.user_id
)
SELECT u.platform,
       COUNT(v.user_id) AS viewed,
       COUNT(c.user_id) AS carted,
       COUNT(k.user_id) AS checked_out,
       COUNT(p.user_id) AS purchased,
       ROUND(100.0 * COUNT(p.user_id) / COUNT(v.user_id), 1) AS view_to_purchase_pct
FROM app_users u
LEFT JOIN v ON v.user_id = u.user_id
LEFT JOIN c ON c.user_id = u.user_id
LEFT JOIN k ON k.user_id = u.user_id
LEFT JOIN p ON p.user_id = u.user_id
GROUP BY u.platform
ORDER BY u.platform""",
     why="Each CTE has at most one row per user, so the final LEFT JOINs cannot multiply rows and COUNT(x.user_id) "
         "counts users who reached step x in order. Taking the first time at each step is the standard "
         "\"greedy\" choice: it gives every user the most room to complete the next step. Web converts clearly "
         "worse (21.2% versus about 32%), so look at the web checkout first. Timestamps in 'YYYY-MM-DD HH:MM:SS' "
         "compare correctly as text in SQLite; in PostgreSQL they are real timestamps.",
     complexity="One group by per step; each join is on user_id.",
     mistakes="Joining all events to all events (one row per combination: huge and double counted). Comparing "
              "with the previous step's LAST time instead of the first. Using `>=` when two steps can share a "
              "timestamp only by logging error (decide and say it).",
     learn=["sql-funnels", "sql-cte", "sql-left-join-nulls"])

# ---------------------------------------------------------------- Q3 time-bounded conversion
ex.q("Carts that turn into orders within a day", minutes=7, kind="sql",
     prompt="""Shopping app. For every `add_to_cart` event, check whether the **same user** has a `purchase` event
**after** it and **at most 24 hours** later. Per `platform` return `carts` (cart events), `converted_24h` and
`abandonment_pct` (carts without a purchase in 24 hours, 1 decimal).

Example: cart at 2024-01-05 21:10:00 and purchase at 2024-01-06 20:00:00 converts; purchase at 2024-01-06 21:30:00
does not.

Follow-up: two carts at 10:00 and 10:20 followed by one purchase at 10:30 both count as converted. Is that what
the PM wants?""",
     hint1="Signal: \"followed by X within T\". Pattern: a correlated EXISTS (or LEFT JOIN with a time range) "
           "per cart event.",
     hint2="1. For each cart e: `EXISTS (SELECT 1 FROM app_events p WHERE p.user_id = e.user_id AND p.event_name = "
           "'purchase' AND p.event_time > e.event_time AND p.event_time <= datetime(e.event_time, '+24 hours'))`.\n"
           "2. Group by platform: COUNT(*) and SUM of the flag.",
     solution="""WITH carts AS (
    SELECT e.event_id, u.platform,
           EXISTS (
               SELECT 1
               FROM app_events p
               WHERE p.user_id = e.user_id
                 AND p.event_name = 'purchase'
                 AND p.event_time > e.event_time
                 AND p.event_time <= datetime(e.event_time, '+24 hours')
           ) AS bought_24h
    FROM app_events e
    JOIN app_users u ON u.user_id = e.user_id
    WHERE e.event_name = 'add_to_cart'
)
SELECT platform,
       COUNT(*)        AS carts,
       SUM(bought_24h) AS converted_24h,
       ROUND(100.0 * (COUNT(*) - SUM(bought_24h)) / COUNT(*), 1) AS abandonment_pct
FROM carts
GROUP BY platform
ORDER BY platform""",
     why="EXISTS answers yes or no per cart without multiplying rows, even if several purchases follow. "
         "In SQLite EXISTS returns 1 or 0, so SUM counts conversions; in PostgreSQL it returns a boolean, use "
         "`SUM(CASE WHEN ... THEN 1 ELSE 0 END)` or `COUNT(*) FILTER (WHERE bought_24h)`. Abandonment is about "
         "77% on every platform, so the web gap from Q2 is not at the cart step. Follow-up: counting at cart level "
         "credits one purchase to two carts. A PM usually wants user-day or session level (\"did this session end "
         "in a purchase?\"), or to attribute each purchase to the latest cart before it (LEAD / MAX).",
     complexity="One correlated lookup per cart; with an index on (user_id, event_name, event_time) it is fast.",
     mistakes="A LEFT JOIN to purchases with the time range, then COUNT(*) (a cart followed by two purchases counts "
              "twice). Forgetting `p.event_time > e.event_time` (purchases before the cart count). Using date() "
              "and losing the hours.",
     learn=["sql-funnels", "sql-dates", "sql-subqueries"])

# ---------------------------------------------------------------- Q4 review: case-when on a real A/B log
ex.q("Clean the experiment before reading it", minutes=6, kind="sql", review=True,
     prompt="""`ab_data` (real Udacity experiment): control users should see the `old_page`, treatment users the
`new_page`. Some rows break this rule. Per `grp` return `n_rows`, `mismatched` (rows where group and page disagree),
`clean_users` (distinct users among rows that agree) and `conv_pct_clean` (conversion rate on the rows that agree,
2 decimals).

Example: a row `treatment | old_page` is mismatched and must not enter the conversion rate.

Then say whether the new page wins.""",
     hint1="Pattern: CASE WHEN inside aggregates (conditional counts and a conditional average). A neat trick: "
           "`(grp = 'treatment') = (landing_page = 'new_page')` is true exactly when the row is consistent.",
     hint2="1. `SUM(CASE WHEN <mismatch> THEN 1 ELSE 0 END)`.\n"
           "2. `COUNT(DISTINCT CASE WHEN <consistent> THEN user_id END)`.\n"
           "3. `AVG(CASE WHEN <consistent> THEN converted END)`: no ELSE, so mismatched rows become NULL and AVG "
           "skips them.",
     solution="""SELECT grp,
       COUNT(*) AS n_rows,
       SUM(CASE WHEN (grp = 'treatment') <> (landing_page = 'new_page') THEN 1 ELSE 0 END) AS mismatched,
       COUNT(DISTINCT CASE WHEN (grp = 'treatment') = (landing_page = 'new_page') THEN user_id END) AS clean_users,
       ROUND(100.0 * AVG(CASE WHEN (grp = 'treatment') = (landing_page = 'new_page') THEN converted END), 2)
           AS conv_pct_clean
FROM ab_data
GROUP BY grp""",
     why="Comparing two booleans is a compact XOR test. Leaving out ELSE in the AVG is the key trick: NULLs are "
         "ignored, so the average is over clean rows only (ELSE 0 would wrongly count mismatches as non-converted). "
         "About 1.3% of rows are mismatched in each group. Treatment has one more clean row than clean users (a "
         "duplicated user): deduplicate before testing. Clean conversion is 12.04% for control and 11.88% for "
         "treatment: the new page does not win (it is slightly lower; a z-test is the stats notebook's job).",
     complexity="One pass over 294,478 rows.",
     mistakes="`ELSE 0` in the conversion average. Counting rows as users. Analysing without checking assignment "
              "consistency first. `group` is a reserved word in SQL: quote it or rename it (done here: `grp`).",
     learn=["sql-case-when", "sql-dedup-cleaning", "stats-ab-analysis"])

# ---------------------------------------------------------------- Q5 review: retention by first-day behaviour
ex.q("Is an early cart an activation signal?", minutes=6, kind="sql", review=True,
     prompt="""Shopping app. Product believes users who **add to cart on their signup day** stick around. Split users
into 'carted on day 0' and 'did not cart on day 0' and return `segment`, `users` and `d7_pct` (percent active exactly
7 days after signup, 1 decimal).

What do you tell Product?""",
     hint1="Pattern: per user, two EXISTS flags (did the action on day 0; active on day 7), then a group by on the "
           "first flag with AVG of the second.",
     hint2="1. CTE over app_users with `EXISTS (... add_to_cart AND substr(event_time, 1, 10) = signup_date)` and "
           "`EXISTS (... activity_date = date(signup_date, '+7 day'))`.\n2. CASE to label, group by it.",
     solution="""WITH day0 AS (
    SELECT u.user_id,
           EXISTS (SELECT 1 FROM app_events e
                   WHERE e.user_id = u.user_id AND e.event_name = 'add_to_cart'
                     AND substr(e.event_time, 1, 10) = u.signup_date) AS carted_day0,
           EXISTS (SELECT 1 FROM daily_activity d
                   WHERE d.user_id = u.user_id AND d.activity_date = date(u.signup_date, '+7 day')) AS d7
    FROM app_users u
)
SELECT CASE WHEN carted_day0 = 1 THEN 'carted on day 0' ELSE 'did not cart on day 0' END AS segment,
       COUNT(*) AS users,
       ROUND(100.0 * AVG(d7), 1) AS d7_pct
FROM day0
GROUP BY CASE WHEN carted_day0 = 1 THEN 'carted on day 0' ELSE 'did not cart on day 0' END""",
     why="EXISTS flags keep one row per user, so AVG(d7) is a clean retention rate per segment. Here the early "
         "cart users retain slightly worse (28.0% versus 30.3%), so in this data a day-0 cart is not an activation "
         "signal. Tell Product: test other first-day actions (number of sessions, minutes), and remember that "
         "even a strong correlation would not prove that pushing users to cart causes retention; that needs an "
         "experiment.",
     complexity="Two correlated lookups per user.",
     mistakes="Joining events directly (users with several carts get several rows and dominate the average). "
              "Comparing a timestamp to a date without truncating. Claiming causation.",
     learn=["sql-retention", "sql-case-when", "stats-product-metrics"])

ex.save()
