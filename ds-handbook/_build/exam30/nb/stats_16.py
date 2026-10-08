import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam  # noqa: F401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stats_mid_common import start, q, pm

# Day 16 stats: focus CUPED; review ratio metrics and power/MDE.
EXTRA = '''
# Customer table for today: real revenue before (x) and during (y) a pretend 6-month experiment.
ok = retail.CustomerID.notna() & ~retail.InvoiceNo.str.startswith("C") & (retail.Quantity > 0) & (retail.UnitPrice > 0)
d = retail[ok].assign(rev=lambda t: t.Quantity * t.UnitPrice)
pre = d[d.InvoiceDate < "2011-06-01"].groupby("CustomerID").rev.sum()
during = d[(d.InvoiceDate >= "2011-06-01") & (d.InvoiceDate < "2011-12-01")]
cust = pd.DataFrame({"y": during.groupby("CustomerID").rev.sum(),
                     "orders": during.groupby("CustomerID").InvoiceNo.nunique()})
cust["x"] = pre.reindex(cust.index).fillna(0)                   # 0 = no purchase before the experiment
cust["y"] = cust.y.clip(upper=cust.y.quantile(0.99))           # cap both at their 99th percentile
cust["x"] = cust.x.clip(upper=cust.x.quantile(0.99))
# A pretend experiment (SIMULATED assignment and effect): random 50/50 split, treatment revenue +5%.
rng = np.random.default_rng(16)
cust["treat"] = rng.integers(0, 2, len(cust))
cust["y_exp"] = np.where(cust.treat == 1, cust.y * 1.05, cust.y)
print(cust.shape, "share with pre-period revenue:", round((cust.x > 0).mean(), 3))
'''
ex = start(16, ["retail"], extra=EXTRA,
           note="The setup builds `cust`, one row per customer who bought something between 2011-06-01 and "
                "2011-11-30 (the pretend experiment window): `y` = revenue in the window, `orders` = orders in the "
                "window, `x` = revenue in the 6 months before (2010-12-01 to 2011-05-31, 0 if none), both capped at "
                "the 99th percentile. These are **real** numbers. The assignment `treat` and the +5% effect in "
                "`y_exp` are **simulated** (the shop never ran this test), so we know the true effect. In Colab, "
                "upload `online_retail.csv.gz` to the data folder if it is missing.")

# ---------------------------------------------------------------- Q1
q(ex, title="How much noise does last half-year explain?", minutes=6,
  prompt="Using `cust` (ignore `treat` for now):\n\n"
         "(a) Compute `theta = cov(x, y) / var(x)` and the adjusted metric `y_cuped = y - theta * (x - mean(x))`.\n\n"
         "(b) Compare `var(y_cuped) / var(y)` with `1 - corr(x, y)^2`. What share of the variance is removed?\n\n"
         "(c) Why does subtracting `theta * (x - mean(x))` not change the average treatment effect?\n\n"
         "(d) Say it to a PM.",
  stub="x, y = cust.x.values, cust.y.values\n# your code here",
  hint1="Signal: a metric with a strongly correlated pre-period version. Method: CUPED (control variate with the "
        "pre-period metric).",
  hint2="1. `theta = np.cov(x, y)[0, 1] / x.var(ddof=1)`. 2. `y_cv = y - theta * (x - x.mean())`. "
        "3. `rho = np.corrcoef(x, y)[0, 1]`.",
  solution='''x, y = cust.x.values, cust.y.values
theta = np.cov(x, y)[0, 1] / x.var(ddof=1)
y_cv = y - theta * (x - x.mean())
rho = np.corrcoef(x, y)[0, 1]
print(f"theta {theta:.3f}, rho {rho:.3f}")
print(f"var ratio {y_cv.var(ddof=1) / y.var(ddof=1):.3f}, 1 - rho^2 {1 - rho ** 2:.3f}")
# theta 1.099, rho 0.763
# var ratio 0.418, 1 - rho^2 0.418  -> CUPED removes 58% of the variance''',
  why="CUPED is regression adjustment: the part of y that is predictable from x (before the test) is noise for the "
      "comparison, so we remove it. The remaining variance is exactly `1 - rho^2` of the original. Because x was "
      "measured before randomisation, its mean is the same in both arms in expectation, so `theta * (mean(x_T) - "
      "mean(x_C))` has expectation 0 and the effect estimate stays unbiased."
      + pm("Last half-year's spending predicts most of this half-year's spending, so after we account for it, the "
           "test needs much less data to see the same effect.",
           [("Which x to use?", "The same metric in a pre-period of similar length is usually best. Any variable "
             "fixed before assignment is allowed; anything measured after assignment is not."),
            ("Why not just use y - x?", "That is CUPED with theta = 1. It helps only if theta is near 1; theta from "
             "the data minimises the variance.")]),
  complexity="O(n).",
  mistakes="Estimating theta separately in each arm with very different values (fine in theory, but use pooled data "
           "for a stable estimate). Using a covariate measured during the test.",
  learn=["stats-cuped"])

# ---------------------------------------------------------------- Q2
q(ex, title="Same test, narrower interval", minutes=7,
  prompt="Now use the pretend experiment: `treat` (0/1) and `y_exp` (revenue with a simulated +5% effect in "
         "treatment).\n\n"
         "(a) Plain estimate: difference in mean `y_exp`, its SE (Welch) and 95% CI, and the effect as % of the "
         "control mean.\n\n"
         "(b) CUPED estimate: compute theta on the pooled data with `y_exp` and `x`, adjust, then take the same "
         "difference, SE and CI.\n\n"
         "(c) Check (b) with OLS `y_exp ~ treat + x_centered`. Do you get the same estimate?\n\n"
         "(d) Say it to a PM.\n\n"
         "Follow-up: 45% of customers have `x = 0` (new customers). Is CUPED still valid? Can you do better?",
  stub="# your code here",
  hint1="Signal: an A/B readout with pre-period data available. Method: CUPED (equivalently, regression on "
        "treatment plus the centred covariate).",
  hint2="1. `diff_ci(a, b)` helper: mean diff, `sqrt(var_a/n_a + var_b/n_b)`. 2. Adjust `y_exp` with pooled theta. "
        "3. `smf.ols('y_exp ~ treat + xc', data=...)`, read the `treat` coefficient.",
  solution='''def diff_ci(v, t):
    a, b = v[t == 1], v[t == 0]
    diff = a.mean() - b.mean()
    se = np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return diff, se, b.mean()

t, x, y = cust.treat.values, cust.x.values, cust.y_exp.values
theta = np.cov(x, y)[0, 1] / x.var(ddof=1)
y_cv = y - theta * (x - x.mean())
for name, v in [("plain", y), ("CUPED", y_cv)]:
    diff, se, base = diff_ci(v, t)
    print(f"{name}: diff {diff:.1f} ({diff / base * 100:.1f}%), SE {se:.1f}, "
          f"CI [{diff - 1.96 * se:.1f}, {diff + 1.96 * se:.1f}]")
fit = smf.ols("y_exp ~ treat + xc", data=cust.assign(xc=x - x.mean())).fit()
print(f"OLS treat coef {fit.params['treat']:.1f}, SE {fit.bse['treat']:.1f}")
# plain: diff -14.1 (-1.2%), SE 64.8, CI [-141.0, 112.8]
# CUPED: diff 36.5 (3.1%), SE 41.9, CI [-45.5, 118.6]
# OLS treat coef 36.5, SE 41.9''',
  why="Both estimators target the same effect; CUPED removes the customer-to-customer differences that existed "
      "before the test, so its SE falls from 64.8 to 41.9 (a factor `sqrt(1 - rho^2)` = 0.65). OLS with the centred covariate gives "
      "the same estimate and SE here (in general it fits theta jointly with the treatment effect, so tiny "
      "differences are normal). Note the plain estimate is even negative (-1.2%) in this split: by chance the "
      "treatment arm got customers who spent less before the test. CUPED corrects for that imbalance (+3.1%); the "
      "true effect is +5%, and both CIs include it."
      + pm("With the same customers, accounting for what they spent before the test makes our error bar about "
           "two thirds as wide, so we can call smaller effects or finish tests sooner.",
           [("Customers with x = 0?", "Still valid: x = 0 is a pre-treatment value, so no bias. But one slope for "
             "'new' and 'returning' customers is a poor fit. Add an indicator `has_pre = x > 0` (and its interaction) "
             "to the regression, or use a better predictor (CUPAC: a model's prediction from pre-period features).")]),
  complexity="O(n).",
  mistakes="Computing theta on the control group only and then applying it to both (fine) versus on treatment only "
           "(can leak the effect into theta; avoid). Forgetting to centre x (the treat coefficient is unchanged, but "
           "the intercept is harder to read).",
  learn=["stats-cuped", "stats-regression"])

# ---------------------------------------------------------------- Q3
q(ex, title="Is it unbiased, and what does it buy us?", minutes=6,
  prompt="(a) Repeat the pretend experiment 500 times (seed 0): new random split, +5% on treatment `y`, plain and "
         "CUPED difference in means. Report the mean and standard deviation of each estimator across the 500 runs "
         "and the true average effect `0.05 * mean(y over treated)` (about `0.05 * mean(y)`).\n\n"
         "(b) Sample size per group to detect a 5% lift with 80% power (alpha 0.05): `n = 2 (z_a + z_b)^2 sd^2 / "
         "delta^2`, with sd of y, and with sd of y_cuped.\n\n"
         "(c) Say it to a PM.",
  stub="rng = np.random.default_rng(0)\n# your code here",
  hint1="Signal: check an estimator by simulation, then translate variance into users. Method: Monte Carlo over "
        "random assignments; CUPED sample size = plain n times `1 - rho^2`.",
  hint2="1. In each run: `t = rng.integers(0, 2, n)`, `ye = y * (1 + 0.05 * t)`, theta from pooled (x, ye). "
        "2. Store both differences. 3. Means and sds of the two lists. 4. delta = 0.05 * mean(y).",
  solution='''rng = np.random.default_rng(0)
x, y = cust.x.values, cust.y.values
plain, cuped = [], []
for _ in range(500):
    t = rng.integers(0, 2, len(y))
    ye = y * (1 + 0.05 * t)
    theta = np.cov(x, ye)[0, 1] / x.var(ddof=1)
    yc = ye - theta * (x - x.mean())
    plain.append(ye[t == 1].mean() - ye[t == 0].mean())
    cuped.append(yc[t == 1].mean() - yc[t == 0].mean())
print(f"true effect about {0.05 * y.mean():.1f}")
print(f"plain: mean {np.mean(plain):.1f}, sd {np.std(plain):.1f}")
print(f"CUPED: mean {np.mean(cuped):.1f}, sd {np.std(cuped):.1f}")
# true effect about 57.9
# plain: mean 61.0, sd 66.8
# CUPED: mean 58.2, sd 44.3

z = stats.norm.ppf(0.975) + stats.norm.ppf(0.8)
theta = np.cov(x, y)[0, 1] / x.var(ddof=1)
sd_plain, sd_cuped = y.std(ddof=1), (y - theta * (x - x.mean())).std(ddof=1)
delta = 0.05 * y.mean()
n_plain = int(np.ceil(2 * z ** 2 * sd_plain ** 2 / delta ** 2))
n_cuped = int(np.ceil(2 * z ** 2 * sd_cuped ** 2 / delta ** 2))
print("n per group plain:", n_plain, " CUPED:", n_cuped)
# n per group plain: 16317  CUPED: 6825''',
  why="Across 500 random splits both estimators centre on the true effect of about 57.9 (61.0 and 58.2, no bias "
      "beyond simulation noise), but the CUPED estimates spread less (sd 44.3 vs 66.8). The ratio of the two sample sizes equals `1 - rho^2`. With only about 3,500 customers "
      "in this shop, a 5% lift is not detectable either way; CUPED cuts the requirement from 16,317 to 6,825 per group, which in "
      "a real company means weeks of test time."
      + pm("CUPED gives the same answer on average, just with less noise; for this metric it cuts the number of "
           "customers we need by more than half, which means shorter tests at no extra risk.",
           [("When does CUPED not help?", "When the pre-period metric is weakly correlated with the outcome "
             "(new-user tests, rare events such as first purchase). Gain = rho^2, so rho = 0.3 only saves 9%.")]),
  complexity="O(runs * n), about a second for 500 runs.",
  mistakes="Judging unbiasedness from a single run. Forgetting the factor 2 in the per-group formula.",
  learn=["stats-cuped", "stats-power-mde"])

# ---------------------------------------------------------------- Q4 review
q(ex, title="Order value in the pretend test", minutes=6, review=True,
  prompt="In the pretend experiment, the +5% was applied to revenue but not to the number of orders, so average "
         "order value (AOV) per arm should be about 5% higher in treatment.\n\n"
         "(a) For each arm compute AOV = `sum(y_exp) / sum(orders)` and its delta-method variance with customers as "
         "units (formula from day 15). Give the relative lift and a 95% CI for the difference.\n\n"
         "(b) Say it to a PM.\n\n"
         "Follow-up: can you apply CUPED to a ratio metric like AOV?",
  stub="# your code here",
  hint1="Signal: a ratio of two sums, randomised by customer. Method: delta method per arm, then the SE of the "
        "difference is `sqrt(Var_T + Var_C)`.",
  hint2="1. `delta_ratio(Y, N)` returns (R, Var). 2. Apply to each arm's `y_exp` and `orders`. "
        "3. CI = (R_T - R_C) plus or minus 1.96 * sqrt(Var_T + Var_C).",
  solution='''def delta_ratio(Y, N):
    n, mY, mN = len(Y), Y.mean(), N.mean()
    R = mY / mN
    return R, (Y.var(ddof=1) - 2 * R * np.cov(Y, N)[0, 1] + R ** 2 * N.var(ddof=1)) / (n * mN ** 2)

arm = {k: delta_ratio(g.y_exp.values, g.orders.values.astype(float)) for k, g in cust.groupby("treat")}
(Rc, vc), (Rt, vt) = arm[0], arm[1]
se = np.sqrt(vc + vt)
print(f"AOV control {Rc:.1f}, treatment {Rt:.1f}, lift {(Rt / Rc - 1) * 100:.1f}%, "
      f"CI for diff [{Rt - Rc - 1.96 * se:.1f}, {Rt - Rc + 1.96 * se:.1f}]")
# AOV control 384.6, treatment 413.2, lift 7.4%, CI for diff [-4.8, 62.0]''',
  why="The delta method gives an honest SE for the ratio at the customer level. With about 1,700 customers per arm "
      "the CI (-4.8 to 62.0) includes 0 even though the true lift is about 5% (the "
      "observed 7.4% is partly chance), which is the same lesson as Q3: this shop is too small for this test "
      "without variance reduction."
      + pm("Order value looks higher in the new version, but with this many customers the range of plausible "
           "effects is wide, so on its own this would not be a conclusive result.",
           [("CUPED for a ratio?", "Yes, after linearisation: build the per-customer variable "
             "`L = (Y - R * N) / mean(N)` (the delta-method influence term) for the experiment period and the same "
             "for the pre-period, then apply CUPED to L. Many platforms do exactly this.")]),
  complexity="O(n).",
  mistakes="Computing AOV per customer and averaging (a different metric, see day 15). Treating orders as "
           "independent rows.",
  learn=["stats-ratio-metrics", "stats-cuped"])

ex.save()
