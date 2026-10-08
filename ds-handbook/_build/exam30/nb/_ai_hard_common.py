"""Shared start for the AI exam notebooks of days 21 to 30 (builders ai_21.py ... ai_30.py)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam

BASE = """import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")
pd.set_option("display.width", 120)
np.set_printoptions(precision=4, suppress=True)"""

# loaders for files whose source is a zip (data_path would save the zip under the wrong name)
LOADERS = {
    "sms": '''def load_sms():
    """UCI SMS Spam Collection: 5,572 messages, label ham/spam."""
    p = os.path.join(DATA, "sms_spam.tsv")
    if not os.path.exists(p):
        import zipfile
        z = data_path("sms_spam.zip", "https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip")
        with zipfile.ZipFile(z) as f:
            open(p, "wb").write(f.read("SMSSpamCollection"))
    return pd.read_csv(p, sep="\\t", header=None, names=["label", "text"])

sms = load_sms()''',
    "retail": '''def load_retail():
    """UCI Online Retail: 541,909 invoice lines of a UK web shop, 2010-12-01 to 2011-12-09."""
    p = os.path.join(DATA, "online_retail.csv.gz")
    if not os.path.exists(p):
        import zipfile
        z = data_path("online_retail.zip", "https://archive.ics.uci.edu/static/public/352/online+retail.zip")
        with zipfile.ZipFile(z) as f:                       # needs openpyxl (installed in Colab)
            pd.read_excel(f.open("Online Retail.xlsx")).to_csv(p, index=False, compression="gzip")
    return pd.read_csv(p, dtype={"InvoiceNo": str, "StockCode": str}, parse_dates=["InvoiceDate"])

retail = load_retail()''',
    "movielens": '''def load_ratings():
    """MovieLens latest-small: 100,836 ratings (userId, movieId, rating 0.5 to 5, unix timestamp)."""
    p = os.path.join(DATA, "movielens_ratings.csv")
    if not os.path.exists(p):
        import zipfile
        z = data_path("ml-latest-small.zip", "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip")
        with zipfile.ZipFile(z) as f:
            open(p, "wb").write(f.read("ml-latest-small/ratings.csv"))
    return pd.read_csv(p)

ratings = load_ratings()''',
}

MOCK_INTRO = ("**Mock exam.** One timer for the whole notebook: **30 minutes** for all questions. Answer the concept "
              "questions out loud (or in two or three written lines), compute the numeric ones, and do not open any "
              "hint or solution until the 30 minutes are over. Then grade each answer: full, partial or missed, "
              "and put every partial or missed one in the mistake log.")


def start(day, intro="", loads=(), extra="", data_note="", title=None):
    ex = Exam(day, "ai", intro=intro, title=title)
    if data_note:
        ex.text("## Data\n\n" + data_note)
    parts = [BASE] + [LOADERS[k] for k in loads]
    if extra:
        parts.append(extra.strip())
    ex.setup("\n\n".join(parts), data=bool(loads))
    return ex


def ask(ex, **kw):
    """ex.q plus a print of the solution output at build time (so numbers in comments can be checked)."""
    ex.last_output = ""
    ex.q(**kw)
    if kw.get("kind", "python") == "python":
        print(f"----- day {ex.day} Q{ex.n}: {kw['title']}\n{ex.last_output}")
