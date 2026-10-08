"""Shared start for the stats exam notebooks of days 11 to 20 (builders stats_11.py ... stats_20.py)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam

URLS = {
    "cookie_cats.csv": "https://raw.githubusercontent.com/robguilarr/ab_testing_cookie_cats/main/datasets/cookie_cats.csv",
    "ab_data.csv": "https://raw.githubusercontent.com/F-Zarian/Analyze_AB_test_results/main/ab_data.csv",
    "ab_countries.csv": "https://raw.githubusercontent.com/F-Zarian/Analyze_AB_test_results/main/countries.csv",
    "telco_churn.csv": "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv",
    "tips.csv": "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/tips.csv",
    "mpg.csv": "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/mpg.csv",
    "diamonds.csv": "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/diamonds.csv",
    "titanic.csv": "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv",
}

# variable name -> (file, extra read_csv code)
LOADS = {
    "cats": "cats = pd.read_csv(data_path(\"cookie_cats.csv\", \"{u}\"))",
    "ab": "ab = pd.read_csv(data_path(\"ab_data.csv\", \"{u}\"))",
    "countries": "countries = pd.read_csv(data_path(\"ab_countries.csv\", \"{u}\"))",
    "telco": "telco = pd.read_csv(data_path(\"telco_churn.csv\", \"{u}\"))",
    "tips": "tips = pd.read_csv(data_path(\"tips.csv\", \"{u}\"))",
    "mpg": "mpg = pd.read_csv(data_path(\"mpg.csv\", \"{u}\"))",
    "diamonds": "diamonds = pd.read_csv(data_path(\"diamonds.csv\", \"{u}\"))",
    "titanic": "titanic = pd.read_csv(data_path(\"titanic.csv\", \"{u}\"))",
    "retail": "retail = pd.read_csv(data_path(\"online_retail.csv.gz\"), dtype={{\"InvoiceNo\": str, \"StockCode\": str}},\n"
              "                     parse_dates=[\"InvoiceDate\"])",
}
FILES = {"cats": "cookie_cats.csv", "ab": "ab_data.csv", "countries": "ab_countries.csv", "telco": "telco_churn.csv",
         "tips": "tips.csv", "mpg": "mpg.csv", "diamonds": "diamonds.csv", "titanic": "titanic.csv"}

DOCS = {
    "cats": "`cats` (Cookie Cats, a real mobile-game A/B test, 90,189 players): `userid`, `version` (gate_30 = control, "
            "gate_40 = treatment: the first gate moved from level 30 to level 40), `sum_gamerounds` (rounds played in "
            "the first 14 days after install), `retention_1`, `retention_7` (True if the player came back 1 / 7 days "
            "after install).",
    "ab": "`ab` (Udacity e-commerce landing page test, real, 294,478 rows): `user_id`, `timestamp`, `group` "
          "(control / treatment), `landing_page` (old_page / new_page), `converted` (0/1). It has some rows where "
          "group and page do not match and some repeated users.",
    "countries": "`countries` (290,584 rows): `user_id`, `country` (UK, US, CA). Joins to `ab`.",
    "telco": "`telco` (IBM Telco churn, real, 7,043 customers): `tenure` (months), `Contract`, `MonthlyCharges`, "
             "`TotalCharges` (text with blanks), service columns such as `InternetService`, `TechSupport`, and "
             "`Churn` (Yes/No).",
    "tips": "`tips` (244 restaurant bills, real): `total_bill`, `tip`, `sex`, `smoker`, `day`, `time`, `size`.",
    "mpg": "`mpg` (398 cars, real): `mpg`, `cylinders`, `displacement`, `horsepower` (6 NaN), `weight`, "
           "`acceleration`, `model_year`, `origin`, `name`.",
    "diamonds": "`diamonds` (53,940 diamonds, real): `carat`, `cut`, `color`, `clarity`, `depth`, `table`, `price`, "
                "`x`, `y`, `z`.",
    "titanic": "`titanic` (891 passengers, real): `survived`, `pclass`, `sex`, `age`, `fare`, ...",
    "retail": "`retail` (UCI Online Retail, real, 541,909 invoice lines from a UK web shop, 2010-12 to 2011-12): "
              "`InvoiceNo` (a C prefix means a cancellation), `StockCode`, `Description`, `Quantity`, "
              "`InvoiceDate`, `UnitPrice`, `CustomerID` (about 25% missing), `Country`.",
}

BASE = """import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
import warnings
warnings.filterwarnings("ignore")
pd.set_option("display.width", 120)"""


def start(day, loads=(), intro="", note="", extra=""):
    ex = Exam(day, "stats", intro=intro)
    docs = [DOCS[k] for k in loads]
    if docs or note:
        ex.text("## Data\n\n" + "\n\n".join("- " + d for d in docs) + ("\n\n" + note if note else ""))
    lines = [BASE]
    for k in loads:
        u = URLS.get(FILES.get(k, ""), "")
        lines.append(LOADS[k].format(u=u))
    if loads:
        lines.append("print(\"loaded:\", " + ", ".join(f"\"{k}\", {k}.shape" for k in loads) + ")")
    if extra:
        lines.append(extra.strip())
    ex.setup("\n".join(lines), data=bool(loads))
    return ex


def q(ex, **kw):
    """ex.q plus: print the solution output at build time so the numbers in comments can be checked."""
    ex.last_output = None
    ex.q(**kw)
    if kw.get("kind", "python") == "python":
        print(f"----- Q{ex.n} output -----")
        print(ex.last_output)


def pm(say, follow=()):
    """'Say it to a PM' model sentence plus follow-up answers, appended to the solution's why text."""
    s = f"\n\n**Say it to a PM:** {say}"
    if follow:
        s += "\n\n**Follow-ups:**\n\n" + "\n".join(f"- *{a}* {b}" for a, b in follow)
    return s
