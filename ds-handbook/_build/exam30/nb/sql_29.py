import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam
from sql_hard_tables import load, put_doc

EXTRA = r'''# pandas copies of the tables (same names as the SQL tables) and the answer checker.
import numpy as np
retail = pd.read_sql("SELECT * FROM retail", db)
ml_ratings = pd.read_sql("SELECT * FROM ml_ratings", db)
ml_movies = pd.read_sql("SELECT * FROM ml_movies", db)
ml_movie_genres = pd.read_sql("SELECT * FROM ml_movie_genres", db)
app_users = pd.read_sql("SELECT * FROM app_users", db)
app_events = pd.read_sql("SELECT * FROM app_events", db)
purchases = pd.read_sql("SELECT * FROM purchases", db)

def _norm(t):
    t = pd.DataFrame(t).reset_index(drop=True).copy()
    t.columns = range(t.shape[1])
    for c in t.columns:
        conv = pd.to_numeric(t[c], errors="coerce")
        if conv.notna().sum() == t[c].notna().sum():          # a numeric column (NULLs allowed)
            t[c] = conv.astype(float)
        else:
            t[c] = t[c].astype(str)
    return t

def _close(a, b):
    if isinstance(a, float) or isinstance(b, float):
        try:
            a, b = float(a), float(b)
        except (TypeError, ValueError):
            return False
        return (np.isnan(a) and np.isnan(b)) or abs(a - b) <= 0.06
    return str(a) == str(b)

def same(sql, df, rows=None, first=None):
    """Checks one task: your SQL result and your pandas result must hold the same rows (column names and row order
    are ignored, numbers may differ by rounding), and match the expected row count and first row of the SQL result."""
    if not str(sql).strip() or df is None:
        print("Not done yet: write the SQL string and the pandas function, then run this cell again.")
        return
    a, b = _norm(run(sql)), _norm(df)
    if a.shape != b.shape:
        print(f"FAIL SQL gives {a.shape[0]} rows x {a.shape[1]} columns, pandas gives {b.shape[0]} x {b.shape[1]}")
    else:
        sa = a.sort_values(list(a.columns)).reset_index(drop=True)
        sb = b.sort_values(list(b.columns)).reset_index(drop=True)
        bad = [(i, j) for i in range(len(sa)) for j in sa.columns if not _close(sa.iat[i, j], sb.iat[i, j])]
        print("PASS SQL and pandas agree" if not bad else f"FAIL SQL and pandas differ, e.g. row {bad[0][0]} column {bad[0][1]}")
    if rows is not None:
        print(("PASS" if a.shape[0] == rows else "FAIL") + f" expected {rows} rows, SQL gives {a.shape[0]}")
    if first is not None:
        got = [v.item() if hasattr(v, "item") else v for v in a.iloc[0]] if len(a) else []
        got = [int(v) if isinstance(v, float) and v.is_integer() else v for v in got]
        ok = len(got) == len(first) and all(_close(float("nan") if f is None else f, g) for f, g in zip(first, got))
        print(("PASS" if ok else "FAIL") + f" first row of the SQL result: {got}")'''

SMALL = """**pandas:** the setup cell also loads `retail`, `ml_ratings`, `ml_movies`, `ml_movie_genres`, `app_users`,
`app_events` and `purchases` as DataFrames (same names and columns as the SQL tables). `same(sql, df, ...)` checks a
task: SQL and pandas must agree, and the SQL result must have the expected size and first row."""

INTRO = """**Full exam round (45 minutes): an analytical SQL round with pandas follow-ups.**

- Treat this as the real thing: 5 tasks, about 9 minutes each, one timer. For each task write the **SQL first**
  (the main ask), then the **pandas** version (the usual follow-up, and what a take-home expects).
- Talk while you work: state the grain (one row = ?), the definition, and one edge case before you type.
- The check cell prints PASS when SQL and pandas agree with each other and with the expected answer.
- No hints until the 45 minutes are over. Afterwards, read every solution: the pandas idioms are the part to memorise."""

ex = Exam(29, "sql", title="Day 29: SQL full round (SQL and pandas)", intro=INTRO)
code, doc = load("apps", "retail", "movielens", extra=EXTRA)
ex.setup(code, data=True)
put_doc(ex, doc, SMALL)


def stub(k):
    return (f'q{k}_sql = """\n\n"""\n\ndef q{k}_pandas():\n    # your pandas code: return a DataFrame with the same columns\n'
            f'    return None\n\nprint(run(q{k}_sql) if q{k}_sql.strip() else "")')


ex.q("Monthly revenue and growth", minutes=8, stub=stub(1),
     tests='same(q1_sql, q1_pandas(), rows=12, first=("2010-12", 748957.0, None))',
     prompt="""UCI Online Retail (real). Net revenue = `SUM(quantity * unit_price)` over ALL rows (cancellations have
negative quantities, so they reduce revenue). Use full months only: `invoice_date < '2011-12-01'`. Return `month`
('YYYY-MM'), `revenue` (rounded to whole numbers) and `mom_pct`: month over month change in % (1 decimal; NULL for the
first month). Order by month.

pandas: return the same three columns.""",
     hint1="Signal: 'compared with the previous month'. Pattern: aggregate by month, then LAG (SQL) / `pct_change` or "
           "`shift` (pandas).",
     hint2="SQL: CTE with SUM per `substr(invoice_date, 1, 7)`, then `revenue / LAG(revenue) OVER (ORDER BY month) - 1`.\n"
           "pandas: filter, `assign(month=..., rev=...)`, `groupby('month', as_index=False)['rev'].sum()`, then "
           "`rev.pct_change() * 100`.",
     solution='''q1_sql = """
WITH m AS (
  SELECT substr(invoice_date, 1, 7) AS month, SUM(quantity * unit_price) AS revenue
  FROM retail
  WHERE invoice_date < '2011-12-01'
  GROUP BY substr(invoice_date, 1, 7)
)
SELECT month, ROUND(revenue, 0) AS revenue,
  ROUND(100.0 * (revenue / LAG(revenue) OVER (ORDER BY month) - 1), 1) AS mom_pct
FROM m
ORDER BY month
"""

def q1_pandas():
    d = retail[retail["invoice_date"] < "2011-12-01"]
    d = d.assign(month=d["invoice_date"].str[:7], rev=d["quantity"] * d["unit_price"])
    m = d.groupby("month", as_index=False)["rev"].sum().sort_values("month")
    m["mom_pct"] = (m["rev"].pct_change() * 100).round(1)
    m["revenue"] = m["rev"].round(0)
    return m[["month", "revenue", "mom_pct"]]''',
     why="LAG in SQL and `pct_change` (or `rev / rev.shift(1) - 1`) in pandas both need the rows sorted by month; "
         "groupby sorts its keys, and the explicit sort_values makes that visible. November 2011 is the peak (1,461,756, "
         "+36.5%) before the gift season; the partial December is excluded on purpose, otherwise it shows a fake crash.",
     complexity="One pass to aggregate; the monthly table has 12 rows.",
     mistakes="Leaving December 2011 (9 days) in. `pct_change` on an unsorted frame. pandas mean of the column when "
              "the task says sum. Forgetting `as_index=False` and then losing the month column.",
     learn=["sql-pandas-equivalents", "sql-lag-lead"])

ex.q("Best movies per genre", minutes=9, stub=stub(2),
     tests='same(q2_sql, q2_pandas(), rows=9, first=("Comedy", 1, "Princess Bride, The (1987)", 142, 4.23))',
     prompt="""MovieLens (real). For the genres Comedy, Drama and Sci-Fi (`ml_movie_genres`), consider movies with at least
100 ratings. Return the **top 3 per genre** by average rating (ties: more ratings first): `genre`, `rn` (1 to 3),
`title`, `n` (ratings), `avg_rating` (2 decimals). Order by genre, rn.

pandas: same columns.""",
     hint1="Signal: 'top 3 per genre'. Pattern: top-N per group: ROW_NUMBER (SQL); sort + `groupby().cumcount()` or "
           "`groupby().head(3)` (pandas).",
     hint2="SQL: stats CTE (GROUP BY genre, movie HAVING COUNT(*) >= 100), then `ROW_NUMBER() OVER (PARTITION BY genre "
           "ORDER BY avg_rating DESC, n DESC)`.\npandas: merge ratings with the filtered genres, "
           "`groupby(['genre', 'movie_id']).agg(n=('rating', 'size'), avg_rating=('rating', 'mean'))`, filter n, merge "
           "titles, sort, `cumcount() + 1`.",
     solution='''q2_sql = """
WITH stats AS (
  SELECT g.genre, m.title, COUNT(*) AS n, AVG(r.rating) AS avg_rating
  FROM ml_ratings r
  JOIN ml_movie_genres g ON g.movie_id = r.movie_id
  JOIN ml_movies m ON m.movie_id = r.movie_id
  WHERE g.genre IN ('Comedy', 'Drama', 'Sci-Fi')
  GROUP BY g.genre, r.movie_id, m.title
  HAVING COUNT(*) >= 100
), ranked AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY genre ORDER BY avg_rating DESC, n DESC) AS rn
  FROM stats
)
SELECT genre, rn, title, n, ROUND(avg_rating, 2) AS avg_rating
FROM ranked
WHERE rn <= 3
ORDER BY genre, rn
"""

def q2_pandas():
    g = ml_movie_genres[ml_movie_genres["genre"].isin(["Comedy", "Drama", "Sci-Fi"])]
    s = (ml_ratings.merge(g, on="movie_id")
         .groupby(["genre", "movie_id"])
         .agg(n=("rating", "size"), avg_rating=("rating", "mean"))
         .reset_index())
    s = s[s["n"] >= 100].merge(ml_movies[["movie_id", "title"]], on="movie_id")
    s = s.sort_values(["genre", "avg_rating", "n"], ascending=[True, False, False])
    s["rn"] = s.groupby("genre").cumcount() + 1
    out = s[s["rn"] <= 3][["genre", "rn", "title", "n", "avg_rating"]]
    return out.assign(avg_rating=out["avg_rating"].round(2))''',
     why="HAVING and the pandas boolean filter both run AFTER the aggregation (a WHERE on n would not exist yet). "
         "`sort_values` + `groupby().cumcount()` is the pandas ROW_NUMBER; `groupby('genre').head(3)` works too once "
         "sorted. Shawshank Redemption leads Drama with 4.43 from 317 ratings; Pulp Fiction counts as a Comedy too "
         "(multi-genre movies appear in each of their genres).",
     complexity="A join of 100k ratings to genres, one groupby and one sort.",
     mistakes="`rank(method='first')` without sorting by the tiebreaker. Filtering n before grouping. Using "
              "`nlargest` per group with apply (slow and drops the tiebreaker).",
     learn=["sql-pandas-equivalents", "sql-top-n"])

ex.q("Two week conversion by channel and month", minutes=9, stub=stub(3),
     tests='same(q3_sql, q3_pandas(), rows=8, first=("2024-01", "paid_social", 227, 21.6))',
     prompt="""Shopping app (made up). A user **converts** if they have a `completed` purchase within 14 days of signup
(`order_time < signup_date + 14 days`). Return `signup_month` ('YYYY-MM'), `channel`, `users`, `conv_14d_pct` (1
decimal), ordered by month, then conversion descending. Users without purchases must count.

pandas: same columns.""",
     hint1="Signal: a rate where non-buyers must stay in the denominator. Pattern: LEFT JOIN with the filter in ON + "
           "MAX(CASE) flag per user (SQL); `isin` flag + groupby mean (pandas).",
     hint2="SQL: per user `MAX(CASE WHEN p.order_time < date(u.signup_date, '+14 days') THEN 1 ELSE 0 END)` from "
           "`app_users LEFT JOIN purchases ... AND status = 'completed'`; then AVG per month and channel.\n"
           "pandas: merge completed purchases with signup dates, keep those inside 14 days, flag users with "
           "`isin`, then `groupby(['signup_month', 'channel']).agg(users=..., conv=('flag', 'mean'))`.",
     solution='''q3_sql = """
WITH conv AS (
  SELECT u.user_id, u.channel, substr(u.signup_date, 1, 7) AS signup_month,
    MAX(CASE WHEN p.order_time < date(u.signup_date, '+14 days') THEN 1 ELSE 0 END) AS bought_14d
  FROM app_users u
  LEFT JOIN purchases p ON p.user_id = u.user_id AND p.status = 'completed'
  GROUP BY u.user_id, u.channel, u.signup_date
)
SELECT signup_month, channel, COUNT(*) AS users,
  ROUND(100.0 * AVG(bought_14d), 1) AS conv_14d_pct
FROM conv
GROUP BY signup_month, channel
ORDER BY signup_month, conv_14d_pct DESC
"""

def q3_pandas():
    p = purchases[purchases["status"] == "completed"].merge(app_users[["user_id", "signup_date"]], on="user_id")
    inside = pd.to_datetime(p["order_time"]) < pd.to_datetime(p["signup_date"]) + pd.Timedelta(days=14)
    buyers = p.loc[inside, "user_id"].unique()
    u = app_users.assign(signup_month=app_users["signup_date"].str[:7],
                         bought_14d=app_users["user_id"].isin(buyers).astype(int))
    o = (u.groupby(["signup_month", "channel"])
          .agg(users=("user_id", "size"), conv_14d_pct=("bought_14d", "mean"))
          .reset_index())
    o["conv_14d_pct"] = (o["conv_14d_pct"] * 100).round(1)
    return o.sort_values(["signup_month", "conv_14d_pct"], ascending=[True, False])''',
     why="Both versions build ONE 0/1 flag per user first and only then average, so users with several orders count "
         "once and users with none count as 0. Paid social converts best in January (21.6%) but worst in February "
         "(15.7%): a channel ranking that flips month to month needs a significance check before anyone acts on it.",
     complexity="One join and two aggregations in both versions.",
     mistakes="Inner merge in pandas (non-buyers vanish). `status = 'completed'` in WHERE after the LEFT JOIN. "
              "Comparing a date string with a timestamp string in pandas without `to_datetime`.",
     learn=["sql-pandas-equivalents", "sql-ratios"])

ex.q("Sessions from an event log", minutes=10, stub=stub(4),
     tests='same(q4_sql, q4_pandas(), rows=3, first=("android", 5065, 1.71, 60.2))',
     prompt="""Shopping app (made up), `app_events`. A new session starts when a user's event comes more than 30 minutes
after their previous event (or is their first event). Per `platform` (from `app_users`) return `sessions`,
`events_per_session` (2 decimals) and `single_event_pct` (% of sessions with only one event, 1 decimal), ordered by
platform. Break timestamp ties with `event_id`.

pandas: same columns. (Today's algorithms notebook asks the same in plain Python.)""",
     hint1="Signal: '30 minutes after the previous event'. Pattern: sessionization: LAG + flag + running SUM (SQL); "
           "`groupby().diff()` + flag + `groupby().cumsum()` (pandas).",
     hint2="SQL: LAG(event_time) per user; new_s = 1 if NULL or gap > 30 min; `SUM(new_s) OVER (PARTITION BY user_id ORDER "
           "BY event_time, event_id ROWS UNBOUNDED PRECEDING)` = session id; count events per session.\n"
           "pandas: sort by user, time, id; `gap = t.groupby(user).diff()`; `flag = gap.isna() | (gap > 30 min)`; "
           "`sid = flag.astype(int).groupby(user).cumsum()`.",
     solution='''q4_sql = """
WITH e AS (
  SELECT e.user_id, u.platform, e.event_id, e.event_time,
    LAG(e.event_time) OVER (PARTITION BY e.user_id ORDER BY e.event_time, e.event_id) AS prev_time
  FROM app_events e
  JOIN app_users u ON u.user_id = e.user_id
), f AS (
  SELECT *,
    CASE WHEN prev_time IS NULL
           OR (julianday(event_time) - julianday(prev_time)) * 1440 > 30 THEN 1 ELSE 0 END AS new_s
  FROM e
), s AS (
  SELECT user_id, platform,
    SUM(new_s) OVER (PARTITION BY user_id ORDER BY event_time, event_id ROWS UNBOUNDED PRECEDING) AS sid
  FROM f
), per AS (
  SELECT platform, user_id, sid, COUNT(*) AS events FROM s GROUP BY platform, user_id, sid
)
SELECT platform, COUNT(*) AS sessions,
  ROUND(AVG(events), 2) AS events_per_session,
  ROUND(100.0 * AVG(CASE WHEN events = 1 THEN 1 ELSE 0 END), 1) AS single_event_pct
FROM per
GROUP BY platform
ORDER BY platform
"""

def q4_pandas():
    e = (app_events.merge(app_users[["user_id", "platform"]], on="user_id")
         .sort_values(["user_id", "event_time", "event_id"]))
    t = pd.to_datetime(e["event_time"])
    gap = t.groupby(e["user_id"]).diff()
    new_s = gap.isna() | (gap > pd.Timedelta(minutes=30))
    e["sid"] = new_s.astype(int).groupby(e["user_id"]).cumsum()
    per = e.groupby(["platform", "user_id", "sid"]).size().rename("events").reset_index()
    out = per.groupby("platform").agg(sessions=("events", "size"),
                                      events_per_session=("events", "mean"),
                                      single_event_pct=("events", lambda x: (x == 1).mean() * 100)).reset_index()
    return out.round({"events_per_session": 2, "single_event_pct": 1})''',
     why="The flag-and-cumsum idea is identical in both languages: a boolean 'starts a new session' turned into a "
         "running count per user. In pandas, `groupby(...).diff()` must be used (a plain `diff()` would compare the "
         "first event of a user with the last event of the previous user). Android has 5,065 sessions with 1.71 "
         "events each; about 60% of sessions on every platform are a single event, a typical bounce signal.",
     complexity="One sort by user and time: O(n log n); everything else is linear.",
     mistakes="Plain `diff()` across users. Sorting by time only (users interleave). Gap measured in the wrong unit "
              "(`gap > 30` compares a Timedelta with an int: error). Forgetting the tie breaker.",
     learn=["sql-pandas-equivalents", "sql-gaps-islands"])

ex.q("Funnel table by platform", minutes=9, stub=stub(5),
     tests='same(q5_sql, q5_pandas(), rows=3, first=("android", 695, 642, 522, 421, 205, 31.9))',
     prompt="""Shopping app (made up). Per `platform` return `users` (all users of the platform), and the number of users
who EVER had each event: `viewed`, `carted`, `checked_out`, `purchased`, plus `view_to_buy_pct` = purchased / viewed
(1 decimal). Order matters NOT here (the strict ordered funnel was day 21). Order by platform.

pandas: same columns, using a pivot table.""",
     hint1="Signal: counts per category as columns. Pattern: pivot: COUNT(DISTINCT CASE ...) (SQL); "
           "`drop_duplicates` + `pivot_table(aggfunc='count')` or `pd.crosstab` (pandas).",
     hint2="SQL: `app_users LEFT JOIN app_events`, one `COUNT(DISTINCT CASE WHEN e.event_name = 'view_item' THEN u.user_id END)` per step.\n"
           "pandas: `app_events.drop_duplicates(['user_id', 'event_name'])`, merge platform, "
           "`pivot_table(index='platform', columns='event_name', values='user_id', aggfunc='count', fill_value=0)`, "
           "join the user counts, reorder the columns.",
     solution='''q5_sql = """
SELECT u.platform,
  COUNT(DISTINCT u.user_id) AS users,
  COUNT(DISTINCT CASE WHEN e.event_name = 'view_item' THEN u.user_id END) AS viewed,
  COUNT(DISTINCT CASE WHEN e.event_name = 'add_to_cart' THEN u.user_id END) AS carted,
  COUNT(DISTINCT CASE WHEN e.event_name = 'checkout' THEN u.user_id END) AS checked_out,
  COUNT(DISTINCT CASE WHEN e.event_name = 'purchase' THEN u.user_id END) AS purchased,
  ROUND(100.0 * COUNT(DISTINCT CASE WHEN e.event_name = 'purchase' THEN u.user_id END)
      / COUNT(DISTINCT CASE WHEN e.event_name = 'view_item' THEN u.user_id END), 1) AS view_to_buy_pct
FROM app_users u
LEFT JOIN app_events e ON e.user_id = u.user_id
GROUP BY u.platform
ORDER BY u.platform
"""

def q5_pandas():
    reach = (app_events.drop_duplicates(["user_id", "event_name"])
             .merge(app_users[["user_id", "platform"]], on="user_id")
             .pivot_table(index="platform", columns="event_name", values="user_id",
                          aggfunc="count", fill_value=0))
    out = app_users.groupby("platform").size().rename("users").to_frame().join(reach).reset_index()
    out = out[["platform", "users", "view_item", "add_to_cart", "checkout", "purchase"]]
    out.columns = ["platform", "users", "viewed", "carted", "checked_out", "purchased"]
    out["view_to_buy_pct"] = (100 * out["purchased"] / out["viewed"]).round(1)
    return out''',
     why="`drop_duplicates` on (user, event) is the pandas form of COUNT(DISTINCT ...): after it, counting rows counts "
         "users. The users column comes from `app_users`, not from events, so users without events stay in the "
         "denominator (the LEFT JOIN in SQL). Web converts viewers to buyers far less (21.2% versus about 32%). Note "
         "that this unordered table can count a purchaser who never viewed; the ordered version (day 21) cannot.",
     complexity="One join and one aggregation (SQL); one dedup and one pivot (pandas).",
     mistakes="`aggfunc='count'` without dedup (counts events, not users). `pivot` instead of `pivot_table` "
              "(fails on duplicate index pairs). Forgetting `fill_value=0`, which gives NaN for missing steps.",
     learn=["sql-pandas-equivalents", "sql-pivot", "sql-funnels"])

ex.save()
