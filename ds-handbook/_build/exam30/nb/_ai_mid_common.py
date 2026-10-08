"""Shared setup snippets for the AI exam notebooks (ai_11 ... ai_20; file name prefixed with _ to avoid clashes). Used only by ai_*.py builders."""
import os

HELPERS = '''import numpy as np
import pandas as pd
np.set_printoptions(precision=4, suppress=True)

def check(name, fn, want, tol=1e-6):
    """fn: a zero-argument lambda that calls your code. want: expected value (number, list, array, string)
    or a function got -> True/False. Prints PASS or FAIL and never stops the notebook."""
    try:
        got = fn()
        if callable(want):
            ok = bool(want(got))
        elif isinstance(want, str) or isinstance(got, str):
            ok = got == want
        else:
            ok = got is not None and np.shape(got) == np.shape(want) and np.allclose(
                np.asarray(got, dtype=float), np.asarray(want, dtype=float), atol=tol, rtol=0)
    except Exception as e:
        got, ok = "error: " + repr(e)[:120], False
    shown = repr(got)
    shown = shown if len(shown) < 120 else shown[:117] + "..."
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else "   got " + shown))'''

ZIP = '''import io, zipfile

def zip_member(name, url, member):
    """Local path of `name` in the data folder; if missing, downloads the zip at url and extracts `member`."""
    path = os.path.join(DATA, name)
    if not os.path.exists(path):
        print("downloading", url)
        raw = urllib.request.urlopen(url).read()
        with zipfile.ZipFile(io.BytesIO(raw)) as z, open(path, "wb") as f:
            f.write(z.read(member))
    return path'''

ML_URL = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
SMS_URL = "https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip"

SMS = f'''sms = pd.read_csv(zip_member("sms_spam.tsv", "{SMS_URL}", "SMSSpamCollection"),
                  sep="\\t", header=None, names=["label", "text"])
sms["y"] = (sms["label"] == "spam").astype(int)
print("sms:", sms.shape, "spam share:", round(sms["y"].mean(), 4))'''

MOVIELENS = f'''ratings = pd.read_csv(zip_member("movielens_ratings.csv", "{ML_URL}", "ml-latest-small/ratings.csv"))
movies = pd.read_csv(zip_member("movielens_movies.csv", "{ML_URL}", "ml-latest-small/movies.csv"))
title_of = dict(zip(movies["movieId"], movies["title"]))
print("ratings:", ratings.shape, "users:", ratings["userId"].nunique(), "movies:", ratings["movieId"].nunique())'''


def setup(ex, *parts, data=False):
    """Adds the setup cell: helpers + optional snippets (strings)."""
    ex.setup("\n\n".join((HELPERS,) + ((ZIP,) if data else ()) + parts), data=data)
    if os.environ.get("AI_DEBUG"):
        orig = ex.q

        def q(*a, **k):
            ex.last_output = ""
            orig(*a, **k)
            print(f"----- Q{ex.n}: {a[0] if a else k.get('title')}\n{ex.last_output}")
        ex.q = q
