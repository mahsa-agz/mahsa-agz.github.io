"""Setup code + table docs for the hard SQL exam days 21 to 30 (builders sql_21.py ... sql_30.py).

Each *_SETUP string is python for the notebook setup cell (it expects `db`, `pd`, `sqlite3` and `data_path`, which the
libx setup cell provides when data=True). Each *_DOC string is the markdown table description shown at the top.

Real data: Northwind (nw_*), MovieLens small (ml_*), UCI Online Retail (retail), Google Play Store (play_apps).
Made-up data (generated with numpy's legacy RandomState, whose stream is frozen across numpy versions, so Colab and
local runs give the same rows): short-video app (tt_*), web search log (searches, clicks), phone fleet (devices,
firmware_updates, crash_logs, health_steps).
STABLE: do not change the generators; expected answers in the notebooks depend on them.

Use:  from sql_hard_tables import load
      code, doc = load("chinook", "retail", "tiktok")   # also "apps" and "video" from the other SQL modules
      ex.setup(code, data=True); put_doc(ex, doc)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sql_product_tables import CHINOOK_SETUP, CHINOOK_DOC, PRODUCT_SETUP, PRODUCT_DOC  # noqa: E402
from sql_events_tables import APP_SETUP, APP_DOC  # noqa: E402

URL_NW = "https://raw.githubusercontent.com/jpwhite3/northwind-SQLite3/main/dist/northwind.db"
URL_ML = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
URL_RETAIL = "https://archive.ics.uci.edu/static/public/352/online+retail.zip"
URL_PLAY = "https://raw.githubusercontent.com/malborroni/Foundations_of_Computer-Science/master/datasets/googleplaystore.csv"

# ----------------------------------------------------------------------------------------------- Northwind (real)
NORTHWIND_SETUP = '''# Real data: Northwind orders (jpwhite3/northwind-SQLite3, MIT). Copied into db with short table names.
db.execute("ATTACH DATABASE ? AS nw", (data_path("northwind.db", "''' + URL_NW + '''"),))
db.executescript("""
CREATE TABLE nw_customers  AS SELECT CustomerID AS customer_id, CompanyName AS company, City AS city, Country AS country FROM nw.Customers;
CREATE TABLE nw_employees  AS SELECT EmployeeID AS employee_id, FirstName || ' ' || LastName AS name, Title AS title, ReportsTo AS reports_to FROM nw.Employees;
CREATE TABLE nw_categories AS SELECT CategoryID AS category_id, CategoryName AS category FROM nw.Categories;
CREATE TABLE nw_products   AS SELECT ProductID AS product_id, ProductName AS product, CategoryID AS category_id, UnitPrice AS list_price, Discontinued AS discontinued FROM nw.Products;
CREATE TABLE nw_orders     AS SELECT OrderID AS order_id, CustomerID AS customer_id, EmployeeID AS employee_id, OrderDate AS order_date, ShippedDate AS shipped_date, ShipCountry AS ship_country FROM nw.Orders;
CREATE TABLE nw_order_items AS SELECT OrderID AS order_id, ProductID AS product_id, UnitPrice AS unit_price, Quantity AS quantity, Discount AS discount FROM nw."Order Details";
""")
db.execute("DETACH DATABASE nw")'''

NORTHWIND_DOC = """**Real tables: Northwind** (a food wholesaler; orders 2012-07 to 2023-10; MIT license, jpwhite3/northwind-SQLite3):

| Table | One row is | Columns |
|---|---|---|
| `nw_orders` | one order (16,282) | `order_id`, `customer_id`, `employee_id`, `order_date` ('YYYY-MM-DD HH:MM:SS'), `shipped_date`, `ship_country` |
| `nw_order_items` | one product line of an order (609,283) | `order_id`, `product_id`, `unit_price`, `quantity`, `discount` (0 to 0.25). Revenue = `unit_price * quantity * (1 - discount)` |
| `nw_products` | one product (77) | `product_id`, `product`, `category_id`, `list_price`, `discontinued` |
| `nw_categories` | one category (8) | `category_id`, `category` |
| `nw_customers` | one customer (93) | `customer_id`, `company`, `city`, `country` |
| `nw_employees` | one employee (9) | `employee_id`, `name`, `title`, `reports_to` (manager, NULL for the boss) |"""

# ----------------------------------------------------------------------------------------------- MovieLens (real)
MOVIELENS_SETUP = '''# Real data: MovieLens small (GroupLens, research and education use). Downloads the zip if the CSVs are missing.
import zipfile
if not os.path.exists(os.path.join(DATA, "movielens_ratings.csv")):
    _z = data_path("ml-latest-small.zip", "''' + URL_ML + '''")
    with zipfile.ZipFile(_z) as zf:
        for _n in ("ratings", "movies"):
            with open(os.path.join(DATA, f"movielens_{_n}.csv"), "wb") as fh:
                fh.write(zf.read(f"ml-latest-small/{_n}.csv"))
_r = pd.read_csv(data_path("movielens_ratings.csv"))
_r["rated_at"] = pd.to_datetime(_r["timestamp"], unit="s").dt.strftime("%Y-%m-%d %H:%M:%S")
_r = _r.rename(columns={"userId": "user_id", "movieId": "movie_id"})[["user_id", "movie_id", "rating", "rated_at"]]
_r.to_sql("ml_ratings", db, index=False)
_m = pd.read_csv(data_path("movielens_movies.csv")).rename(columns={"movieId": "movie_id"})
_m["year"] = pd.to_numeric(_m["title"].str.extract(r"\\((\\d{4})\\)\\s*$")[0], errors="coerce").astype("Int64")
_m[["movie_id", "title", "year", "genres"]].to_sql("ml_movies", db, index=False)
_g = _m.assign(genre=_m["genres"].str.split("|")).explode("genre")[["movie_id", "genre"]]
_g[_g["genre"] != "(no genres listed)"].to_sql("ml_movie_genres", db, index=False)'''

MOVIELENS_DOC = """**Real tables: MovieLens small** (GroupLens; 610 users rated 9,742 movies, 1996 to 2018):

| Table | One row is | Columns |
|---|---|---|
| `ml_ratings` | one rating (100,836) | `user_id`, `movie_id`, `rating` (0.5 to 5.0 in steps of 0.5), `rated_at` ('YYYY-MM-DD HH:MM:SS', UTC) |
| `ml_movies` | one movie (9,742) | `movie_id`, `title`, `year` (from the title, can be NULL), `genres` (pipe separated, e.g. 'Action|Comedy') |
| `ml_movie_genres` | one (movie, genre) pair | `movie_id`, `genre` (the `genres` string split into rows) |"""

# ----------------------------------------------------------------------------------------------- Online Retail (real)
RETAIL_SETUP = '''# Real data: UCI Online Retail (a UK gift shop, 2010-12 to 2011-12, CC BY 4.0).
import io, zipfile
_p = os.path.join(DATA, "online_retail.csv.gz")
if not os.path.exists(_p):                       # first run in Colab: download the UCI zip and convert it once
    with zipfile.ZipFile(data_path("online_retail.zip", "''' + URL_RETAIL + '''")) as zf:
        pd.read_excel(io.BytesIO(zf.read("Online Retail.xlsx"))).to_csv(_p, index=False, compression="gzip")
_o = pd.read_csv(_p, dtype={"InvoiceNo": str, "StockCode": str})
_o.columns = ["invoice_no", "stock_code", "description", "quantity", "invoice_date", "unit_price", "customer_id", "country"]
_o["invoice_date"] = pd.to_datetime(_o["invoice_date"]).dt.strftime("%Y-%m-%d %H:%M:%S")
_o["customer_id"] = _o["customer_id"].astype("Int64")
_o.to_sql("retail", db, index=False)'''

RETAIL_DOC = """**Real table: Online Retail** (UCI, a UK online gift shop, 2010-12-01 to 2011-12-09, CC BY 4.0):

| Table | One row is | Columns |
|---|---|---|
| `retail` | one product line of an invoice (541,909) | `invoice_no` (text; a 'C' prefix = cancellation), `stock_code`, `description`, `quantity` (negative for cancellations), `invoice_date` ('YYYY-MM-DD HH:MM:SS'), `unit_price` (GBP), `customer_id` (NULL for about 25% of rows), `country` |"""

# ----------------------------------------------------------------------------------------------- Google Play (real)
PLAY_SETUP = '''# Real data: Google Play Store apps (scraped 2018, Kaggle lava18 mirror; study use only). Cleaned into numbers.
_a = pd.read_csv(data_path("googleplaystore.csv", "''' + URL_PLAY + '''"))
_a = _a[_a["Category"] != "1.9"].copy()          # one shifted row in the raw file
_a["App"] = _a["App"].str.replace("[\\u2013\\u2014]", "-", regex=True)   # long dashes in names -> '-'
_a["reviews"] = pd.to_numeric(_a["Reviews"], errors="coerce").astype("Int64")
_a["installs"] = pd.to_numeric(_a["Installs"].str.replace("[+,]", "", regex=True), errors="coerce").astype("Int64")
_a["price"] = pd.to_numeric(_a["Price"].str.replace("$", "", regex=False), errors="coerce")
_a["last_updated"] = pd.to_datetime(_a["Last Updated"], format="%B %d, %Y").dt.strftime("%Y-%m-%d")
_a = _a.rename(columns={"App": "app", "Category": "category", "Rating": "rating", "Type": "type",
                        "Content Rating": "content_rating", "Genres": "genres"})
_a[["app", "category", "rating", "reviews", "installs", "type", "price", "content_rating", "genres",
    "last_updated"]].to_sql("play_apps", db, index=False)'''

PLAY_DOC = """**Real table: Google Play Store** (scraped in 2018, Kaggle "lava18/google-play-store-apps" mirror; study use only):

| Table | One row is | Columns |
|---|---|---|
| `play_apps` | one scraped listing (10,840). Some apps appear more than once (scraped twice) | `app`, `category` (e.g. 'GAME'), `rating` (1 to 5, NULL if unrated), `reviews`, `installs` (lower bound of the bucket, e.g. 1000000 for '1,000,000+'), `type` (Free / Paid), `price` (USD), `content_rating`, `genres`, `last_updated` ('YYYY-MM-DD') |"""

# ----------------------------------------------------------------------------------------------- short video (made up)
TIKTOK_SETUP = r'''# Made-up short-video tables (generated with a fixed seed; numpy's legacy RandomState is frozen across versions).
import numpy as np

def make_video_tables(con, seed=25):
    rs = np.random.RandomState(seed)
    cats = ["dance", "food", "comedy", "education", "gaming"]
    nc = 40
    creators = pd.DataFrame({
        "creator_id": np.arange(1, nc + 1),
        "category": [cats[i] for i in rs.randint(0, 5, nc)],
        "country": [["US", "KR", "BR", "ID", "DE"][i] for i in rs.choice(5, nc, p=[.3, .25, .2, .15, .1])],
    })
    pop = rs.lognormal(0, 1.0, nc)                              # creator popularity
    start = pd.Timestamp("2024-05-01")
    vids = []
    vid = 1000
    for c in range(nc):
        for _ in range(1 + rs.poisson(6)):
            vid += 1
            posted = start + pd.Timedelta(seconds=int(rs.randint(0, 27 * 86400)))
            cat = creators.category[c] if rs.rand() < 0.85 else cats[rs.randint(0, 5)]
            vids.append((vid, c + 1, posted, int(rs.choice([15, 30, 45, 60, 90, 180])), cat))
    videos = pd.DataFrame(vids, columns=["video_id", "creator_id", "posted_at", "duration_s", "category"])
    videos = videos.sort_values("posted_at", kind="mergesort").reset_index(drop=True)
    vq = rs.beta(2, 2, len(videos))                             # video quality: how much of it people watch
    w = pop[videos.creator_id.values - 1] * (0.5 + vq)
    posted_s = ((videos.posted_at - start).dt.total_seconds()).values
    views, follows, followed = [], [], set()
    for u in range(1, 1201):
        n_sess = rs.poisson(4)
        for _ in range(n_sess):
            t = int(rs.randint(1 * 86400, 31 * 86400))
            n_vid = 1 + rs.geometric(1 / 6.0)
            source = "following" if rs.rand() < 0.15 else "fyp"
            for _ in range(n_vid):
                ok = np.nonzero(posted_s < t)[0]
                if len(ok) == 0:
                    break
                p = w[ok] / w[ok].sum()
                i = ok[rs.choice(len(ok), p=p)]
                dur = videos.duration_s[i]
                frac = min(rs.beta(1 + 4 * vq[i], 2), 1.0)
                if rs.rand() < 0.08:
                    frac += 1 + rs.rand()                       # rewatch loop: watched more than the length
                watch = max(1, int(round(frac * dur)))
                views.append((u, int(videos.video_id[i]), start + pd.Timedelta(seconds=t), watch, source))
                cid = int(videos.creator_id[i])
                if frac > 0.8 and (u, cid) not in followed and rs.rand() < 0.06:
                    followed.add((u, cid))
                    follows.append((u, cid, start + pd.Timedelta(seconds=t + watch + 2)))
                t += watch + int(rs.randint(1, 15))
                source = "fyp"
    fmt = "%Y-%m-%d %H:%M:%S"
    views = pd.DataFrame(views, columns=["viewer_id", "video_id", "view_time", "watch_s", "source"])
    views = views.sort_values(["view_time", "viewer_id"], kind="mergesort").reset_index(drop=True)
    views.insert(0, "view_id", np.arange(1, len(views) + 1))
    views["view_time"] = views["view_time"].dt.strftime(fmt)
    follows = pd.DataFrame(follows, columns=["follower_id", "creator_id", "followed_at"])
    follows = follows.sort_values("followed_at", kind="mergesort").reset_index(drop=True)
    follows["followed_at"] = follows["followed_at"].dt.strftime(fmt)
    videos["posted_at"] = videos["posted_at"].dt.strftime(fmt)
    for name, df in [("tt_creators", creators), ("tt_videos", videos), ("tt_views", views), ("tt_follows", follows)]:
        df.to_sql(name, con, index=False, if_exists="replace")

make_video_tables(db)'''

TIKTOK_DOC = """**Made-up short-video tables** (invented for practice, fixed seed; May 2024):

| Table | One row is | Columns |
|---|---|---|
| `tt_creators` | one creator (40) | `creator_id`, `category` (main category), `country` |
| `tt_videos` | one posted video | `video_id`, `creator_id`, `posted_at` ('YYYY-MM-DD HH:MM:SS'), `duration_s`, `category` |
| `tt_views` | one play of a video | `view_id`, `viewer_id`, `video_id`, `view_time`, `watch_s` (seconds watched; can be MORE than `duration_s` when the video loops), `source` (fyp / following) |
| `tt_follows` | one follow | `follower_id`, `creator_id`, `followed_at` |"""

# ----------------------------------------------------------------------------------------------- web search (made up)
SEARCH_SETUP = r'''# Made-up web search log (generated with a fixed seed).
import numpy as np

def make_search_tables(con, seed=26):
    rs = np.random.RandomState(seed)
    topics = ["weather", "flights to seoul", "python list sort", "pizza near me", "nba scores", "tax deadline",
              "how to tie a tie", "galaxy s24 review", "bitcoin price", "sql window functions", "cheap hotels paris",
              "translate hello", "movie times", "covid symptoms", "best laptop 2024"]
    quality = rs.beta(4, 2, len(topics))                      # how often result 1 answers the query
    quality[[2, 9, 14]] = [0.25, 0.30, 0.20]                   # three hard queries
    devices = ["mobile", "desktop", "tablet"]
    start = pd.Timestamp("2024-06-03")
    s_rows, c_rows = [], []
    sid = 0
    for u in range(1, 801):
        dev = devices[rs.choice(3, p=[.6, .32, .08])]
        for _ in range(rs.poisson(5)):
            t = int(rs.randint(0, 7 * 86400))
            k = rs.randint(len(topics))
            q = topics[k]
            for attempt in range(3):
                sid += 1
                s_rows.append((sid, u, start + pd.Timedelta(seconds=t), q, dev))
                p_ok = quality[k] if attempt == 0 else min(quality[k] + 0.3, 0.95)
                if rs.rand() < p_ok:                           # satisfied: one long click near the top
                    pos = 1 if rs.rand() < 0.7 else int(rs.randint(2, 4))
                    c_rows.append((sid, pos, start + pd.Timedelta(seconds=t + int(rs.randint(2, 12))), int(rs.randint(31, 400))))
                    break
                if rs.rand() < 0.5:                            # short click, then back to the results
                    pos = int(rs.randint(1, 6))
                    c_rows.append((sid, pos, start + pd.Timedelta(seconds=t + int(rs.randint(2, 12))), int(rs.randint(2, 30))))
                    t += int(rs.randint(20, 60))
                if rs.rand() < 0.55:                           # reformulate the query a few seconds later
                    t += int(rs.randint(5, 50))
                    q = q + (" " + ["2024", "best", "how", "free", "near me"][rs.randint(5)])
                else:
                    break
    fmt = "%Y-%m-%d %H:%M:%S"
    s = pd.DataFrame(s_rows, columns=["search_id", "user_id", "search_time", "query", "device"])
    s["search_time"] = s["search_time"].dt.strftime(fmt)
    c = pd.DataFrame(c_rows, columns=["search_id", "position", "click_time", "dwell_s"])
    c["click_time"] = c["click_time"].dt.strftime(fmt)
    s.to_sql("searches", con, index=False, if_exists="replace")
    c.to_sql("clicks", con, index=False, if_exists="replace")

make_search_tables(db)'''

SEARCH_DOC = """**Made-up search tables** (invented for practice, fixed seed; one week from 2024-06-03):

| Table | One row is | Columns |
|---|---|---|
| `searches` | one query typed by a user | `search_id`, `user_id`, `search_time` ('YYYY-MM-DD HH:MM:SS'), `query`, `device` (mobile / desktop / tablet) |
| `clicks` | one click on a result | `search_id`, `position` (1 = top result), `click_time`, `dwell_s` (seconds on the page before coming back; > 30 counts as a "good click") |"""

# ----------------------------------------------------------------------------------------------- phones (made up)
DEVICE_SETUP = r'''# Made-up phone fleet tables (generated with a fixed seed).
import numpy as np

def make_device_tables(con, seed=27):
    rs = np.random.RandomState(seed)
    models = [("Galaxy S21", "S", 21), ("Galaxy S22", "S", 22), ("Galaxy S23", "S", 23), ("Galaxy S24", "S", 24),
              ("Galaxy A52", "A", 52), ("Galaxy A53", "A", 53), ("Galaxy A54", "A", 54),
              ("Galaxy Z Flip4", "Z", 4), ("Galaxy Z Flip5", "Z", 5)]
    release = {"Galaxy S21": "2021-01-29", "Galaxy S22": "2022-02-25", "Galaxy S23": "2023-02-17",
               "Galaxy S24": "2024-01-31", "Galaxy A52": "2021-03-26", "Galaxy A53": "2022-03-24",
               "Galaxy A54": "2023-03-24", "Galaxy Z Flip4": "2022-08-26", "Galaxy Z Flip5": "2023-08-11"}
    end = pd.Timestamp("2024-06-30")
    dev_rows, did = [], 0
    for u in range(1, 701):
        m = models[rs.choice(len(models))]
        t = pd.Timestamp(release[m[0]]) + pd.Timedelta(days=int(rs.randint(0, 200)))
        while t <= end:
            did += 1
            dev_rows.append((did, u, m[0], m[1], t))
            nxt = [x for x in models if x[1] == m[1] and x[2] > m[2]]
            if rs.rand() < 0.15:                                # switches line
                nxt = [x for x in models if x[1] != m[1] and pd.Timestamp(release[x[0]]) > t]
            if not nxt or rs.rand() < 0.35:
                break
            m = nxt[rs.randint(len(nxt))]
            t = max(t + pd.Timedelta(days=int(rs.randint(150, 900))), pd.Timestamp(release[m[0]]))
    devices = pd.DataFrame(dev_rows, columns=["device_id", "user_id", "model", "series", "activated_at"])
    # firmware: everybody active in May 2024 gets v6.0 then v6.1 (v6.1 has a crash bug on Galaxy A54 and Z Flip5)
    fw, cr = [], []
    active = devices[devices.activated_at < pd.Timestamp("2024-05-01")]
    nxt_act = devices.groupby("user_id")["activated_at"].shift(-1)
    for i, d in active.iterrows():
        if pd.notna(nxt_act[i]) and nxt_act[i] < pd.Timestamp("2024-05-01"):
            continue                                            # replaced before May: not in use any more
        up = pd.Timestamp("2024-05-01") + pd.Timedelta(seconds=int(rs.randint(0, 25 * 86400)))
        fw.append((d.device_id, "6.0", pd.Timestamp("2024-04-01") + pd.Timedelta(days=int(rs.randint(0, 20)))))
        took_update = rs.rand() < 0.8
        if took_update:
            fw.append((d.device_id, "6.1", up))
        base = {"S": 0.04, "A": 0.07, "Z": 0.09}[d.series]
        for day in range(61):
            ts = pd.Timestamp("2024-05-01") + pd.Timedelta(days=day, seconds=int(rs.randint(0, 86400)))
            rate = base
            if took_update and ts >= up and d.model in ("Galaxy A54", "Galaxy Z Flip5"):
                rate = base * 3.5
            if rs.rand() < rate:
                cr.append((d.device_id, ts, ["camera", "launcher", "messages", "gallery"][rs.randint(4)]))
    fmt = "%Y-%m-%d %H:%M:%S"
    devices["activated_at"] = devices["activated_at"].dt.strftime("%Y-%m-%d")
    fw = pd.DataFrame(fw, columns=["device_id", "version", "installed_at"])
    fw["installed_at"] = pd.to_datetime(fw["installed_at"]).dt.strftime(fmt)
    fw = fw.sort_values(["installed_at", "device_id"], kind="mergesort").reset_index(drop=True)
    cr = pd.DataFrame(cr, columns=["device_id", "crash_time", "app"])
    cr["crash_time"] = pd.to_datetime(cr["crash_time"]).dt.strftime(fmt)
    cr = cr.sort_values(["crash_time", "device_id"], kind="mergesort").reset_index(drop=True)
    # health steps for users 1..60 in June 2024: the watch syncs several times a day; each sync sends the day's total so far
    hs = []
    for u in range(1, 61):
        level = rs.randint(4000, 13000)
        for day in range(30):
            if rs.rand() < 0.08:
                continue                                        # watch not worn
            total = max(300, int(rs.normal(level, 3500)))
            n_sync = 1 + rs.poisson(1.5)
            cuts = np.sort(rs.rand(n_sync))
            cuts[-1] = 1.0
            for k, f in enumerate(cuts):
                ts = pd.Timestamp("2024-06-01") + pd.Timedelta(days=day, hours=8 + int(14 * (k + 1) / n_sync), minutes=int(rs.randint(0, 59)))
                hs.append((u, (pd.Timestamp("2024-06-01") + pd.Timedelta(days=day)).strftime("%Y-%m-%d"), int(total * f), ts.strftime(fmt)))
                if rs.rand() < 0.05:
                    hs.append(hs[-1])                           # duplicate upload of the same sync
    hs = pd.DataFrame(hs, columns=["user_id", "step_date", "steps", "synced_at"])
    for name, df in [("devices", devices), ("firmware_updates", fw), ("crash_logs", cr), ("health_steps", hs)]:
        df.to_sql(name, con, index=False, if_exists="replace")

make_device_tables(db)'''

DEVICE_DOC = """**Made-up phone tables** (invented for practice, fixed seed):

| Table | One row is | Columns |
|---|---|---|
| `devices` | one phone a user activated | `device_id`, `user_id`, `model` (e.g. 'Galaxy S23'), `series` (S / A / Z), `activated_at` ('YYYY-MM-DD'). A user's next device replaces the previous one |
| `firmware_updates` | one firmware install | `device_id`, `version` ('6.0' or '6.1'), `installed_at` ('YYYY-MM-DD HH:MM:SS') |
| `crash_logs` | one app crash, May and June 2024 | `device_id`, `crash_time`, `app` |
| `health_steps` | one sync from a watch, June 2024 | `user_id`, `step_date` ('YYYY-MM-DD'), `steps` (the day's total SO FAR at sync time), `synced_at`. Several syncs per day; some syncs are uploaded twice |"""

PARTS = {
    "chinook": (CHINOOK_SETUP, CHINOOK_DOC),
    "video": (PRODUCT_SETUP, PRODUCT_DOC),
    "apps": (APP_SETUP, APP_DOC),
    "northwind": (NORTHWIND_SETUP, NORTHWIND_DOC),
    "movielens": (MOVIELENS_SETUP, MOVIELENS_DOC),
    "retail": (RETAIL_SETUP, RETAIL_DOC),
    "play": (PLAY_SETUP, PLAY_DOC),
    "tiktok": (TIKTOK_SETUP, TIKTOK_DOC),
    "search": (SEARCH_SETUP, SEARCH_DOC),
    "device": (DEVICE_SETUP, DEVICE_DOC),
}

SHOW_CODE = '''
def tables():
    """Prints every table with its row count and columns."""
    for (t,) in db.execute("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"):
        cols = [r[1] for r in db.execute(f'PRAGMA table_info("{t}")')]
        n = db.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
        print(f"{t} ({n:,} rows): {', '.join(cols)}")

tables()'''


def load(*names, extra=""):
    """Returns (setup code, markdown doc) for the named table groups (+ extra code such as small CREATE TABLEs)."""
    names = sorted(names, key=lambda n: n != "chinook")      # the Chinook backup replaces db, so it must run first
    code = "\n\n".join(PARTS[n][0] for n in names)
    if extra:
        code += "\n\n" + extra.strip()
    code += "\n" + SHOW_CODE
    doc = "\n\n".join(PARTS[n][1] for n in names)
    return code, doc


def put_doc(ex, doc, small_doc=""):
    """Puts the table description right after the notebook title (before the setup cell)."""
    text = "## Tables\n\n" + doc + ("\n\n" + small_doc if small_doc else "") + \
           "\n\nThe setup cell prints every table with its columns. Call `tables()` again any time."
    ex.cells.insert(0, ("md", text.strip()))
