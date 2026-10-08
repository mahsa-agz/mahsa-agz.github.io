import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam  # noqa: F401  (Exam is created inside stats_common.start)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stats_common import start, Q

# Day 10 statistics: focus power, sample size and MDE (Q1 to Q3; Q3 also revisits choosing a test).
# Review: Bayes (Q4: how often is a significant result real?).
ex = start(10, ["ab", "cookie"])

Q(ex, "How many users do we need?", minutes=7,
  prompt="The landing-page team wants a new test. Use the control conversion rate of the cleaned `ab` table as "
         "the baseline.\n"
         "1. How many users per arm are needed to detect an **absolute** lift of 1 percentage point, with "
         "`alpha = 0.05` (two-sided) and 80% power? Use "
         "`n = (z_(1 - alpha/2) + z_(power))^2 * (p1 (1 - p1) + p2 (1 - p2)) / (p2 - p1)^2`.\n"
         "2. Check with `statsmodels` (`NormalIndPower` with Cohen's h from `proportion_effectsize`).\n"
         "3. Check the power by simulating 2,000 experiments of that size (`rng = np.random.default_rng(0)`, "
         "two-proportion z-test each).\n"
         "4. The site gets 5,000 new users a day, split 50/50. How many days does the test need? What if the "
         "team wants to detect 0.5 points instead?",
  stub="# ab is loaded and cleaned in the setup\n",
  hint1="Signal: 'how many users / how long' before a test. Topic: power analysis for two proportions; n grows "
        "with `1 / effect^2`.",
  hint2="1. `p1 = ab[ab.group == 'control'].converted.mean()`, `p2 = p1 + 0.01`. 2. `z_a = st.norm.ppf(0.975)`, "
        "`z_b = st.norm.ppf(0.8)`. 3. statsmodels: `NormalIndPower().solve_power(effect_size=h, alpha=0.05, "
        "power=0.8)` with `h = proportion_effectsize(p2, p1)`. 4. Simulate conversions with `rng.binomial(n, p, "
        "2000)` for each arm, compute z with the pooled SE, count `|z| > 1.96`. 5. Days = `2 n / 5000`, round up.",
  solution='''from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

def n_per_arm(p1, p2, alpha=0.05, power=0.8):
    z = st.norm.ppf(1 - alpha / 2) + st.norm.ppf(power)
    return int(np.ceil(z ** 2 * (p1 * (1 - p1) + p2 * (1 - p2)) / (p2 - p1) ** 2))

p1 = ab.loc[ab["group"] == "control", "converted"].mean()
p2 = p1 + 0.01
n = n_per_arm(p1, p2)
n_sm = NormalIndPower().solve_power(effect_size=proportion_effectsize(p2, p1), alpha=0.05, power=0.8)
print(f"baseline {p1:.4f}   n per arm (formula) {n:,}   (statsmodels {n_sm:,.0f})")

rng = np.random.default_rng(0)
k1, k2 = rng.binomial(n, p1, 2000), rng.binomial(n, p2, 2000)
pp = (k1 + k2) / (2 * n)
z = (k2 / n - k1 / n) / np.sqrt(pp * (1 - pp) * 2 / n)
print(f"simulated power {(np.abs(z) > 1.96).mean():.3f}")
print(f"days at 5,000 users/day: {np.ceil(2 * n / 5000):.0f}")
n_half = n_per_arm(p1, p1 + 0.005)
print(f"for +0.5 pp: n per arm {n_half:,}   days {np.ceil(2 * n_half / 5000):.0f}")''',
  out="""baseline 0.1204   n per arm (formula) 17,211   (statsmodels 17,209)
simulated power 0.784
days at 5,000 users/day: 7
for +0.5 pp: n per arm 67,676   days 28""",
  why="Power is the chance to detect a real effect of the given size. The formula adds the two z values "
      "(1.96 for alpha, 0.84 for 80% power) because the test statistic must clear the 1.96 bar even when it "
      "lands on the low side of the true effect. statsmodels uses Cohen's h (an arcsine scale), so its n is "
      "slightly different but close. The simulation confirms about 80% power. Halving the effect needs about 4 "
      "times the users (n grows like `1 / effect^2`), which turns a one-week test into a month. In practice, "
      "round the duration up to whole weeks to cover weekday cycles.",
  pm="To reliably detect a 1-point lift on our 12% conversion rate we need about 17,000 users per group, which "
     "is 7 days of traffic. Detecting half that lift would take about 4 weeks, so we should agree on the "
     "smallest lift that is worth shipping before we start.",
  mistakes="Using the relative lift (8%) as if it were absolute (8 points). Forgetting that n is *per arm*. "
           "Stopping as soon as the result looks significant (peeking) instead of running the planned "
           "duration.",
  learn=["stats-power-mde", "stats-ab-design"])

Q(ex, "What could the Cookie Cats test detect?", minutes=6,
  prompt="Turn the question around: given the traffic, what is the smallest effect a test can detect?\n"
         "1. For 7-day retention in `cookie`, use the `gate_30` rate as the baseline and the actual group sizes. "
         "Compute the minimum detectable effect (MDE) at `alpha = 0.05` two-sided and 80% power: "
         "`MDE = (z_(1 - alpha/2) + z_(power)) * sqrt(p (1 - p) (1/n1 + 1/n2))`.\n"
         "2. Compare it with the observed difference (about -0.82 points). Was the test big enough?\n"
         "3. What would the MDE be with only 5,000 players per arm?",
  stub="# cookie is loaded in the setup\n",
  hint1="Signal: traffic is fixed, the question is the size of effect you can see. Topic: the minimum "
        "detectable effect, the inverse of the sample-size formula.",
  hint2="1. `p = cookie[cookie.version == 'gate_30'].retention_7.mean()`, `n1, n2` = group sizes. 2. `(1.96 + "
        "0.8416) * sqrt(p (1 - p) (1/n1 + 1/n2))`. 3. Same with `n1 = n2 = 5000`. 4. Relative MDE = MDE / p.",
  solution='''p = cookie.loc[cookie["version"] == "gate_30", "retention_7"].mean()
n1, n2 = (cookie["version"] == "gate_30").sum(), (cookie["version"] == "gate_40").sum()
z = st.norm.ppf(0.975) + st.norm.ppf(0.8)
mde = z * np.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
print(f"baseline {p:.4f}   n1 {n1}   n2 {n2}")
print(f"MDE {100 * mde:.2f} pp  ({100 * mde / p:.1f}% relative)   observed |difference| 0.82 pp")
mde5k = z * np.sqrt(p * (1 - p) * 2 / 5000)
print(f"MDE with 5,000 per arm: {100 * mde5k:.2f} pp  ({100 * mde5k / p:.1f}% relative)")''',
  out="""baseline 0.1902   n1 44700   n2 45489
MDE 0.73 pp  (3.8% relative)   observed |difference| 0.82 pp
MDE with 5,000 per arm: 2.20 pp  (11.6% relative)""",
  why="The MDE is the effect size that the test would detect with 80% probability. Here it is about 0.73 "
      "points, a bit smaller than the observed 0.82, so the test was adequately sized for an effect of this "
      "size. With 5,000 players per arm, the MDE would be about 2.2 points (about 12% relative): a real "
      "0.8-point drop would usually be missed, and the team could wrongly conclude that moving the gate is "
      "harmless. Note: the MDE is a planning number; do not compute 'observed power' after the test from the "
      "observed effect (it is just a re-expression of the p-value).",
  pm="With 45,000 players per version, this test could reliably spot a change in 7-day retention of about "
     "0.7 points or more, and the real drop (0.8 points) was just above that. With only 5,000 players per "
     "version we would probably have missed it.",
  mistakes="Calling a non-significant result from an underpowered test 'proof of no effect'. Computing post-hoc "
           "power from the observed effect. Forgetting to say whether the MDE is absolute or relative.",
  learn=["stats-power-mde", "stats-confidence-intervals"])

Q(ex, "Which test has more power on rounds played?", minutes=8,
  prompt="A simulation study, to choose the analysis *before* a test on the heavy-tailed metric "
         "`sum_gamerounds`. Use the `gate_30` players (without the 49,854 account) as the population.\n\n"
         "For each of 400 simulated experiments (`rng = np.random.default_rng(0)`): draw 2,000 players for "
         "control and 2,000 for treatment from the population, and multiply the treatment values by 1.10 (a true "
         "10% lift for every player). Then run:\n"
         "- (a) a Welch t-test on the raw values,\n"
         "- (b) a Welch t-test after capping both arms at the population's 99th percentile,\n"
         "- (c) a Mann-Whitney U test.\n\n"
         "Print the power (share of p < 0.05) of each. Repeat **without** the lift (factor 1.00) and print the "
         "false positive rate of each. Which analysis would you plan?",
  stub="# cookie is loaded in the setup\npop = cookie.loc[(cookie.version == 'gate_30') & (cookie.sum_gamerounds < 49854), 'sum_gamerounds'].to_numpy()\n",
  hint1="Signal: heavy tails make the variance huge, and power depends on effect / sd. Topic: power by "
        "simulation, and choosing a test (raw mean, capped mean, rank test).",
  hint2="1. `cap = np.percentile(pop, 99)`. 2. In a loop: `a = rng.choice(pop, 2000)`, `b = rng.choice(pop, "
        "2000) * lift`. 3. `st.ttest_ind(a, b, equal_var=False).pvalue`, the same on `np.minimum(x, cap)`, and "
        "`st.mannwhitneyu(a, b).pvalue`. 4. Average `p < 0.05` over the 400 runs.",
  solution='''pop = cookie.loc[(cookie["version"] == "gate_30") & (cookie["sum_gamerounds"] < 49854), "sum_gamerounds"].to_numpy()
cap = np.percentile(pop, 99)
rng = np.random.default_rng(0)

def power(lift, sims=400, n=2000):
    hits = np.zeros(3)
    for _ in range(sims):
        a, b = rng.choice(pop, n), rng.choice(pop, n) * lift
        hits += [st.ttest_ind(a, b, equal_var=False).pvalue < 0.05,
                 st.ttest_ind(np.minimum(a, cap), np.minimum(b, cap), equal_var=False).pvalue < 0.05,
                 st.mannwhitneyu(a, b, alternative="two-sided").pvalue < 0.05]
    return hits / sims

print(f"cap at p99 = {cap:.0f} rounds")
for lift in (1.10, 1.00):
    raw, capped, mw = power(lift)
    label = "power (10% lift)" if lift > 1 else "false positives (no lift)"
    print(f"{label:<26} raw t {raw:.3f}   capped t {capped:.3f}   Mann-Whitney {mw:.3f}")''',
  out="""cap at p99 = 493 rounds
power (10% lift)           raw t 0.325   capped t 0.335   Mann-Whitney 0.482
false positives (no lift)  raw t 0.037   capped t 0.043   Mann-Whitney 0.045""",
  why="Power depends on effect size divided by the sd. Raw rounds have a huge sd (about 2 times the mean), so "
      "the raw t-test finds a real 10% lift only about 1 time in 3 at this sample size. Capping at p99 barely "
      "helps *here* (0.335 versus 0.325): the lift is proportional, so the heavy players carry a large part of "
      "the extra rounds, and capping removes their signal together with their noise. Capping helps most when "
      "the extreme values are noise unrelated to the treatment (bots, logging bugs). Mann-Whitney works on "
      "ranks, so every player counts equally, and it is clearly the most powerful here (0.48); but it tests "
      "'do treatment players tend to rank higher', not 'is the mean higher'. With no lift, all three keep the "
      "false positive rate near 5% (simulation noise is about +- 2 points with 400 runs), so none of them "
      "cheats. Most important: no method reaches 80% power, so 2,000 players per arm is too small for a 10% "
      "lift on this metric. Plan the metric, the test and the sample size before the experiment; do not "
      "choose after seeing the p-values.",
  pm="With 2,000 players per group, a real 10% increase in rounds played would be caught only about 1 time in "
     "3 by a simple average comparison, and about half the time by the best method. We need a bigger test, and "
     "we should fix the analysis method before we start.",
  mistakes="Computing the cap separately per arm (the cap then depends on the treatment). Choosing the test "
           "after seeing which one is significant. Forgetting to check the false positive rate of a new method.",
  learn=["stats-power-mde", "stats-choosing-a-test", "stats-ab-pitfalls"])

Q(ex, "How often is a significant result real?", minutes=6, review=True,
  prompt="Review of Bayes, applied to experiments. At a company, only 10% of tested ideas truly improve the "
         "metric. Tests use `alpha = 0.05` and have 80% power for the typical true effect.\n"
         "1. A test comes out significant (in the positive direction for a good idea, or as a false positive "
         "for a useless idea; ignore the direction for simplicity). What is the probability that the idea "
         "really works?\n"
         "2. Same question if the tests are underpowered (power 30%).\n"
         "3. Check part 1 by simulating 100,000 experiments (`rng = np.random.default_rng(0)`).",
  hint1="Signal: P(real | significant) with a base rate of good ideas. Topic: Bayes' rule: power plays the role "
        "of sensitivity, alpha the role of the false positive rate.",
  hint2="1. `P(sig) = 0.10 * power + 0.90 * 0.05`. 2. `P(real | sig) = 0.10 * power / P(sig)`. 3. Simulate "
        "`real = rng.random(n) < 0.1`, `sig = np.where(real, rng.random(n) < 0.8, rng.random(n) < 0.05)`.",
  solution='''def p_real_given_sig(prior=0.10, power=0.80, alpha=0.05):
    return prior * power / (prior * power + (1 - prior) * alpha)

print(f"power 80%: P(real | significant) = {p_real_given_sig():.3f}")
print(f"power 30%: P(real | significant) = {p_real_given_sig(power=0.30):.3f}")
rng = np.random.default_rng(0)
n = 100_000
real = rng.random(n) < 0.10
sig = np.where(real, rng.random(n) < 0.80, rng.random(n) < 0.05)
print(f"simulated (power 80%): {real[sig].mean():.3f}   share of tests significant {sig.mean():.3f}")''',
  out="""power 80%: P(real | significant) = 0.640
power 30%: P(real | significant) = 0.400
simulated (power 80%): 0.644   share of tests significant 0.127""",
  why="Out of 1,000 ideas, 100 are real and 80 of them are detected; 900 are useless and 45 of them are false "
      "positives. So 80 of 125 wins are real, 64%. With 30% power only 30 real ideas are detected against the "
      "same 45 false positives, so only 40% of wins are real. This is why underpowered tests are dangerous: "
      "they do not just miss effects, they make a 'significant' result much less trustworthy (and the detected "
      "effects are exaggerated, the 'winner's curse'). A p-value of 0.05 does not mean a 95% chance that the "
      "idea works.",
  pm="Even with well-designed tests, about 1 in 3 'winning' experiments is a false alarm when most ideas do not "
     "work; with small tests it is more than half. For big launches we should replicate a surprising win or "
     "use a stricter threshold.",
  mistakes="Saying 'significant at 5%' means '95% sure the idea works'. Ignoring the base rate of good ideas. "
           "Thinking low power only causes missed effects.",
  learn=["stats-bayes", "stats-power-mde"])

ex.save()
