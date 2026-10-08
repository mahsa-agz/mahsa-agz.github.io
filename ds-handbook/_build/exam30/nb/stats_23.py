import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam  # noqa: F401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _stats_hard_common import start, load, shown, PM, AB_CLEAN

# Day 23 stats. Focus: launch-decisions. Review: metric-drop, ab-pitfalls.

SETUP = (load("ab", "ab_data.csv") + "\n" + AB_CLEAN + "\n" + load("cats", "cookie_cats.csv") + '''
from statsmodels.stats.proportion import proportions_ztest
print(ab.shape, cats.shape)''')

DATA = """| Table | One row = | Columns | Real or simulated |
|---|---|---|---|
| `ab` | one user in an e-commerce landing-page test (Udacity data, already cleaned: one row per user, group and page agree) | `user_id`, `timestamp`, `group` (control/treatment), `landing_page`, `converted` (0/1) | real |
| `cats` | one player of the mobile game Cookie Cats; the test moved the first gate from level 30 to level 40 | `userid`, `version` (gate_30 = control, gate_40 = treatment), `sum_gamerounds` (rounds in the first 14 days), `retention_1`, `retention_7` (came back 1 and 7 days after install) | real |"""

ex = start(23, extra=SETUP, data_doc=DATA)

# ---------------------------------------------------------------- Q1 flat but well powered (ab_data)
q1 = '''g = ab.groupby("group").converted.agg(["sum", "count", "mean"])
pc, pt = g.loc["control", "mean"], g.loc["treatment", "mean"]
nc, nt = g.loc["control", "count"], g.loc["treatment", "count"]
diff = pt - pc
se = np.sqrt(pc * (1 - pc) / nc + pt * (1 - pt) / nt)
z, p = proportions_ztest(g.loc[["treatment", "control"], "sum"], g.loc[["treatment", "control"], "count"])
print(f"control {pc:.4f}, treatment {pt:.4f}, diff {diff:+.4f} ({diff / pc:+.1%} relative)")
print(f"95% CI [{diff - 1.96 * se:+.4f}, {diff + 1.96 * se:+.4f}], z = {z:.2f}, p = {p:.3f}")
p0 = ab.converted.mean()
mde = (1.96 + 0.84) * np.sqrt(p0 * (1 - p0) * (1 / nc + 1 / nt))
print(f"MDE at 80% power: {mde:.4f} ({mde / pc:.1%} relative)")
print(f"largest lift still compatible with the data: {(diff + 1.96 * se) / pc:+.1%} relative")
# control 0.1204, treatment 0.1188, diff -0.0016 (-1.3% relative)
# 95% CI [-0.0039, +0.0008], z = -1.31, p = 0.190
# MDE at 80% power: 0.0034 (2.8% relative)
# largest lift still compatible with the data: +0.6% relative'''
ex.q("Not significant: so what?", minutes=6, kind="python",
     prompt="Real data: `ab`. The design team built a new landing page and hopes it lifts conversion by at least "
            "**2% relative**. The test ran for about three weeks with roughly 145k users per group.\n\n"
            "1. Compute the conversion rates, the difference, its 95% CI and the p-value.\n"
            "2. What was the minimum detectable effect of this test (two-sided alpha 0.05, power 80%)?\n"
            "3. The designer says \"not significant just means we need more data\". Decide: launch, iterate, or "
            "stop, and defend it with the numbers." +
            PM + "your decision in two sentences.",
     hint1="Signal: a null result in a large test. Method: read the confidence interval against the effect the "
           "business cares about (and the MDE), not only the p-value.",
     hint2="1. Two-proportion z-test. 2. `MDE = (z_0.975 + z_0.8) * sqrt(p(1-p)(1/nc + 1/nt))`. 3. Compare the "
           "upper end of the CI with the 2% target.",
     solution=q1,
     why="A non-significant result is informative when the test is well powered: the upper end of the CI is "
         "+0.6% relative, so a lift of 2% is ruled out (the test could detect 2.8% with 80% power, and the whole "
         "CI sits below the target). More data would only narrow an interval that is already centred slightly "
         "below zero. Decision: do not launch this page; if the team believes in the idea, iterate on the design "
         "and test a new version. Keeping a new page also has a maintenance cost, so ties go to the old page." +
         PM + "\"The new page does not lift conversion: our best estimate is -1.3%, and the data rule out any gain "
         "above about 0.6%, far below the 2% we wanted. I recommend we keep the old page and test a bolder "
         "redesign instead of running this one longer.\"",
     mistakes="Saying 'no effect' (the CI still allows small effects in both directions). Asking for more data "
              "without computing what more data could show. Ignoring the target effect size the business set.",
     learn=["stats-launch-decisions", "stats-power-mde"])
shown(ex)

# ---------------------------------------------------------------- Q2 mixed metrics (cookie cats)
q2 = '''rows = []
for m in ["retention_1", "retention_7"]:
    s = cats.groupby("version")[m].agg(["sum", "count"])
    p30, p40 = s.loc["gate_30", "sum"] / s.loc["gate_30", "count"], s.loc["gate_40", "sum"] / s.loc["gate_40", "count"]
    se = np.sqrt(p30 * (1 - p30) / s.loc["gate_30", "count"] + p40 * (1 - p40) / s.loc["gate_40", "count"])
    z, p = proportions_ztest(s.loc[["gate_40", "gate_30"], "sum"], s.loc[["gate_40", "gate_30"], "count"])
    rows.append((m, round(p30, 4), round(p40, 4), round(p40 - p30, 4),
                 round(p40 - p30 - 1.96 * se, 4), round(p40 - p30 + 1.96 * se, 4), round(p, 4)))
print(pd.DataFrame(rows, columns=["metric", "gate_30", "gate_40", "diff", "ci_low", "ci_high", "p"]))

print("max rounds:", cats.sum_gamerounds.max())                            # one extreme player
r = cats[cats.sum_gamerounds < cats.sum_gamerounds.max()]
a, b = r[r.version == "gate_30"].sum_gamerounds, r[r.version == "gate_40"].sum_gamerounds
print(f"mean rounds {a.mean():.2f} vs {b.mean():.2f}, Welch p = {stats.ttest_ind(b, a, equal_var=False).pvalue:.2f}")
print(f"Mann-Whitney p = {stats.mannwhitneyu(b, a).pvalue:.3f}")
#         metric  gate_30  gate_40    diff  ci_low  ci_high       p
# 0  retention_1   0.4482   0.4423 -0.0059 -0.0124   0.0006  0.0744
# 1  retention_7   0.1902   0.1820 -0.0082 -0.0133  -0.0031  0.0016
# max rounds: 49854
# mean rounds 51.34 vs 51.30, Welch p = 0.95
# Mann-Whitney p = 0.051'''
ex.q("Move the gate or not?", minutes=7, kind="python",
     prompt="Real data: `cats`. In the puzzle game Cookie Cats players hit a gate (wait or pay) at level 30. "
            "The test moved it to level 40. The game designer argues that rounds played did not change, so the "
            "later gate is harmless and \"feels nicer\".\n\n"
            "1. For `retention_1` and `retention_7`, give each rate, the difference (gate_40 minus gate_30), a 95% "
            "CI and the p-value.\n"
            "2. Compare mean `sum_gamerounds`. Look at the maximum first and decide what to do with it.\n"
            "3. Three metrics, mixed signals. What do you recommend and why? Which metric decides?" +
            PM + "the recommendation.",
     hint1="Signal: several metrics disagree after a test. Method: launch decision with a metric hierarchy "
           "(which metric matters for the business), multiple-testing awareness, and effect sizes with CIs.",
     hint2="1. Two-proportion z-test and CI for each retention metric. 2. One player has about 50,000 rounds: "
           "check the result with and without, and use a test that is robust to the heavy tail. 3. Day-7 "
           "retention is closest to long-term value; check it still holds with a Bonferroni threshold 0.05 / 3.",
     solution=q2,
     why="Day-7 retention is lower with the gate at 40 by 0.82 points (19.02% to 18.20%, CI -1.33 to -0.31 "
         "points, p = 0.0016, still significant after a Bonferroni correction for 3 metrics: 0.0016 < 0.0167). "
         "Day-1 retention points the same way but is not significant. Rounds played are flat in the mean (after "
         "removing one player with 49,854 rounds, likely a bot or a logging error), and the rank test is "
         "borderline. Retention drives long-term revenue and is the metric the gate is supposed to protect, so it "
         "decides; 'no change in rounds' does not compensate for losing about 4% of the players who return on day 7 "
         "(0.0082 / 0.1902). A plausible mechanism: the earlier gate forces a break that brings players back. "
         "Recommendation: keep the gate at level 30." + PM +
         "\"Moving the gate to level 40 loses about 4% of players who come back after a week (18.2% instead of "
         "19.0%, and the gap is clearly real), while play time does not improve, so we should keep the gate at "
         "level 30.\"",
     mistakes="Letting the metric with no effect (rounds) decide. Leaving the 49,854-round outlier in a mean test. "
              "Restricting the analysis to players who reached level 30 using `sum_gamerounds`: rounds are "
              "affected by the treatment, so this conditions on a post-treatment variable and biases the result.",
     learn=["stats-launch-decisions", "stats-ab-analysis", "stats-ab-pitfalls"])
shown(ex)

# ---------------------------------------------------------------- Q3 mixed results case
ex.q("Watch time up, creators down", minutes=6, kind="text",
     prompt="A new feed ranking model was tested for 2 weeks on 10% of users (user-level randomization). "
            "Pre-registered primary metric: watch time per user. Results, treatment versus control:\n\n"
            "| Metric | Relative change | 95% CI | p |\n|---|---|---|---|\n"
            "| Watch time per user (primary) | +1.2% | +0.6% to +1.8% | 0.0001 |\n"
            "| DAU | 0.0% | -0.3% to +0.3% | 0.98 |\n"
            "| Videos posted per user (creators) | -2.0% | -3.1% to -0.9% | 0.0004 |\n"
            "| Content reports per 1k views | +4.0% | -0.5% to +8.5% | 0.08 |\n"
            "| Ad revenue per user | +0.4% | -0.4% to +1.2% | 0.33 |\n\n"
            "The PM wants to ship because the primary metric won. What do you recommend? Cover: what each result "
            "means, what might explain the creator drop, what you would check before deciding, and a concrete "
            "decision with its conditions." +
            PM + "the recommendation in three sentences.",
     hint1="Signal: primary metric wins, a guardrail loses. Method: launch decision framework: primary versus "
           "guardrails, ecosystem effects (two-sided platform), long-term versus short-term, then a decision "
           "with a fix or follow-up.",
     hint2="1. Primary is real and modest. 2. Creator posting is a guardrail and it is clearly down; think about "
           "why a viewer-side change moves creators. 3. Reports are not significant but the CI allows +8.5%. "
           "4. Ask: novelty, which videos gained views (concentration), long-term creator supply. 5. Decide: "
           "ship with a fix, ship to a holdout, or iterate.",
     solution="""**Reading the results.** Watch time +1.2% is real but modest. DAU is flat with a tight CI, so the
gain is engagement per user, not reach. Creator posting -2.0% is a guardrail failure, clearly outside noise. Reports
+4% is not significant but the CI allows up to +8.5%, so it is a warning, not a pass. Revenue is flat.

**Why could creators post less when only viewers were randomized?** The new model probably concentrates views on
fewer, already-popular videos. Smaller creators in the treatment users' feeds get fewer views and less feedback, so
they post less. Note also interference: treated viewers and control viewers share the same creators, so the 2-week
user-level test *underestimates* the creator effect at 100% launch (at 10% traffic, creators lose only part of
their views). A creator-side effect of -2% at 10% traffic could be much larger after full launch.

**Checks before deciding.** (1) Distribution of views across creators in each arm (Gini, share of views to the top 1%
of creators, views to new creators). (2) Daily lift of watch time: is it decaying (novelty)? (3) Content type of the
extra watch time: are the reports concentrated in some content? (4) A creator-side experiment or a market-level
test to measure the full ecosystem effect.

**Decision.** Do not ship as is. Short-term watch time of +1.2% does not justify a measured 2% loss in creator
supply, which drives future content and long-term watch time. Ask the ranking team for a version with an
exploration or fairness constraint for small creators, retest it with creator-side metrics as pre-registered
guardrails, and keep a long-term holdout if it ships. If leadership must ship now, ship with a 5% holdout and an
explicit rollback trigger on creator posting.

**Say it to a PM:** "The new model adds 1.2% watch time, but creators post 2% less and that loss will grow at full
launch because all viewers will see the new ranking. Shipping trades future content for a small engagement gain.
Let us fix the exposure for smaller creators and retest in two weeks with creator metrics as guardrails.\"""",
     why="Strong candidates do not let the pre-registered primary metric override a significant guardrail, explain "
         "the mechanism, notice that interference biases the guardrail toward zero, and give a decision with "
         "conditions instead of 'it depends'.",
     learn=["stats-launch-decisions", "stats-network-effects"])

# ---------------------------------------------------------------- Q4 review: SRM and a worst-case bound
q4 = '''counts = cats.version.value_counts()
chi2, p = stats.chisquare(counts)
print(counts.to_dict(), f"chi2 = {chi2:.2f}, p = {p:.4f}, gap = {counts.gate_40 - counts.gate_30}")
# worst case: gate_30 lost the missing players, and all of them would have been retained (or none)
r30 = cats.loc[cats.version == "gate_30", "retention_7"].sum()
miss = counts.gate_40 - counts.gate_30
lo, hi = r30 / counts.gate_40, (r30 + miss) / counts.gate_40
print(f"gate_30 retained on day 7: {r30}; bounds for its rate: {lo:.4f} to {hi:.4f}")
print(f"gate_40 rate: {cats.loc[cats.version == 'gate_40', 'retention_7'].mean():.4f}")
# {'gate_40': 45489, 'gate_30': 44700} chi2 = 6.90, p = 0.0086, gap = 789
# gate_30 retained on day 7: 8502; bounds for its rate: 0.1869 to 0.2042
# gate_40 rate: 0.1820'''
ex.q("Can we trust the split?", minutes=5, kind="python", review=True,
     prompt="Same `cats` test. The design was a 50/50 split.\n\n"
            "1. Test whether the observed group sizes are compatible with 50/50.\n"
            "2. Many experimentation platforms alarm only when this p-value is below 0.001. What would you do here?\n"
            "3. Suppose the imbalance happened because some gate_30 players were lost from the data. Bound the "
            "gate_30 day-7 retention in the worst cases (all lost players retained, or none) and say whether "
            "the Q2 decision survives." +
            PM + "is the test still usable?",
     hint1="Signal: unequal group sizes in a designed split. Method: sample ratio mismatch (SRM) check with a "
           "chi-square goodness-of-fit test, then a sensitivity (bounds) analysis.",
     hint2="1. `stats.chisquare(counts)` (expected equal). 2. Compare p with the threshold and think about why "
           "platforms use a strict one. 3. Add the gap of missing players to gate_30 with retention 0 or 1 and "
           "recompute the rate with the larger denominator.",
     solution=q4,
     why="With p = 0.0086 a 50/50 split is unlikely (789 more players in gate_40, 0.9% of the sample). Platforms "
         "use a strict 0.001 threshold because they check thousands of experiments and a looser one would cause "
         "many false alarms; here the result sits between 0.001 and 0.01, so investigate before trusting it: "
         "check the assignment code, platform or app-version splits, and the first days of logging. The bounds "
         "show the decision is robust: even if every lost gate_30 player was retained, gate_30's day-7 rate is "
         "at least 18.69%, still above gate_40's 18.20%." + PM + "\"The groups are slightly unbalanced, which "
         "usually signals a data problem, so we are checking the assignment; but even in the worst case for "
         "our conclusion the gate at level 30 still keeps more players, so the recommendation stands.\"",
     mistakes="Ignoring an SRM because the groups 'look close'. Reweighting the groups to 50/50 (it does not fix "
              "a selection problem). Applying a 0.05 threshold to SRM checks across a whole platform.",
     learn=["stats-ab-pitfalls", "stats-launch-decisions"])
shown(ex)

ex.save()
