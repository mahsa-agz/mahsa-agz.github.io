"""Shared MADE-UP shopping-app tables for SQL exam days 11 to 20 (retention, funnels, ratios, streaks, dedup).

Richer than sql_product_tables.py (20 users, one month): 1,500 users who signed up 2024-01-01 to 2024-02-29, with
daily activity and funnel events until 2024-03-31 (3 months). Table names do not clash with sql_product_tables
(users / videos / events), so a notebook can load both.

STABLE: the data is generated in the notebook with a fixed seed and numpy's legacy RandomState (its random stream is
frozen across numpy versions), so every run in Colab or locally gives the same rows. Do not change the code below:
expected answers in many notebooks depend on it. A day that needs more data creates an extra table in its own setup.

Use in a builder:
    from sql_events_tables import APP_SETUP, APP_DOC
    ex.setup(APP_SETUP, data=True)       # APP_SETUP expects a sqlite3 connection named db (the setup cell has one)
"""

APP_SETUP = r'''# Made-up shopping-app tables (generated with a fixed seed, so everyone gets the same rows).
import numpy as np

def make_app_tables(con, seed=7):
    rs = np.random.RandomState(seed)
    start, end = pd.Timestamp("2024-01-01"), pd.Timestamp("2024-03-31")
    n = 1500
    countries, c_p = ["US", "KR", "BR", "ID", "DE"], [0.30, 0.25, 0.20, 0.15, 0.10]
    platforms, p_p = ["ios", "android", "web"], [0.40, 0.45, 0.15]
    channels, ch_p = ["organic", "paid_social", "search", "referral"], [0.35, 0.30, 0.20, 0.15]
    signup_off = np.sort(rs.randint(0, 60, n))                     # day offsets 0..59 (Jan 1 to Feb 29)
    country = rs.choice(len(countries), n, p=c_p)
    platform = rs.choice(len(platforms), n, p=p_p)
    channel = rs.choice(len(channels), n, p=ch_p)
    referred_by = [None] * n
    for i in range(n):
        if channels[channel[i]] == "referral":
            earlier = np.nonzero(signup_off[:i] < signup_off[i])[0]
            if len(earlier):
                referred_by[i] = int(earlier[rs.randint(len(earlier))]) + 1
            else:
                channel[i] = 0                                       # nobody to refer them: organic
    users = pd.DataFrame({
        "user_id": np.arange(1, n + 1),
        "signup_date": [(start + pd.Timedelta(days=int(d))).strftime("%Y-%m-%d") for d in signup_off],
        "country": [countries[c] for c in country],
        "platform": [platforms[p] for p in platform],
        "channel": [channels[c] for c in channel],
        "referred_by": pd.array(referred_by, dtype="Int64"),
    })
    plat_boost = {"ios": 0.08, "android": 0.0, "web": -0.10}
    chan_boost = {"organic": 0.05, "paid_social": -0.08, "search": 0.0, "referral": 0.08}
    act, ev, buys = [], [], []
    total_days = (end - start).days + 1
    for i in range(n):
        uid = i + 1
        p = rs.beta(2, 3) + plat_boost[platforms[platform[i]]] + chan_boost[channels[channel[i]]]
        p = min(max(p, 0.03), 0.9)
        life = 1 if rs.rand() < 0.30 else 1 + int(rs.exponential(35))   # days until the user stops coming back
        buyer = rs.rand() < 0.55
        prev = True
        for t in range(0, total_days - signup_off[i]):
            if t == 0:
                active = True
            elif t >= life:
                active = rs.rand() < 0.01                                 # rare comeback after churn
            else:
                active = rs.rand() < (min(p + 0.25, 0.95) if prev else p * 0.7)
            prev = active
            if not active:
                continue
            day = start + pd.Timedelta(days=int(signup_off[i] + t))
            sessions = 1 + rs.poisson(0.8)
            minutes = int(sum(rs.randint(2, 25) for _ in range(sessions)))
            act.append((uid, day.strftime("%Y-%m-%d"), sessions, minutes))
            clock = day + pd.Timedelta(seconds=int(rs.randint(6 * 3600, 22 * 3600)))
            if rs.rand() < 0.65:
                steps = ["view_item"]
                if rs.rand() < 0.40:
                    steps.append("add_to_cart")
                    if rs.rand() < 0.55:
                        steps.append("checkout")
                        if buyer and rs.rand() < 0.75:
                            steps.append("purchase")
                elif rs.rand() < 0.03:
                    steps = ["add_to_cart"]                               # from the wishlist, no view that day
                for s in steps:
                    clock = clock + pd.Timedelta(seconds=int(rs.randint(15, 900)))
                    ev.append((uid, clock.strftime("%Y-%m-%d %H:%M:%S"), s))
                    if s == "purchase":
                        amount = round(float(rs.gamma(2.0, 18.0)) + 5, 2)
                        status = "refunded" if rs.rand() < 0.07 else "completed"
                        buys.append((uid, clock.strftime("%Y-%m-%d %H:%M:%S"), amount, status))
    activity = pd.DataFrame(act, columns=["user_id", "activity_date", "sessions", "minutes"])
    events = pd.DataFrame(ev, columns=["user_id", "event_time", "event_name"])
    events = events.sort_values(["event_time", "user_id"], kind="mergesort").reset_index(drop=True)
    events.insert(0, "event_id", np.arange(1, len(events) + 1))
    purchases = pd.DataFrame(buys, columns=["user_id", "order_time", "amount", "status"])
    purchases = purchases.sort_values(["order_time", "user_id"], kind="mergesort").reset_index(drop=True)
    purchases.insert(0, "order_id", np.arange(1, len(purchases) + 1))
    # raw event log as it arrives from the apps: retries create exact copies, double taps create near copies
    raw = events.copy()
    dup = raw[rs.rand(len(raw)) < 0.04]
    tap = raw[rs.rand(len(raw)) < 0.01].copy()
    tap["event_time"] = (pd.to_datetime(tap["event_time"]) +
                         pd.to_timedelta(rs.randint(1, 4, len(tap)), unit="s")).dt.strftime("%Y-%m-%d %H:%M:%S")
    raw = pd.concat([raw, dup, tap]).sort_values(["event_time", "user_id"], kind="mergesort").reset_index(drop=True)
    raw = raw.drop(columns="event_id")
    raw.insert(0, "raw_id", np.arange(1, len(raw) + 1))
    raw["received_at"] = (pd.to_datetime(raw["event_time"]) +
                          pd.to_timedelta(rs.randint(1, 600, len(raw)), unit="s")).dt.strftime("%Y-%m-%d %H:%M:%S")
    for name, df in [("app_users", users), ("daily_activity", activity), ("app_events", events),
                     ("purchases", purchases), ("app_events_raw", raw)]:
        df.to_sql(name, con, index=False, if_exists="replace")

make_app_tables(db)'''

APP_DOC = """**Made-up shopping-app tables** (invented for practice, generated with a fixed seed: 1,500 users signed up
2024-01-01 to 2024-02-29, activity until 2024-03-31):

| Table | One row is | Columns |
|---|---|---|
| `app_users` | one user | `user_id`, `signup_date` ('YYYY-MM-DD'), `country` (US/KR/BR/ID/DE), `platform` (ios/android/web), `channel` (organic/paid_social/search/referral), `referred_by` (user_id of the referrer, NULL unless channel = referral) |
| `daily_activity` | one user on one day they opened the app | `user_id`, `activity_date` ('YYYY-MM-DD'), `sessions`, `minutes`. No row = not active that day |
| `app_events` | one shopping event | `event_id`, `user_id`, `event_time` ('YYYY-MM-DD HH:MM:SS'), `event_name` (view_item / add_to_cart / checkout / purchase) |
| `purchases` | one order | `order_id`, `user_id`, `order_time`, `amount` (USD), `status` (completed / refunded) |
| `app_events_raw` | one event as received from the apps (has retries and double taps) | `raw_id`, `user_id`, `event_time`, `event_name`, `received_at` |"""
