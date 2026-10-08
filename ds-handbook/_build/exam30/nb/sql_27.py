import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam
from sql_hard_tables import load, put_doc

SS = ("DataLemur Samsung SQL questions (inspiration, own wording and data)",
      "https://datalemur.com/blog/samsung-sql-interview-questions")

INTRO = ("**Company style: Samsung.** Devices, firmware, quality and sales data. Samsung data science rounds often "
         "mix SQL with a product or quality question (did the update cause crashes? which phones do users upgrade "
         "to?). Normalise by exposure, and say what could confound the comparison.")

ex = Exam(27, "sql", intro=INTRO)
code, doc = load("device", "northwind")
ex.setup(code, data=True)
put_doc(ex, doc)

ex.q("Where do users go when they replace a phone?", minutes=6, kind="sql", review=True, source=SS,
     prompt="""`devices` holds every phone a user activated; a user's next device replaces the previous one. Using a
**self-join** (no LEAD), pair each device with the SAME user's very next device. Return the transition matrix:
`from_series`, `to_series`, `switches`, `pct_of_from` (share of all transitions that leave `from_series`, 1 decimal)
and `avg_days` between the two activations (integer). Order by `from_series`, then `switches` descending.

Example: a user with S21 (2021), A53 (2022), S23 (2023) gives two transitions: S to A and A to S.

*Follow-up:* rewrite the pairing with a window function. Which version would you use on 1 billion rows?""",
     hint1="Signal: 'the very next row of the same user' without LEAD. Pattern: self-join on user with a later date, "
           "plus NOT EXISTS for a device in between; then a ratio with a window SUM over groups.",
     hint2="1. `devices d1 JOIN devices d2 ON d2.user_id = d1.user_id AND d2.activated_at > d1.activated_at`.\n"
           "2. `WHERE NOT EXISTS (SELECT 1 FROM devices d3 WHERE same user AND d1 < d3 < d2)`.\n"
           "3. GROUP BY d1.series, d2.series; `SUM(COUNT(*)) OVER (PARTITION BY d1.series)` as the denominator.",
     solution="""SELECT d1.series AS from_series, d2.series AS to_series,
  COUNT(*) AS switches,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY d1.series), 1) AS pct_of_from,
  CAST(ROUND(AVG(julianday(d2.activated_at) - julianday(d1.activated_at))) AS INTEGER) AS avg_days
FROM devices d1
JOIN devices d2
  ON d2.user_id = d1.user_id AND d2.activated_at > d1.activated_at
WHERE NOT EXISTS (
  SELECT 1 FROM devices d3
  WHERE d3.user_id = d1.user_id
    AND d3.activated_at > d1.activated_at
    AND d3.activated_at < d2.activated_at
)
GROUP BY d1.series, d2.series
ORDER BY d1.series, switches DESC""",
     why="The join alone pairs a device with ALL later devices; NOT EXISTS keeps only the immediate successor. "
         "`SUM(COUNT(*)) OVER (...)` is a window over the grouped result, so the row share needs no second query. "
         "S users are the most loyal (89.9% stay in S); Z Flip users leave most often (22.2% go to S, after only 276 "
         "days on average). Follow-up: `LEAD(series) OVER (PARTITION BY user_id ORDER BY activated_at)` is one sort and "
         "scales linearly; the self-join with NOT EXISTS is quadratic per user. Use LEAD at scale; know the self-join "
         "for engines or exams that forbid windows.",
     complexity="Self-join: O(sum of k^2) pairs per user (k = devices per user, small here). LEAD: O(n log n).",
     mistakes="Forgetting NOT EXISTS (S21 to S23 appears as a fake skip transition). Denominator = all transitions "
              "instead of transitions from the same series. Ties: two devices on the same day need a tiebreaker (device_id).",
     learn=["sql-self-join", "sql-ratios"])

ex.q("Steps from a watch that syncs many times a day", minutes=5, kind="sql", review=True, source=SS,
     prompt="""`health_steps` gets one row per sync, and `steps` is the day's total **so far** at sync time. Some syncs
were uploaded twice. The true daily steps of a user is the value of the **latest** sync of that day. Return one row:
`user_days`, `avg_steps` (true daily steps averaged over user-days, integer), `pct_10k` (% of user-days with at least
10,000 steps, 1 decimal) and `naive_avg` (what you get if you SUM all rows per user-day, integer).

Example: syncs at 10:00 (2,100), 15:00 (6,500), 15:00 again (6,500, a duplicate upload), 21:00 (9,800): the day's
steps are 9,800; the naive SUM gives 24,900.""",
     hint1="Signal: cumulative snapshots plus duplicate uploads. Pattern: dedup by keeping the latest row per key with "
           "ROW_NUMBER (duplicates disappear on the way).",
     hint2="1. `ROW_NUMBER() OVER (PARTITION BY user_id, step_date ORDER BY synced_at DESC, steps DESC)`, keep rn = 1.\n"
           "2. Aggregate: COUNT, AVG(steps), AVG(CASE WHEN steps >= 10000 ...).\n"
           "3. Naive: AVG of SUM(steps) per user-day in a scalar subquery.",
     solution="""WITH ranked AS (
  SELECT user_id, step_date, steps,
    ROW_NUMBER() OVER (PARTITION BY user_id, step_date
                       ORDER BY synced_at DESC, steps DESC) AS rn
  FROM health_steps
), final AS (
  SELECT user_id, step_date, steps FROM ranked WHERE rn = 1
)
SELECT COUNT(*) AS user_days,
  CAST(ROUND(AVG(steps)) AS INTEGER) AS avg_steps,
  ROUND(100.0 * AVG(CASE WHEN steps >= 10000 THEN 1 ELSE 0 END), 1) AS pct_10k,
  (SELECT CAST(ROUND(AVG(s)) AS INTEGER)
   FROM (SELECT SUM(steps) AS s FROM health_steps GROUP BY user_id, step_date)) AS naive_avg
FROM final""",
     why="Each sync is a snapshot of a running total, so the rows of a day must not be added; the last snapshot is the "
         "day's value. ROW_NUMBER with `synced_at DESC` picks it and also drops the duplicate upload (same time, same "
         "value). True average 8,641 steps; the naive SUM says 14,210 (+64%), and would make 10k-step goals look easy. "
         "Because the counter only grows, `MAX(steps)` per day gives the same answer here; say that it relies on that "
         "assumption (a counter reset at midnight or a bad sync breaks it).",
     complexity="One window sort over the syncs.",
     mistakes="SUM per day (counts the same steps several times). DISTINCT only (removes duplicates but still sums "
              "snapshots). Ordering by steps alone without synced_at (fine for a counter, wrong for values that can go down).",
     learn=["sql-dedup-cleaning", "sql-window-ranking"])

ex.q("Did firmware 6.1 increase crashes?", minutes=8, kind="sql", source=SS,
     prompt="""Firmware 6.1 rolled out during May 2024 (`firmware_updates`, version '6.1'). `crash_logs` covers
2024-05-01 to 2024-06-30. For devices that installed 6.1, compare crash rates **per 1,000 device-days** before and after
their own install time, per `model`:
- days before = install time minus 2024-05-01; days after = 2024-07-01 minus install time (fractional days are fine);
- crashes before / after = crashes of that device before / after its install time.

Return `model`, `devices`, `before_per_1k_days`, `after_per_1k_days` (1 decimal) and `ratio` (after rate / before rate,
2 decimals), highest ratio first.

*Follow-up:* the after period is in June, the before period in May. What else could explain a higher ratio, and how do
you check?""",
     hint1="Signal: compare event counts between periods of different length. Pattern: ratios normalised by exposure "
           "(events / time at risk), with the period boundary per device.",
     hint2="1. `up`: MIN(installed_at) of 6.1 per device.\n2. `exposure`: days_before and days_after per device with julianday.\n"
           "3. `crashes`: LEFT JOIN crash_logs, SUM(CASE WHEN crash_time < up_t ...) per device.\n"
           "4. Per model: `1000.0 * SUM(crashes) / SUM(days)` for each period (sum first, then divide).",
     solution="""WITH up AS (
  SELECT device_id, MIN(installed_at) AS up_t
  FROM firmware_updates WHERE version = '6.1'
  GROUP BY device_id
), exposure AS (
  SELECT d.model, u.device_id, u.up_t,
    julianday(u.up_t) - julianday('2024-05-01') AS days_before,
    julianday('2024-07-01') - julianday(u.up_t) AS days_after
  FROM up u JOIN devices d ON d.device_id = u.device_id
), crashes AS (
  SELECT e.device_id,
    SUM(CASE WHEN c.crash_time < e.up_t THEN 1 ELSE 0 END) AS before_n,
    SUM(CASE WHEN c.crash_time >= e.up_t THEN 1 ELSE 0 END) AS after_n
  FROM exposure e
  LEFT JOIN crash_logs c ON c.device_id = e.device_id
  GROUP BY e.device_id
)
SELECT e.model, COUNT(*) AS devices,
  ROUND(1000.0 * SUM(c.before_n) / SUM(e.days_before), 1) AS before_per_1k_days,
  ROUND(1000.0 * SUM(c.after_n) / SUM(e.days_after), 1) AS after_per_1k_days,
  ROUND((1.0 * SUM(c.after_n) / SUM(e.days_after))
        / (1.0 * SUM(c.before_n) / SUM(e.days_before)), 2) AS ratio
FROM exposure e
JOIN crashes c ON c.device_id = e.device_id
GROUP BY e.model
ORDER BY ratio DESC""",
     why="Raw crash counts are meaningless here: a device updated on May 3 has 3 days before and 59 after. Dividing by "
         "device-days (exposure) makes the periods comparable, and summing numerators and denominators per model "
         "before dividing weights each device by its exposure. Galaxy A54 (4.41x) and Z Flip5 (3.27x) jump; the other "
         "models stay near 1. Follow-up: seasonality, app updates in June, or self-selection (early updaters differ). "
         "Use the 20% of devices that did NOT take 6.1 as a control over the same calendar days (a difference in "
         "differences), or compare crashes by app and look at the crash signatures.",
     complexity="One join of crashes to updated devices and two small aggregations.",
     mistakes="Comparing counts, not rates. Averaging per-device rates (devices with 1 day of exposure dominate). "
              "Using a global cutoff date instead of each device's own install time. Inner join that drops "
              "devices with zero crashes (they still contribute exposure).",
     learn=["sql-ratios", "sql-dates"])

ex.q("Best seller: by units or by revenue?", minutes=6, kind="sql", source=SS,
     prompt="""Northwind (real), orders from 2023-01-01 on. Per category, find the top product by **units**
(`SUM(quantity)`) and the top product by **revenue** (`unit_price * quantity * (1 - discount)`). Return `category`,
`top_by_units`, `units`, `top_by_revenue`, `revenue` (rounded) in one row per category, ordered by category.

*Follow-up:* the sales director asks for "our best-selling product". What do you ask back?""",
     hint1="Signal: two different 'top 1 per group' in one row. Pattern: top-N with two RANK windows, then a pivot "
           "with MAX(CASE WHEN rank = 1 ...).",
     hint2="1. `rev`: per category and product, SUM(quantity) and SUM(revenue).\n"
           "2. `RANK() OVER (PARTITION BY category ORDER BY units DESC)` and the same by revenue.\n"
           "3. GROUP BY category with `MAX(CASE WHEN ru = 1 THEN product END)` etc.",
     solution="""WITH rev AS (
  SELECT c.category, p.product,
    SUM(i.quantity) AS units,
    SUM(i.unit_price * i.quantity * (1 - i.discount)) AS revenue
  FROM nw_orders o
  JOIN nw_order_items i ON i.order_id = o.order_id
  JOIN nw_products p ON p.product_id = i.product_id
  JOIN nw_categories c ON c.category_id = p.category_id
  WHERE o.order_date >= '2023-01-01'
  GROUP BY c.category, p.product
), r AS (
  SELECT *,
    RANK() OVER (PARTITION BY category ORDER BY units DESC) AS ru,
    RANK() OVER (PARTITION BY category ORDER BY revenue DESC) AS rr
  FROM rev
)
SELECT category,
  MAX(CASE WHEN ru = 1 THEN product END) AS top_by_units,
  MAX(CASE WHEN ru = 1 THEN units END) AS units,
  MAX(CASE WHEN rr = 1 THEN product END) AS top_by_revenue,
  ROUND(MAX(CASE WHEN rr = 1 THEN revenue END)) AS revenue
FROM r
GROUP BY category
ORDER BY category""",
     why="Two windows over the same aggregated table give both rankings in one pass; the MAX(CASE ...) pivot puts the "
         "two winners side by side. In 2023 the leaders differ in EVERY category: e.g. Beverages sells the most units "
         "of Chartreuse verte but earns the most from the expensive Côte de Blaye. Follow-up: ask 'best by units, "
         "revenue or margin, over which period, and do returns count?'. Units matter for supply planning, revenue or "
         "margin for business value.",
     complexity="One big join and aggregation (44,567 order lines in 2023), then windows over 77 products.",
     mistakes="ORDER BY ... LIMIT 1 (gives one row overall, not per category). ROW_NUMBER hides ties (RANK + MAX shows "
              "one of them; say how you break ties). Forgetting the discount.",
     learn=["sql-top-n", "sql-pivot"])

ex.q("Raise a crash alert", minutes=6, kind="sql", source=SS,
     prompt="""Quality wants an alert when crashes trend up. Daily crashes = rows of `crash_logs` per calendar day. The
**baseline** is the average daily count of 2024-05-01 to 2024-05-07. Compute a 7-day rolling average (the day and the
6 days before it; only days with a full 7-day window) and return the **first 3 days** where the rolling average is at
least 30% above the baseline: `day`, `crashes`, `avg7` (1 decimal), `baseline` (1 decimal).

*Follow-up:* why a rolling average and not the daily count against the baseline?""",
     hint1="Signal: 'rolling 7 days' and 'first day above a threshold'. Pattern: moving average with a ROWS frame, "
           "plus a COUNT over the same frame to require a full window.",
     hint2="1. `daily`: COUNT(*) per date(crash_time).\n"
           "2. `AVG(n) OVER (ORDER BY day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)` and `COUNT(*) OVER (same frame)`.\n"
           "3. `base`: AVG(n) over the first week; CROSS JOIN; filter frame size 7 and avg7 >= 1.3 * baseline; LIMIT 3.",
     solution="""WITH daily AS (
  SELECT date(crash_time) AS day, COUNT(*) AS crashes
  FROM crash_logs
  GROUP BY date(crash_time)
), r AS (
  SELECT day, crashes,
    AVG(crashes) OVER (ORDER BY day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS avg7,
    COUNT(*) OVER (ORDER BY day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS frame_days
  FROM daily
), base AS (
  SELECT AVG(crashes) AS baseline FROM daily
  WHERE day BETWEEN '2024-05-01' AND '2024-05-07'
)
SELECT day, crashes, ROUND(avg7, 1) AS avg7, ROUND(baseline, 1) AS baseline
FROM r CROSS JOIN base
WHERE frame_days = 7 AND avg7 >= 1.3 * baseline
ORDER BY day
LIMIT 3""",
     why="A ROWS frame of 6 PRECEDING plus the current row is a 7 row moving window; it equals 7 days only because "
         "every day has crashes (61 days, 61 rows). With missing days you would first build a date spine. The "
         "baseline is 43.9 crashes a day; the rolling average first passes 1.3x on 2024-05-17 (57.7), about two weeks "
         "into the 6.1 rollout. Follow-up: single days are noisy (2024-05-16 alone had 75 crashes, then it fell back); "
         "a 7-day average removes day-of-week noise and avoids false alarms, at the cost of a few days of delay.",
     complexity="One aggregation and one window over 61 days.",
     mistakes="RANGE instead of ROWS (in PostgreSQL use `RANGE BETWEEN INTERVAL '6 days' PRECEDING AND CURRENT ROW` "
              "if days can be missing). Keeping the first 6 days with partial windows. Comparing with a baseline that "
              "includes the period you are testing.",
     learn=["sql-running-totals", "sql-dates"])

ex.save()
