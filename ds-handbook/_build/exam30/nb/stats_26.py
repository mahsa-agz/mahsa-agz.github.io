import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam  # noqa: F401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _stats_hard_common import start, load, shown, PM, AB_CLEAN

# Day 26 stats. Focus: bayesian-sequential. Review: ab-pitfalls, probability-puzzles.

SETUP = load("ab", "ab_data.csv") + "\n" + AB_CLEAN + '''
rng = np.random.default_rng(26)
print(ab.shape)'''

DATA = """| Table | One row = | Columns | Real or simulated |
|---|---|---|---|
| `ab` | one user in an e-commerce landing-page test (Udacity data, cleaned: one row per user) | `user_id`, `timestamp`, `group` (control/treatment), `landing_page`, `converted` (0/1) | real |

Q2 and Q4 simulate experiments with numpy (`rng`, seed 26). Simulated numbers can differ slightly on another numpy
version; the conclusions do not."""

ex = start(26, extra=SETUP, data_doc=DATA)

# ---------------------------------------------------------------- Q1 Bayesian A/B on real data
q1 = '''s = ab.groupby("group").converted.agg(["sum", "count"])
post = {g: rng.beta(1 + s.loc[g, "sum"], 1 + s.loc[g, "count"] - s.loc[g, "sum"], 400_000) for g in s.index}
pc, pt = post["control"], post["treatment"]
rel = pt / pc - 1
print(f"P(treatment better) = {(pt > pc).mean():.3f}")
print(f"relative lift: mean {rel.mean():+.2%}, 95% credible interval [{np.quantile(rel, .025):+.2%}, {np.quantile(rel, .975):+.2%}]")
print(f"expected loss if we ship treatment: {np.maximum(pc - pt, 0).mean():.5f}")
print(f"expected loss if we keep control:   {np.maximum(pt - pc, 0).mean():.5f}")
z = (pt.mean() - pc.mean()) / np.sqrt(pc.var() + pt.var())
print(f"frequentist check: one-sided p-value for H1 'treatment worse' = {stats.norm.cdf(z):.3f}")
# P(treatment better) = 0.095
# relative lift: mean -1.30%, 95% credible interval [-3.24%, +0.66%]
# expected loss if we ship treatment: 0.00163
# expected loss if we keep control:   0.00005
# frequentist check: one-sided p-value for H1 'treatment worse' = 0.095'''
ex.q("A Bayesian read of the landing page test", minutes=7, kind="python",
     prompt="Real data: `ab`. Leadership prefers Bayesian answers: \"what is the chance the new page is better, "
            "and what do we risk if we pick it?\"\n\n"
            "1. Use Beta(1, 1) priors and the binomial likelihood to get the posterior conversion rate of each "
            "group. Sample from the posteriors.\n"
            "2. Report P(treatment better), a 95% credible interval for the relative lift, and the **expected "
            "loss** (as a conversion-rate difference, e.g. 0.001 = 0.1 points) of shipping treatment and of keeping control.\n"
            "3. A common rule ships when the expected loss of the chosen option is below 0.0001 (0.01 points). "
            "Which option does the rule pick?\n"
            "4. How does P(treatment better) relate to the frequentist one-sided p-value here, and why?" +
            PM + "the result in the language leadership asked for.",
     hint1="Signal: conversion data and questions phrased as 'chance that B is better' and 'risk'. Method: "
           "Beta-binomial Bayesian A/B test with posterior sampling and expected loss.",
     hint2="1. Posterior: `Beta(1 + conversions, 1 + non-conversions)`. 2. Draw many samples per group; "
           "`P = mean(pt > pc)`. 3. `loss(ship treatment) = mean(max(pc - pt, 0))`. 4. With flat priors and a "
           "big sample, the posterior is close to normal around the observed rates.",
     solution=q1,
     why="With about 145k users per group the flat prior barely matters, and P(treatment better) = 0.095 is "
         "almost exactly the frequentist one-sided p-value for 'treatment worse' (0.095): with a flat prior and "
         "a normal likelihood the two calculations coincide. The new statement is about decisions: shipping "
         "treatment risks losing 0.00163 conversion points on average, keeping control risks only 0.00005. "
         "Control is below the 0.0001 threshold, so the rule keeps control. Expected loss is more useful than "
         "P(better) because it weights how much worse you could be, not only how often." + PM +
         "\"There is about a 10% chance the new page is better; if we switched, the expected cost is about 0.16 "
         "conversion points, while staying with the old page costs almost nothing, so we keep the old page.\"",
     mistakes="Treating P(B > A) = 0.9 as a launch rule without thinking about the size of the possible loss. "
              "Claiming that Bayesian tests are immune to peeking (see Q2 and Q3). Using an informative prior "
              "without saying where it comes from.",
     learn=["stats-bayesian-sequential", "stats-bayes"])
shown(ex)

# ---------------------------------------------------------------- Q2 peeking and boundaries
q2 = '''K, reps = 20, 40_000
z_inc = rng.normal(size=(reps, K))                         # A/A test: no effect; one look per day for 20 days
Z = np.cumsum(z_inc, axis=1) / np.sqrt(np.arange(1, K + 1))   # z-statistic after each day's data
print(f"one look at the end: {np.mean(np.abs(Z[:, -1]) > 1.96):.3f}")
print(f"stop at any daily look with |z| > 1.96: {np.mean((np.abs(Z) > 1.96).any(axis=1)):.3f}")

def fpr(bounds):
    return np.mean((np.abs(Z) > bounds).any(axis=1))

def calibrate(shape):                                       # find c so that FPR = 0.05 (bisection)
    lo, hi = 1.5, 5.0
    for _ in range(40):
        c = (lo + hi) / 2
        lo, hi = (c, hi) if fpr(c * shape) > 0.05 else (lo, c)
    return c

k = np.arange(1, K + 1)
c_poc = calibrate(np.ones(K))
c_obf = calibrate(np.sqrt(K / k))
print(f"Pocock constant boundary: {c_poc:.2f}")
print(f"O'Brien-Fleming: day 1 {c_obf * np.sqrt(K):.2f}, day 10 {c_obf * np.sqrt(2):.2f}, day 20 {c_obf:.2f}")
# one look at the end: 0.050
# stop at any daily look with |z| > 1.96: 0.245
# Pocock constant boundary: 2.68
# O'Brien-Fleming: day 1 9.52, day 10 3.01, day 20 2.13
# (third decimal of the simulated rates moves a little with the random draws)'''
ex.q("Looking every day", minutes=8, kind="python",
     prompt="A team checks its experiment dashboard every day for 20 days and stops as soon as the two-sided "
            "p-value is below 0.05.\n\n"
            "1. Simulate many **A/A** tests (no true effect) with one look per day. What is the false positive "
            "rate with this habit? (Hint for speed: the z-statistic after day k is the sum of k independent "
            "standard normals divided by `sqrt(k)`.)\n"
            "2. Find by simulation a **constant** boundary c (Pocock style) so that stopping when `|z| > c` at any "
            "look gives a 5% false positive rate.\n"
            "3. Do the same for an O'Brien-Fleming shape `c * sqrt(20 / k)`. Print the boundary on day 1, 10 "
            "and 20.\n"
            "4. Which design would you recommend to a team that wants to stop early only for big wins?" +
            PM + "why the team cannot stop the first day the dashboard turns green.",
     hint1="Signal: repeated significance tests on accumulating data. Method: the peeking problem and group "
           "sequential boundaries (Pocock, O'Brien-Fleming), calibrated by simulation.",
     hint2="1. `Z = cumsum(normals, axis=1) / sqrt(1..20)`. 2. FPR = share of runs where any `|Z_k|` crosses. "
           "3. Bisection on c for each boundary shape. 4. Compare the final-day boundary with 1.96.",
     solution=q2,
     why="Each extra look is another chance for noise to cross 1.96, and the z-path wanders: with 20 daily looks "
         "about 25% of A/A tests 'win', five times the promised 5%. A constant Pocock boundary of about 2.68 "
         "restores 5%, but then even the final analysis needs |z| > 2.68, so power at the end is lower. "
         "O'Brien-Fleming spends almost nothing early (|z| > 9.52 on day 1, practically impossible) and keeps "
         "the final boundary close to the fixed test (2.13 versus 1.96), so it stops early only for huge effects "
         "and loses very little power. That matches a team that wants early stops only for big wins. "
         "Alternatives: alpha-spending functions (looks at any time), or always-valid p-values (mSPRT) for "
         "continuous monitoring." + PM + "\"If we check daily and stop at the first green, one in four tests "
         "of a useless change looks like a win; with a stricter early bar we can still stop early for big wins "
         "while keeping false wins at 5%.\"",
     mistakes="Applying 1.96 at every look. Thinking the problem disappears with Bayesian probabilities "
              "(stopping when P(better) > 95% also inflates false wins). Using Pocock when the team mostly "
              "cares about the final analysis.",
     learn=["stats-bayesian-sequential", "stats-ab-pitfalls"])
shown(ex)

# ---------------------------------------------------------------- Q3 case: stop early?
ex.q("The PM wants to stop on day 3", minutes=5, kind="text",
     prompt="A test of a new checkout flow was planned for 14 days (two full weeks, power computed for a 2% "
            "relative lift in purchases). On day 3 the Bayesian dashboard shows **\"97% chance to beat "
            "control, expected lift +6%\"**. The PM wants to stop and ship today because \"Bayesian results are "
            "valid at any time\".\n\n"
            "Give your answer: what is right and wrong in the PM's claim, what risks you see in stopping on day 3, "
            "and what you propose instead." +
            PM + "your answer in three sentences.",
     hint1="Signal: early stopping on a large early effect. Method: optional stopping, novelty and weekly "
           "cycles, winner's curse, pre-registered sequential designs.",
     hint2="1. The posterior is valid given the prior, but a 'stop when > 95%' rule still has a frequentist false "
           "win rate. 2. Day 3 has no weekend and early adopters only. 3. A +6% estimate with a 2% design is a "
           "warning sign of noise or novelty. 4. Propose a pre-registered sequential rule or a loss threshold.",
     solution="""**What is right:** the posterior on day 3 is a correct summary of the data under the chosen prior.
Bayesian inference does not need a fixed sample size to be *coherent*.

**What is wrong:** a *decision rule* "stop when P(better) > 95%" checked every day still produces many false wins
when the true effect is zero (just like p-value peeking), and with a flat prior the posterior probability is almost
the same number as `1 - p`. Bayes does not protect the error rate; it only answers a different question.

**Risks of stopping on day 3:** (1) The sample covers no weekend: buyers on weekends behave differently, and the
plan asked for two full weekly cycles. (2) Early users are heavy and curious users, so novelty inflates early lifts.
(3) Winner's curse: the test was powered for 2%, so a +6% estimate on 3 days is far more likely to be an
overestimate than a real 6% (the estimate is selected because it is big). (4) Guardrails (refunds, payment errors,
support tickets) have almost no data yet.

**Proposal:** keep the 14-day plan unless a **pre-registered** rule says otherwise. For future tests, set a group
sequential design (for example O'Brien-Fleming with looks at day 7 and 14) or a Bayesian rule with a sensible prior
from past experiments and an expected-loss threshold, plus a minimum run time of one full week. If the business
needs speed, ship to 50% while the test continues, which costs little if the effect is real.

**Say it to a PM:** "The 97% is real but it is a day-3 number without a weekend, from a test designed for a 2% lift,
so a +6% reading is most likely inflated by novelty and noise. If we stop every test at the first good reading, many
of our wins will be fake. Let us wait until day 7 for a pre-planned check, and we can ship early then if it holds.\"""",
     why="The examiner checks that you separate inference (the posterior) from the decision rule (its error "
         "rate), and that you bring product reasons (weekly cycle, novelty, guardrails) plus a constructive plan.",
     learn=["stats-bayesian-sequential", "stats-launch-decisions"])

# ---------------------------------------------------------------- Q4 review: winner's curse
q4 = '''true_lift, se, reps = 0.002, 0.0019, 200_000      # base rate 10%, 50k users per group -> SE about 0.0019
est = rng.normal(true_lift, se, reps)
win = est / se > 1.96
print(f"power {win.mean():.3f}")
print(f"mean estimate among wins {est[win].mean():.4f} = {est[win].mean() / true_lift:.1f} x the true lift")
print(f"share of wins that overstate the true lift: {(est[win] > true_lift).mean():.3f}")
# power 0.181
# mean estimate among wins 0.0048 = 2.4 x the true lift
# share of wins that overstate the true lift: 1.000'''
ex.q("Why do launched wins shrink?", minutes=5, kind="python", review=True,
     prompt="A test has a true lift of +0.2 conversion points (on a 10% base) and a standard error of 0.0019 for "
            "the difference (about 50k users per group). The team only ships significant positive results "
            "(z > 1.96).\n\n"
            "1. Simulate many such tests. What is the power?\n"
            "2. Among the tests that win, what is the average estimated lift, compared with the truth?\n"
            "3. What share of winning estimates overstate the true lift? Explain why." +
            PM + "why the launch forecast should be lower than the test result.",
     hint1="Signal: we only look at estimates that passed a significance filter. Method: the winner's curse "
           "(selection bias of significant estimates), most severe in underpowered tests.",
     hint2="1. Draw estimates from `N(true, se)`. 2. Keep those with `est / se > 1.96`. 3. Compare their mean "
           "with the truth. 4. What is the smallest estimate that can win?",
     solution=q4,
     why="The power is only about 18%, so a test wins only when noise pushes the estimate up: the smallest "
         "winning estimate is `1.96 x 0.0019 = 0.0037`, already almost twice the truth, so 100% of the wins "
         "overstate it and their average is about 2.4 times the true lift. Remedies: run tests with enough power, "
         "shrink estimates toward a prior from past tests (empirical Bayes), and measure launches with a holdout." +
         PM + "\"Because we ship only winners, the measured lift is biased upward, here by about 2.4 times for a "
         "small, underpowered test, so I would forecast well below the test number and confirm it with a "
         "holdout.\"",
     mistakes="Taking the significant estimate as the expected impact. Thinking a larger p-value threshold fixes "
              "it. Forgetting that the bias is small for well-powered tests.",
     learn=["stats-ab-pitfalls", "stats-power-mde"])
shown(ex)

ex.save()
