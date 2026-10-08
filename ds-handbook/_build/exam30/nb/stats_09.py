import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam  # noqa: F401  (Exam is created inside stats_common.start)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stats_common import start, Q

# Day 9 statistics: focus choosing a test (data type, groups, pairing, distribution shape). Review: hypothesis
# tests (Q4).
ex = start(9, ["titanic", "cookie", "ab"])

Q(ex, "Pick the test, fast", minutes=6, kind="text",
  prompt="Rapid fire, as in a phone screen. For each scenario name the test (and one assumption or caveat) in "
         "one line:\n\n"
         "1. Checkout conversion, control versus new button, 80,000 users per arm.\n"
         "2. Average order value per user (heavy right tail), control versus treatment, 50,000 users per arm.\n"
         "3. The same 40 users do a task on the old and the new design; we measure seconds to finish.\n"
         "4. Click-through rate for 4 different banner colours.\n"
         "5. Mean session length in 3 regions.\n"
         "6. A pilot: 12 of 40 users converted; the historical rate is 20%.\n"
         "7. Is app rating related to the number of downloads?",
  hint1="Signal: for every scenario ask three questions: what type is the metric (0/1, numeric, counts)? How "
        "many groups? Are the groups independent or paired? Topic: the test chooser.",
  hint2="0/1 metric with 2 groups -> z-test for proportions (or chi-square). Numeric, 2 independent groups -> "
        "Welch t-test (rank test or bootstrap if small and skewed). Same units twice -> paired test. More than 2 "
        "groups -> chi-square (0/1) or ANOVA (numeric). Small counts -> exact test. Two numeric variables -> "
        "correlation.",
  solution='''**Model answer.**

| # | Test | Assumption or caveat |
|---|---|---|
| 1 | Two-proportion z-test (same as a 2x2 chi-square test) | Independent users; large counts (at least about 10 successes and 10 failures per arm). |
| 2 | Welch t-test on the means; check with a bootstrap CI | With 50,000 per arm the CLT makes the mean normal, but extreme values inflate the variance: cap (winsorize) or use CUPED for power. Mann-Whitney tests a shift in the *distribution*, not the mean, so it answers a different question. |
| 3 | Paired t-test on the 40 differences (or Wilcoxon signed-rank if the differences are skewed) | Pairing removes person-to-person variation; an unpaired test would waste it. Randomise the order of old and new to avoid a learning effect. |
| 4 | Chi-square test of independence on the 4 x 2 table (clicked / not clicked) | It only says 'some colour differs'; follow up with pairwise tests and a multiple-testing correction. |
| 5 | One-way ANOVA (Welch ANOVA if the spreads differ), or Kruskal-Wallis for skewed data | Same issue: a significant result needs post-hoc pairwise comparisons (Tukey). Regions are not randomised, so differences are not causal. |
| 6 | Exact binomial test (`st.binomtest(12, 40, 0.2)`) | n is small, so avoid the normal approximation. The pilot users may not be representative. |
| 7 | Spearman rank correlation (downloads are extremely skewed), or Pearson on log(downloads) | Correlation is not causation: popular apps get more ratings and more visibility. |''',
  why="Examiners rarely want formulas here; they want the decision path: metric type, number of groups, "
      "independent or paired, sample size and shape. Saying the caveat (what the test does *not* tell you) is "
      "what separates a strong answer from a memorised list.",
  pm="For each question, the test is just the tool; what you would tell a PM is the size of the difference with "
     "an error bar and whether it is big enough to act on, for example: 'the new button lifts conversion by 0.5 "
     "points, give or take 0.2'.",
  mistakes="Using a t-test for a 0/1 metric in a small sample, or for paired data. Running 6 pairwise t-tests "
           "for 4 groups without correction. Saying Mann-Whitney compares medians (it compares whole "
           "distributions; it equals a median test only under extra assumptions).",
  learn=["stats-choosing-a-test", "cheat-stats-tests"])

Q(ex, "Class and survival: one test for a whole table", minutes=6,
  prompt="Using `titanic`, is survival independent of passenger class (`pclass`, 3 levels)?\n"
         "1. Build the 3 x 2 contingency table with `pd.crosstab`.\n"
         "2. Run a chi-square test of independence and print the statistic, degrees of freedom and p-value.\n"
         "3. Print the table of expected counts under H0, and the survival rate per class.\n"
         "4. Why not run three separate two-proportion tests instead?",
  stub="# titanic is loaded in the setup\n",
  hint1="Signal: two categorical variables, one of them with more than 2 levels. Topic: the chi-square test of "
        "independence.",
  hint2="1. `tab = pd.crosstab(titanic.pclass, titanic.survived)`. 2. `chi2, p, dof, expected = "
        "st.chi2_contingency(tab)`. 3. `dof = (rows - 1) (cols - 1) = 2`. 4. Check all expected counts are at "
        "least 5.",
  solution='''tab = pd.crosstab(titanic["pclass"], titanic["survived"])
chi2, p, dof, expected = st.chi2_contingency(tab)
print(tab.to_string())
print(f"chi2 {chi2:.1f}   dof {dof}   p {p:.1e}")
print("expected counts under H0:")
print(pd.DataFrame(expected, index=tab.index, columns=tab.columns).round(1).to_string())
print("survival rate by class:", titanic.groupby("pclass")["survived"].mean().round(3).to_dict())''',
  out="""survived    0    1
pclass
1          80  136
2          97   87
3         372  119
chi2 102.9   dof 2   p 4.5e-23
expected counts under H0:
survived      0      1
pclass
1         133.1   82.9
2         113.4   70.6
3         302.5  188.5
survival rate by class: {1: 0.63, 2: 0.473, 3: 0.242}""",
  why="The chi-square test compares observed counts with the counts expected if class and survival were "
      "independent (`row total x column total / grand total`). One test with 2 degrees of freedom answers 'does "
      "survival differ across classes at all' without multiplying the false-positive risk; the pairwise tests "
      "come after, with a correction. All expected counts are far above 5, so the chi-square approximation is "
      "valid (otherwise use Fisher's exact test). The p-value is tiny, but remember that the test says nothing "
      "about *why*: class is mixed up with sex and cabin position.",
  pm="Survival clearly depended on ticket class: 63% in first class, 47% in second and 24% in third. A gap "
     "this large could not come from chance.",
  mistakes="Running the test on percentages instead of counts. Forgetting that a significant chi-square does "
           "not say which class differs. Using chi-square when some expected counts are below 5.",
  learn=["stats-choosing-a-test", "stats-hypothesis-tests"])

Q(ex, "Rounds played: which test?", minutes=8,
  prompt="In `cookie`, compare `sum_gamerounds` between `gate_30` and `gate_40` (remove the one 49,854-round "
         "account first).\n"
         "1. Print the mean and median per version.\n"
         "2. Run a Welch t-test and a Mann-Whitney U test and print both p-values.\n"
         "3. Bootstrap a 95% CI for the difference in **means** (`gate_40 - gate_30`, 1,000 resamples, "
         "`rng = np.random.default_rng(0)`).\n"
         "4. The two tests disagree a little. Explain what each one tests and which one answers the business "
         "question 'did players play more rounds?'.",
  stub="# cookie is loaded in the setup\nc = cookie[cookie.sum_gamerounds < 49854]\n",
  hint1="Signal: a heavy-tailed engagement metric with large groups. Topic: choosing between a test on means "
        "(Welch t, bootstrap) and a rank test (Mann-Whitney), and knowing they ask different questions.",
  hint2="1. `a, b = c[c.version == 'gate_30'].sum_gamerounds, ...`. 2. `st.ttest_ind(b, a, equal_var=False)`, "
        "`st.mannwhitneyu(b, a, alternative='two-sided')`. 3. Resample each group separately with "
        "`rng.choice(x, size=(1000, len(x)))`, take row means, subtract, use percentiles 2.5 and 97.5.",
  solution='''c = cookie[cookie["sum_gamerounds"] < 49854]
a = c.loc[c["version"] == "gate_30", "sum_gamerounds"].to_numpy()
b = c.loc[c["version"] == "gate_40", "sum_gamerounds"].to_numpy()
print(f"gate_30 mean {a.mean():.2f} median {np.median(a):.0f}   gate_40 mean {b.mean():.2f} median {np.median(b):.0f}")
print(f"Welch t-test p {st.ttest_ind(b, a, equal_var=False).pvalue:.3f}")
print(f"Mann-Whitney p {st.mannwhitneyu(b, a, alternative='two-sided').pvalue:.3f}")
rng = np.random.default_rng(0)
diffs = rng.choice(b, size=(1000, len(b))).mean(axis=1) - rng.choice(a, size=(1000, len(a))).mean(axis=1)
lo, hi = np.percentile(diffs, [2.5, 97.5])
print(f"bootstrap 95% CI for the mean difference: [{lo:.2f}, {hi:.2f}] rounds")''',
  out="""gate_30 mean 51.34 median 17   gate_40 mean 51.30 median 16
Welch t-test p 0.949
Mann-Whitney p 0.051
bootstrap 95% CI for the mean difference: [-1.30, 1.31] rounds""",
  why="Welch's t-test and the bootstrap ask: 'is the *mean* number of rounds different?'. That is the business "
      "question when total engagement matters (total rounds = mean x players). The mean difference is tiny "
      "(0.04 rounds) and its CI, about -1.3 to +1.3 rounds, is centred on 0, so we cannot claim a change in "
      "rounds played. Mann-Whitney asks a different question: 'does a random gate_40 player tend to rank above "
      "a random gate_30 player?'. It is robust to outliers and sensitive to shifts among light players, which "
      "is why its p-value differs. Pick the test from the question and decide it before looking at the data; "
      "running both and reporting the smaller p-value is p-hacking.",
  pm="Players in the two versions played about the same number of rounds in their first week: the difference "
     "is under one round per player and could be chance. The real effect of the change is on retention, not "
     "on how much people play.",
  mistakes="Saying 'the data is not normal, so use Mann-Whitney' with 45,000 users per arm (the CLT covers the "
           "mean). Saying Mann-Whitney compares medians. Reporting whichever test is significant.",
  learn=["stats-choosing-a-test", "stats-confidence-intervals"])

Q(ex, "The landing page test", minutes=5, review=True,
  prompt="Review of hypothesis tests. Using the cleaned `ab` table (one row per user):\n"
         "1. Print the conversion rate and n for control and treatment.\n"
         "2. Run a two-sided two-proportion z-test (`proportions_ztest`) and print z and p.\n"
         "3. The company only cares whether the new page is **better**. Print the one-sided p-value for "
         "H1: treatment > control. What do you conclude?",
  stub="# ab is loaded and cleaned in the setup\nfrom statsmodels.stats.proportion import proportions_ztest\n",
  hint1="Signal: two independent groups, 0/1 metric, large n. Topic: the two-proportion z-test, and the "
        "direction of a one-sided alternative.",
  hint2="1. `g = ab.groupby('group').converted.agg(['sum', 'count'])`. 2. `proportions_ztest([k_t, k_c], [n_t, "
        "n_c])`. 3. `alternative='larger'` tests treatment > control when treatment comes first.",
  solution='''from statsmodels.stats.proportion import proportions_ztest
g = ab.groupby("group")["converted"].agg(["sum", "count", "mean"])
print("per group:")
print(g.round(4).to_string())
k = [g.loc["treatment", "sum"], g.loc["control", "sum"]]
n = [g.loc["treatment", "count"], g.loc["control", "count"]]
z, p2 = proportions_ztest(k, n)
_, p1 = proportions_ztest(k, n, alternative="larger")
print(f"z {z:.3f}   two-sided p {p2:.3f}   one-sided p (treatment > control) {p1:.3f}")''',
  out="""per group:
             sum   count    mean
group
control    17489  145274  0.1204
treatment  17264  145310  0.1188
z -1.311   two-sided p 0.190   one-sided p (treatment > control) 0.905""",
  why="The treatment converts slightly *worse* (11.88% versus 12.04%), so z is negative. The two-sided p-value "
      "is 0.19: the gap is compatible with chance. For the one-sided alternative 'treatment is better', the "
      "observed result points the wrong way, so the p-value is large (0.90): there is no evidence at all that "
      "the new page is better. A one-sided test is fine only if the direction is chosen before the data, and "
      "it never turns a negative result into a positive one.",
  pm="The new page does not convert better: it is 0.16 points lower, and the gap is small enough to be chance. "
     "With about 145,000 users per group the test could detect a lift of about a third of a point, so we can "
     "keep the old page.",
  mistakes="Passing the groups in the wrong order with `alternative='larger'` (that tests control > "
           "treatment). Switching to one-sided after seeing the result. Analysing the raw file with duplicate "
           "users and mismatched pages.",
  learn=["stats-hypothesis-tests", "stats-ab-analysis"])

ex.save()
