import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam  # noqa: F401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stats_mid_common import start, q, pm

# Day 13 stats: focus A/B pitfalls (peeking, multiple testing, novelty); review A/B analysis.
ex = start(13, ["ab"], note="Q1 to Q3 use **simulated** experiments (made-up data with a known truth), because "
           "the point is to see how often a method fools you, which needs many repeated experiments. Q4 uses the "
           "real `ab` table.")

# ---------------------------------------------------------------- Q1
q(ex, title="The PM checks the dashboard every morning", minutes=7,
  prompt="Simulate 2,000 A/A tests (no true difference). Each test runs 20 days; each day 1,000 new users join "
         "each arm and convert with probability 0.10. Every day the PM runs a two-proportion z-test on all data so "
         "far.\n\n"
         "(a) What share of A/A tests is 'significant' (|z| > 1.96) on day 20 only? What share is significant on "
         "**at least one** of the 20 days (stop at the first win)?\n\n"
         "(b) What constant threshold on |z| would keep the false positive rate at 5% with 20 daily looks?\n\n"
         "(c) Say it to a PM.\n\n"
         "Follow-ups: name two valid ways to look early. Does peeking also bias the size of the effect you report?",
  stub="rng = np.random.default_rng(1)\nsims, days, n_day, p = 2000, 20, 1000, 0.10\n# your code here",
  hint1="Signal: repeated significance tests on accumulating data. Pitfall: peeking (optional stopping) inflates "
        "the false positive rate. Simulate it as an A/A test.",
  hint2="1. `rng.binomial(n_day, p, size=(sims, days))` for each arm, then `cumsum(axis=1)`. 2. Cumulative n is "
        "`n_day * (day + 1)`. 3. Pooled z per day. 4. `(abs(z) > 1.96).any(axis=1).mean()` vs `abs(z[:, -1]) > "
        "1.96`. 5. Threshold: 95th percentile of `abs(z).max(axis=1)`.",
  solution='''rng = np.random.default_rng(1)
sims, days, n_day, p = 2000, 20, 1000, 0.10
xa = rng.binomial(n_day, p, size=(sims, days)).cumsum(axis=1)
xb = rng.binomial(n_day, p, size=(sims, days)).cumsum(axis=1)
n = n_day * np.arange(1, days + 1)                    # users per arm so far
pool = (xa + xb) / (2 * n)
z = (xb / n - xa / n) / np.sqrt(pool * (1 - pool) * 2 / n)
print("false positives, look once on day 20:", (abs(z[:, -1]) > 1.96).mean())          # 0.0445
print("false positives, stop at first p < 0.05:", (abs(z) > 1.96).any(axis=1).mean())  # 0.2325
print("threshold for 5% with 20 looks:", np.percentile(abs(z).max(axis=1), 95).round(2))  # 2.66''',
  why="Each look is another chance for noise to cross 1.96. With 20 looks about 23% of A/A tests are declared "
      "winners, almost 5 times the promised 5%. Keeping 5% overall needs a stricter bar at each look (about 2.66 "
      "here, close to the Pocock boundary for 20 looks), or a method built for peeking."
      + pm("If we stop the test the first day the dashboard turns green, about 1 in 4 'wins' will be pure noise, so "
           "we either wait for the planned end date or use a sequential method that is designed for daily checks.",
           [("Valid early looks?", "Group sequential designs with alpha spending (O'Brien-Fleming: very strict early, "
             "close to 1.96 at the end), always-valid p-values / mSPRT, or Bayesian monitoring with a pre-set rule. "
             "Early stopping for clear *harm* on guardrails is usually allowed and encouraged."),
            ("Effect size bias?", "Yes. Tests stopped at an early peak stop exactly when noise pushed the estimate "
             "up, so reported effects of early stopped winners are too large (a winner's curse).")]),
  complexity="O(sims * days) vectorised numpy, under a second.",
  mistakes="Simulating a single test (you need many to estimate a rate). Using 20 independent tests instead of "
           "cumulative data (the looks are correlated, which is why the rate is 23% and not `1 - 0.95^20` = 64%).",
  learn=["stats-ab-pitfalls", "stats-bayesian-sequential"])

# ---------------------------------------------------------------- Q2
q(ex, title="Twenty metrics, one winner", minutes=7,
  prompt="(a) Simulate 2,000 A/A tests that each compare 20 independent metrics (500 users per arm, each metric "
         "standard normal). For each test, use Welch t-tests. What share of tests has at least one metric with "
         "p < 0.05? Compare with `1 - 0.95^20`.\n\n"
         "(b) Apply Bonferroni (p < 0.05/20) and Benjamini-Hochberg (FDR 0.05, use "
         "`statsmodels.stats.multitest.multipletests`) to each test. What share still has a false winner?\n\n"
         "(c) A real readout has these 8 p-values: `[0.001, 0.008, 0.012, 0.03, 0.04, 0.21, 0.45, 0.77]`. "
         "Which are significant with Bonferroni, Holm and BH at 0.05?\n\n"
         "(d) Say it to a PM.\n\n"
         "Follow-up: the PM slices the result by 'heavy vs light users, defined by sessions during the test'. "
         "What is wrong besides multiple testing?",
  stub="from statsmodels.stats.multitest import multipletests\nrng = np.random.default_rng(2)\n# your code here",
  hint1="Signal: many metrics or segments tested at once. Pitfall: multiple comparisons; the family-wise error "
        "rate grows with the number of tests. Fixes: Bonferroni / Holm (FWER) or Benjamini-Hochberg (FDR).",
  hint2="1. Arrays shaped (sims, 20, 500) for each arm. 2. `stats.ttest_ind(a, b, axis=2, equal_var=False)`. "
        "3. Any p < 0.05 per row. 4. `multipletests(p_row, method='bonferroni' | 'holm' | 'fdr_bh')[0]`.",
  solution='''from statsmodels.stats.multitest import multipletests

rng = np.random.default_rng(2)
sims, k, n = 2000, 20, 500
a = rng.standard_normal((sims, k, n))
b = rng.standard_normal((sims, k, n))
pv = stats.ttest_ind(a, b, axis=2, equal_var=False).pvalue        # shape (2000, 20)
print("any p < 0.05:", (pv < 0.05).any(axis=1).mean(), " theory:", round(1 - 0.95 ** 20, 3))
print("Bonferroni false winner:", (pv < 0.05 / k).any(axis=1).mean())
print("BH false winner:", np.mean([multipletests(r, 0.05, "fdr_bh")[0].any() for r in pv]))
# any p < 0.05: 0.65  theory: 0.642
# Bonferroni false winner: 0.0465
# BH false winner: 0.047

p8 = [0.001, 0.008, 0.012, 0.03, 0.04, 0.21, 0.45, 0.77]
for m in ["bonferroni", "holm", "fdr_bh"]:
    print(m, multipletests(p8, 0.05, m)[0].astype(int))
# bonferroni [1 0 0 0 0 0 0 0]
# holm [1 0 0 0 0 0 0 0]
# fdr_bh [1 1 1 0 0 0 0 0]''',
  why="With 20 null metrics, about 65% of tests show at least one 'significant' metric (theory 64%). Bonferroni "
      "and Holm control the chance of any false winner (FWER) at 5%. When *all* nulls are true, BH also gives about "
      "5% (FDR equals FWER in that case); its advantage is power when some effects are real. In (c) Bonferroni uses "
      "0.05/8 = 0.00625, so only 0.001 passes; Holm compares the 2nd smallest with 0.05/7 = 0.0071 and stops at "
      "0.008. BH compares the i-th smallest with `0.05 * i / 8`: 0.012 <= 0.01875 passes, 0.03 > 0.025 and "
      "0.04 > 0.03125 fail, so three discoveries."
      + pm("We checked 8 metrics, so some 'wins' are expected by luck; after correcting for that, one metric is a "
           "solid win and two more are promising (expected to be mostly real), and the rest are noise.",
           [("Segments by in-test sessions?", "Sessions during the test can be changed by the treatment, so 'heavy "
             "users' in treatment are not the same people as 'heavy users' in control. This is conditioning on a "
             "post-treatment variable and can create effects out of nothing. Segment only on attributes fixed "
             "before assignment (country, platform, pre-period activity)."),
            ("Primary metric?", "Pick one primary metric (and maybe a few guardrails) before the test; correct the "
             "rest or treat them as exploratory.")]),
  complexity="O(sims * k * n) for the simulation (20 million numbers per arm, a few seconds).",
  mistakes="Using BH to claim 'no false positives' (it controls the expected *share* of false discoveries). "
           "Forgetting that slicing by segments is also multiple testing.",
  learn=["stats-ab-pitfalls", "stats-hypothesis-tests"])

# ---------------------------------------------------------------- Q3
q(ex, title="A great first week", minutes=7,
  prompt="Simulate a 28-day test on a fixed panel of returning users: 20,000 per arm, each user visits every day, "
         "control clicks with probability 0.10 per day. The treatment lift on day `t` (0 to 27) is "
         "`0.01 + 0.03 * exp(-t / 3)` (a novelty bump that fades to a true long-run lift of 1 pp).\n\n"
         "(a) Estimate the lift (pp) from week 1 only and from week 4 only.\n\n"
         "(b) Regress the daily lift on day number. How would you detect novelty in real data without knowing "
         "the truth?\n\n"
         "(c) Say it to a PM.\n\n"
         "Follow-ups: what is the opposite pattern called and when does it happen? How do new users help?",
  stub="rng = np.random.default_rng(3)\nn, days = 20000, 28\nt = np.arange(days)\n# your code here",
  hint1="Signal: an effect that changes with time since exposure. Pitfall: novelty (or primacy) effect. "
        "Look at the lift by day or by days since first exposure.",
  hint2="1. Daily clicks per arm: `rng.binomial(n, p_day)`. 2. Daily lift = treatment rate minus control rate. "
        "3. Average days 0 to 6 and days 21 to 27. 4. `np.polyfit(t, lift, 1)` for a slope.",
  solution='''rng = np.random.default_rng(3)
n, days = 20000, 28
t = np.arange(days)
true_lift = 0.01 + 0.03 * np.exp(-t / 3)
ctl = rng.binomial(n, 0.10, days) / n
trt = rng.binomial(n, 0.10 + true_lift) / n
lift = trt - ctl
print(f"week 1 lift: {lift[:7].mean() * 100:.2f} pp")     # 2.29 pp
print(f"week 4 lift: {lift[21:].mean() * 100:.2f} pp")    # 0.87 pp
slope = np.polyfit(t, lift, 1)[0]
print(f"slope: {slope * 100:.3f} pp per day")             # -0.065 pp per day''',
  why="The first week mixes the real 1 pp lift with a curiosity bump, so it more than doubles the long-run effect "
      "(2.29 pp vs 0.87 pp, where the true long-run lift is 1 pp and the rest is noise). A clearly negative trend of the daily lift is the warning sign. In real data, plot the "
      "lift by calendar day and, better, by *days since first exposure* (which separates novelty from calendar "
      "events), and compare users who joined late with users who joined early."
      + pm("Users clicked a lot more in the first week because the design was new; by week four the gain settled "
           "at about 1 point, and that is the number we should plan with.",
           [("Opposite pattern?", "Primacy effect (change aversion): existing users first react badly to a change "
             "they must relearn, and the lift grows later. Common with navigation or layout changes."),
            ("New users?", "New users have no old habit to compare against, so their effect has no novelty or "
             "primacy part. If new and existing users show the same lift late in the test, novelty is gone. A long "
             "term holdout answers it for good.")]),
  complexity="O(days).",
  mistakes="Running a test for 3 days because the result is already significant. Using calendar day only (a holiday "
           "can look like novelty). Extending a test forever: users clear cookies and change devices, which also "
           "dilutes the effect.",
  learn=["stats-ab-pitfalls"])

# ---------------------------------------------------------------- Q4 review
q(ex, title="Not significant: so is it the same?", minutes=6, review=True,
  prompt="Use the cleaned `ab` table (drop group/page mismatches, keep the first row per user; you did this on day "
         "12). The difference was not significant.\n\n"
         "(a) Compute the 95% CI of the difference in conversion (treatment minus control).\n\n"
         "(b) The business says any change smaller than 0.5 pp in absolute value does not matter. Run an "
         "equivalence test (TOST): two one-sided z-tests against -0.5 pp and +0.5 pp. Report the larger of the two "
         "p-values.\n\n"
         "(c) Say it to a PM.\n\n"
         "Follow-up: why is the 90% CI (not 95%) the one that matches a TOST at alpha 0.05?",
  stub="# your code here",
  hint1="Signal: 'no significant difference' and the PM wants 'the same'. Method: confidence interval and an "
        "equivalence test (TOST) with a margin chosen before the test.",
  hint2="1. Clean as on day 12. 2. `se = sqrt(p_t(1-p_t)/n_t + p_c(1-p_c)/n_c)`. 3. Lower test: "
        "`z1 = (diff + m) / se`, `p1 = norm.sf(z1)`. Upper: `z2 = (diff - m) / se`, `p2 = norm.cdf(z2)`. "
        "4. TOST p = max(p1, p2).",
  solution='''ok = (ab.group == "treatment") == (ab.landing_page == "new_page")
clean = ab[ok].sort_values("timestamp").drop_duplicates("user_id")
g = clean.groupby("group").converted.agg(["mean", "count"])
(p_c, n_c), (p_t, n_t) = g.loc["control"], g.loc["treatment"]
diff = p_t - p_c
se = np.sqrt(p_t * (1 - p_t) / n_t + p_c * (1 - p_c) / n_c)
print(f"diff {diff * 100:.3f} pp, 95% CI [{(diff - 1.96 * se) * 100:.3f}, {(diff + 1.96 * se) * 100:.3f}] pp")
# diff -0.158 pp, 95% CI [-0.394, 0.078] pp
m = 0.005
p1 = stats.norm.sf((diff + m) / se)       # H0: diff <= -m
p2 = stats.norm.cdf((diff - m) / se)      # H0: diff >= +m
print(f"TOST p = {max(p1, p2):.2g}")      # TOST p = 0.0022''',
  why="The CI from -0.39 to +0.08 pp lies inside the plus or minus 0.5 pp margin, and the TOST p-value is 0.0022, so "
      "we can claim the pages are practically equivalent. That is a different, stronger statement than 'not "
      "significant', and it is only possible because the test was large (SE 0.12 pp)."
      + pm("The new page is not better, and we can say more: any difference is smaller than half a point either way, "
           "so if the new page is cheaper to maintain it is safe to switch.",
           [("Why 90%?", "TOST runs two one-sided tests, each at 5%. Both pass exactly when the 90% two-sided CI "
             "(which leaves 5% in each tail) sits inside the margin.")]),
  complexity="O(n log n) for the cleaning sort.",
  mistakes="Saying 'no effect' from p > 0.05. Choosing the equivalence margin after seeing the data. Using a margin "
           "so wide that anything is 'equivalent'.",
  learn=["stats-ab-analysis", "stats-confidence-intervals"])

ex.save()
