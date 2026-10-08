import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam
from sql_hard_tables import load, put_doc

ex = Exam(24, "sql")
code, doc = load("chinook", "northwind", "apps", "retail")
ex.setup(code, data=True)
put_doc(ex, doc)

ex.q("Reporting chain for every employee", minutes=5, kind="sql",
     prompt="""Chinook (real) `Employee` has `ReportsTo` (the manager's EmployeeId; NULL for the top person). Return every
employee with `EmployeeId`, `name` (first + last), `Title`, `level` (0 for the top person, 1 for their direct
reports, ...) and `path`: last names from the top down, joined with ' > '. Order by `path`.

Example: if Adams manages Edwards and Edwards manages Park, Park's row is `level 2, path 'Adams > Edwards > Park'`.

*Follow-up:* the HR table has a data bug: A reports to B and B reports to A. What happens to your query, and how do you protect it?""",
     hint1="Signal: a hierarchy of unknown depth. Pattern: recursive CTE: an anchor (the root) UNION ALL a step that "
           "joins children to the rows found so far.",
     hint2="1. `WITH RECURSIVE chain(...) AS (`\n2. Anchor: `SELECT ..., 0, LastName FROM Employee WHERE ReportsTo IS NULL`.\n"
           "3. Step: `SELECT e..., c.level + 1, c.path || ' > ' || e.LastName FROM Employee e JOIN chain c ON e.ReportsTo = c.EmployeeId`.\n"
           "4. Close the CTE, SELECT from chain ORDER BY path.",
     solution="""WITH RECURSIVE chain(EmployeeId, name, Title, level, path) AS (
  SELECT EmployeeId, FirstName || ' ' || LastName, Title, 0, LastName
  FROM Employee
  WHERE ReportsTo IS NULL
  UNION ALL
  SELECT e.EmployeeId, e.FirstName || ' ' || e.LastName, e.Title,
         c.level + 1, c.path || ' > ' || e.LastName
  FROM Employee e
  JOIN chain c ON e.ReportsTo = c.EmployeeId
)
SELECT EmployeeId, name, Title, level, path
FROM chain
ORDER BY path""",
     why="The anchor returns the root; each pass of the recursive part adds the next level by joining employees whose "
         "manager is already in `chain`; it stops when a pass adds no rows. The path string is built on the way down. "
         "Andrew Adams is level 0; the three Sales Support Agents are level 2 under Edwards. Follow-up: with a cycle "
         "and no root, the anchor finds nothing for those two rows (they never appear); a cycle BELOW a root loops "
         "forever. Protect with a depth limit (`WHERE c.level < 20`) or a visited check "
         "(`WHERE c.path NOT LIKE '%' || e.LastName || '%'`, better on ids); PostgreSQL 14 also has a `CYCLE` clause.",
     complexity="O(n) rows produced for a tree; one join per level.",
     mistakes="Forgetting the RECURSIVE keyword (needed in PostgreSQL and SQLite style). UNION instead of UNION ALL "
              "(extra dedup work; also hides bugs). Starting from the leaves and walking up when the question asks top down.",
     learn=["sql-recursive-cte", "sql-self-join"])

ex.q("Revenue of each manager's whole team", minutes=6, kind="sql",
     prompt="""Northwind (real). Revenue = `unit_price * quantity * (1 - discount)`, orders in **2022**, credited to the
order's `employee_id`. For **every** employee return `name`, `title`, `reports_all` (direct AND indirect reports)
and `team_revenue_2022`: revenue of the employee plus everyone below them (rounded), plus `pct_of_company` (1 decimal).
Order by team revenue descending.

Example: if Fuller manages Buchanan, who manages Suyama, Fuller's team revenue includes Suyama's orders.""",
     hint1="Signal: 'direct and indirect' = the whole subtree. Pattern: recursive CTE that builds (manager, member) "
           "pairs, then a join to revenue and GROUP BY manager.",
     hint2="1. Anchor: every employee is in their own team: `SELECT employee_id, employee_id FROM nw_employees`.\n"
           "2. Step: `SELECT s.manager_id, e.employee_id FROM sub s JOIN nw_employees e ON e.reports_to = s.employee_id`.\n"
           "3. CTE `rev`: 2022 revenue per employee.\n4. `sub LEFT JOIN rev`, GROUP BY manager; `COUNT(*) - 1` = reports.",
     solution="""WITH RECURSIVE sub(manager_id, employee_id) AS (
  SELECT employee_id, employee_id FROM nw_employees
  UNION ALL
  SELECT s.manager_id, e.employee_id
  FROM sub s
  JOIN nw_employees e ON e.reports_to = s.employee_id
), rev AS (
  SELECT o.employee_id, SUM(i.unit_price * i.quantity * (1 - i.discount)) AS revenue
  FROM nw_orders o
  JOIN nw_order_items i ON i.order_id = o.order_id
  WHERE o.order_date >= '2022-01-01' AND o.order_date < '2023-01-01'
  GROUP BY o.employee_id
)
SELECT m.name, m.title, COUNT(*) - 1 AS reports_all,
  ROUND(SUM(r.revenue)) AS team_revenue_2022,
  ROUND(100.0 * SUM(r.revenue) / (SELECT SUM(revenue) FROM rev), 1) AS pct_of_company
FROM sub s
JOIN nw_employees m ON m.employee_id = s.manager_id
LEFT JOIN rev r ON r.employee_id = s.employee_id
GROUP BY s.manager_id, m.name, m.title
ORDER BY team_revenue_2022 DESC""",
     why="Starting the recursion from EVERY employee (not only the root) gives the full subtree of each person in one "
         "query: the pair (manager, member) exists once for every member at any depth. The VP (Andrew Fuller) has all "
         "8 others below him, so his team is 100% of 2022 revenue; Steven Buchanan's team of 3 makes 47.1%. "
         "Pre-aggregating revenue per employee BEFORE joining the tree keeps the join small.",
     complexity="Pairs = sum of subtree sizes (O(n * depth)); revenue is aggregated once.",
     mistakes="Only direct reports (a self-join, not recursion). Joining 600k order lines to the tree before "
              "aggregating (slow, same answer). `COUNT(*)` as reports (it includes the person: subtract 1).",
     learn=["sql-recursive-cte", "sql-aggregation"])

ex.q("Fill the missing days, then take the median", minutes=6, kind="sql", review=True,
     prompt="""UCI Online Retail (real). Daily revenue = `SUM(quantity * unit_price)` of real sales (`invoice_no` not
starting with 'C', `quantity > 0`, `unit_price > 0`) by calendar day of `invoice_date`. Days with no sales do not appear
in the table at all. For **2010-12-01 to 2011-02-28** (90 days) return one row: `days`, `sales_days`,
`median_all_days` (zero-revenue days included), `median_sales_days`, `mean_all_days`, `mean_sales_days` (all rounded
to whole numbers).

*Follow-up:* the shop is closed on Saturdays and over Christmas. Which median would you put in a forecast, and why?""",
     hint1="Signal: 'days with no rows' must count as zero. Pattern: a date spine from a recursive CTE, LEFT JOIN the "
           "data, COALESCE to 0; then medians with ROW_NUMBER / COUNT.",
     hint2="1. `WITH RECURSIVE days(d) AS (SELECT '2010-12-01' UNION ALL SELECT date(d, '+1 day') FROM days WHERE d < '2011-02-28')`.\n"
           "2. `sales`: revenue per `substr(invoice_date, 1, 10)`.\n3. `daily`: days LEFT JOIN sales, COALESCE(revenue, 0).\n"
           "4. Two ranked CTEs (all days / days with revenue > 0) and scalar subqueries for each number.",
     solution="""WITH RECURSIVE days(d) AS (
  SELECT '2010-12-01'
  UNION ALL
  SELECT date(d, '+1 day') FROM days WHERE d < '2011-02-28'
), sales AS (
  SELECT substr(invoice_date, 1, 10) AS d, SUM(quantity * unit_price) AS revenue
  FROM retail
  WHERE invoice_no NOT LIKE 'C%' AND quantity > 0 AND unit_price > 0
  GROUP BY substr(invoice_date, 1, 10)
), daily AS (
  SELECT days.d, COALESCE(s.revenue, 0) AS revenue
  FROM days LEFT JOIN sales s ON s.d = days.d
), r AS (
  SELECT revenue, ROW_NUMBER() OVER (ORDER BY revenue) AS rn, COUNT(*) OVER () AS cnt
  FROM daily
), s AS (
  SELECT revenue, ROW_NUMBER() OVER (ORDER BY revenue) AS rn, COUNT(*) OVER () AS cnt
  FROM daily WHERE revenue > 0
)
SELECT
  (SELECT COUNT(*) FROM daily) AS days,
  (SELECT COUNT(*) FROM daily WHERE revenue > 0) AS sales_days,
  (SELECT ROUND(AVG(revenue)) FROM r WHERE rn IN ((cnt + 1) / 2, (cnt + 2) / 2)) AS median_all_days,
  (SELECT ROUND(AVG(revenue)) FROM s WHERE rn IN ((cnt + 1) / 2, (cnt + 2) / 2)) AS median_sales_days,
  (SELECT ROUND(AVG(revenue)) FROM daily) AS mean_all_days,
  (SELECT ROUND(AVG(revenue)) FROM daily WHERE revenue > 0) AS mean_sales_days""",
     why="Without the spine, the 22 closed days simply do not exist and every daily statistic is computed on 68 days "
         "only: the mean jumps from 22,653 to 29,982. The recursive CTE generates one row per calendar day, and the "
         "LEFT JOIN keeps days without sales. Follow-up: for a calendar forecast (how much per day next quarter) use "
         "all days (median 21,501); to describe a typical trading day use sales days (median 25,834). Saying which "
         "denominator you chose is the point.",
     complexity="The spine is 90 rows; the sales aggregation is one scan.",
     mistakes="Joining the spine with `date(invoice_date) = d` on 500k rows without pre-aggregating (slow). Forgetting "
              "COALESCE (NULLs are skipped by AVG and the median, so zeros vanish again). PostgreSQL has "
              "`generate_series('2010-12-01'::date, '2011-02-28', interval '1 day')` instead of the recursive CTE.",
     learn=["sql-recursive-cte", "sql-median-percentiles", "sql-dates"])

ex.q("Biggest referral trees", minutes=6, kind="sql",
     prompt="""Shopping app (made up). `app_users.referred_by` is the user who invited this user (NULL if nobody did).
A **root** is a user with `referred_by IS NULL`. Everyone invited by a root, by someone they invited, and so on,
belongs to the root's tree. Return the 5 roots with the largest trees: `root_id`, `referred_total` (everyone in the
tree except the root), `direct` (invited by the root personally) and `max_depth` (1 = direct invites only). Ties: lower
`root_id` first.

Example: 2 invites 10 and 11; 10 invites 50: root 2 has referred_total 3, direct 2, max_depth 2.

*Follow-up:* growth wants to reward "super referrers". Is `referred_total` or `direct` the fairer metric?""",
     hint1="Signal: invites of invites of invites. Pattern: recursive CTE that carries the root id and the depth down the tree.",
     hint2="1. Anchor: `SELECT user_id AS root_id, user_id, 0 AS depth FROM app_users WHERE referred_by IS NULL`.\n"
           "2. Step: join `app_users u ON u.referred_by = t.user_id`, keep `t.root_id`, depth + 1.\n"
           "3. GROUP BY root_id: COUNT(*) - 1, SUM(depth = 1), MAX(depth).",
     solution="""WITH RECURSIVE tree(root_id, user_id, depth) AS (
  SELECT user_id, user_id, 0
  FROM app_users
  WHERE referred_by IS NULL
  UNION ALL
  SELECT t.root_id, u.user_id, t.depth + 1
  FROM tree t
  JOIN app_users u ON u.referred_by = t.user_id
)
SELECT root_id,
  COUNT(*) - 1 AS referred_total,
  SUM(CASE WHEN depth = 1 THEN 1 ELSE 0 END) AS direct,
  MAX(depth) AS max_depth
FROM tree
GROUP BY root_id
ORDER BY referred_total DESC, root_id
LIMIT 5""",
     why="Carrying `root_id` unchanged through the recursion labels every descendant with its tree. All 1,500 users "
         "land in exactly one of 1,273 trees (227 users were referred), and the deepest chain is 3 levels. User 2 "
         "leads with 8 people in the tree but only 2 direct invites. Follow-up: `direct` measures the user's own "
         "action; `referred_total` rewards being early (old users have had more time for their invitees to invite). "
         "Use direct invites for rewards, and the tree size to study virality (k-factor per level).",
     complexity="Every user is visited once: O(n) rows, one join per level.",
     mistakes="Self-joining a fixed number of times (misses deeper levels). Starting from all users instead of roots "
              "(each subtree is counted several times). No cycle guard for real referral data (add a depth limit).",
     learn=["sql-recursive-cte"])

ex.q("Users who came back after a long break", minutes=5, kind="sql", review=True,
     prompt="""Shopping app (made up), `daily_activity`. A **comeback** is an active day that follows 14 or more inactive
days in a row (e.g. active Jan 1, next active Jan 16: 14 inactive days, a comeback). Per `platform` return `users`
(users with any activity), `resurrected` (users with at least one comeback), `resurrected_pct` (1 decimal) and
`longest_gap` (the longest run of inactive days seen on that platform, as an integer). Order by platform.""",
     hint1="Signal: the gap between one active day and the next. Pattern: gaps and islands with LAG: gap = days between "
           "consecutive rows minus 1.",
     hint2="1. `julianday(d) - julianday(LAG(d) OVER (PARTITION BY user_id ORDER BY d)) - 1` = inactive days before d.\n"
           "2. Per user: MAX(gap), SUM(gap >= 14).\n3. Join platform, aggregate.",
     solution="""WITH g AS (
  SELECT user_id, activity_date,
    CAST(julianday(activity_date)
      - julianday(LAG(activity_date) OVER (PARTITION BY user_id ORDER BY activity_date)) - 1 AS INTEGER) AS gap_days
  FROM daily_activity
), per_user AS (
  SELECT user_id, MAX(gap_days) AS longest_gap,
    SUM(CASE WHEN gap_days >= 14 THEN 1 ELSE 0 END) AS comebacks
  FROM g
  GROUP BY user_id
)
SELECT u.platform, COUNT(*) AS users,
  SUM(CASE WHEN p.comebacks > 0 THEN 1 ELSE 0 END) AS resurrected,
  ROUND(100.0 * SUM(CASE WHEN p.comebacks > 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS resurrected_pct,
  MAX(p.longest_gap) AS longest_gap
FROM per_user p
JOIN app_users u ON u.user_id = p.user_id
GROUP BY u.platform
ORDER BY u.platform""",
     why="LAG gives the previous active day of the same user; the difference minus 1 is the number of inactive days in "
         "between (Jan 1 to Jan 16 is 15 days apart, 14 inactive). The first row of each user has a NULL gap, which "
         "the CASE and MAX ignore. About 27% to 29% of users on every platform come back after a 2 week break, so "
         "'14 days inactive = churned' would mislabel many users.",
     complexity="One window sort per user: O(n log n).",
     mistakes="Forgetting the minus 1 (off by one: a 13 day gap is counted). Counting comebacks instead of users. "
              "Ignoring the gap at the END (a user inactive since their last day is churned, not resurrected; that is "
              "a different question).",
     learn=["sql-gaps-islands", "sql-lag-lead"])

ex.save()
