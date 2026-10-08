"""Shared start for the statistics exam notebooks of days 1 to 10 (builders stats_01.py ... stats_10.py).

start(day, datasets)  -> Exam with a setup cell that imports numpy/pandas/scipy and loads the named real datasets.
Q(ex, ..., pm=..., out=...) -> wraps ex.q:
  * adds the "say it to a PM" instruction to the prompt and the model PM sentence to the solution,
  * appends the expected printed output as comments under the solution code and CHECKS it against the real
    build-time output (the build fails on any mismatch, so every number in the code comments is true).
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam

SEABORN = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/{}.csv"
LOADERS = {
    "tips": 'tips = pd.read_csv(data_path("tips.csv", "%s"))' % SEABORN.format("tips"),
    "taxis": 'taxis = pd.read_csv(data_path("taxis.csv", "%s"), parse_dates=["pickup", "dropoff"])'
             % SEABORN.format("taxis"),
    "penguins": 'penguins = pd.read_csv(data_path("penguins.csv", "%s"))' % SEABORN.format("penguins"),
    "titanic": 'titanic = pd.read_csv(data_path("titanic.csv", "%s"))' % SEABORN.format("titanic"),
    "cookie": 'cookie = pd.read_csv(data_path("cookie_cats.csv", '
              '"https://raw.githubusercontent.com/robguilarr/ab_testing_cookie_cats/main/datasets/cookie_cats.csv"))',
    "telco": 'telco = pd.read_csv(data_path("telco_churn.csv", '
             '"https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/'
             'Telco-Customer-Churn.csv"))',
    "ab": 'ab_raw = pd.read_csv(data_path("ab_data.csv", '
          '"https://raw.githubusercontent.com/F-Zarian/Analyze_AB_test_results/main/ab_data.csv"))\n'
          '# clean copy: keep rows where group and page agree, one row per user (the raw file has both problems)\n'
          'ab = ab_raw[(ab_raw["group"] == "treatment") == (ab_raw["landing_page"] == "new_page")]\n'
          'ab = ab.drop_duplicates("user_id").reset_index(drop=True)',
    "sms": '_sms = os.path.join(DATA, "sms_spam.tsv")\n'
           'if not os.path.exists(_sms):  # the UCI file comes as a zip\n'
           '    import zipfile, io as _io\n'
           '    _z = urllib.request.urlopen("https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip").read()\n'
           '    open(_sms, "wb").write(zipfile.ZipFile(_io.BytesIO(_z)).read("SMSSpamCollection"))\n'
           'sms = pd.read_csv(_sms, sep="\\t", header=None, names=["label", "text"], quoting=3)',
}
DOCS = {
    "tips": "`tips`: 244 restaurant bills (`total_bill`, `tip`, `sex`, `smoker`, `day`, `time`, `size`).",
    "taxis": "`taxis`: 6,433 New York taxi trips from March 2019 (`pickup`, `distance`, `fare`, `tip`, `total`, "
             "`payment`, `pickup_borough` ...).",
    "penguins": "`penguins`: 344 penguins (`species`, `island`, `bill_length_mm`, `bill_depth_mm`, "
                "`flipper_length_mm`, `body_mass_g`, `sex`; some NaN).",
    "titanic": "`titanic`: 891 passengers (`survived` 0/1, `pclass`, `sex`, `age`, `fare`, `class`, `who` ...).",
    "cookie": "`cookie`: Cookie Cats mobile game A/B test, 90,189 players. `version` is `gate_30` (control) or "
              "`gate_40` (treatment: the first gate moved from level 30 to 40); `sum_gamerounds` = rounds played "
              "in the first week; `retention_1`, `retention_7` = came back 1 / 7 days after install (bool).",
    "telco": "`telco`: 7,043 telecom customers (`tenure` in months, `Contract`, `MonthlyCharges`, `TotalCharges` "
             "(text!), `Churn` Yes/No ...).",
    "ab": "`ab`: Udacity landing-page A/B test, cleaned in the setup to one row per user (`user_id`, `group` "
          "control/treatment, `converted` 0/1). `ab_raw` is the raw file.",
    "sms": "`sms`: 5,574 SMS messages (`label` ham/spam, `text`).",
}

BASE = '''import numpy as np
import pandas as pd
from scipy import stats as st
pd.set_option("display.width", 120)'''


def start(day, datasets, intro=""):
    ex = Exam(day, "stats", intro=intro)
    ex.text("## Data\n\nAll real datasets (see DATASETS.md for sources). The setup cell loads them:\n\n" +
            "\n".join("- " + DOCS[d] for d in datasets) +
            "\n\nClassic probability questions need no data: solve them on paper first, then check with a "
            "simulation (`rng = np.random.default_rng(0)`).")
    loads = "\n".join(LOADERS[d] for d in datasets)
    shapes = "for _name in %r:\n    print(_name, globals()[_name].shape)" % (list(datasets),)
    ex.setup(BASE + "\n\n" + loads + "\n" + shapes, data=True)
    return ex


PM_ASK = ("\n\n**Then say it to a PM:** one or two plain sentences with the number and what it means for the "
          "product (no jargon).")


def Q(ex, title, prompt, hint1, hint2, solution, why, pm, out=None, kind="python", minutes=6, stub=None,
      mistakes="", learn=(), source=None, review=False, level=None):
    """Statistics question. `out` = the exact text the solution prints (checked at build time)."""
    esc = lambda t: re.sub(r"(?<!\\)\$", r"\\$", t)   # money signs: escape so markdown does not read math
    prompt, hint1, hint2, why, pm, mistakes = map(esc, (prompt, hint1, hint2, why, pm, mistakes))
    if kind == "text":
        solution = esc(solution)
    sol = solution.strip()
    if kind == "python" and out is not None:
        sol += "\n\n# Output:\n" + "\n".join("# " + line if line else "#" for line in out.strip().splitlines())
    if kind == "python" and stub is None:
        stub = "# your code here\n"
    if kind == "text":
        sol = sol + "\n\n**Say it to a PM:** " + pm.strip()
        why_full = why
    else:
        why_full = why + "\n\n**Say it to a PM:** " + pm.strip()
    ex.q(title, prompt.strip() + PM_ASK, hint1, hint2, sol, why_full, minutes=minutes, level=level, kind=kind,
         stub=stub, mistakes=mistakes, learn=learn, source=source, review=review)
    if kind == "python":
        got = ex.last_output.strip()
        if out is None:
            print(f"----- Q{ex.n} output (no `out` given):\n{got}\n-----")
        else:
            want = out.strip()
            norm = lambda s: [l.rstrip() for l in s.splitlines()]
            if norm(got) != norm(want):
                raise AssertionError(f"Day {ex.day} stats Q{ex.n}: printed output differs.\n--- got:\n{got}\n"
                                     f"--- expected:\n{want}")
