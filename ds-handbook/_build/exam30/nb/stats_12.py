import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam  # noqa: F401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stats_mid_common import start, q, pm

# Day 12 stats: focus A/B analysis; review A/B design and choosing a test.
ex = start(12, ["cats", "ab"])

# ---------------------------------------------------------------- Q1
q(ex, title="Did the later gate change retention?", minutes=6,
  prompt="Cookie Cats: compare gate_40 (treatment) with gate_30 (control).\n\n"
         "(a) For `retention_1` and `retention_7`, print the rate in each group, the absolute difference "
         "(treatment minus control, in pp), the relative change, a two-sided p-value from a two-proportion z-test, "
         "and a 95% confidence interval for the difference (unpooled standard error).\n\n"
         "(b) Say it to a PM: what would you recommend?\n\n"
         "Follow-ups: why is the pooled SE used for the test but the unpooled SE for the CI? You looked at two "
         "metrics; does that change how you read the p-values?",
  stub="def two_prop(x_t, n_t, x_c, n_c):\n    \"\"\"return diff, z, p, (lo, hi)\"\"\"\n    pass\n\n# your code here",
  hint1="Signal: binary metric, two independent groups, large n. Method: two-proportion z-test plus a Wald CI for "
        "the difference.",
  hint2="1. Pooled p = (x_t + x_c) / (n_t + n_c); SE0 = sqrt(p(1-p)(1/n_t + 1/n_c)); z = diff / SE0. "
        "2. p-value = 2 * (1 - norm.cdf(|z|)). 3. CI: diff plus or minus 1.96 * sqrt(p_t(1-p_t)/n_t + "
        "p_c(1-p_c)/n_c).",
  solution='''def two_prop(x_t, n_t, x_c, n_c):
    p_t, p_c = x_t / n_t, x_c / n_c
    diff = p_t - p_c
    p_pool = (x_t + x_c) / (n_t + n_c)
    z = diff / np.sqrt(p_pool * (1 - p_pool) * (1 / n_t + 1 / n_c))
    p = 2 * stats.norm.sf(abs(z))
    se = np.sqrt(p_t * (1 - p_t) / n_t + p_c * (1 - p_c) / n_c)
    return diff, z, p, (diff - 1.96 * se, diff + 1.96 * se)

for m in ["retention_1", "retention_7"]:
    g = cats.groupby("version")[m].agg(["sum", "count"])
    x_t, n_t = g.loc["gate_40"]
    x_c, n_c = g.loc["gate_30"]
    diff, z, p, (lo, hi) = two_prop(x_t, n_t, x_c, n_c)
    print(f"{m}: control {x_c / n_c:.4f}, treatment {x_t / n_t:.4f}, diff {diff * 100:+.2f} pp "
          f"({diff / (x_c / n_c) * 100:+.1f}%), z {z:.2f}, p {p:.4f}, CI [{lo * 100:.2f}, {hi * 100:.2f}] pp")
# retention_1: control 0.4482, treatment 0.4423, diff -0.59 pp (-1.3%), z -1.78, p 0.0744, CI [-1.24, 0.06] pp
# retention_7: control 0.1902, treatment 0.1820, diff -0.82 pp (-4.3%), z -3.16, p 0.0016, CI [-1.33, -0.31] pp''',
  why="Day-1 retention fell by 0.59 pp but the CI includes 0 (p = 0.074). Day-7 retention fell by 0.82 pp (4.3% "
      "relative), p = 0.0016 and the whole CI is below zero. Day-7 retention is the metric closest to long-term "
      "value, so this is a real harm. Even with a Bonferroni correction for 2 metrics (alpha 0.025) the day-7 "
      "result stays significant."
      + pm("Moving the gate to level 40 lowered 7-day retention from 19.0% to 18.2%, a 4% relative drop that is very "
           "unlikely to be noise, so I recommend keeping the gate at level 30.",
           [("Pooled vs unpooled SE?", "The test assumes H0 (both groups share one rate), so it uses the pooled "
             "rate. The CI describes the difference without assuming H0, so it uses each group's own rate. With "
             "large n the two are almost the same."),
            ("Two metrics?", "Decide the primary metric before the test. If both are confirmatory, correct (for "
             "example Bonferroni or Holm); day-7 still passes. Do not pick whichever metric looks best afterwards.")]),
  complexity="O(n) for the counts.",
  mistakes="Reporting only the relative change (4.3%) without the absolute one, or the reverse. Swapping treatment "
           "and control so the sign flips. Saying 'retention_1 shows no effect' instead of 'not significant, CI from "
           "-1.24 to +0.06 pp'.",
  learn=["stats-ab-analysis", "stats-hypothesis-tests"])

# ---------------------------------------------------------------- Q2
q(ex, title="Clean the landing page test, then read it", minutes=8,
  prompt="The `ab` table is a real landing page test with messy logging.\n\n"
         "(a) Count rows where `group` and `landing_page` do not match (treatment should see new_page). Drop them.\n\n"
         "(b) After that, how many user ids appear more than once? Keep the first exposure (earliest timestamp) per "
         "user.\n\n"
         "(c) Sample ratio mismatch (SRM) check: the design was 50/50. Run a chi-square goodness-of-fit test on the "
         "group counts.\n\n"
         "(d) Conversion rate per group, difference, p-value (two-proportion z-test, you may use "
         "`statsmodels.stats.proportion.proportions_ztest`), and a 95% CI.\n\n"
         "(e) Say it to a PM.\n\n"
         "Follow-ups: the mismatched rows are 1.3% of the data. When would dropping them bias the result? Why keep "
         "the first exposure and not the last?",
  stub="# your code here",
  hint1="Signal: real logs before a test read. Method: data-quality checks (assignment consistency, dedup, SRM), "
        "then a two-proportion test.",
  hint2="1. `ok = (ab.group == 'treatment') == (ab.landing_page == 'new_page')`. 2. Sort by timestamp, "
        "`drop_duplicates('user_id', keep='first')`. 3. `stats.chisquare(counts)` (expected equal by default). "
        "4. `proportions_ztest([x_t, x_c], [n_t, n_c])`.",
  solution='''from statsmodels.stats.proportion import proportions_ztest

ok = (ab.group == "treatment") == (ab.landing_page == "new_page")
print("mismatched rows:", (~ok).sum())                           # 3893
clean = ab[ok].sort_values("timestamp")
print("repeated user ids:", clean.user_id.duplicated().sum())    # 1
clean = clean.drop_duplicates("user_id", keep="first")

g = clean.groupby("group").converted.agg(["sum", "count", "mean"])
print(g)
#             sum   count      mean
# control   17489  145274  0.120386
# treatment 17264  145310  0.118808
print("SRM p-value:", round(stats.chisquare(g["count"]).pvalue, 3))   # 0.947

x = g.loc[["treatment", "control"], "sum"].values
n = g.loc[["treatment", "control"], "count"].values
z, p = proportions_ztest(x, n)
p_t, p_c = x / n
diff = p_t - p_c
se = np.sqrt(p_t * (1 - p_t) / n[0] + p_c * (1 - p_c) / n[1])
print(f"diff {diff * 100:+.3f} pp, z {z:.2f}, p {p:.3f}, "
      f"CI [{(diff - 1.96 * se) * 100:.2f}, {(diff + 1.96 * se) * 100:.2f}] pp")
# diff -0.158 pp, z -1.31, p 0.190, CI [-0.39, 0.08] pp''',
  why="Mismatched rows (3,893, about 1.3%) mean we do not know which page the user really saw. They are split almost "
      "evenly (1,928 in control, 1,965 in treatment), so dropping them is the usual choice here; there is 1 repeated "
      "user. The SRM test (p = 0.95) shows the split is fine. The new page "
      "converts 0.16 pp lower, not significant, and the CI from -0.39 to +0.08 pp rules out any gain larger than "
      "0.08 pp."
      + pm("The new landing page did not improve conversion: it was 0.16 points lower, within noise, and the "
           "data rules out any lift bigger than about 0.1 point, so I would not launch it on conversion grounds.",
           [("When is dropping mismatches biased?", "If the mismatch is caused by the treatment (for example the new "
             "page crashes on some browsers and they fall back to the old page), the dropped users are not random and "
             "the comparison is no longer like for like. Check the mismatch rate per arm and per browser; if it "
             "differs, analyse by assigned group (intent to treat) instead."),
            ("First or last exposure?", "The first exposure is the moment of randomisation; later rows may be "
             "affected by the first experience. Keeping the last one is a post-treatment choice.")]),
  complexity="O(n log n) for the sort, then O(n).",
  mistakes="Skipping the cleaning (the raw table double counts). Running the test before the SRM check. Reading "
           "p = 0.19 as 'the pages are equal' instead of looking at the CI.",
  learn=["stats-ab-analysis", "stats-ab-design"])

# ---------------------------------------------------------------- Q3
q(ex, title="Rounds played: a very skewed metric", minutes=7,
  prompt="Compare `sum_gamerounds` between the two Cookie Cats versions.\n\n"
         "(a) Print mean, median and max per group. One value is extreme. What is it?\n\n"
         "(b) Bootstrap (1,000 resamples, seed 0) a 95% percentile CI for the difference in means (gate_40 minus "
         "gate_30), with and without that single player. Also run a Mann-Whitney U test.\n\n"
         "(c) Say it to a PM.\n\n"
         "Follow-ups: why not a plain t-test here? Is the Mann-Whitney test a test of medians?",
  stub="rng = np.random.default_rng(0)\n# your code here",
  hint1="Signal: heavy tail and an outlier, large n. Methods: bootstrap CI (no normality assumption) and a "
        "rank test (robust to outliers). Compare them with the t-test logic.",
  hint2="1. `groupby('version').sum_gamerounds.agg(['mean','median','max'])`. 2. For each resample draw "
        "`rng.choice(x, len(x))` per group and store the mean difference. 3. `np.percentile(diffs, [2.5, 97.5])`. "
        "4. Drop the row with the max and repeat. 5. `stats.mannwhitneyu(t, c)`.",
  solution='''print(cats.groupby("version").sum_gamerounds.agg(["mean", "median", "max"]).round(2))
#            mean  median    max
# gate_30   52.46    17.0  49854
# gate_40   51.30    16.0   2640

def boot_diff(t, c, b=1000, seed=0):
    rng = np.random.default_rng(seed)
    d = [rng.choice(t, len(t)).mean() - rng.choice(c, len(c)).mean() for _ in range(b)]
    return np.percentile(d, [2.5, 97.5])

t = cats.loc[cats.version == "gate_40", "sum_gamerounds"].values
c = cats.loc[cats.version == "gate_30", "sum_gamerounds"].values
c_trim = c[c < c.max()]
print("mean diff with outlier:", round(t.mean() - c.mean(), 2), boot_diff(t, c).round(2))
print("mean diff without it:  ", round(t.mean() - c_trim.mean(), 2), boot_diff(t, c_trim).round(2))
print("Mann-Whitney p:", round(stats.mannwhitneyu(t, c).pvalue, 4))
# mean diff with outlier: -1.16 [-4.06  0.9 ]
# mean diff without it:   -0.04 [-1.34  1.22]
# Mann-Whitney p: 0.0502''',
  why="One control player has 49,854 rounds (almost 1,000 times the mean). That single row moves the mean difference "
      "from -0.04 to -1.16 rounds and widens the bootstrap CI. Both CIs include 0. The rank test (p = 0.0502) is "
      "borderline and is driven by the bulk of players, not by the outlier. Engagement is not where the effect is; "
      "retention is."
      + pm("Players played about the same number of rounds in both versions; the one big gap you might see comes "
           "from a single player with 49,854 rounds, which we treat as a logging problem or a bot.",
           [("Why not a t-test?", "With n = 45,000 per group the CLT makes the mean roughly normal even for skewed "
             "data, so a Welch t-test is not wrong. The problem is that the mean itself is dominated by outliers. "
             "Fixes: cap (winsorize) at the 99th or 99.9th percentile, use the bootstrap, or use a rank test."),
            ("Mann-Whitney = medians?", "Only if the two distributions have the same shape. In general it tests "
             "whether a random treatment user tends to beat a random control user (P(T > C) = 0.5). Say "
             "'distributions differ', not 'medians differ'.")]),
  complexity="O(B * n) for B bootstrap resamples (here about 1,000 * 90,000 draws).",
  mistakes="Reporting the mean without checking the max. Deleting outliers only in one group without a rule written "
           "before the test (write the cap rule into the analysis plan). Calling Mann-Whitney a median test.",
  learn=["stats-ab-analysis", "stats-choosing-a-test"])

# ---------------------------------------------------------------- Q4 review
q(ex, title="Is the split itself healthy?", minutes=5, review=True,
  prompt="Cookie Cats was designed as a 50/50 split. The groups have 44,700 (gate_30) and 45,489 (gate_40) "
         "players.\n\n"
         "(a) Run the SRM chi-square test. What p-value do you get? Most teams flag SRM at p < 0.001 or p < 0.01.\n\n"
         "(b) Name three causes of SRM and what each one means for the result.\n\n"
         "(c) Say it to a PM.\n\n"
         "Follow-up: the difference is only 789 players out of 90,189. Why does that matter at all?",
  stub="# your code here",
  hint1="Signal: observed split vs designed split. Method: chi-square goodness of fit (SRM check), done before "
        "any metric is read.",
  hint2="1. `counts = cats.version.value_counts()`. 2. `stats.chisquare(counts)` uses equal expected counts. "
        "3. Also print the treatment share.",
  solution='''counts = cats.version.value_counts().sort_index()
print(counts.to_dict())                                   # {'gate_30': 44700, 'gate_40': 45489}
res = stats.chisquare(counts)
print(f"share gate_40 {counts['gate_40'] / counts.sum():.4f}, chi2 {res.statistic:.2f}, p {res.pvalue:.4f}")
# share gate_40 0.5044, chi2 6.90, p 0.0086''',
  why="A 50.44% share looks harmless, but with 90,000 users the expected random wobble is only about 0.17 pp (SE of a "
      "share = `sqrt(0.25/90189)`), so a 0.44 pp gap is 2.6 SEs away: p = 0.0086. This is below 0.01, so under a "
      "strict 0.001 rule it passes, under a 0.01 rule it is flagged. Either way, investigate before trusting the "
      "metrics. Typical causes: (1) assignment bugs (some users hashed wrongly), (2) the treatment changes who gets "
      "logged (for example a crash or a slower first session in one arm drops events), (3) filters applied after "
      "assignment (bots removed in one arm only, or a data pipeline that drops rows). Causes 2 and 3 mean the "
      "missing users are not random, so the metric comparison may be biased."
      + pm("The split is slightly but suspiciously off (50.4% vs 50%), so before we act on the retention result we "
           "should check the logging and assignment; if we find no cause, the result still stands but with a "
           "caveat.",
           [("Only 789 players?", "SRM is not about the size of the imbalance but about what caused it. If 789 "
             "low-engagement players are missing from one arm, that alone can create a retention difference of the "
             "size we are testing.")]),
  complexity="O(n).",
  mistakes="Checking SRM only by eye. Checking it after reading the metric and only when the metric looks bad. "
           "Using the 0.05 cutoff (SRM tests are run on every experiment, so teams use a stricter cutoff).",
  learn=["stats-ab-design", "stats-ab-pitfalls"])

ex.save()
