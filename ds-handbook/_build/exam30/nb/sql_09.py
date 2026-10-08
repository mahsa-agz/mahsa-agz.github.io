import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sql_easy_common import start, nrows

# Day 9 SQL: focus dates (truncate to month/day, date differences, quarters); review CTEs and joins.
ex = start(9)

q1 = """SELECT strftime('%Y-%m', InvoiceDate) AS month,
       COUNT(*) AS invoices,
       ROUND(SUM(Total), 2) AS revenue
FROM Invoice
WHERE InvoiceDate >= '2012-01-01' AND InvoiceDate < '2013-01-01'
GROUP BY month
ORDER BY month"""
ex.q("Monthly revenue in 2012", minutes=4, level="easy", kind="sql",
     prompt="Return one row per month of 2012: `month` (text like `2012-01`), `invoices` and `revenue` "
            "(2 decimals), in calendar order.\n\n"
            f"Expected: {nrows(ex, q1)} rows.",
     hint1="Signal: 'per month'. Pattern: truncate the date to the month, then GROUP BY.",
     hint2="1. strftime('%Y-%m', InvoiceDate) gives `2012-01`. 2. Filter the year with a half-open range. "
           "3. GROUP BY month, ORDER BY month.",
     solution=q1,
     why="Truncating to a month turns many dates into one label to group on. A half-open range `>= start AND < next "
         "start` keeps an index usable and never misses times on the last day. PostgreSQL: "
         "`DATE_TRUNC('month', invoice_date)` or `TO_CHAR(invoice_date, 'YYYY-MM')`.",
     complexity="One scan of Invoice.",
     mistakes="`WHERE strftime('%Y', InvoiceDate) = 2012` compares text with a number in SQLite (no rows); use '2012'. "
              "`BETWEEN '2012-01-01' AND '2012-12-31'` misses `2012-12-31 15:00:00`. Grouping by month number only "
              "(mixes years).",
     learn=["sql-dates"])

q2 = """SELECT DATE(event_time) AS day,
       COUNT(DISTINCT user_id) AS dau,
       COUNT(*) AS events
FROM events
WHERE event_time >= '2024-03-18' AND event_time < '2024-03-25'
GROUP BY day
ORDER BY day"""
ex.q("Daily active users for one week", minutes=4, level="easy", kind="sql",
     prompt="On the made-up `events` table: daily active users (DAU = distinct users with any event that day) for "
            "the week 2024-03-18 to 2024-03-24. Return `day`, `dau` and `events`, by day.\n\n"
            "Follow-up: a day with no events at all would be missing from your result. How would you show it with "
            "0?",
     hint1="Signal: 'per day' and 'distinct users'. Pattern: DATE() of a timestamp, GROUP BY, COUNT(DISTINCT).",
     hint2="1. DATE(event_time) drops the time. 2. WHERE event_time >= '2024-03-18' AND < '2024-03-25'. "
           "3. GROUP BY day with COUNT(DISTINCT user_id).",
     solution=q2,
     why="DAU counts people, not events, so COUNT(DISTINCT user_id). Follow-up: build a calendar of all days "
         "(a recursive CTE or `generate_series` in PostgreSQL), LEFT JOIN the counts to it and COALESCE to 0.",
     complexity="One scan of events.",
     mistakes="COUNT(user_id) (counts events). `event_time <= '2024-03-24'` misses everything after midnight of the "
              "24th, because '2024-03-24 10:00:00' > '2024-03-24' as text.",
     learn=["sql-dates", "sql-aggregation"])

q3 = """WITH activity AS (
    SELECT user_id,
           DATE(MAX(event_time)) AS last_active_day,
           COUNT(DISTINCT DATE(event_time)) AS active_days
    FROM events
    GROUP BY user_id
)
SELECT u.user_id, u.signup_date, a.last_active_day,
       CAST(julianday(a.last_active_day) - julianday(u.signup_date) AS INTEGER) AS days_signup_to_last,
       a.active_days
FROM users u
JOIN activity a ON a.user_id = u.user_id
ORDER BY days_signup_to_last DESC, u.user_id"""
ex.q("How long do users stick around?", minutes=6, level="medium", kind="sql",
     prompt="On the made-up tables: for each user with at least one event, return `user_id`, `signup_date`, "
            "`last_active_day` (date of their latest event), `days_signup_to_last` (whole days from signup to that "
            "day; 0 = only active on the signup day) and `active_days` (number of different days with an event). "
            "Longest span first, ties by user_id.\n\n"
            f"Expected: {nrows(ex, q3)} rows.\n\n"
            "Follow-up: call a user *churned* if their last activity is more than 7 days before 2024-03-31. "
            "How would you count churned users, and what about users with no events at all?",
     hint1="Signal: latest event per user, then a difference between two dates. Pattern: MAX and "
           "COUNT(DISTINCT DATE(...)) per user in a CTE, then date subtraction.",
     hint2="1. CTE: per user, DATE(MAX(event_time)) and COUNT(DISTINCT DATE(event_time)). 2. Join users. "
           "3. SQLite: julianday(a) - julianday(b) gives days. 4. Compare dates, not timestamps (DATE() first).",
     solution=q3,
     why="MAX on ISO timestamps gives the latest one, and DATE() turns timestamps into calendar days, so "
         "COUNT(DISTINCT DATE(...)) counts active days. julianday returns a day number, so the difference is in days. "
         "PostgreSQL: `last_active_day - signup_date` on DATE columns gives an integer. Follow-up: "
         "`SUM(CASE WHEN julianday('2024-03-31') - julianday(last_active_day) > 7 THEN 1 ELSE 0 END)`; users with no "
         "events never activated, so report them separately (or start from users with a LEFT JOIN and count them "
         "as churned, but say which you chose).",
     complexity="One scan of events plus a join with users.",
     mistakes="Subtracting timestamps and getting fractions of a day. COUNT(*) instead of COUNT(DISTINCT DATE(...)) "
              "for active days. Subtracting text columns directly in SQLite (it reads '2024-03-12' as the number 2024, "
              "so the difference is 0).",
     learn=["sql-dates", "sql-cte"])

q4 = """SELECT strftime('%Y', InvoiceDate) AS year,
       (CAST(strftime('%m', InvoiceDate) AS INTEGER) + 2) / 3 AS quarter,
       COUNT(*) AS invoices,
       ROUND(SUM(Total), 2) AS revenue
FROM Invoice
WHERE InvoiceDate >= '2010-01-01' AND InvoiceDate < '2012-01-01'
GROUP BY year, quarter
ORDER BY year, quarter"""
ex.q("Quarterly revenue", minutes=5, level="medium", kind="sql",
     prompt="Return revenue per calendar quarter for 2010 and 2011: `year`, `quarter` (1 to 4), `invoices` and "
            "`revenue` (2 decimals), in time order.\n\n"
            "Example: May is month 5, so it is in quarter 2.",
     hint1="Signal: a period that SQLite has no function for. Pattern: derive it from the month with integer "
           "arithmetic, then GROUP BY year and quarter.",
     hint2="1. Month number: CAST(strftime('%m', InvoiceDate) AS INTEGER). 2. Quarter = (month + 2) / 3 with integer "
           "division. 3. GROUP BY year, quarter.",
     solution=q4,
     why="Integer division maps months 1 to 3 to 1, 4 to 6 to 2, and so on. Grouping by year as well keeps Q1 2010 "
         "and Q1 2011 apart. PostgreSQL: `EXTRACT(QUARTER FROM invoice_date)` or `DATE_TRUNC('quarter', ...)`.",
     complexity="One scan of Invoice.",
     mistakes="Forgetting the CAST (strftime returns text). Grouping by quarter only. Here integer division is what "
              "you want; elsewhere it is a bug.",
     learn=["sql-dates"])

q5 = """WITH views AS (
    SELECT DISTINCT e.user_id, v.creator_id, v.category
    FROM events e
    JOIN videos v ON v.video_id = e.video_id
    WHERE e.event_type = 'view'
      AND v.creator_id <> e.user_id
)
SELECT user_id,
       COUNT(DISTINCT creator_id) AS creators_watched,
       COUNT(DISTINCT category)   AS categories_watched
FROM views
GROUP BY user_id
ORDER BY creators_watched DESC, categories_watched DESC, user_id"""
ex.q("How broad is each viewer's taste?", minutes=5, level="easy", kind="sql", review=True,
     prompt="On the made-up product tables: for each user with at least one view, count the distinct creators and "
            "the distinct categories they watched. Do not count a creator watching their own videos. Return "
            "`user_id`, `creators_watched`, `categories_watched`, broadest first (ties by categories, then user_id).\n\n"
            f"Expected: {nrows(ex, q5)} rows.",
     hint1="Signal: attributes of the video (creator, category) per viewer. Pattern: JOIN events to videos in a CTE, "
           "then COUNT(DISTINCT).",
     hint2="1. CTE: events JOIN videos, views only, exclude rows where creator_id = user_id. 2. GROUP BY user_id. "
           "3. COUNT(DISTINCT creator_id), COUNT(DISTINCT category).",
     solution=q5,
     why="The join brings the creator and category onto each view. DISTINCT counts ignore repeat views. The self-view "
         "filter is a typical product detail examiners expect you to ask about.",
     complexity="O(events + videos).",
     mistakes="COUNT(creator_id) (counts views). Putting the self-view filter on users instead of on the join row.",
     learn=["sql-joins", "sql-cte"])

ex.save()
