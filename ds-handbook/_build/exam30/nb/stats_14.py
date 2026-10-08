import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam  # noqa: F401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stats_mid_common import start, q, pm

# Day 14 stats: MOCK. Review hypothesis tests, choosing a test, power/MDE, A/B design, analysis, pitfalls.
INTRO = ("**Mock exam rules.** One timer for the whole notebook: **30 minutes**. Run the setup cell, then start the "
         "timer. Work through Q1 to Q5 in order; skip and come back if stuck. Open hints and solutions **only after "
         "time is up**. For each question give the number *and* the sentence for the PM; in a real exam the "
         "sentence is half of the grade. Afterwards, score yourself: 2 points per question (1 for the number or the "
         "method, 1 for the interpretation).")
ex = start(14, ["tips", "telco", "cats", "ab"], intro=INTRO)

# ---------------------------------------------------------------- Q1
q(ex, title="Do smokers tip differently?", minutes=5, level="medium",
  prompt="Using `tips`, define `pct = tip / total_bill`. Do smokers and non-smokers tip a different percentage?\n\n"
         "(a) Mean and standard deviation of `pct` per group, a Welch t-test p-value, and a 95% CI for the "
         "difference in means (smokers minus non-smokers; use the Welch-Satterthwaite df or 1.96, say which).\n\n"
         "(b) Say it to a PM.\n\n"
         "Follow-up: smokers' standard deviation is twice as large. Why Welch and not Student's t-test? What does a "
         "single 71% tip do to the result?",
  stub="tips[\"pct\"] = tips.tip / tips.total_bill\n# your code here",
  hint1="Signal: a numeric outcome, two independent groups, unequal spread. Method: Welch two-sample t-test.",
  hint2="1. `a, b = pct[smoker=='Yes'], pct[smoker=='No']`. 2. `stats.ttest_ind(a, b, equal_var=False)`. "
        "3. `se = sqrt(var_a/n_a + var_b/n_b)`, CI = diff plus or minus 1.96 * se.",
  solution='''tips["pct"] = tips.tip / tips.total_bill
a = tips.pct[tips.smoker == "Yes"]
b = tips.pct[tips.smoker == "No"]
print(tips.groupby("smoker").pct.agg(["mean", "std", "count"]).round(4))
#           mean     std  count
# No      0.1593  0.0399    151
# Yes     0.1632  0.0851     93
res = stats.ttest_ind(a, b, equal_var=False)
diff = a.mean() - b.mean()
se = np.sqrt(a.var() / len(a) + b.var() / len(b))
print(f"diff {diff * 100:.2f} pp, p {res.pvalue:.2f}, CI [{(diff - 1.96 * se) * 100:.2f}, {(diff + 1.96 * se) * 100:.2f}] pp")
# diff 0.39 pp, p 0.68, CI [-1.46, 2.23] pp''',
  why="Both groups tip about 16% of the bill; the 0.39 pp gap is far inside the noise (p = 0.68) and the CI runs from "
      "-1.46 to +2.23 pp (1.96 used; the Welch df is about 117, which would widen it very slightly)."
      + pm("Smokers and non-smokers tip about the same share of the bill (around 16%); with 244 bills we cannot "
           "rule out a gap of up to about 2 points either way.",
           [("Why Welch?", "Student's test pools the variances, which is wrong when they differ (0.085 vs 0.040) "
             "and the group sizes differ; Welch does not assume equal variances and costs almost nothing when they "
             "are equal, so use it by default."),
            ("The 71% tip?", "It inflates the smokers' mean and standard deviation. Check robustness with a "
             "Mann-Whitney test (p = 0.56 here) or by excluding it with a stated rule; the conclusion does not "
             "change.")]),
  complexity="O(n).",
  mistakes="Testing `tip` instead of tip percentage (bigger bills get bigger tips). Using a paired test (the groups "
           "are different bills).",
  learn=["stats-hypothesis-tests", "stats-choosing-a-test"])

# ---------------------------------------------------------------- Q2
q(ex, title="Contract type and churn", minutes=5, level="medium",
  prompt="Using `telco`:\n\n"
         "(a) Churn rate per `Contract` type. Test whether churn and contract type are related, and give an effect "
         "size (Cramer's V = `sqrt(chi2 / (n * (min(rows, cols) - 1)))`).\n\n"
         "(b) Say it to a PM, careful with the wording.\n\n"
         "(c) Rapid fire, name the test: (1) day-7 retention, treatment vs control; (2) revenue per user, very "
         "skewed, 2 arms; (3) the same users rate the old and the new design; (4) clicks / views per user, "
         "randomised by user; (5) conversion across 4 arms.",
  stub="# your code here",
  hint1="Signal: two categorical variables. Method: chi-square test of independence on the contingency table; "
        "Cramer's V for the size.",
  hint2="1. `tab = pd.crosstab(telco.Contract, telco.Churn)`. 2. `stats.chi2_contingency(tab)` returns "
        "chi2, p, dof, expected. 3. V with min(3, 2) - 1 = 1.",
  solution='''tab = pd.crosstab(telco.Contract, telco.Churn)
print((tab["Yes"] / tab.sum(axis=1)).round(3).to_dict())
# {'Month-to-month': 0.427, 'One year': 0.113, 'Two year': 0.028}
chi2, p, dof, _ = stats.chi2_contingency(tab)
v = np.sqrt(chi2 / (tab.values.sum() * (min(tab.shape) - 1)))
print(f"chi2 {chi2:.0f}, dof {dof}, p {p:.1e}, Cramer's V {v:.2f}")
# chi2 1185, dof 2, p 5.9e-258, Cramer's V 0.41''',
  why="Month-to-month customers churn at 42.7%, fifteen times the 2.8% of two-year customers. The chi-square test "
      "says the link is not chance, and V = 0.41 says it is strong (above 0.3 is usually called large for a 2-column "
      "table). The data is observational, so this is association, not proof that contracts cause loyalty: "
      "committed customers choose long contracts."
      + pm("Churn is much higher on month-to-month plans (43% vs 3% on two-year plans); that tells us where to "
           "focus, but to know whether pushing people to longer contracts *reduces* churn we would need an "
           "experiment, for example a discount offer test.",
           [("Rapid fire answers", "(1) two-proportion z-test (or chi-square 2x2); (2) Welch t-test on capped "
             "values, bootstrap, or Mann-Whitney if a distribution shift is the question; (3) paired t-test or "
             "Wilcoxon signed-rank; (4) delta method (or bootstrap by user) for the ratio, because views within a "
             "user are correlated; (5) chi-square on the 4x2 table, then pairwise tests with a multiple-testing "
             "correction.")]),
  complexity="O(n).",
  mistakes="Reporting only the p-value (with 7,043 rows almost anything is significant; give rates and V). Saying "
           "'contracts reduce churn'.",
  learn=["stats-choosing-a-test", "stats-hypothesis-tests"])

# ---------------------------------------------------------------- Q3
q(ex, title="Size a test on rounds played", minutes=6, level="medium",
  prompt="The game team wants a new test with primary metric `sum_gamerounds` (use Cookie Cats gate_30 as the "
         "baseline). They want to detect a change of 2 rounds per player.\n\n"
         "(a) Players per group for alpha 0.05 (two-sided), power 0.8: `n = 2 * (z_a + z_b)^2 * sd^2 / delta^2`. "
         "Use the raw standard deviation.\n\n"
         "(b) Repeat after capping the metric at its 99th percentile (winsorizing). What does capping change about "
         "what you measure?\n\n"
         "(c) Say it to a PM.",
  stub="# your code here",
  hint1="Signal: sample size for a mean difference, and a heavy tail. Method: power formula for two means; "
        "variance reduction by capping.",
  hint2="1. `x = cats.sum_gamerounds[cats.version=='gate_30']`. 2. `sd = x.std()`. 3. `cap = x.quantile(0.99)`, "
        "`x.clip(upper=cap).std()`. 4. Plug both into the formula.",
  solution='''x = cats.loc[cats.version == "gate_30", "sum_gamerounds"]
z = stats.norm.ppf(0.975) + stats.norm.ppf(0.8)
def n_means(sd, delta=2):
    return int(np.ceil(2 * z ** 2 * sd ** 2 / delta ** 2))
cap = x.quantile(0.99)
sd_raw, sd_cap = x.std(), x.clip(upper=cap).std()
print(f"sd raw {sd_raw:.1f}, cap at {cap:.0f} rounds, sd capped {sd_cap:.1f}")
print("n per group raw:", n_means(sd_raw), " capped:", n_means(sd_cap))
# sd raw 256.7, cap at 493 rounds, sd capped 84.5
# n per group raw: 258634  capped: 28002''',
  why="One player with 49,854 rounds makes the raw standard deviation 256.7; capping at the 99th percentile (493 "
      "rounds) brings it to 84.5, and since n grows with sd squared, the needed sample falls more than 9 times "
      "(258,634 to 28,002 per group). The capped metric is a slightly different question: it ignores how far the top "
      "1% go beyond 493 rounds. Set the cap from pre-test data and write it in the plan."
      + pm("If we cap extreme players at about 500 rounds, a 2 round change becomes detectable with about 28,000 "
           "players per group instead of about 260,000, at the cost of not measuring changes among the top 1% of "
           "players.",
           [("Other ways to cut variance?", "CUPED with pre-period rounds (day 16), a log transform (changes the "
             "estimand to a ratio), or a triggered analysis.")]),
  complexity="O(n).",
  mistakes="Using the per-group formula without the factor 2. Choosing the cap after seeing test results. Capping "
           "at a different value in each arm.",
  learn=["stats-power-mde", "stats-cuped"])

# ---------------------------------------------------------------- Q4
q(ex, title="Would daily checking have fooled us?", minutes=6, level="medium",
  prompt="Use the cleaned `ab` table (drop group/page mismatches, keep the first row per user).\n\n"
         "(a) For each calendar day, compute the two-proportion z-test p-value on all data **up to and including** "
         "that day. On how many days is p < 0.05? What is the smallest p-value and on which day?\n\n"
         "(b) What is the final p-value?\n\n"
         "(c) Say it to a PM.",
  stub="ok = (ab.group == \"treatment\") == (ab.landing_page == \"new_page\")\n"
       "clean = ab[ok].sort_values(\"timestamp\").drop_duplicates(\"user_id\")\n# your code here",
  hint1="Signal: a p-value tracked over time. Pitfall: peeking. Compute the cumulative test day by day.",
  hint2="1. `day = pd.to_datetime(clean.timestamp).dt.date`. 2. Daily sums and counts per group with "
        "`groupby([day, 'group'])`, then `cumsum()`. 3. z-test per row.",
  solution='''ok = (ab.group == "treatment") == (ab.landing_page == "new_page")
clean = ab[ok].sort_values("timestamp").drop_duplicates("user_id")
clean["day"] = pd.to_datetime(clean.timestamp).dt.date
d = clean.groupby(["day", "group"]).converted.agg(["sum", "count"]).unstack().cumsum()
x_c, x_t = d["sum"]["control"], d["sum"]["treatment"]
n_c, n_t = d["count"]["control"], d["count"]["treatment"]
pool = (x_c + x_t) / (n_c + n_t)
z = (x_t / n_t - x_c / n_c) / np.sqrt(pool * (1 - pool) * (1 / n_t + 1 / n_c))
p = pd.Series(2 * stats.norm.sf(abs(z)), index=z.index)
print("days:", len(p), " days with p < 0.05:", (p < 0.05).sum())
print("smallest p:", round(p.min(), 3), "on", p.idxmin(), " final p:", round(p.iloc[-1], 3))
# days: 23  days with p < 0.05: 0
# smallest p: 0.127 on 2017-01-05  final p: 0.19''',
  why="Over 23 calendar days the cumulative p-value never went below 0.05; its lowest point was 0.127 on 2017-01-05 "
      "(when little data had arrived) and it ended at 0.19. Here peeking would not have produced a false win, but "
      "that is luck, not a property of the method: a p-value path that wanders up and down is normal under the null, "
      "which is why one pre-registered look (or a sequential method) is needed."
      + pm("Checking every day, we would have seen the p-value move around, but it never gave a reliable signal; the "
           "final read after the planned 3 weeks says there is no meaningful difference.",
           [("If it had dipped below 0.05 on one day?", "Under daily peeking the false positive rate is not 5% but "
             "about 20 to 25% for 20 looks (day 13), so a single dip is not evidence. Use the planned end date or "
             "an alpha spending boundary.")]),
  complexity="O(n log n) for the sort, then O(days).",
  mistakes="Using daily (not cumulative) data and calling it peeking. Forgetting the first and last days are partial "
           "days.",
  learn=["stats-ab-pitfalls", "stats-ab-analysis"])

# ---------------------------------------------------------------- Q5 case
q(ex, title="Case: should Cookie Cats move the gate?", minutes=8, level="medium", kind="text",
  prompt="You have this readout from the Cookie Cats test (gate_30 = control, gate_40 = treatment):\n\n"
         "| metric | gate_30 | gate_40 | diff | p |\n|---|---|---|---|---|\n"
         "| players | 44,700 | 45,489 | | SRM p = 0.0086 |\n"
         "| day-1 retention | 44.82% | 44.23% | -0.59 pp | 0.074 |\n"
         "| day-7 retention | 19.02% | 18.20% | -0.82 pp | 0.0016 |\n"
         "| mean rounds | 52.5 | 51.3 | -1.2 | CI includes 0 |\n\n"
         "The PM says: 'Day-1 is flat and rounds are flat, the later gate gives players more free play, let's ship "
         "gate_40.' Give your recommendation in 5 to 7 bullets: what you trust, what you check first, the decision, "
         "and what you would do next. Then say it to the PM in two sentences.",
  hint1="Framework: data quality first (SRM), then the primary metric, then guardrails and mechanism, then the "
        "decision with its risk, then next steps.",
  hint2="1. SRM p = 0.0086: investigate before trusting. 2. Day-7 retention is the long-term metric and is clearly "
        "down. 3. 'Flat' day-1 is not zero (CI to -1.24 pp). 4. Mechanism: the gate forces a break that may build "
        "anticipation. 5. Decide, and say what would change your mind.",
  solution="""- **Check data quality first.** The split is 50.44 / 49.56 with SRM p = 0.0086. Before any decision, check
  assignment logs, platform/version mix, and whether one arm lost users through logging. If a cause is found and it
  is unrelated to engagement, the metrics can still be used; if not, re-run or treat the result with caution.
- **Primary metric:** day-7 retention is closest to long-term value (revenue, lifetime). It dropped 0.82 pp (4.3%
  relative), p = 0.0016, CI about -1.33 to -0.31 pp. That is a clear harm, not noise.
- **Day-1 is not "flat":** -0.59 pp with a CI from -1.24 to +0.06 pp. Not significant, but it points the same way.
- **Rounds:** the mean is dominated by one player with 49,854 rounds; without that player the difference is about
  0. So more free play did not translate into more play.
- **Mechanism (plausible story):** the gate at level 30 forces a pause that keeps the game fresh (hedonic
  adaptation); moving it to 40 lets players burn out faster. This is a hypothesis, not proven by this test.
- **Decision:** keep gate_30. Shipping gate_40 risks about 1 in 23 day-7 retained players (0.82 / 19.02).
- **Next:** fix or explain the SRM; if the team still wants a later gate, test intermediate options (gate at 35) and
  track day-14 and day-30 retention and revenue.

**Say it to a PM:** "The later gate loses about 4% of the players who would still be playing after a week, and that
drop is very unlikely to be chance, so I recommend we keep the gate at level 30. Before we close this, I want to check
why the two groups are slightly unequal in size, but that is unlikely to reverse the result."
""",
  why="A good case answer is ordered (trust, then metrics, then decision), uses the primary metric agreed before the "
      "test instead of the most convenient one, and corrects 'flat' into 'not significant, here is the CI'.",
  mistakes="Agreeing with the PM because two of three metrics are 'flat'. Ignoring the SRM flag. Calling the rounds "
           "difference significant because of the outlier.",
  learn=["stats-launch-decisions", "stats-ab-analysis", "stats-ab-pitfalls"])

ex.save()
