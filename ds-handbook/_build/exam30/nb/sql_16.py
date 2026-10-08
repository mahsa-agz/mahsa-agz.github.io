import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
from sql_mid_data import build_setup

ex = Exam(16, "sql")
build_setup(ex, "app", "retail")

# ---------------------------------------------------------------- Q1 D1 / D7 / D30 by weekly cohort
ex.q("Day 1, day 7, day 30", minutes=6, kind="sql",
     prompt="""Shopping app (made up). **Day N retention** of a user = they have a `daily_activity` row exactly N days
after their `signup_date`. For each **signup week** (weeks start Monday: `date(d, 'weekday 0', '-6 days')`) return
`cohort_week`, `users`, `d1_pct`, `d7_pct`, `d30_pct` (percent of the cohort, 1 decimal).

Example: a user who signed up on 2024-01-03 counts for D7 if they were active on 2024-01-10, whatever they did on
other days.

Follow-ups: (a) Is D30 fair for users who signed up on 2024-03-20? (b) How is "rolling" (unbounded) D7 retention
different?""",
     hint1="Signal: \"active exactly N days after signup\", grouped by cohort. Pattern: LEFT JOIN the activity table "
           "once per N with `activity_date = date(signup_date, '+N day')`, then average 0/1 flags.",
     hint2="1. FROM app_users u.\n2. `LEFT JOIN daily_activity d1 ON d1.user_id = u.user_id AND d1.activity_date = "
           "date(u.signup_date, '+1 day')`, the same for 7 and 30.\n"
           "3. Group by cohort week; `100.0 * AVG(CASE WHEN d1.user_id IS NOT NULL THEN 1 ELSE 0 END)`.",
     solution="""SELECT date(u.signup_date, 'weekday 0', '-6 days') AS cohort_week,
       COUNT(*) AS users,
       ROUND(100.0 * AVG(CASE WHEN d1.user_id  IS NOT NULL THEN 1 ELSE 0 END), 1) AS d1_pct,
       ROUND(100.0 * AVG(CASE WHEN d7.user_id  IS NOT NULL THEN 1 ELSE 0 END), 1) AS d7_pct,
       ROUND(100.0 * AVG(CASE WHEN d30.user_id IS NOT NULL THEN 1 ELSE 0 END), 1) AS d30_pct
FROM app_users u
LEFT JOIN daily_activity d1  ON d1.user_id = u.user_id  AND d1.activity_date  = date(u.signup_date, '+1 day')
LEFT JOIN daily_activity d7  ON d7.user_id = u.user_id  AND d7.activity_date  = date(u.signup_date, '+7 day')
LEFT JOIN daily_activity d30 ON d30.user_id = u.user_id AND d30.activity_date = date(u.signup_date, '+30 day')
GROUP BY date(u.signup_date, 'weekday 0', '-6 days')
ORDER BY cohort_week""",
     why="The date condition sits in the ON clause, so users without that activity row are kept (NULL) and count "
         "as 0. Since `daily_activity` has at most one row per user and day, the joins cannot multiply rows. "
         "Retention is about 40% to 50% on day 1, 25% to 30% on day 7 and 12% to 18% on day 30. "
         "(a) Here every signup is on or before Feb 29 and the data runs to Mar 31, so D30 is observable for "
         "everyone. In general, only include users with at least N days of history (`signup_date <= last_date - "
         "N`), otherwise recent cohorts look artificially bad. (b) Rolling D7 = active on day 7 **or later**; it is "
         "higher and never goes down as more data arrives. PostgreSQL: `u.signup_date + 7` or `+ INTERVAL '7 days'`.",
     complexity="Three index lookups per user on (user_id, activity_date).",
     mistakes="Putting `d7.activity_date = ...` in WHERE (turns the LEFT JOIN into an inner join: D7 becomes "
              "100%). Using `BETWEEN signup and signup + 7` (that is \"active in the first week\", a different "
              "metric). Not removing cohorts that are too young.",
     learn=["sql-retention", "sql-left-join-nulls", "sql-dates"])

# ---------------------------------------------------------------- Q2 monthly cohort matrix with censoring
ex.q("Monthly cohort table", minutes=6, kind="sql",
     prompt="""Shopping app. Build the classic cohort table: one row per **signup month** with `users` and the
percent of the cohort active in **month 0, 1 and 2** after signup (`m0`, `m1`, `m2`, 1 decimal). Month k = calendar
month of signup + k (a user who signed up on Jan 31 and came back on Feb 1 is active in month 1).

Months that are not observable yet (after March 2024) must be NULL, not 0.

Example shape: `2024-01 | 779 | 100.0 | 58.3 | 38.3`.""",
     hint1="Signal: \"cohort by first month, activity by months since\". Pattern: month index = year * 12 + month, "
           "the difference gives k; then COUNT(DISTINCT CASE WHEN k = ... ) / cohort size.",
     hint2="1. CTE act: DISTINCT user, cohort month, k = month index of activity minus month index of signup.\n"
           "2. CTE size: users per cohort.\n"
           "3. Join and pivot with `COUNT(DISTINCT CASE WHEN k = 1 THEN user_id END)`. Wrap m2 in a CASE that "
           "returns NULL when cohort month + 2 is after the last data month.",
     solution="""WITH act AS (
    SELECT DISTINCT d.user_id,
           substr(u.signup_date, 1, 7) AS cohort,
           (CAST(substr(d.activity_date, 1, 4) AS INTEGER) * 12 + CAST(substr(d.activity_date, 6, 2) AS INTEGER))
         - (CAST(substr(u.signup_date, 1, 4) AS INTEGER) * 12 + CAST(substr(u.signup_date, 6, 2) AS INTEGER)) AS k
    FROM daily_activity d
    JOIN app_users u ON u.user_id = d.user_id
), size AS (
    SELECT substr(signup_date, 1, 7) AS cohort, COUNT(*) AS users
    FROM app_users
    GROUP BY substr(signup_date, 1, 7)
), last AS (
    SELECT MAX(substr(activity_date, 1, 7)) AS last_month FROM daily_activity
)
SELECT s.cohort, s.users,
       ROUND(100.0 * COUNT(DISTINCT CASE WHEN a.k = 0 THEN a.user_id END) / s.users, 1) AS m0,
       CASE WHEN date(s.cohort || '-01', '+1 month') <= l.last_month || '-01'
            THEN ROUND(100.0 * COUNT(DISTINCT CASE WHEN a.k = 1 THEN a.user_id END) / s.users, 1) END AS m1,
       CASE WHEN date(s.cohort || '-01', '+2 month') <= l.last_month || '-01'
            THEN ROUND(100.0 * COUNT(DISTINCT CASE WHEN a.k = 2 THEN a.user_id END) / s.users, 1) END AS m2
FROM size s
JOIN act a ON a.cohort = s.cohort
CROSS JOIN last l
GROUP BY s.cohort, s.users, l.last_month
ORDER BY s.cohort""",
     why="The month index turns calendar months into integers, so 'months since signup' is a subtraction that "
         "works across years. Conditional COUNT(DISTINCT) pivots k into columns. m0 is 100% because every user is "
         "active on signup day. The February cohort's month 2 is April, which is not in the data, so it must be "
         "NULL: a 0 would read as \"everybody churned\". PostgreSQL: "
         "`(EXTRACT(YEAR FROM age(date_trunc('month', activity_date), date_trunc('month', signup_date))) * 12 + "
         "EXTRACT(MONTH FROM age(...)))`, or simply compare `date_trunc('month', ...)` values.",
     complexity="One pass over daily_activity with a join to users, then a small group by.",
     mistakes="Dividing by the number of active users in month 0 instead of the cohort size (same here, different "
              "when users can sign up without being active). Days / 30 instead of calendar months. Showing 0 for "
              "unobserved cells.",
     learn=["sql-retention", "sql-pivot", "sql-case-when"])

# ---------------------------------------------------------------- Q3 real cohort retention (retail)
ex.q("Do gift-shop customers come back?", minutes=7, kind="sql",
     prompt="""Online Retail (real). A customer's **cohort** is the month of their first purchase (ignore missing
`customer_id` and cancellation invoices starting with 'C'). For each cohort return `cohort` ('YYYY-MM'),
`customers` and the percent who bought again in month +1, +2 and +3 (`m1`, `m2`, `m3`, 1 decimal). Cells after the
last month of data must be NULL.

Then name two reasons why the 2010-12 cohort looks so much better than the others.""",
     hint1="Pattern: same cohort template as Q2, but the cohort is the first purchase month (MIN per customer) "
           "instead of a signup date.",
     hint2="1. CTE buys: DISTINCT customer and month index (`year * 12 + month`).\n2. CTE firsts: MIN month index "
           "per customer.\n3. k = month index minus cohort index; pivot with COUNT(DISTINCT CASE ...); NULL when "
           "cohort + k is after the last month index. `printf('%d-%02d', ...)` turns the index back into text.",
     solution="""WITH buys AS (
    SELECT DISTINCT customer_id,
           CAST(substr(invoice_date, 1, 4) AS INTEGER) * 12 + CAST(substr(invoice_date, 6, 2) AS INTEGER) AS mi
    FROM retail
    WHERE customer_id IS NOT NULL AND invoice_no NOT LIKE 'C%'
), firsts AS (
    SELECT customer_id, MIN(mi) AS cohort_mi FROM buys GROUP BY customer_id
), joined AS (
    SELECT f.cohort_mi, b.mi - f.cohort_mi AS k, b.customer_id
    FROM buys b
    JOIN firsts f ON f.customer_id = b.customer_id
), last AS (
    SELECT MAX(mi) AS last_mi FROM buys
)
SELECT printf('%d-%02d', (cohort_mi - 1) / 12, (cohort_mi - 1) % 12 + 1) AS cohort,
       COUNT(DISTINCT CASE WHEN k = 0 THEN customer_id END) AS customers,
       CASE WHEN cohort_mi + 1 <= last_mi THEN ROUND(100.0 * COUNT(DISTINCT CASE WHEN k = 1 THEN customer_id END)
            / COUNT(DISTINCT CASE WHEN k = 0 THEN customer_id END), 1) END AS m1,
       CASE WHEN cohort_mi + 2 <= last_mi THEN ROUND(100.0 * COUNT(DISTINCT CASE WHEN k = 2 THEN customer_id END)
            / COUNT(DISTINCT CASE WHEN k = 0 THEN customer_id END), 1) END AS m2,
       CASE WHEN cohort_mi + 3 <= last_mi THEN ROUND(100.0 * COUNT(DISTINCT CASE WHEN k = 3 THEN customer_id END)
            / COUNT(DISTINCT CASE WHEN k = 0 THEN customer_id END), 1) END AS m3
FROM joined
CROSS JOIN last
GROUP BY cohort_mi, last_mi
ORDER BY cohort_mi""",
     why="Same cohort logic on real data. The 2010-12 cohort keeps 32% to 38% while later cohorts keep about 15% "
         "to 25%. Reasons: (1) left censoring: the shop existed before the data starts, so 2010-12 \"new\" customers "
         "include all loyal existing customers seen for the first time; (2) many customers are wholesalers who "
         "buy every month. Also note right censoring at the end: 2011-12 has only 9 days, so the last observed "
         "cell of each cohort (for example 2011-09 m3 = 11.4) is too low. Exclude or flag partial months.",
     complexity="DISTINCT over about 400k lines, then joins and a group by on about 13k customer-months.",
     mistakes="Counting rows instead of distinct customers. Using the first invoice in the whole table as "
              "\"new\" without thinking about data that starts mid-life. Letting the partial last month look "
              "like a real drop.",
     learn=["sql-retention", "sql-dates", "sql-dedup-cleaning"])

# ---------------------------------------------------------------- Q4 growth accounting
ex.q("New, retained, resurrected, churned", minutes=8, kind="sql",
     prompt="""Shopping app. Monthly **growth accounting**. A user is active in a month if they have any
`daily_activity` row in it. For each month M:
- `new_users`: active in M, and M is their first active month;
- `retained`: active in M and in M - 1;
- `resurrected`: active in M, not in M - 1, but active at some point before;
- `churned`: active in M - 1 but not in M;
- `mau`: active in M (= new + retained + resurrected);
- `quick_ratio` = (new + resurrected) / churned (2 decimals; NULL when churned is 0).

Example: a user active in January and March, but not February, is churned in February and resurrected in March.

What does a quick ratio below 1 tell the PM?""",
     hint1="Signal: compare each user's month with the previous / next month. Pattern: a (user, month) table "
           "self joined to itself on the previous month (LEFT JOIN, IS NULL means \"not active then\").",
     hint2="1. CTE m: DISTINCT user_id, month. CTE firsts: MIN(month) per user.\n"
           "2. Active side: m cur LEFT JOIN m prev ON same user AND prev.month = month before cur.month; CASE "
           "counts per month.\n"
           "3. Churn side: m prev LEFT JOIN m nxt ON the next month; rows where nxt IS NULL, grouped by the next "
           "month. 4. Join both on month. Month arithmetic: `strftime('%Y-%m', date(month || '-01', '-1 month'))`.",
     solution="""WITH m AS (
    SELECT DISTINCT user_id, substr(activity_date, 1, 7) AS month FROM daily_activity
), firsts AS (
    SELECT user_id, MIN(month) AS first_month FROM m GROUP BY user_id
), active AS (
    SELECT cur.month,
           COUNT(*) AS mau,
           SUM(CASE WHEN cur.month = f.first_month THEN 1 ELSE 0 END) AS new_users,
           SUM(CASE WHEN prev.user_id IS NOT NULL THEN 1 ELSE 0 END) AS retained,
           SUM(CASE WHEN prev.user_id IS NULL AND cur.month > f.first_month THEN 1 ELSE 0 END) AS resurrected
    FROM m cur
    JOIN firsts f ON f.user_id = cur.user_id
    LEFT JOIN m prev ON prev.user_id = cur.user_id
                    AND prev.month = strftime('%Y-%m', date(cur.month || '-01', '-1 month'))
    GROUP BY cur.month
), churn AS (
    SELECT strftime('%Y-%m', date(prev.month || '-01', '+1 month')) AS month, COUNT(*) AS churned
    FROM m prev
    LEFT JOIN m nxt ON nxt.user_id = prev.user_id
                   AND nxt.month = strftime('%Y-%m', date(prev.month || '-01', '+1 month'))
    WHERE nxt.user_id IS NULL
    GROUP BY strftime('%Y-%m', date(prev.month || '-01', '+1 month'))
)
SELECT a.month, a.mau, a.new_users, a.retained, a.resurrected,
       COALESCE(c.churned, 0) AS churned,
       ROUND(1.0 * (a.new_users + a.resurrected) / NULLIF(c.churned, 0), 2) AS quick_ratio
FROM active a
LEFT JOIN churn c ON c.month = a.month
ORDER BY a.month""",
     why="Every active user-month falls in exactly one of new / retained / resurrected, so they add up to MAU "
         "(a good check: 644 + 78 = 722 in March). Churn lives on the other side (users who are missing), so it "
         "needs its own anti join (LEFT JOIN ... IS NULL). In March no new users arrive (signups ended in "
         "February), 531 users churn and the quick ratio is 0.15: the product is shrinking, because far more "
         "users leave than come in or come back. Above 1 means growth; healthy consumer apps aim well above 1. "
         "The churn CTE also produces a row for April (churned from March); the LEFT JOIN from active months "
         "drops it.",
     complexity="A few passes over the user-month table (about 2,700 rows) with index-like joins on user and month.",
     mistakes="Counting churn from the current month (impossible: churned users have no row in M). Treating "
              "a returning user as new. Forgetting NULLIF and dividing by 0 in January.",
     learn=["sql-retention", "sql-self-join", "stats-product-metrics"])

# ---------------------------------------------------------------- Q5 review: self join on dates
ex.q("Back the next day", minutes=5, kind="sql", review=True,
     prompt="""Shopping app. For each day from **2024-03-01 to 2024-03-30**, return `activity_date`, `dau`,
`back_next_day` (how many of that day's active users are also active the next day) and `pct_back` (1 decimal).

Example: if 260 users are active on Mar 1 and 195 of them are active on Mar 2, pct_back is 75.0.

Why does the question stop at March 30?""",
     hint1="Pattern: self join of daily_activity to itself: same user, date + 1 day; LEFT JOIN so the denominator "
           "keeps everybody.",
     hint2="1. `daily_activity a LEFT JOIN daily_activity b ON b.user_id = a.user_id AND b.activity_date = "
           "date(a.activity_date, '+1 day')`.\n2. Group by a.activity_date: COUNT(*) for dau, COUNT(b.user_id) "
           "for back_next_day.",
     solution="""SELECT a.activity_date,
       COUNT(*)          AS dau,
       COUNT(b.user_id)  AS back_next_day,
       ROUND(100.0 * COUNT(b.user_id) / COUNT(*), 1) AS pct_back
FROM daily_activity a
LEFT JOIN daily_activity b
       ON b.user_id = a.user_id
      AND b.activity_date = date(a.activity_date, '+1 day')
WHERE a.activity_date >= '2024-03-01' AND a.activity_date <= '2024-03-30'
GROUP BY a.activity_date
ORDER BY a.activity_date""",
     why="The self join pairs each user-day with the same user's next day. COUNT(*) counts all rows of `a` (the "
         "LEFT JOIN keeps them) and COUNT(b.user_id) only the matched ones. Day-over-day return is about 65% to "
         "76%. March 31 is the last day of data, so its \"next day\" is unknown: including it would show a fake "
         "0%. The same logic with LEAD is possible, but the self join reads more directly as \"exists on date + 1\".",
     complexity="One lookup per user-day on (user_id, activity_date).",
     mistakes="Inner join (dau becomes back_next_day). Joining on date only, not on user. Including the last day "
              "of data.",
     learn=["sql-self-join", "sql-dates", "sql-retention"])

ex.save()
