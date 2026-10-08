import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam  # noqa: F401  (used through the common helper)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _stats_hard_common import start, load, shown, PM, MOCK_INTRO

# Day 21 stats MOCK. Review topics: ratio-metrics, cuped, regression, causal-did, causal-psm-rd-iv, product-metrics.
# 5 questions, 30 minutes, one short case (Q5).

SETUP = load("telco", "telco_churn.csv") + '''
telco["churn"] = (telco["Churn"] == "Yes").astype(int)

rng = np.random.default_rng(21)

# Q1: SIMULATED feed experiment (made up), randomized by user. One row per user.
n1 = 20000
_g = rng.integers(0, 2, n1)
_imps = rng.negative_binomial(2, 2 / 32, n1) + 1                  # impressions per user, heavy tailed (mean about 31)
_ctr = rng.beta(2, 38, n1) * np.where(_g == 1, 1.04, 1.0)          # each user has an own click rate
feed = pd.DataFrame({"user_id": np.arange(n1),
                     "group": np.where(_g == 1, "treatment", "control"),
                     "impressions": _imps,
                     "clicks": rng.binomial(_imps, _ctr)})

# Q2: SIMULATED watch-time experiment (made up). pre_min = minutes in the 2 weeks before, min = minutes during the test.
rng = np.random.default_rng(214)
n2 = 10000
_pre = rng.gamma(2.0, 15.0, n2)
_t = rng.integers(0, 2, n2)
watch = pd.DataFrame({"user_id": np.arange(n2),
                      "group": np.where(_t == 1, "treatment", "control"),
                      "pre_min": _pre.round(1),
                      "min": np.clip(6 + 0.8 * _pre + rng.normal(0, 12, n2) + 1.0 * _t, 0, None).round(1)})
print(feed.shape, watch.shape, telco.shape)'''

DATA = """| Table | One row = | Columns | Real or simulated |
|---|---|---|---|
| `feed` | one user in a feed experiment | `user_id`, `group`, `impressions`, `clicks` | simulated (made up), seed 21 |
| `watch` | one user in a watch-time experiment | `user_id`, `group`, `pre_min` (minutes in the 2 weeks before), `min` (minutes during the test) | simulated (made up), seed 21 |
| `telco` | one customer of a telecom company | 21 columns from IBM Telco churn, plus `churn` (0/1) | real |"""

ex = start(21, intro=MOCK_INTRO, extra=SETUP, data_doc=DATA)

# ---------------------------------------------------------------- Q1 ratio metric / delta method
q1 = '''ctr = feed.groupby("group")[["clicks", "impressions"]].sum()
ctr["ctr"] = ctr.clicks / ctr.impressions

def ratio_se(d):
    """Delta-method SE of sum(clicks) / sum(impressions) when users are the random unit."""
    n, x, y = len(d), d.impressions, d.clicks
    r = y.sum() / x.sum()
    var = (y.var() - 2 * r * np.cov(x, y)[0, 1] + r**2 * x.var()) / (n * x.mean()**2)
    return r, np.sqrt(var)

rc, sc = ratio_se(feed[feed.group == "control"])
rt, st = ratio_se(feed[feed.group == "treatment"])
diff, se = rt - rc, np.sqrt(sc**2 + st**2)
naive = np.sqrt(sum(r * (1 - r) / ctr.loc[g, "impressions"] for g, r in (("control", rc), ("treatment", rt))))
print(f"CTR control {rc:.4f}, treatment {rt:.4f}, relative lift {diff / rc:+.1%}")
print(f"delta-method SE {se:.5f}, naive SE {naive:.5f}, ratio {se / naive:.2f}")
print(f"95% CI for the difference: [{diff - 1.96 * se:.4f}, {diff + 1.96 * se:.4f}], z = {diff / se:.2f}")
print(f"naive z = {diff / naive:.2f}")
# CTR control 0.0502, treatment 0.0516, relative lift +2.8%
# delta-method SE 0.00082, naive SE 0.00056, ratio 1.46
# 95% CI for the difference: [-0.0002, 0.0030], z = 1.72
# naive z = 2.51'''
ex.q("Click rate when the unit is a user", minutes=7, kind="python",
     prompt="The `feed` table is a made-up experiment randomized **by user**. The team reports click-through rate "
            "as `CTR = total clicks / total impressions` for each group.\n\n"
            "1. Compute CTR per group and the relative lift.\n"
            "2. Compute a correct standard error for the difference in CTR and a 95% confidence interval.\n"
            "3. A colleague used `sqrt(p(1-p)/impressions)` for each group. Compare their SE with yours. Which is "
            "right and why?\n\n"
            "Example of the shape: if control has 1,000 users with 30,000 impressions and 1,500 clicks, its CTR is "
            "0.05, but the sample size for the SE is 1,000 users, not 30,000 impressions." +
            PM + "one sentence with the lift, the interval and whether it is real.",
     hint1="Signal: the metric is a ratio of two sums and the analysis unit (impression) is smaller than the "
           "randomization unit (user). Method: delta method for a ratio metric (or a user-level bootstrap).",
     hint2="1. Per group: n users, mean impressions `mx`, mean clicks `my`, `R = my / mx`. "
           "2. `Var(R) = (var(y) - 2 R cov(x, y) + R^2 var(x)) / (n mx^2)`. "
           "3. SE of the difference = `sqrt(SE_c^2 + SE_t^2)`. 4. Compare with the binomial formula on impressions.",
     solution=q1,
     why="Impressions of the same user are correlated (each user has an own click rate and heavy users see many "
         "items), so they are not independent Bernoulli trials. The binomial SE treats every impression as an "
         "independent trial and is about 1.5 times too small here. With it the lift looks significant (z = 2.51); "
         "with the delta method, which uses users (the unit that was randomized), it is not (z = 1.72, the CI "
         "includes 0). This is how dashboards ship false wins." +
         PM + "\"CTR is 2.8% higher in the test (5.02% to 5.16%), but the 95% interval runs from -0.02 to +0.30 "
         "points, so we cannot yet tell a real gain from noise; the dashboard looked significant only because it "
         "counted every impression as an independent observation.\"",
     mistakes="Using the number of impressions as n. Averaging per-user CTRs and calling it the same metric (it "
              "weights light users as much as heavy ones: a different metric). Forgetting the covariance term.",
     learn=["stats-ratio-metrics", "stats-clt-se"])
shown(ex)

# ---------------------------------------------------------------- Q2 CUPED
q2 = '''c, t = watch[watch.group == "control"], watch[watch.group == "treatment"]

def diff_ci(yc, yt):
    d = yt.mean() - yc.mean()
    se = np.sqrt(yc.var() / len(yc) + yt.var() / len(yt))
    return d, se

d0, se0 = diff_ci(c["min"], t["min"])
theta = np.cov(watch.pre_min, watch["min"])[0, 1] / watch.pre_min.var()
adj = watch["min"] - theta * (watch.pre_min - watch.pre_min.mean())
d1, se1 = diff_ci(adj[watch.group == "control"], adj[watch.group == "treatment"])
rho = np.corrcoef(watch.pre_min, watch["min"])[0, 1]
print(f"plain: diff {d0:.2f} min, 95% CI [{d0 - 1.96 * se0:.2f}, {d0 + 1.96 * se0:.2f}]")
print(f"theta {theta:.3f}, corr {rho:.3f}, variance left 1 - rho^2 = {1 - rho**2:.2f}")
print(f"CUPED: diff {d1:.2f} min, 95% CI [{d1 - 1.96 * se1:.2f}, {d1 + 1.96 * se1:.2f}]")
print(f"SE ratio {se1 / se0:.2f}, so the same precision needs about {(se1 / se0)**2:.0%} of the users")
# plain: diff 0.48 min, 95% CI [-0.32, 1.28]
# theta 0.792, corr 0.824, variance left 1 - rho^2 = 0.32
# CUPED: diff 1.00 min, 95% CI [0.55, 1.46]
# SE ratio 0.57, so the same precision needs about 32% of the users'''
ex.q("Same test, smaller interval", minutes=6, kind="python",
     prompt="The `watch` table is a made-up experiment on watch minutes. `pre_min` was measured **before** "
            "randomization. The plain difference in means is not significant and the PM wants to run the test "
            "two more weeks.\n\n"
            "1. Compute the plain difference in mean `min` (treatment minus control) with a 95% CI.\n"
            "2. Use the pre-period to reduce variance: compute `theta`, the adjusted metric, and the new 95% CI.\n"
            "3. How much traffic does the adjustment save?" +
            PM + "should the test run two more weeks?",
     hint1="Signal: a noisy metric and a pre-experiment measure of the same metric. Method: CUPED (regression "
           "adjustment with a pre-period covariate).",
     hint2="1. `theta = cov(pre, y) / var(pre)` on all users. 2. `y_adj = y - theta * (pre - mean(pre))`. "
           "3. Welch-style SE on `y_adj` per group. 4. Variance shrinks by about `rho^2`, the squared correlation.",
     solution=q2,
     why="The covariate is measured before randomization, so it is independent of the treatment and the adjustment "
         "cannot add bias; it only removes the part of the variance that past behaviour explains. With "
         "`rho = 0.82` the variance falls to about a third. The point estimate also moves (0.48 to 1.00): by chance "
         "the treatment group had lighter users before the test, and CUPED corrects for that imbalance. The true "
         "simulated effect is 1.0 minute; the plain estimate missed half of it." +
         PM + "\"Using each user's past watch time, the new version adds about 1.0 minute per user (95% CI 0.55 to "
         "1.46); we do not need two more weeks, because the adjustment gives the precision of about three times as "
         "many users.\"",
     mistakes="Using a covariate measured after the treatment started (it can absorb the effect and bias the "
              "result). Fitting theta separately per group and then claiming the plain t-test SE. Forgetting new "
              "users who have no pre-period (fill with 0 and add an indicator, or use the group mean).",
     learn=["stats-cuped", "stats-power-mde"])
shown(ex)

# ---------------------------------------------------------------- Q3 regression on real data
q3 = '''telco["echeck"] = (telco.PaymentMethod == "Electronic check").astype(int)
print(telco.groupby("echeck").churn.mean().round(3).to_dict())          # raw churn rate
raw = smf.logit("churn ~ echeck", telco).fit(disp=0)
adj = smf.logit("churn ~ echeck + C(Contract) + tenure + C(InternetService) + MonthlyCharges", telco).fit(disp=0)
for name, m in (("raw", raw), ("adjusted", adj)):
    lo, hi = np.exp(m.conf_int().loc["echeck"])
    print(f"{name}: odds ratio {np.exp(m.params['echeck']):.2f}, 95% CI [{lo:.2f}, {hi:.2f}]")
lpm = smf.ols("churn ~ echeck + C(Contract) + tenure + C(InternetService) + MonthlyCharges", telco).fit(cov_type="HC1")
print(f"adjusted difference in churn probability (linear model): {lpm.params['echeck']:+.3f}")
print(pd.crosstab(telco.Contract, telco.echeck, normalize="columns").round(2))
# {0: 0.171, 1: 0.453}
# raw: odds ratio 4.02, 95% CI [3.60, 4.50]
# adjusted: odds ratio 1.63, 95% CI [1.43, 1.86]
# adjusted difference in churn probability (linear model): +0.106
# echeck             0     1
# Contract
# Month-to-month  0.43  0.78
# One year        0.24  0.15
# Two year        0.33  0.07'''
ex.q("Does paying by electronic check cause churn?", minutes=6, kind="python",
     prompt="Real data: `telco`. Customers who pay by **electronic check** churn much more. The PM proposes a "
            "campaign that moves them to automatic card payment and expects churn to fall to the level of the "
            "other customers.\n\n"
            "1. Compute the raw churn rate for e-check payers and for everyone else.\n"
            "2. Fit a logistic regression of churn on an e-check indicator, first alone, then controlling for "
            "contract type, tenure, internet service and monthly charges. Report both odds ratios with 95% CIs.\n"
            "3. What does the change tell you, and what would you do before funding the campaign?" +
            PM + "is the expected churn reduction realistic?",
     hint1="Signal: an observational comparison where the groups differ in other ways (contract, tenure). "
           "Method: regression adjustment for confounders, then a causal caveat.",
     hint2="1. `groupby(echeck).churn.mean()`. 2. `smf.logit('churn ~ echeck', ...)` and the same with controls. "
           "3. `exp(coef)` is the odds ratio. 4. Look at how e-check payers differ (crosstab with Contract).",
     solution=q3,
     why="78% of e-check payers are on month-to-month contracts against 43% of the others, and month-to-month "
         "customers churn the most. Controlling for contract, tenure, internet service and charges shrinks the "
         "odds ratio from 4.0 to 1.6: most of the raw gap is confounding. The linear probability model puts the adjusted gap at about 11 points instead of 28. Even that is not causal: "
         "unmeasured traits (for example people who avoid automatic payments may be less committed) can explain it, "
         "and the campaign changes the payment method, not those traits. The clean answer is an experiment: "
         "randomly offer the switch incentive (an encouragement design) and estimate the effect with IV." +
         PM + "\"Most of the gap comes from contract type, not the payment method: after adjusting, e-check payers "
         "churn about 11 points more, not 28 points, and even that may not be caused by the payment method, so "
         "let us test the switch offer on a random half before we fund it.\"",
     mistakes="Reading the raw odds ratio as the campaign effect. Saying an odds ratio of 1.63 means 63% more churn "
              "(it is odds, not probability). Adding a post-treatment variable such as TotalCharges, which mixes "
              "tenure and price.",
     learn=["stats-regression", "stats-causal-psm-rd-iv"])
shown(ex)

# ---------------------------------------------------------------- Q4 choose the causal method
ex.q("Three launches without an A/B test", minutes=5, kind="text",
     prompt="For each situation, name the method, the key assumption, how you would check it, and the estimate "
            "where numbers are given.\n\n"
            "**(a)** A feature launched in Canada only. Weekly active users: Canada 100k before, 108k after; "
            "Australia (no launch) 200k before, 210k after.\n\n"
            "**(b)** Accounts with at least 1,000 followers automatically get the Live feature. You want the effect "
            "of Live on creator retention.\n\n"
            "**(c)** You want the effect of watching a tutorial on 30-day retention. An old experiment randomly sent "
            "a push about the tutorial: 40% of pushed users watched it versus 10% of the others; 30-day retention was "
            "22.0% versus 20.5%." +
            PM + "one sentence for (c).",
     hint1="Signal: no randomization of the treatment itself, but (a) a comparison region over time, (b) a sharp "
           "cutoff, (c) a randomized nudge. Methods: difference-in-differences, regression discontinuity, "
           "instrumental variables.",
     hint2="(a) Compare growth rates, not raw differences, because the countries have different sizes. "
           "(b) Compare accounts just below and just above 1,000. (c) Wald estimator: effect of the push on "
           "retention divided by effect of the push on watching.",
     solution="""**(a) Difference-in-differences.** Canada grew 8%, Australia 5%. On the relative scale the effect is
`1.08 / 1.05 - 1 = 2.9%` (about 3 percentage points of growth). The absolute DiD `(108 - 100) - (210 - 200) = -2k` is
misleading because the countries differ in size: parallel trends are more believable in percentages (logs).
Key assumption: without the launch, Canada would have grown like Australia. Check: plot the 8 weeks before the launch
for both countries and test that the pre-trends are parallel (placebo DiD on a fake launch date); watch for
Canada-only events (holidays, marketing).

**(b) Regression discontinuity** at 1,000 followers. Compare retention of creators just above and just below the
cutoff (for example 900 to 1,100), with a local linear fit on each side. Assumption: nothing else changes at 1,000
and creators cannot precisely sort around it. Check: a density test for bunching just above 1,000 (people buying
followers to get Live), and balance of pre-cutoff covariates. The estimate is local: it holds for creators near
1,000 followers, not for large creators.

**(c) Instrumental variables.** The push is the instrument: it was randomized and changes watching.
`LATE = (0.220 - 0.205) / (0.40 - 0.10) = 0.015 / 0.30 = 0.05`, so watching the tutorial raises 30-day retention
by about 5 percentage points for the users who watch because of the push (compliers). Assumptions: the push affects
retention only through the tutorial (exclusion: doubtful, since a push itself can bring users back), and nobody
watches *because* they were not pushed (monotonicity). A weak first stage (here a 30-point jump, which is strong)
would make the estimate unstable.

**Say it to a PM:** "Among users who watch the tutorial because we nudge them, it adds about 5 points of 30-day
retention, but part of that may be the push itself, so I would confirm it with a test that pushes something
unrelated to the control group.\"""",
     why="Examiners check that you match the data shape to the design, state the identifying assumption and "
         "know a concrete check for it.",
     learn=["stats-causal-did", "stats-causal-psm-rd-iv"])

# ---------------------------------------------------------------- Q5 short case
ex.q("Short case: measuring Series", minutes=6, kind="text",
     prompt="A short-video app launches **Series**: creators sell a paid collection of 5 to 20 videos. Users "
            "buy access to one series at a time.\n\n"
            "Give: the goal in one line, one primary success metric with an exact definition, two or three driver "
            "metrics, two guardrails, and what you would look at after 2 weeks to decide whether Series works." +
            PM + "explain your primary metric in one sentence.",
     hint1="Signal: a new feature with two sides (creators and viewers) and money involved. Method: goal, then "
           "metric tree (primary, drivers, guardrails), then how to read it early.",
     hint2="1. Goal: creators earn and viewers find content worth paying for. 2. Primary metric tied to value on "
           "both sides (for example buyers and completion). 3. Funnel drivers. 4. Guardrails: free watch time, "
           "refunds, creator churn. 5. Early read: compare to an expected curve, cohort repeat purchase.",
     solution="""**Goal:** creators earn money from deep content and viewers find series worth paying for, without
hurting the free feed.

**Primary metric:** weekly paying viewers who finish at least 50% of a purchased series (per 1,000 weekly active
users). It needs a purchase *and* real consumption, so it rewards value, not clickbait trailers.

**Drivers (funnel):** series preview impressions -> preview to purchase conversion -> completion rate of purchased
series -> repeat purchase within 30 days. Creator side: number of creators publishing a series and their weekly
earnings (median, not mean, because earnings are very skewed).

**Guardrails:** free-feed watch time per user (cannibalisation), refund rate and reports per purchase (bad
content), feed session starts, and creator churn among creators who do not sell series.

**After 2 weeks:** purchases are rare and early buyers are enthusiasts, so do not extrapolate the first days.
Look at (1) the funnel by cohort of first exposure, (2) completion and refunds of buyers, (3) whether repeat purchase
starts, and (4) the free watch time guardrail from a holdout or an A/B test on the preview placement. Network
effects matter: creators react to earnings, so a viewer-level A/B test cannot measure the creator side; use a
creator-side rollout or a market-level test for that.

**Say it to a PM:** "Our main number is how many people pay for a series and watch at least half of it, because
that shows both that they valued it and that creators earned from it, and we watch free watch time to make sure we
are not just moving time out of the feed.\"""",
     why="A strong case answer gives one exact primary metric, connects drivers to it, protects the core product "
         "with guardrails, and admits what the early data cannot say.",
     learn=["stats-product-metrics", "stats-case-framework"])

ex.save()
