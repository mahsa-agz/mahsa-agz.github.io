import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam  # noqa: F401  (Exam is created inside stats_common.start)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stats_common import start, Q

# Day 6 statistics: focus confidence intervals (t interval, difference of proportions, bootstrap). Review: CLT/SE (Q4).
ex = start(6, ["tips", "cookie", "taxis"])

Q(ex, "A range for the tip rate", minutes=6,
  prompt="Using `tips`, let `tip_pct = 100 * tip / total_bill`.\n"
         "1. Compute a 95% confidence interval for the mean tip percentage with the t distribution.\n"
         "2. Which of these sentences is correct?\n"
         "   - (a) 'There is a 95% probability that the true mean is inside this interval.'\n"
         "   - (b) '95% of tables tip a percentage inside this interval.'\n"
         "   - (c) 'If we repeated this sampling many times, 95% of intervals built this way would contain the "
         "true mean.'\n"
         "3. Print the share of individual tables whose tip_pct falls inside the interval.",
  stub="# tips is loaded in the setup\n",
  hint1="Signal: a range for a mean from one sample with unknown sd. Topic: the t confidence interval "
        "`mean +- t(0.975, n - 1) * sd / sqrt(n)`.",
  hint2="1. `x = 100 * tips.tip / tips.total_bill`; `se = x.std() / np.sqrt(len(x))`. 2. `t = st.t.ppf(0.975, "
        "len(x) - 1)`. 3. Interval = `x.mean() +- t * se` (or `st.t.interval(0.95, df, loc, scale)`). 4. Count "
        "tables between the two limits.",
  solution='''x = 100 * tips["tip"] / tips["total_bill"]
n, m, se = len(x), x.mean(), x.std() / np.sqrt(len(x))
t = st.t.ppf(0.975, n - 1)
lo, hi = m - t * se, m + t * se
print(f"n {n}  mean {m:.2f}  SE {se:.3f}  t {t:.3f}")
print(f"95% CI for the mean tip %: [{lo:.2f}, {hi:.2f}]")
print(f"share of tables inside the CI: {((x >= lo) & (x <= hi)).mean():.3f}")''',
  out="""n 244  mean 16.08  SE 0.391  t 1.970
95% CI for the mean tip %: [15.31, 16.85]
share of tables inside the CI: 0.127""",
  why="The CI describes uncertainty about the *mean*, so it is narrow (width about 1.5 points) while single "
      "tables vary a lot: only about 1 in 8 tables (12.7%) tips inside it. That shows (b) is wrong: a range for "
      "individual values is a *prediction* interval, roughly `mean +- 2 sd`. Sentence (c) is the correct "
      "frequentist meaning. Sentence (a) is the common Bayesian-sounding reading; strictly, the true mean is "
      "fixed and the interval is random, but in practice examiners accept 'we are 95% confident' as long as "
      "you can explain (c). The t interval assumes roughly normal sample means: with n = 244 and moderate skew "
      "(one 71% tip), that holds well enough; a bootstrap would be a good robustness check.",
  pm="On average, people tip between about 15.3% and 16.9% of the bill, and we are 95% confident the true "
     "average is in that range. Individual tables vary much more, so do not use this range to predict one "
     "table's tip.",
  mistakes="Choosing (a) or (b). Using 1.96 instead of the t quantile for small samples (here they are close: "
           "1.970). Using the sd instead of the SE, which gives a prediction range, not a CI.",
  learn=["stats-confidence-intervals"])

Q(ex, "Did moving the gate change 7-day retention?", minutes=7,
  prompt="In `cookie`, the treatment `gate_40` moved the first gate from level 30 to level 40.\n"
         "1. Print the 7-day retention rate and the number of players in each version.\n"
         "2. Compute a 95% confidence interval for the difference `gate_40 - gate_30` with the normal "
         "approximation (unpooled SE).\n"
         "3. Also print the relative change in percent. Does the interval include 0? What would you tell the "
         "game team?",
  stub="# cookie is loaded in the setup\n",
  hint1="Signal: two independent groups, a 0/1 metric, 'how big is the difference'. Topic: CI for a difference "
        "of two proportions, `SE = sqrt(p1 (1 - p1) / n1 + p2 (1 - p2) / n2)`.",
  hint2="1. `g = cookie.groupby('version').retention_7.agg(['mean', 'count'])`. 2. `diff = p40 - p30`. 3. "
        "`se = sqrt(p30 (1 - p30) / n30 + p40 (1 - p40) / n40)`. 4. `diff +- 1.96 * se`. 5. Relative change "
        "= `diff / p30`.",
  solution='''g = cookie.groupby("version")["retention_7"].agg(["mean", "count"])
(p30, n30), (p40, n40) = g.loc["gate_30"], g.loc["gate_40"]
diff = p40 - p30
se = np.sqrt(p30 * (1 - p30) / n30 + p40 * (1 - p40) / n40)
lo, hi = diff - 1.96 * se, diff + 1.96 * se
print(f"gate_30: {p30:.4f} (n={n30:.0f})   gate_40: {p40:.4f} (n={n40:.0f})")
print(f"difference {100 * diff:.2f} pp   95% CI [{100 * lo:.2f}, {100 * hi:.2f}] pp")
print(f"relative change {100 * diff / p30:.1f}%")''',
  out="""gate_30: 0.1902 (n=44700)   gate_40: 0.1820 (n=45489)
difference -0.82 pp   95% CI [-1.33, -0.31] pp
relative change -4.3%""",
  why="The two groups are independent random samples, so the variance of the difference is the sum of the two "
      "variances. The whole interval is below 0: the data are not compatible with 'no effect' at the 5% level, "
      "and they also tell us the size, roughly 0.3 to 1.3 points lower retention. A CI is more useful than a "
      "p-value alone because it shows the size and the uncertainty in the units the team cares about. The "
      "normal approximation is excellent here (about 45,000 players per arm and thousands of retained players "
      "in each).",
  pm="Moving the gate to level 40 lowered 7-day retention from 19.0% to 18.2%, a drop of about 0.8 points "
     "(4% relative), and we are 95% confident the true drop is between about 0.3 and 1.3 points. Keep the gate "
     "at level 30.",
  mistakes="Adding the standard errors instead of the variances. Using the pooled SE for a CI (pooled is for "
           "the test under H0). Reporting only 'significant' without the size. Mixing absolute points and "
           "relative percent.",
  learn=["stats-confidence-intervals", "stats-ab-analysis"])

Q(ex, "A range for the tip rate of card rides", minutes=7,
  prompt="For taxi rides paid by credit card (`taxis.payment == 'credit card'`), the finance team defines the "
         "tip rate as `sum(tip) / sum(fare)` (a ratio of two sums).\n"
         "1. Compute it.\n"
         "2. Build a 95% percentile bootstrap CI with 2,000 resamples of rides "
         "(`rng = np.random.default_rng(0)`).\n"
         "3. Why is the bootstrap convenient here?",
  stub="# taxis is loaded in the setup\ncard = taxis[taxis.payment == 'credit card']\n",
  hint1="Signal: a statistic with no easy SE formula (a ratio of sums). Topic: the bootstrap: resample the units "
        "with replacement, recompute the statistic, take the 2.5% and 97.5% percentiles.",
  hint2="1. `tip, fare = card.tip.to_numpy(), card.fare.to_numpy()`. 2. `idx = rng.integers(0, n, size=(2000, "
        "n))`. 3. `boot = tip[idx].sum(axis=1) / fare[idx].sum(axis=1)`. 4. `np.percentile(boot, [2.5, 97.5])`.",
  solution='''card = taxis[taxis["payment"] == "credit card"]
tip, fare = card["tip"].to_numpy(), card["fare"].to_numpy()
n = len(card)
rate = tip.sum() / fare.sum()
rng = np.random.default_rng(0)
idx = rng.integers(0, n, size=(2000, n))          # each row = one bootstrap sample of rides
boot = tip[idx].sum(axis=1) / fare[idx].sum(axis=1)
lo, hi = np.percentile(boot, [2.5, 97.5])
print(f"rides {n}   tip rate {100 * rate:.2f}%")
print(f"bootstrap SE {100 * boot.std():.2f} pp   95% CI [{100 * lo:.2f}%, {100 * hi:.2f}%]")''',
  out="""rides 4577   tip rate 20.31%
bootstrap SE 0.23 pp   95% CI [19.86%, 20.78%]""",
  why="A ratio of sums is not a mean of independent values, so `sd / sqrt(n)` does not apply directly; the "
      "exact alternative is the delta method. The bootstrap avoids the algebra: it treats the sample as the "
      "population, resamples whole rides (keeping each ride's tip and fare together), and reads the spread of "
      "the recomputed statistic. Resample the independent unit: here the ride; in an A/B test, the user. The "
      "percentile method works well for smooth statistics with large n; it is less reliable for extremes "
      "(max, p99) and tiny samples.",
  pm="Card-paying riders tip about 20.3% of the fare, and the plausible range is roughly 19.9% to 20.8%. That is "
     "a precise number we can use in the driver earnings model.",
  mistakes="Resampling tips and fares separately (it breaks the pairs). Averaging per-ride tip percentages and "
           "calling it the same metric (that weights short rides more). Using too few resamples (under 1,000) "
           "for a 95% interval.",
  learn=["stats-confidence-intervals", "stats-ratio-metrics"])

Q(ex, "How many rides to pin down the average tip?", minutes=5, review=True,
  prompt="Review of the standard error. Using all rides in `taxis`:\n"
         "1. Print the mean and sd of `tip` and the SE of the mean.\n"
         "2. How many rides would we need for a 95% margin of error of +- 5 cents (0.05)?\n"
         "3. If we doubled the number of rides in this sample, by what factor would the margin shrink?",
  stub="# taxis is loaded in the setup\n",
  hint1="Signal: 'how many observations for a given precision'. Topic: the square-root law, "
        "`margin = 1.96 * sd / sqrt(n)`, so `n = (1.96 * sd / margin)^2`.",
  hint2="1. `sd = taxis.tip.std()`, `se = sd / np.sqrt(len(taxis))`. 2. `n = (1.96 * sd / 0.05) ** 2`, round up. "
        "3. Doubling n divides the margin by `sqrt(2)`.",
  solution='''x = taxis["tip"]
sd, n = x.std(), len(x)
print(f"mean {x.mean():.3f}   sd {sd:.3f}   SE {sd / np.sqrt(n):.4f}   margin now +- {1.96 * sd / np.sqrt(n):.3f}")
print(f"rides for +- 0.05: {int(np.ceil((1.96 * sd / 0.05) ** 2)):,}")
print(f"doubling n shrinks the margin by a factor {np.sqrt(2):.3f}")''',
  out="""mean 1.979   sd 2.449   SE 0.0305   margin now +- 0.060
rides for +- 0.05: 9,213
doubling n shrinks the margin by a factor 1.414""",
  why="The margin is `1.96 * sd / sqrt(n)`. To make it a target size, solve for n: it grows with the square of "
      "`sd / margin`. Halving the margin costs 4 times the data, and doubling the data only shrinks the margin "
      "by 29% (factor 1.414). This is the same arithmetic behind A/B sample sizes (day 10).",
  pm="Today we know the average tip to within about 6 cents. To get it within 5 cents we would need roughly "
     "9,200 rides instead of 6,433.",
  mistakes="Forgetting to square. Using the SE where the sd belongs in the sample-size formula. Rounding n down.",
  learn=["stats-clt-se", "stats-power-mde"])

ex.save()
