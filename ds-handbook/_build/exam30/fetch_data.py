"""Download exam-practice datasets into exam_prep/data and verify they load."""
import io, os, zipfile, sqlite3, json, requests, pandas as pd

D = r"C:\Users\USER\Desktop\personal\my_personal\learn\exam_prep\data"
os.makedirs(D, exist_ok=True)
SB = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/"

def get(url):
    r = requests.get(url, timeout=300); r.raise_for_status(); return r.content

def save(name, data):
    with open(os.path.join(D, name), "wb") as f: f.write(data)

def plain(name, url):
    save(name, get(url))

def from_zip(url, members):  # members: {inner_path: local_name}
    z = zipfile.ZipFile(io.BytesIO(get(url)))
    for inner, local in members.items():
        save(local, z.read(inner))

jobs = []
for n in ["tips", "penguins", "titanic", "flights", "diamonds", "taxis", "mpg"]:
    jobs.append((f"{n}.csv", lambda n=n: plain(f"{n}.csv", SB + f"{n}.csv")))
jobs += [
 ("chinook.sqlite", lambda: plain("chinook.sqlite", "https://github.com/lerocha/chinook-database/releases/download/v1.4.5/Chinook_Sqlite.sqlite")),
 ("northwind.db", lambda: plain("northwind.db", "https://raw.githubusercontent.com/jpwhite3/northwind-SQLite3/main/dist/northwind.db")),
 ("cookie_cats.csv", lambda: plain("cookie_cats.csv", "https://raw.githubusercontent.com/robguilarr/ab_testing_cookie_cats/main/datasets/cookie_cats.csv")),
 ("ab_data.csv", lambda: plain("ab_data.csv", "https://raw.githubusercontent.com/F-Zarian/Analyze_AB_test_results/main/ab_data.csv")),
 ("ab_countries.csv", lambda: plain("ab_countries.csv", "https://raw.githubusercontent.com/F-Zarian/Analyze_AB_test_results/main/countries.csv")),
 ("googleplaystore.csv", lambda: plain("googleplaystore.csv", "https://raw.githubusercontent.com/malborroni/Foundations_of_Computer-Science/master/datasets/googleplaystore.csv")),
 ("googleplaystore_user_reviews.csv", lambda: plain("googleplaystore_user_reviews.csv", "https://raw.githubusercontent.com/malborroni/Foundations_of_Computer-Science/master/datasets/googleplaystore_user_reviews.csv")),
 ("telco_churn.csv", lambda: plain("telco_churn.csv", "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv")),
 ("movielens", lambda: from_zip("https://files.grouplens.org/datasets/movielens/ml-latest-small.zip",
     {f"ml-latest-small/{f}.csv": f"movielens_{f}.csv" for f in ["ratings", "movies", "tags", "links"]})),
 ("sms_spam", lambda: from_zip("https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip", {"SMSSpamCollection": "sms_spam.tsv"})),
]
def bank():
    outer = zipfile.ZipFile(io.BytesIO(get("https://archive.ics.uci.edu/static/public/222/bank+marketing.zip")))
    inner = zipfile.ZipFile(io.BytesIO(outer.read("bank-additional.zip")))
    save("bank_marketing.csv", inner.read("bank-additional/bank-additional-full.csv"))
jobs.append(("bank_marketing.csv", bank))
def retail():
    z = zipfile.ZipFile(io.BytesIO(get("https://archive.ics.uci.edu/static/public/352/online+retail.zip")))
    df = pd.read_excel(io.BytesIO(z.read("Online Retail.xlsx")))
    df.to_csv(os.path.join(D, "online_retail.csv.gz"), index=False, compression="gzip")
jobs.append(("online_retail.csv.gz", retail))
for t in ["raw_customers", "raw_orders", "raw_payments"]:
    jobs.append((f"jaffle_{t}.csv", lambda t=t: plain(f"jaffle_{t}.csv", f"https://raw.githubusercontent.com/dbt-labs/jaffle_shop/main/seeds/{t}.csv")))

for name, fn in jobs:
    if name not in ("movielens", "sms_spam") and os.path.exists(os.path.join(D, name)):
        continue
    try: fn(); print("OK ", name)
    except Exception as e: print("FAIL", name, e)

# verify
rep = {}
for f in sorted(os.listdir(D)):
    p = os.path.join(D, f); mb = os.path.getsize(p) / 1e6
    if f.endswith((".sqlite", ".db")):
        con = sqlite3.connect(p)
        tabs = [r[0] for r in con.execute("select name from sqlite_master where type='table'")]
        info = {t: con.execute(f'select count(*) from "{t}"').fetchone()[0] for t in tabs}
        rep[f] = dict(mb=round(mb, 2), tables=info)
    else:
        kw = dict(sep="\t", header=None, names=["label", "text"]) if f.endswith(".tsv") else (dict(sep=";") if f == "bank_marketing.csv" else {})
        df = pd.read_csv(p, **kw)
        rep[f] = dict(mb=round(mb, 2), rows=len(df), cols=list(df.columns))
print(json.dumps(rep, indent=1))
