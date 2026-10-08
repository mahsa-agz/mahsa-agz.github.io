import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam  # noqa: F401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stats_mid_common import start, q, pm

# Day 19 stats: focus PSM, regression discontinuity, instrumental variables; review DiD.
ex = start(19, ["telco"],
           note="Q1 uses the real `telco` data. Q2 (regression discontinuity) and Q3 (instrumental variable) use "
                "**simulated** data generated in the question, because the real datasets here have no sharp cutoff "
                "or random encouragement; with simulated data we also know the true effect.")

# ---------------------------------------------------------------- Q1
q(ex, title="Does tech support keep customers?", minutes=8,
  prompt="Among `telco` customers with internet (`InternetService != 'No'`), compare churn for customers with "
         "`TechSupport == 'Yes'` (treated) vs `'No'`.\n\n"
         "(a) Naive difference in churn rate (treated minus untreated, pp).\n\n"
         "(b) Propensity score matching: fit a logistic model for `P(TechSupport)` from `tenure`, `MonthlyCharges`, "
         "`Contract`, `InternetService`, `SeniorCitizen`, `Partner`, `Dependents`, `PaperlessBilling`, "
         "`PaymentMethod`. Match each treated customer to the nearest untreated customer on the logit of the score "
         "(with replacement, caliper 0.2 * sd of the logit). Report the ATT (effect on the treated) and how many "
         "treated customers were matched.\n\n"
         "(c) Balance check: standardised mean difference (SMD) of `tenure` and of 'two-year contract' before and "
         "after matching.\n\n"
         "(d) Say it to a PM, with the main caveat.",
  stub="d = telco[telco.InternetService != \"No\"].copy()\n"
       "d[\"treat\"] = (d.TechSupport == \"Yes\").astype(int)\n"
       "d[\"churn\"] = (d.Churn == \"Yes\").astype(int)\n# your code here",
  hint1="Signal: observational data, the 'treatment' is chosen by customers, many observed confounders. Method: "
        "propensity score matching, then a balance check.",
  hint2="1. `smf.logit('treat ~ tenure + MonthlyCharges + C(Contract) + ...', data=d).fit(disp=0)`. "
        "2. `lp = fit.predict(..., which='linear')` or `np.log(p / (1 - p))`. 3. For each treated logit, "
        "`np.searchsorted` on the sorted control logits, take the closer neighbour, drop matches beyond the "
        "caliper. 4. ATT = mean(churn treated) - mean(churn of their matches). 5. SMD = diff in means / "
        "sqrt((var_t + var_c) / 2).",
  solution='''d = telco[telco.InternetService != "No"].copy()
d["treat"] = (d.TechSupport == "Yes").astype(int)
d["churn"] = (d.Churn == "Yes").astype(int)
d["two_year"] = (d.Contract == "Two year").astype(int)
naive = d[d.treat == 1].churn.mean() - d[d.treat == 0].churn.mean()
print(f"naive diff {naive * 100:.1f} pp")

ps = smf.logit("treat ~ tenure + MonthlyCharges + C(Contract) + C(InternetService) + SeniorCitizen + C(Partner)"
               " + C(Dependents) + C(PaperlessBilling) + C(PaymentMethod)", data=d).fit(disp=0).predict(d)
d["logit"] = np.log(ps / (1 - ps))
def match(d):
    """1:1 nearest neighbour on the logit, with replacement, caliper 0.2 sd. Returns treated rows, their matches."""
    t, c = d[d.treat == 1], d[d.treat == 0].sort_values("logit")
    cl, tl = c.logit.values, t.logit.values
    i = np.clip(np.searchsorted(cl, tl), 1, len(cl) - 1)
    nearest = np.where(abs(cl[i - 1] - tl) <= abs(cl[i] - tl), i - 1, i)
    keep = abs(cl[nearest] - tl) <= 0.2 * d.logit.std()
    return t[keep], c.iloc[nearest[keep]]

t, c = d[d.treat == 1], d[d.treat == 0]
tm, cm = match(d)
print(f"matched {len(tm)} of {len(t)} treated; ATT {(tm.churn.mean() - cm.churn.mean()) * 100:.1f} pp")
rng = np.random.default_rng(0)          # bootstrap CI (scores kept fixed: a quick approximation)
boot = []
for _ in range(200):
    a, b = match(d.iloc[rng.integers(0, len(d), len(d))])
    boot.append(a.churn.mean() - b.churn.mean())
print("bootstrap 95% CI (pp):", (np.percentile(boot, [2.5, 97.5]) * 100).round(1))

def smd(a, b):
    return (a.mean() - b.mean()) / np.sqrt((a.var() + b.var()) / 2)
for col in ["tenure", "two_year"]:
    print(f"SMD {col}: before {smd(t[col], c[col]):.2f}, after {smd(tm[col], cm[col]):.2f}")
# naive diff -26.5 pp
# matched 2041 of 2044 treated; ATT -4.3 pp
# bootstrap 95% CI (pp): [-7.4 -0.9]
# SMD tenure: before 0.83, after 0.04
# SMD two_year: before 0.86, after 0.05''',
  why="Customers who buy tech support differ a lot from those who do not (longer tenure, more long contracts), and "
      "those traits also lower churn, so the naive gap (-26.5 pp) overstates the benefit."
      " After matching, tenure and two-year-contract SMDs fall from 0.83 and 0.86 to 0.04 and 0.05, and the ATT is "
      "-4.3 pp (bootstrap CI -7.4 to -0.9 pp): much smaller, but still below zero. Matching on the propensity score "
      "compares treated customers with untreated customers who looked equally likely to buy support; after matching "
      "the SMDs should be below about 0.1 (they are). The remaining gap is the effect *only if* there is no unobserved "
      "confounder (for example how tech-savvy or committed a customer is)."
      + pm("Customers with tech support churn less, but much of the raw gap comes from them being long-term, "
           "contract customers; comparing like with like, support still goes with about 4 points lower churn, which makes "
           "a test of offering free support for 3 months worth running.",
           [("PSM vs regression?", "Both adjust only for observed variables. Matching makes the comparison "
             "transparent (you can show balance tables) and avoids extrapolating outside the overlap region; "
             "regression is simpler and uses all data. Doubly robust methods combine both."),
            ("Overlap?", "Check the propensity distributions of both groups. Treated customers with scores where "
             "there are no controls cannot be matched (that is what the caliper drops); report how many.")]),
  complexity="O(n log n) for the sort and binary search matching.",
  mistakes="Skipping the balance check. Matching without a caliper (bad matches). Claiming causality without "
           "naming the unobserved confounders. Using standard errors that ignore matching with replacement "
           "(use a bootstrap or Abadie-Imbens SEs).",
  learn=["stats-causal-psm-rd-iv"])

# ---------------------------------------------------------------- Q2
q(ex, title="Gold members spend more. Because of gold?", minutes=7,
  prompt="Simulate (seed 19) 20,000 shoppers: `points ~ Uniform(500, 1500)` earned last quarter; everyone with "
         "`points >= 1000` gets Gold status (free shipping). Next-quarter spend: "
         "`spend = 50 + 0.03 * (points - 1000) + 0.00000004 * (points - 1000)^3 + 5 * gold + Normal(0, 10)`. The true "
         "effect of Gold is 5.\n\n"
         "(a) Naive difference in mean spend, gold vs not.\n\n"
         "(b) Regression discontinuity: local linear regression `spend ~ gold * r` where `r = points - 1000`, "
         "using only shoppers with `|r| <= h`, for h = 100, 200 and 500. Report estimate and SE for each.\n\n"
         "(c) Say it to a PM.\n\n"
         "Follow-up: what could break this design in real life?",
  stub="rng = np.random.default_rng(19)\nn = 20000\n# your code here",
  hint1="Signal: treatment assigned by a sharp cutoff on a score. Method: regression discontinuity; compare "
        "people just above and just below the cutoff.",
  hint2="1. Simulate. 2. Naive: `spend[gold].mean() - spend[~gold].mean()`. 3. For each h: subset, "
        "`smf.ols('spend ~ gold * r')`, read the `gold` coefficient (the jump at r = 0). Use robust SEs (HC1).",
  solution='''rng = np.random.default_rng(19)
n = 20000
points = rng.uniform(500, 1500, n)
r = points - 1000
gold = (r >= 0).astype(int)
spend = 50 + 0.03 * r + 0.00000004 * r ** 3 + 5 * gold + rng.normal(0, 10, n)
df = pd.DataFrame(dict(r=r, gold=gold, spend=spend))
print(f"naive: {df[df.gold == 1].spend.mean() - df[df.gold == 0].spend.mean():.2f}")
for h in [100, 200, 500]:
    fit = smf.ols("spend ~ gold * r", data=df[abs(df.r) <= h]).fit(cov_type="HC1")
    print(f"h={h}: estimate {fit.params['gold']:.2f}, SE {fit.bse['gold']:.2f}, n {int(fit.nobs)}")
# naive: 22.52
# h=100: estimate 4.89, SE 0.62, n 4109
# h=200: estimate 4.52, SE 0.44, n 8030
# h=500: estimate 2.94, SE 0.28, n 20000''',
  why="Gold members spent more partly because they were already bigger shoppers (higher points), so the naive gap "
      "(22.52) is more than four times the true 5. Just around the cutoff, people with 990 and 1,010 points are essentially the same, so the "
      "jump in the regression line at 0 is the effect of Gold for shoppers near 1,000 points. A narrow window gives "
      "less bias but more noise; a wide window adds bias when the true relation is curved. Here h = 100 gives 4.89 (SE 0.62), "
      "h = 200 gives 4.52 (SE 0.44), and h = 500 (all data) gives 2.94 with the smallest SE (0.28): precise and "
      "wrong, because a straight line cannot follow the cubic curve over the whole range. Report a few "
      "bandwidths or a data-driven choice."
      + pm("Comparing shoppers just above and just below the Gold threshold, Gold status itself adds about 5 in "
           "spend per quarter; the much bigger raw gap mostly reflects that Gold members were already heavy "
           "shoppers.",
           [("What breaks it?", "Manipulation: shoppers who buy a little extra to cross 1,000 points (check for a "
             "bump in the density of points just above the cutoff, a McCrary test). Other things that change at "
             "1,000 points too. And the effect is local: it says nothing about shoppers far from the cutoff.")]),
  complexity="O(n) per fit.",
  mistakes="Using a global high-order polynomial (unstable at the cutoff). Reading the result as the effect for "
           "all members.",
  learn=["stats-causal-psm-rd-iv"])

# ---------------------------------------------------------------- Q3
q(ex, title="A random nudge as a lever", minutes=7,
  prompt="Simulate (seed 3) 50,000 users. Hidden motivation `m ~ Normal(0, 1)`. A **random** push notification "
         "`z` (50/50) invites users to try a new playlist feature. Use: "
         "`d = 1 if -0.5 + 1.2 * z + m + Normal(0, 1) > 0`. Outcome minutes next week: "
         "`y = 10 + 2 * d + 4 * m + Normal(0, 3)`. The true effect of using the feature is 2.\n\n"
         "(a) Naive OLS of `y` on `d`.\n\n"
         "(b) Intent-to-treat effect (effect of the push on y), first stage (effect of the push on d), and the "
         "Wald / IV estimate `ITT / first stage`, with an approximate SE `SE(ITT) / first stage`.\n\n"
         "(c) Say it to a PM. What does the IV estimate measure exactly?\n\n"
         "Follow-up: list the IV assumptions and which one you cannot test.",
  stub="rng = np.random.default_rng(3)\nn = 50000\n# your code here",
  hint1="Signal: you cannot randomise the feature use, but you randomised an encouragement. Method: instrumental "
        "variable (Wald estimator / 2SLS).",
  hint2="1. Simulate in the given order. 2. Naive: `smf.ols('y ~ d')`. 3. ITT: mean y by z; first stage: mean d by "
        "z. 4. IV = ITT / FS.",
  solution='''rng = np.random.default_rng(3)
n = 50000
m = rng.normal(0, 1, n)
z = rng.integers(0, 2, n)
d = (-0.5 + 1.2 * z + m + rng.normal(0, 1, n) > 0).astype(int)
y = 10 + 2 * d + 4 * m + rng.normal(0, 3, n)
df = pd.DataFrame(dict(z=z, d=d, y=y))
print(f"naive OLS: {smf.ols('y ~ d', data=df).fit().params['d']:.2f}")
itt_fit = smf.ols("y ~ z", data=df).fit()
fs = df[df.z == 1].d.mean() - df[df.z == 0].d.mean()
itt = itt_fit.params["z"]
print(f"ITT {itt:.3f} (SE {itt_fit.bse['z']:.3f}), first stage {fs:.3f}, "
      f"IV {itt / fs:.2f} (SE about {itt_fit.bse['z'] / fs:.2f})")
# naive OLS: 6.10
# ITT 0.701 (SE 0.049), first stage 0.326, IV 2.15 (SE about 0.15)''',
  why="Motivated users both use the feature and listen more, so naive OLS mixes the feature effect with "
      "motivation and is far too high (6.10 vs the true 2). The push is random, so its effect on minutes (ITT, 0.70) is clean, but small, "
      "because the push raises feature use by only 32.6 pp. Dividing by the first stage scales the ITT up to the users whose "
      "feature use was changed by the push. The IV estimate, 0.701 / 0.326 = 2.15 (SE about 0.15), is within one SE of the true "
      "2, with a wider CI than an "
      "experiment on the feature itself would give."
      + pm("Users who try the feature listen much more, but most of that is because they were keen listeners "
           "anyway; using the random push as a lever, the feature itself adds about 2 minutes a week for the users "
           "the push convinced.",
           [("Assumptions", "(1) Relevance: z moves d (testable: first stage, F-statistic above about 10). (2) "
             "Independence: z is as good as random (true here by design). (3) Exclusion: z affects y only through d, "
             "not testable (a push might itself remind people to open the app, which breaks it). (4) Monotonicity: "
             "nobody uses the feature *because* they got no push. Under these, IV estimates the LATE: the effect "
             "for compliers."),
            ("Weak instrument?", "If the push barely changes usage, the ratio is unstable and biased toward OLS. "
             "Report the first stage.")]),
  complexity="O(n).",
  mistakes="Running OLS of y on predicted d by hand and trusting its SE (the second-stage SE is wrong; use a 2SLS "
           "routine). Claiming the IV estimate holds for all users (it is the complier effect).",
  learn=["stats-causal-psm-rd-iv"])

# ---------------------------------------------------------------- Q4 review
q(ex, title="Android got the redesign first", minutes=5, review=True,
  prompt="A notification redesign shipped on Android only. Average weekly active minutes per user (made-up "
         "numbers): Android 30.0 before and 33.0 after; iOS 35.0 before and 36.5 after.\n\n"
         "(a) Compute the DiD in minutes. Then compute the DiD on the log scale (percent changes) "
         "`(log 33 - log 30) - (log 36.5 - log 35)`, shown as a percentage.\n\n"
         "(b) The two answers tell slightly different stories. Which assumption does each one make? Say it to a "
         "PM.",
  stub="# your code here",
  hint1="Signal: 2x2 before/after, treated/untreated. Method: difference-in-differences; parallel trends can be "
        "assumed in levels or in logs (percent).",
  hint2="1. Level DiD = (33 - 30) - (36.5 - 35). 2. Log DiD with `np.log`. 3. Convert: `np.exp(x) - 1`.",
  solution='''lvl = (33.0 - 30.0) - (36.5 - 35.0)
logd = (np.log(33.0) - np.log(30.0)) - (np.log(36.5) - np.log(35.0))
print(f"DiD in minutes: {lvl:.2f}")                       # 1.50
print(f"DiD on log scale: {(np.exp(logd) - 1) * 100:.2f}%")  # 5.48%
print(f"1.5 minutes as % of Android before: {lvl / 30 * 100:.1f}%")  # 5.0%''',
  why="The level DiD assumes that without the redesign Android would have gained the same 1.5 *minutes* as iOS, "
      "giving +1.5 minutes. The log DiD assumes Android would have grown by the same *percentage* as iOS (+4.3%), so "
      "the counterfactual is 31.29 minutes and the effect is +5.48%, or about 1.71 minutes. Groups with different "
      "baselines (30 vs 35) make this choice matter. Pick the scale where pre-period trends look parallel."
      + pm("The redesign added about 1.5 to 1.7 minutes a week per Android user (about 5%), depending on whether we "
           "assume Android would have grown by the same minutes or the same percentage as iOS; the pre-launch "
           "weeks will tell us which assumption fits better.",
           [("Also check", "Concurrent Android-only changes (an OS update, a Play Store feature) in the same weeks "
             "would break either version.")]),
  complexity="O(1).",
  mistakes="Comparing Android after vs before only (+3 minutes, which includes the general growth). Ignoring "
           "the scale of the parallel-trends assumption.",
  learn=["stats-causal-did"])

ex.save()
