"""Data pieces for the SQL exam notebooks of days 11 to 20 (builders sql_11.py ... sql_20.py).

Each piece is (setup code, markdown doc). `build_setup(ex, *names)` puts the chosen pieces into the setup cell and a
table overview right after it. Chinook and the short-video tables come from sql_product_tables.py (shared with days
1 to 10); the shopping-app tables come from sql_events_tables.py. Real datasets load from exam_prep/data
(or download from the source URLs in DATASETS.md).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sql_product_tables import CHINOOK_SETUP, CHINOOK_DOC, PRODUCT_SETUP, PRODUCT_DOC  # noqa: E402
from sql_events_tables import APP_SETUP, APP_DOC  # noqa: E402

NW_URL = "https://raw.githubusercontent.com/jpwhite3/northwind-SQLite3/main/dist/northwind.db"
ML_URL = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
RETAIL_URL = "https://archive.ics.uci.edu/static/public/352/online+retail.zip"
COOKIE_URL = "https://raw.githubusercontent.com/robguilarr/ab_testing_cookie_cats/main/datasets/cookie_cats.csv"
AB_URL = "https://raw.githubusercontent.com/F-Zarian/Analyze_AB_test_results/main/ab_data.csv"
GPLAY_URL = ("https://raw.githubusercontent.com/malborroni/Foundations_of_Computer-Science/master/datasets/"
             "googleplaystore.csv")

NORTHWIND_SETUP = f'''# Real data: Northwind orders (enlarged version, 2012 to 2023). Copied into tables with an nw_ prefix.
db.execute("ATTACH DATABASE ? AS nw", (data_path("northwind.db", "{NW_URL}"),))
db.executescript("""
CREATE TABLE nw_orders AS SELECT OrderID AS order_id, CustomerID AS customer_id, EmployeeID AS employee_id,
       substr(OrderDate, 1, 10) AS order_date, ShipCountry AS ship_country FROM nw.Orders;
CREATE TABLE nw_order_details AS SELECT OrderID AS order_id, ProductID AS product_id, UnitPrice AS unit_price,
       Quantity AS quantity, Discount AS discount FROM nw."Order Details";
CREATE TABLE nw_products AS SELECT ProductID AS product_id, ProductName AS product_name, CategoryID AS category_id
       FROM nw.Products;
CREATE TABLE nw_categories AS SELECT CategoryID AS category_id, CategoryName AS category_name FROM nw.Categories;
""")
db.execute("DETACH DATABASE nw")'''
NORTHWIND_DOC = """**Real tables: Northwind** (orders of a food wholesaler; enlarged build with dates 2012 to 2023; MIT license,
jpwhite3/northwind-SQLite3). Columns renamed to snake_case:

| Table | One row is | Columns |
|---|---|---|
| `nw_orders` | one order (16,282) | `order_id`, `customer_id`, `employee_id`, `order_date` ('YYYY-MM-DD'), `ship_country` |
| `nw_order_details` | one product line in an order (609,283) | `order_id`, `product_id`, `unit_price`, `quantity`, `discount` (0 to 1). Revenue = `unit_price * quantity * (1 - discount)` |
| `nw_products` / `nw_categories` | one product (77) / category (8) | `product_id`, `product_name`, `category_id` / `category_id`, `category_name` |"""

MOVIELENS_SETUP = f'''# Real data: MovieLens small (GroupLens, research and education use).
def movielens(short):
    path = os.path.join(DATA, f"movielens_{{short}}.csv")
    if not os.path.exists(path):
        import io, zipfile
        print("downloading MovieLens")
        z = zipfile.ZipFile(io.BytesIO(urllib.request.urlopen("{ML_URL}").read()))
        for s in ("ratings", "movies", "tags", "links"):
            with open(os.path.join(DATA, f"movielens_{{s}}.csv"), "wb") as f:
                f.write(z.read(f"ml-latest-small/{{s}}.csv"))
    return pd.read_csv(path)

_r = movielens("ratings")
_r["rated_at"] = pd.to_datetime(_r["timestamp"], unit="s").dt.strftime("%Y-%m-%d %H:%M:%S")
_r.rename(columns={{"userId": "user_id", "movieId": "movie_id"}})[["user_id", "movie_id", "rating", "rated_at"]] \\
    .to_sql("ml_ratings", db, index=False)
movielens("movies").rename(columns={{"movieId": "movie_id"}}).to_sql("ml_movies", db, index=False)'''
MOVIELENS_DOC = """**Real tables: MovieLens small** (GroupLens; 610 users rated 9,742 movies, 1996 to 2018):

| Table | One row is | Columns |
|---|---|---|
| `ml_ratings` | one rating (100,836) | `user_id`, `movie_id`, `rating` (0.5 to 5), `rated_at` ('YYYY-MM-DD HH:MM:SS', UTC) |
| `ml_movies` | one movie (9,742) | `movie_id`, `title` (with the year), `genres` (several genres joined by a vertical bar, e.g. Comedy\|Romance) |"""

RETAIL_SETUP = f'''# Real data: UCI Online Retail (UK online shop, 2010-12 to 2011-12; CC BY 4.0).
def online_retail():
    path = os.path.join(DATA, "online_retail.csv.gz")
    if not os.path.exists(path):
        import io, zipfile
        print("downloading Online Retail (about 23 MB, then converting the xlsx)")
        z = zipfile.ZipFile(io.BytesIO(urllib.request.urlopen("{RETAIL_URL}").read()))
        pd.read_excel(io.BytesIO(z.read("Online Retail.xlsx"))).to_csv(path, index=False, compression="gzip")
    return pd.read_csv(path, dtype={{"InvoiceNo": str, "StockCode": str}})

_o = online_retail()
_o.columns = ["invoice_no", "stock_code", "description", "quantity", "invoice_date", "unit_price", "customer_id",
              "country"]
_o["customer_id"] = _o["customer_id"].astype("Int64")
_o["invoice_date"] = pd.to_datetime(_o["invoice_date"]).dt.strftime("%Y-%m-%d %H:%M:%S")
_o.to_sql("retail", db, index=False)'''
RETAIL_DOC = """**Real table: UCI Online Retail** (a UK online gift shop, 2010-12-01 to 2011-12-09; CC BY 4.0):

| Table | One row is | Columns |
|---|---|---|
| `retail` | one product line of an invoice (541,909) | `invoice_no` (starts with 'C' = cancellation), `stock_code`, `description`, `quantity` (negative for returns), `invoice_date` ('YYYY-MM-DD HH:MM:SS'), `unit_price`, `customer_id` (NULL for about 25% of rows), `country` |"""

COOKIE_SETUP = f'''# Real data: Cookie Cats mobile game A/B test (educational use).
pd.read_csv(data_path("cookie_cats.csv", "{COOKIE_URL}")).to_sql("cookie_cats", db, index=False)'''
COOKIE_DOC = """**Real table: Cookie Cats** (a mobile puzzle game moved its first gate from level 30 to level 40 for half of new players):

| Table | One row is | Columns |
|---|---|---|
| `cookie_cats` | one new player (90,189) | `userid`, `version` ('gate_30' control / 'gate_40' treatment), `sum_gamerounds` (rounds in the first week), `retention_1`, `retention_7` (1 = came back on day 1 / day 7) |"""

AB_SETUP = f'''# Real data: Udacity landing-page A/B test log (educational use; has deliberate data problems).
pd.read_csv(data_path("ab_data.csv", "{AB_URL}")).rename(columns={{"group": "grp"}}).to_sql("ab_data", db, index=False)'''
AB_DOC = """**Real table: ab_data** (Udacity landing-page experiment, January 2017; contains deliberate mistakes):

| Table | One row is | Columns |
|---|---|---|
| `ab_data` | one page visit (294,478) | `user_id`, `timestamp` (text with microseconds), `grp` ('control' / 'treatment'; renamed from `group`, a reserved word), `landing_page` ('old_page' / 'new_page'), `converted` (0/1) |"""

GPLAY_SETUP = f'''# Real data: Google Play store apps (scraped; study use only). Messy text columns on purpose.
_g = pd.read_csv(data_path("googleplaystore.csv", "{GPLAY_URL}")).rename(columns=lambda c: c.lower().replace(" ", "_"))
_g["app"] = _g["app"].str.replace("\\u2013", "-").str.replace("\\u2014", "-")   # long dashes in app names -> "-"
_g.to_sql("play_apps", db, index=False)'''
GPLAY_DOC = """**Real table: Google Play apps** (scraped in 2018; messy on purpose):

| Table | One row is | Columns |
|---|---|---|
| `play_apps` | one scraped app listing (10,841) | `app`, `category`, `rating` (can be NULL), `reviews` (text!), `size`, `installs` (text like '10,000+'), `type`, `price`, `content_rating`, `genres`, `last_updated` (text like 'January 7, 2018'), `current_ver`, `android_ver` |"""

PIECES = {
    "chinook": (CHINOOK_SETUP, CHINOOK_DOC),         # must come first: it copies a whole database into db
    "product": (PRODUCT_SETUP, PRODUCT_DOC),
    "app": (APP_SETUP, APP_DOC),
    "northwind": (NORTHWIND_SETUP, NORTHWIND_DOC),
    "movielens": (MOVIELENS_SETUP, MOVIELENS_DOC),
    "retail": (RETAIL_SETUP, RETAIL_DOC),
    "cookie": (COOKIE_SETUP, COOKIE_DOC),
    "ab": (AB_SETUP, AB_DOC),
    "gplay": (GPLAY_SETUP, GPLAY_DOC),
}


def build_setup(ex, *names, extra=""):
    """Setup cell with the chosen data pieces (in PIECES order) plus a table overview."""
    names = [n for n in PIECES if n in names]
    code = "\n\n".join(PIECES[n][0] for n in names)
    if extra:
        code += "\n\n" + extra.strip()
    code += ('\n\nprint("tables:", ", ".join(r[0] for r in db.execute('
             '"SELECT name FROM sqlite_master WHERE type = \'table\' ORDER BY name")))')
    ex.setup(code, data=True)
    ex.text("## Tables\n\n" + "\n\n".join(PIECES[n][1] for n in names) +
            "\n\nThe queries run in SQLite. They are written in standard SQL that also works in PostgreSQL; "
            "differences (dates, integer division) are noted in the solutions.")
