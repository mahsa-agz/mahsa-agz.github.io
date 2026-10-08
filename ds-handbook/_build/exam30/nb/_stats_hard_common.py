"""Shared start for the hard-band statistics notebooks (builders stats_21.py ... stats_30.py)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam

BASE = '''import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf
pd.set_option("display.width", 120)'''

URL = {
    "cookie_cats.csv": "https://raw.githubusercontent.com/robguilarr/ab_testing_cookie_cats/main/datasets/cookie_cats.csv",
    "ab_data.csv": "https://raw.githubusercontent.com/F-Zarian/Analyze_AB_test_results/main/ab_data.csv",
    "ab_countries.csv": "https://raw.githubusercontent.com/F-Zarian/Analyze_AB_test_results/main/countries.csv",
    "telco_churn.csv": "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv",
    "titanic.csv": "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv",
    "taxis.csv": "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/taxis.csv",
}


def load(var, name, **kw):
    """Setup-cell line that loads a real dataset with the Drive/local/download loader."""
    args = "".join(f", {k}={v!r}" for k, v in kw.items())
    return f'{var} = pd.read_csv(data_path("{name}", "{URL[name]}"){args})'


AB_CLEAN = '''# ab_data cleaning (the standard steps): keep rows where group and page agree, then one row per user
_ok = (((ab.group == "control") & (ab.landing_page == "old_page")) |
       ((ab.group == "treatment") & (ab.landing_page == "new_page")))
ab = ab[_ok].drop_duplicates("user_id").reset_index(drop=True)'''

PM = "\n\n**Say it to a PM:** "

MOCK_INTRO = ("**Mock exam rules.** Set one timer for the whole notebook: **30 minutes**. Answer every question "
              "before you open any hint. Open hints and solutions only after the time is up, then grade yourself: "
              "full marks need the right method, the right number and a clear sentence for the PM. Write down the "
              "time you used per question.")


def start(day, intro="", extra="", data_doc=""):
    ex = Exam(day, "stats", intro=intro)
    if data_doc:
        ex.text("## Data\n\n" + data_doc.strip())
    ex.setup(BASE + ("\n\n" + extra.strip() if extra else ""), data=True)
    return ex


def shown(ex):
    """Print the build-time output of the last python solution (to check the numbers written in comments)."""
    print(f"----- day {ex.day} Q{ex.n} output -----")
    print(getattr(ex, "last_output", ""))


def hidden_setup(ex, title, src):
    """Adds a second setup cell whose code Colab hides (form mode) because it contains the planted answer."""
    import contextlib
    import io
    from libx import code
    cell = (f'# @title {title} {{ display-mode: "form" }}\n'
            "# Spoiler inside: this cell builds made-up data with the answer planted in it. Run it, do not read it.\n"
            + src.strip())
    ex.cells.append(code(cell))
    cwd = os.getcwd()
    os.chdir(ex.workdir)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            exec(cell, ex.ns)
    finally:
        os.chdir(cwd)
