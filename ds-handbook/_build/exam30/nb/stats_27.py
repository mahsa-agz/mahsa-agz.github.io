import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam  # noqa: F401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _stats_hard_common import start, load, shown, PM, AB_CLEAN

# Day 27 stats. Focus: heterogeneous-effects (and Simpson's paradox). Review: regression, launch-decisions.

SETUP = (load("telco", "telco_churn.csv") + '\ntelco["churn"] = (telco["Churn"] == "Yes").astype(int)\n' +
         load("ab", "ab_data.csv") + "\n" + AB_CLEAN + "\n" + load("countries", "ab_countries.csv") + "\n" +
         load("titanic", "titanic.csv") + '''
ab = ab.merge(countries, on="user_id")
ab["t"] = (ab.group == "treatment").astype(int)
print(telco.shape, ab.shape, titanic.shape)''')

DATA = """| Table | One row = | Columns | Real or simulated |
|---|---|---|---|
| `telco` | one customer of a telecom company (IBM sample) | `PhoneService`, `InternetService` (DSL / Fiber optic / No), `Contract`, `tenure`, ... and `churn` (0/1) | real |
| `ab` | one user of the Udacity landing-page test, cleaned and joined with `countries` | `group`, `t` (1 = treatment), `converted`, `country` (US/UK/CA) | real |
| `titanic` | one Titanic passenger | `survived`, `sex`, `pclass` (1/2/3), `age`, ... | real |"""

ex = start(27, extra=SETUP, data_doc=DATA)

# ---------------------------------------------------------------- Q1 Simpson's paradox (telco)
q1 = '''print(telco.groupby("PhoneService").churn.agg(["mean", "size"]).round(3))
tab = telco.groupby(["InternetService", "PhoneService"]).churn.agg(["mean", "size"]).round(3)
print(tab)
print(pd.crosstab(telco.PhoneService, telco.InternetService, normalize="index").round(3))
#               mean  size
# PhoneService
# No           0.249   682
# Yes          0.267  6361
#                               mean  size
# InternetService PhoneService
# DSL             No           0.249   682
#                 Yes          0.166  1739
# Fiber optic     Yes          0.419  3096
# No              Yes          0.074  1526
# InternetService    DSL  Fiber optic     No
# PhoneService
# No               1.000        0.000  0.000
# Yes              0.273        0.487  0.240'''
ex.q("Does phone service make customers leave?", minutes=6, kind="python",
     prompt="Real data: `telco`. A PM sees that customers **with** phone service churn more than customers "
            "without it and proposes a study of \"what is wrong with our phone product\".\n\n"
            "1. Reproduce the overall churn rates by `PhoneService`.\n"
            "2. Repeat the comparison inside each `InternetService` group. What happens?\n"
            "3. Explain the reversal with the mix of customers, and say which comparison is fair and what its "
            "limits are." +
            PM + "should the team study the phone product?",
     hint1="Signal: a comparison of rates between groups that differ in composition. Method: stratify by the "
           "likely confounder and look for Simpson's paradox (and for strata where only one group exists).",
     hint2="1. `groupby(PhoneService).churn.mean()`. 2. `groupby([InternetService, PhoneService])`. 3. Crosstab of "
           "PhoneService by InternetService: where do phone customers sit, and what is the churn level there?",
     solution=q1,
     why="Overall, phone customers churn more (26.7% versus 24.9%). But every customer without phone service "
         "has DSL internet, and inside DSL the comparison reverses: 16.6% with phone versus 24.9% without. The "
         "phone group contains all Fiber customers (49% of them, with 41.9% churn), and the no-phone group has "
         "none, so the overall gap is driven by Fiber, not by phone service. The fair comparison is inside DSL, "
         "the only stratum where both groups exist (positivity: for Fiber and no-internet customers there is "
         "no one without phone to compare with). Even inside DSL it is still observational: customers who "
         "bundle phone and internet may simply be more settled (contract, tenure), so the -8.3-point gap is not "
         "a causal effect of phone service either." + PM + "\"Phone customers look worse only because all our "
         "Fiber customers have phone and Fiber churns a lot; among comparable DSL customers, those with phone "
         "churn less (17% versus 25%), so the problem to study is Fiber churn, not the phone product.\"",
     mistakes="Stopping at the overall rates. Reporting an 'adjusted' effect for Fiber when nobody in Fiber lacks "
              "phone service (no overlap). Concluding that phone service reduces churn (still confounded).",
     learn=["stats-heterogeneous-effects", "stats-descriptive"])
shown(ex)

# ---------------------------------------------------------------- Q2 HTE by country (ab_data)
q2 = '''rows = []
for c, d in ab.groupby("country"):
    g = d.groupby("t").converted.agg(["mean", "count"])
    diff = g.loc[1, "mean"] - g.loc[0, "mean"]
    se = np.sqrt((g["mean"] * (1 - g["mean"]) / g["count"]).sum())
    rows.append((c, int(g["count"].sum()), round(diff, 4), round(diff - 1.96 * se, 4), round(diff + 1.96 * se, 4),
                 round(2 * stats.norm.sf(abs(diff / se)), 3)))
print(pd.DataFrame(rows, columns=["country", "users", "diff", "ci_low", "ci_high", "p"]))

full = smf.logit("converted ~ t * C(country)", ab).fit(disp=0)
main = smf.logit("converted ~ t + C(country)", ab).fit(disp=0)
lr = 2 * (full.llf - main.llf)
print(f"interaction test: LR = {lr:.2f}, df = 2, p = {stats.chi2.sf(lr, 2):.2f}")
print(f"chance that at least one of 3 null segments has p < 0.05: {1 - 0.95 ** 3:.3f}")
#   country   users    diff  ci_low  ci_high      p
# 0      CA   14499 -0.0069 -0.0173   0.0035  0.195
# 1      UK   72466  0.0011 -0.0036   0.0059  0.635
# 2      US  203619 -0.0022 -0.0050   0.0007  0.132
# interaction test: LR = 2.47, df = 2, p = 0.29
# chance that at least one of 3 null segments has p < 0.05: 0.143'''
ex.q("Does the new page work in the UK?", minutes=6, kind="python",
     prompt="Real data: `ab` joined with countries. Overall the new landing page did not help (day 23). The UK "
            "marketing lead notices that the UK point estimate is positive and asks to launch the new page in the "
            "UK only.\n\n"
            "1. For each country, give the treatment minus control conversion difference, a 95% CI and the "
            "p-value.\n"
            "2. Test formally whether the effect differs between countries (an interaction test).\n"
            "3. Answer the UK lead." +
            PM + "the answer to the UK lead.",
     hint1="Signal: a request to act on one segment of a flat experiment. Method: heterogeneous treatment "
           "effects: per-segment CIs plus a formal interaction test, with multiple comparisons in mind.",
     hint2="1. Loop over countries: difference of proportions and its SE. 2. Compare `converted ~ t * "
           "C(country)` with `converted ~ t + C(country)` by a likelihood-ratio test (df = 2). 3. With 3 "
           "segments, what is the chance that at least one looks good by luck?",
     solution=q2,
     why="No country shows a significant effect, and the UK estimate (+0.11 points, CI -0.36 to +0.59) is fully "
         "compatible with zero and with the other countries. The interaction test (p = 0.29) finds no evidence "
         "that the effect differs by country. Looking at segments after the fact gives many chances for a "
         "positive-looking number: with 3 null segments the chance that at least one has p < 0.05 is 14%, and "
         "that one of them has a positive point estimate is almost certain. A segment launch needs a "
         "pre-registered hypothesis, a significant interaction, a plausible mechanism and ideally a replication." +
         PM + "\"The UK number is a little positive by chance: it is within noise and not different from the "
         "other countries, so launching there would most likely change nothing; if there is a UK-specific "
         "reason the page should work, we can test it with a UK-only experiment.\"",
     mistakes="Comparing p-values across segments instead of testing the difference between segments. Launching "
              "on a post-hoc segment. Forgetting that small segments (CA) have wide CIs.",
     learn=["stats-heterogeneous-effects", "stats-launch-decisions"])
shown(ex)

# ---------------------------------------------------------------- Q3 review: interaction in a logistic regression (titanic)
q3 = '''cell = titanic.groupby(["pclass", "sex"]).survived.mean().unstack()
gap = (cell.female - cell.male).round(3)
odds = cell / (1 - cell)
print("female minus male survival, by class:", gap.to_dict())
print("odds ratio female vs male, by class:", (odds.female / odds.male).round(1).to_dict())

full = smf.logit("survived ~ C(sex) * C(pclass)", titanic).fit(disp=0)
main = smf.logit("survived ~ C(sex) + C(pclass)", titanic).fit(disp=0)
lr = 2 * (full.llf - main.llf)
print(f"interaction LR = {lr:.1f}, df = 2, p = {stats.chi2.sf(lr, 2):.1e}")
p_main = main.predict(pd.DataFrame({"sex": ["female", "male"] * 3, "pclass": [1, 1, 2, 2, 3, 3]}))
print("no-interaction model, female minus male gap:", np.round(p_main.values[0::2] - p_main.values[1::2], 3))
# female minus male survival, by class: {1: 0.599, 2: 0.764, 3: 0.365}
# odds ratio female vs male, by class: {1: 51.9, 2: 62.5, 3: 6.4}
# interaction LR = 28.8, df = 2, p = 5.6e-07
# no-interaction model, female minus male gap: [0.494 0.577 0.501]'''
ex.q("Who benefits from \"women first\"?", minutes=6, kind="python", review=True,
     prompt="Real data: `titanic`. Treat being female as the \"treatment\" (this is observational, so it is a "
            "difference, not a causal effect).\n\n"
            "1. Compute the female minus male survival gap in each passenger class, and the odds ratio in each "
            "class.\n"
            "2. Fit a logistic regression with and without a `sex x pclass` interaction and test the interaction.\n"
            "3. A model without the interaction also gives a different gap per class. Why? What does this tell "
            "you about the word 'heterogeneous' on different scales?" +
            PM + "one sentence on where the gap is smallest and why the scale matters when we report "
                 "segment effects.",
     hint1="Signal: an effect that may differ by segment, estimated with a non-linear model. Method: interaction "
           "terms in logistic regression, likelihood-ratio test, and reading effects on the probability scale "
           "versus the odds scale.",
     hint2="1. Cell means per class and sex, then `odds = p / (1 - p)`. 2. `survived ~ C(sex) * C(pclass)` vs "
           "`C(sex) + C(pclass)`; `LR = 2 (llf_full - llf_main)`. 3. Predict probabilities from the main-effects "
           "model and take the female minus male difference per class.",
     solution=q3,
     why="The gap is 60 points in first class, 76 in second and only 37 in third class; on the odds scale the "
         "first two classes are similar (odds ratios 52 and 62) and third class is far lower (6.4). The "
         "interaction is clearly significant (LR = 28.8, p < 0.001), so the female advantage really differs by "
         "class. Point 3 is the "
         "subtle one: a logistic model without interaction has one odds ratio for all classes, yet it still "
         "predicts different probability gaps per class (49, 58 and 50 points), because the same shift in log-odds moves a probability "
         "near 50% much more than one near 0 or 100%. 'The effect is heterogeneous' therefore depends on the "
         "scale: always say whether you mean percentage points, relative lift or odds. Product teams usually act "
         "on absolute effects (users or dollars), so report those." + PM + "\"The female advantage was "
         "smallest in third class (37 points against 60 to 76 in the upper classes); when we compare segment "
         "effects we should report them in percentage points, because a segment can look different on one scale "
         "and similar on another.\"",
     mistakes="Reading the interaction coefficient as a difference in probabilities. Claiming 'no "
              "heterogeneity' from a model that has no interaction term. Calling the titanic gap a causal effect.",
     learn=["stats-regression", "stats-heterogeneous-effects"])
shown(ex)

# ---------------------------------------------------------------- Q4 case: flat overall, one segment positive
ex.q("Flat overall, +5% in one segment", minutes=6, kind="text",
     prompt="A new onboarding flow was tested on all new users for 3 weeks. Overall day-7 retention: **+0.2% "
            "relative, CI -0.8% to +1.2%**. A dashboard with 24 segments (4 platforms x 6 regions) shows **Android "
            "users in Brazil at +5.0% (p = 0.01)**; two segments are negative with p around 0.04. The growth PM "
            "wants to ship to Android Brazil only.\n\n"
            "What do you recommend? Cover: how likely the Brazil result is to be noise, what would make you "
            "believe it, how you would test it properly, and when a targeted launch is a good idea." +
            PM + "your recommendation.",
     hint1="Signal: many segments, one striking winner, flat total. Method: multiple comparisons in "
           "heterogeneous effects, interaction tests, pre-registration and replication, then a launch decision.",
     hint2="1. 24 segments at alpha 0.05 give about 1.2 false positives on average. 2. Bonferroni threshold "
           "0.05 / 24 = 0.002. 3. Mechanism? Sample size of the segment? 4. Confirm with a new test on that "
           "segment. 5. Cost of maintaining two flows.",
     solution="""**How likely is noise?** With 24 segments and no real differences, we expect `24 x 0.05 = 1.2`
segments below p = 0.05, and the chance of at least one is `1 - 0.95^24 = 71%`. Here three segments are below 0.05,
one positive and two negative, which is roughly what noise produces. The Brazil p = 0.01 is above the Bonferroni
threshold `0.05 / 24 = 0.0021`. Its +5% is also likely inflated by selection (winner's curse): we picked the largest
of 24 numbers.

**What would make me believe it:** (1) the segment was named before the test (pre-registered), (2) an interaction
test across segments is significant, not just one segment's p-value, (3) a plausible mechanism (for example the old
flow had a slow step on low-end Android devices common in Brazil, visible in load-time data), (4) consistency in
related metrics (day-1 and day-14 retention move the same way) and in neighbouring segments, (5) a replication.

**Proper test:** run a new experiment on Android Brazil only, with the hypothesis and the metric fixed in advance,
sized for a realistic effect (shrink +5% toward the overall +0.2%, for example to +1% to +2%). Also check the
negative segments: if the flow hurts some users, that is a reason not to ship everywhere either.

**When a targeted launch is good:** when the heterogeneity is confirmed, has a mechanism, the segment is large enough
to matter, and the cost of keeping two onboarding flows (engineering, design, analytics) is lower than the gain.
Otherwise one flow for everyone is simpler.

**Say it to a PM:** "With 24 segments we expect one or two to look great by luck, and Brazil Android does not pass a
correction for that; if there is a real reason it should work there, let us run a two-week test only on Android
Brazil with that hypothesis written down, and ship there if it holds.\"""",
     why="Examiners look for the multiple-comparisons arithmetic, the difference between a segment p-value and "
         "an interaction test, a mechanism check, and a constructive next step instead of a flat no.",
     learn=["stats-heterogeneous-effects", "stats-launch-decisions"])

ex.save()
