import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
from sql_mid_data import build_setup

ex = Exam(18, "sql")
build_setup(ex, "chinook", "app", "retail", "cookie")

# ---------------------------------------------------------------- Q1 ARPU vs ARPPU
ex.q("Which channel brings valuable users?", minutes=6, kind="sql",
     prompt="""Shopping app (made up). Per acquisition `channel` return `users`, `buyers` (users with at least one
completed order), `buyer_pct` (1 decimal), `arpu` (completed revenue per user, all users in the denominator) and
`arppu` (completed revenue per paying user), both with 2 decimals. Order by arpu, highest first.

Example: 4 users, one of whom spent 100: arpu = 25.00, arppu = 100.00.

Follow-up: paid_social has the lowest arpu. What extra number do you need before cutting its budget?""",
     hint1="Signal: per-user and per-payer averages. Pattern: aggregate revenue per user first, LEFT JOIN to all users, "
           "then ratios with the right denominators (COUNT(*) versus COUNT(r.user_id)) and NULLIF.",
     hint2="1. CTE rev: completed revenue per user.\n2. app_users LEFT JOIN rev; group by channel.\n"
           "3. arpu = `COALESCE(SUM(revenue), 0) / COUNT(*)`; arppu = `SUM(revenue) / NULLIF(COUNT(r.user_id), 0)`.",
     solution="""WITH rev AS (
    SELECT user_id, SUM(amount) AS revenue
    FROM purchases
    WHERE status = 'completed'
    GROUP BY user_id
)
SELECT u.channel,
       COUNT(*)                                          AS users,
       COUNT(r.user_id)                                  AS buyers,
       ROUND(100.0 * COUNT(r.user_id) / COUNT(*), 1)     AS buyer_pct,
       ROUND(COALESCE(SUM(r.revenue), 0) / COUNT(*), 2)  AS arpu,
       ROUND(SUM(r.revenue) / NULLIF(COUNT(r.user_id), 0), 2) AS arppu
FROM app_users u
LEFT JOIN rev r ON r.user_id = u.user_id
GROUP BY u.channel
ORDER BY arpu DESC""",
     why="ARPU = buyer rate x ARPPU, so it mixes how many pay with how much they pay. Referral users pay the most "
         "per payer; paid_social has both a lower buyer rate and a lower ARPPU. Pre-aggregating revenue per user "
         "before the join keeps one row per user, so COUNT(*) is the number of users. NULLIF(x, 0) turns a zero "
         "denominator into NULL, so a channel without buyers returns NULL instead of an error. Follow-up: the cost "
         "per acquired user (CAC). A low-ARPU channel can still be the most profitable if it is cheap, and the "
         "comparison should use the same observation window per user.",
     complexity="Group by over purchases, a join to 1,500 users, a group by on 4 channels.",
     mistakes="Joining raw purchases to users and then COUNT(*) (counts orders, not users). Dividing by buyers for "
              "ARPU. Integer division in PostgreSQL when both sides are integers (`buyers / users` is 0).",
     learn=["sql-ratios", "sql-left-join-nulls", "stats-product-metrics"])

# ---------------------------------------------------------------- Q2 conditional rates on a real A/B test
ex.q("Cookie Cats: more than one retention number", minutes=6, kind="sql",
     prompt="""`cookie_cats` (real mobile-game test; `retention_1` and `retention_7` are 0/1). Per `version` return
`players`, `d1_pct`, `d7_pct`, `d7_given_d1_pct` (of players retained on day 1, the percent also retained on day 7)
and `d7_pct_30plus` (day 7 retention among players with at least 30 rounds), all with 2 decimals.

Example: 10 players, 4 retained on day 1 and 2 of those on day 7: d7_given_d1_pct = 50.00.

Why can `d7_pct_30plus` be misleading as an experiment metric here?""",
     hint1="Pattern: rates as averages of 0/1 columns; a conditional rate has a conditional denominator "
           "(SUM over the condition, or AVG of a CASE without ELSE).",
     hint2="1. `AVG(retention_1)` is the D1 rate.\n2. Conditional: `SUM(retention_7 * retention_1) / "
           "NULLIF(SUM(retention_1), 0)`.\n3. Subgroup: `AVG(CASE WHEN sum_gamerounds >= 30 THEN retention_7 END)`.",
     solution="""SELECT version,
       COUNT(*) AS players,
       ROUND(100.0 * AVG(retention_1), 2) AS d1_pct,
       ROUND(100.0 * AVG(retention_7), 2) AS d7_pct,
       ROUND(100.0 * SUM(retention_7 * retention_1) / NULLIF(SUM(retention_1), 0), 2) AS d7_given_d1_pct,
       ROUND(100.0 * AVG(CASE WHEN sum_gamerounds >= 30 THEN retention_7 END), 2) AS d7_pct_30plus
FROM cookie_cats
GROUP BY version""",
     why="AVG of a 0/1 column is a proportion; multiplying two 0/1 columns is an AND. Moving the gate to level 40 "
         "lowers D7 retention from 19.02% to 18.20%, and D1 slightly. `d7_pct_30plus` conditions on a "
         "post-treatment variable: the gate itself changes how many rounds people play, so the players with 30+ "
         "rounds are a different mix in each arm and the comparison is no longer randomised. Use it to explore, "
         "not to decide. In PostgreSQL booleans need a cast: `AVG(retention_7::int)`.",
     complexity="One pass over 90,189 rows.",
     mistakes="`ELSE 0` in the subgroup average (adds players with fewer rounds as zeros). Dividing D7 by all "
              "players when the question asks \"given D1\". Treating a subgroup filtered on behaviour after "
              "assignment as a fair comparison.",
     learn=["sql-ratios", "sql-case-when", "stats-ab-pitfalls"])

# ---------------------------------------------------------------- Q3 share inside a group (Chinook)
ex.q("Genre mix of the biggest markets", minutes=6, kind="sql",
     prompt="""Chinook. For the **5 customer countries with the most revenue**, return `country`, `revenue` and the
**share of that country's revenue** coming from Rock, Latin, Metal and everything else (`rock_pct`, `latin_pct`,
`metal_pct`, `other_pct`, 1 decimal; the four add up to about 100).

Example: a country with revenue 200 of which Rock is 70 has rock_pct = 35.0.""",
     hint1="Pattern: part / whole inside a group: `SUM(CASE WHEN genre = 'Rock' THEN amount ELSE 0 END) / SUM(amount)` "
           "per country. The top 5 countries come from a separate CTE.",
     hint2="1. CTE lines: country, genre, amount (UnitPrice * Quantity), with the joins.\n"
           "2. CTE top5: countries ordered by SUM(amount) DESC LIMIT 5.\n"
           "3. Group lines by country (only top5) with the four conditional sums divided by the total.",
     solution="""WITH lines AS (
    SELECT c.Country AS country, g.Name AS genre, il.UnitPrice * il.Quantity AS amount
    FROM InvoiceLine il
    JOIN Invoice i  ON i.InvoiceId = il.InvoiceId
    JOIN Customer c ON c.CustomerId = i.CustomerId
    JOIN Track t    ON t.TrackId = il.TrackId
    JOIN Genre g    ON g.GenreId = t.GenreId
), top5 AS (
    SELECT country FROM lines GROUP BY country ORDER BY SUM(amount) DESC LIMIT 5
)
SELECT country,
       ROUND(SUM(amount), 2) AS revenue,
       ROUND(100.0 * SUM(CASE WHEN genre = 'Rock'  THEN amount ELSE 0 END) / SUM(amount), 1) AS rock_pct,
       ROUND(100.0 * SUM(CASE WHEN genre = 'Latin' THEN amount ELSE 0 END) / SUM(amount), 1) AS latin_pct,
       ROUND(100.0 * SUM(CASE WHEN genre = 'Metal' THEN amount ELSE 0 END) / SUM(amount), 1) AS metal_pct,
       ROUND(100.0 * SUM(CASE WHEN genre NOT IN ('Rock', 'Latin', 'Metal') THEN amount ELSE 0 END)
             / SUM(amount), 1) AS other_pct
FROM lines
WHERE country IN (SELECT country FROM top5)
GROUP BY country
ORDER BY revenue DESC""",
     why="Conditional sums over the same group give numerator and denominator in one pass, so the shares are "
         "consistent and add to 100. Brazil leans most on Rock (42.2%) and Latin (27.6%); the USA is the most "
         "diverse (40.9% other). An alternative is one row per (country, genre) with "
         "`amount / SUM(amount) OVER (PARTITION BY country)`, better when there are many categories.",
     complexity="One pass over 2,240 lines plus the top-5 subquery.",
     mistakes="Dividing by the global revenue instead of the country revenue. Using AVG(CASE ...) (averages line "
              "amounts, not a share). Forgetting the 'other' bucket so the columns do not add up.",
     learn=["sql-ratios", "sql-case-when", "sql-pivot"])

# ---------------------------------------------------------------- Q4 ratio of sums vs average of ratios (retail)
ex.q("Average order value, two ways", minutes=7, kind="sql",
     prompt="""Online Retail (real). Use non-cancelled invoices with a `customer_id`. An order is one `invoice_no`;
its value is `SUM(quantity * unit_price)`. For countries with **at least 25 customers**, return `customers`, `orders`,
`aov_all_orders` (total revenue / total orders) and `avg_customer_aov` (compute each customer's own AOV, then average
those), 2 decimals, most customers first.

Example: customer A has 1 order of 1,000; customer B has 9 orders of 100. aov_all_orders = 1,900 / 10 = 190;
avg_customer_aov = (1,000 + 100) / 2 = 550.

Which one would you put on a dashboard, and why do France and Germany swap places between the two columns?""",
     hint1="Signal: \"average of a ratio\". Pattern: ratio of sums (weights each order equally) versus average of "
           "per-unit ratios (weights each customer equally). Compute both from a per-customer table.",
     hint2="1. CTE inv: one row per invoice with its value.\n2. CTE per_cust: revenue and order count per (country, "
           "customer).\n3. `SUM(revenue) / SUM(orders)` and `AVG(revenue / orders)` per country, HAVING COUNT(*) >= 25.",
     solution="""WITH inv AS (
    SELECT invoice_no, customer_id, country, SUM(quantity * unit_price) AS amount
    FROM retail
    WHERE customer_id IS NOT NULL AND invoice_no NOT LIKE 'C%'
    GROUP BY invoice_no, customer_id, country
), per_cust AS (
    SELECT country, customer_id, SUM(amount) AS revenue, COUNT(*) AS orders
    FROM inv
    GROUP BY country, customer_id
)
SELECT country,
       COUNT(*)                            AS customers,
       SUM(orders)                         AS orders,
       ROUND(SUM(revenue) / SUM(orders), 2) AS aov_all_orders,
       ROUND(AVG(revenue / orders), 2)      AS avg_customer_aov
FROM per_cust
GROUP BY country
HAVING COUNT(*) >= 25
ORDER BY customers DESC""",
     why="The two answer different questions. Ratio of sums = \"what is a typical order worth\" (customers with "
         "many orders weigh more). Average of ratios = \"what is a typical customer's order worth\" (each customer "
         "weighs 1). France has a higher order-weighted AOV (537.34 versus 500.80), Germany a higher "
         "customer-weighted one (542.89 versus 464.41): in France the frequent buyers place big orders, in Germany "
         "some rare buyers do. For a revenue dashboard use the ratio of sums (it adds up to total revenue); "
         "always say which one you report. In A/B tests a ratio metric needs the delta method because the unit of "
         "randomisation (user) differs from the unit of the metric (order).",
     complexity="Two group bys over about 400k lines.",
     mistakes="`AVG(amount)` on line level (that is average line value, not order value). Mixing both definitions "
              "across reports. `revenue / orders` with integer columns in PostgreSQL (truncates).",
     learn=["sql-ratios", "stats-ratio-metrics"])

# ---------------------------------------------------------------- Q5 review: time-boxed funnel by cohort
ex.q("Bought within two weeks of signup", minutes=5, kind="sql", review=True,
     prompt="""Shopping app. Per signup month (`cohort`), return `users`, `bought_14d` (first order of any status
placed less than 14 days after the signup date, i.e. before `date(signup_date, '+14 day')`) and `pct_14d`
(1 decimal), plus `pct_ever` (bought at any time in the data).

Why is `pct_ever` not a fair comparison between the January and February cohorts, while `pct_14d` is?""",
     hint1="Pattern: a time-bounded funnel: first purchase time per user, LEFT JOIN to users, a CASE on the time "
           "window.",
     hint2="1. CTE first_buy: MIN(order_time) per user.\n2. app_users LEFT JOIN first_buy; "
           "`SUM(CASE WHEN f.t < date(u.signup_date, '+14 day') THEN 1 ELSE 0 END)`.",
     solution="""WITH first_buy AS (
    SELECT user_id, MIN(order_time) AS t FROM purchases GROUP BY user_id
)
SELECT substr(u.signup_date, 1, 7) AS cohort,
       COUNT(*) AS users,
       SUM(CASE WHEN f.t < date(u.signup_date, '+14 day') THEN 1 ELSE 0 END) AS bought_14d,
       ROUND(100.0 * SUM(CASE WHEN f.t < date(u.signup_date, '+14 day') THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_14d,
       ROUND(100.0 * SUM(CASE WHEN f.t IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_ever
FROM app_users u
LEFT JOIN first_buy f ON f.user_id = u.user_id
GROUP BY substr(u.signup_date, 1, 7)
ORDER BY cohort""",
     why="A NULL first purchase makes the CASE false, so non-buyers count as 0. January users had about a month "
         "longer to buy, so `pct_ever` (29.3% versus 26.9%) is biased toward older cohorts. A fixed window gives "
         "every user the same chance: 20.5% versus 19.7%, nearly equal. Comparing a timestamp with a date string "
         "works because 'YYYY-MM-DD' sorts before 'YYYY-MM-DD HH:MM:SS' of the same day.",
     complexity="Group by over purchases, a join to users.",
     mistakes="Writing `<= date(...)` and expecting the whole last day to count: as text '2024-01-15 08:00:00' is "
              "greater than '2024-01-15', so it is excluded. Comparing cohorts "
              "with open-ended windows. Inner join (drops non-buyers from the denominator).",
     learn=["sql-funnels", "sql-retention", "sql-dates"])

ex.save()
