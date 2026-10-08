"""Shared start for the AI exam notebooks of days 1 to 10 (builders ai_01.py ... ai_10.py).
File name prefixed with _ai_easy_ to avoid clashes with the other AI builders.

start(day, loads, builtin, intro) -> Exam with a setup cell that defines the data loaders and loads the day's data.
qc(ex, **kw): ex.q(...) plus a check that every `# out: ...` line in the solution equals what the solution
printed at build time (so the numbers written in comments always match the code).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam

LOADERS = '''import io, zipfile, warnings
import numpy as np
import pandas as pd
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
pd.set_option("display.width", 120)

SEABORN = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/"
TELCO_URL = "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv"
BANK_URL = "https://archive.ics.uci.edu/static/public/222/bank+marketing.zip"

def load_telco():
    """IBM Telco churn, 7,043 customers. Target: Churn (Yes/No)."""
    return pd.read_csv(data_path("telco_churn.csv", TELCO_URL))

def load_seaborn(name):
    """titanic, penguins, diamonds, mpg, tips ... from the seaborn-data repo."""
    return pd.read_csv(data_path(name + ".csv", SEABORN + name + ".csv"))

def load_bank():
    """UCI Bank Marketing (bank-additional-full), 41,188 calls. Target: y (yes/no). The source is a zip in a zip."""
    path = data_path("bank_marketing.csv")
    if not os.path.exists(path):
        print("downloading bank_marketing (zip)")
        outer = zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(BANK_URL).read()))
        inner = zipfile.ZipFile(io.BytesIO(outer.read("bank-additional.zip")))
        with open(path, "wb") as f:
            f.write(inner.read("bank-additional/bank-additional-full.csv"))
    return pd.read_csv(path, sep=";")

def check(fn, cases, tol=1e-6):
    """Runs fn on each (args, expected) case; numbers and arrays are compared with a tolerance."""
    ok = 0
    for args, want in cases:
        args = args if isinstance(args, tuple) else (args,)
        try:
            got = fn(*args)
            good = got is not None and np.shape(got) == np.shape(want) and bool(
                np.allclose(np.asarray(got, dtype=float), np.asarray(want, dtype=float), atol=tol))
        except Exception as e:
            got, good = "error: " + repr(e)[:120], False
        ok += good
        shown = " ".join(repr(got).split())
        shown = shown if len(shown) < 100 else shown[:97] + "..."
        print(("PASS " if good else "FAIL ") + f"{fn.__name__}(...) -> {shown}" + ("" if good else f"   expected {want!r}"))
    print(f"{ok}/{len(cases)} passed")'''

LOAD_LINES = {
    "telco": 'telco = load_telco()\nprint("telco", telco.shape)',
    "bank": 'bank = load_bank()\nprint("bank", bank.shape)',
    "titanic": 'titanic = load_seaborn("titanic")\nprint("titanic", titanic.shape)',
    "penguins": 'penguins = load_seaborn("penguins")\nprint("penguins", penguins.shape)',
    "diamonds": 'diamonds = load_seaborn("diamonds")\nprint("diamonds", diamonds.shape)',
    "mpg": 'mpg = load_seaborn("mpg")\nprint("mpg", mpg.shape)',
}

DOCS = {
    "telco": "`telco`: IBM Telco churn, 7,043 customers, one row = one customer. `Churn` (Yes/No), `tenure` (months), "
             "`Contract`, `MonthlyCharges`, `TotalCharges` (text with blanks), 9 service columns, demographics.",
    "bank": "`bank`: UCI Bank Marketing, 41,188 phone calls of a Portuguese bank, one row = one call. Target `y` "
            "(did the client subscribe a term deposit). Client columns (`age`, `job`, ...), campaign columns "
            "(`contact`, `month`, `duration`, `campaign`, `pdays`, `previous`, `poutcome`), macro columns.",
    "titanic": "`titanic`: 891 passengers, one row = one passenger. `survived` (0/1), `pclass`, `sex`, `age` (has NaN), "
               "`sibsp`, `parch`, `fare`, `embarked`, plus derived columns (`alive`, `who`, ...).",
    "penguins": "`penguins`: 344 Palmer penguins. `species`, `island`, `bill_length_mm`, `bill_depth_mm`, "
                "`flipper_length_mm`, `body_mass_g`, `sex` (MALE/FEMALE, has NaN).",
    "diamonds": "`diamonds`: 53,940 diamonds. `price` (USD), `carat`, `cut`, `color`, `clarity`, `depth`, `table`, `x`, `y`, `z`.",
    "mpg": "`mpg`: 398 cars (1970 to 1982). `mpg`, `cylinders`, `displacement`, `horsepower` (has NaN), `weight`, "
           "`acceleration`, `model_year`, `origin`, `name`.",
}


def start(day, loads=(), builtin="", intro=""):
    ex = Exam(day, "ai", intro=intro)
    docs = [DOCS[k] for k in loads]
    if builtin:
        docs.append(builtin)
    ex.text("## Data\n\n" + "\n".join("- " + d for d in docs) +
            "\n\nThe setup cell loads every table into a pandas DataFrame (from your Drive folder, or downloads it). "
            "Everything runs on the free Colab CPU in seconds. Numbers in the solutions come from scikit-learn 1.8; "
            "other versions can differ in the last digit.")
    extra = LOADERS + ("\n\n" + "\n".join(LOAD_LINES[k] for k in loads) if loads else "")
    ex.setup(extra, data=True)
    return ex


def qc(ex, **kw):
    """ex.q plus: each '# out: <line>' in the solution must equal the next printed line (in order)."""
    ex.q(**kw)
    if kw.get("kind", "python") != "python":
        return
    want = [l.split("# out:", 1)[1].strip() for l in kw.get("solution", "").splitlines() if "# out:" in l]
    got = [l.strip() for l in getattr(ex, "last_output", "").splitlines()
           if l.strip() and not l.startswith(("PASS", "FAIL")) and not l.rstrip().endswith("passed")]
    if os.environ.get("AI_DRAFT"):
        print(f"--- Q{ex.n} printed:\n" + "\n".join(got))
        return
    if want != got:
        raise AssertionError(f"Day {ex.day} ai Q{ex.n}: '# out:' comments do not match the output.\n"
                             f"comments: {want}\nprinted:  {got}")
