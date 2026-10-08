import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam  # noqa: F401  (Exam is used through stats_mid_common.start)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stats_mid_common import start, q, pm

# Day 11 stats: focus A/B design; review power and MDE.
ex = start(11, ["cats"], note="Today you plan experiments before any result exists. Use only the control group "
           "(gate_30) of Cookie Cats as your 'historical baseline', as you would with last month's data.")

# ---------------------------------------------------------------- Q1
q(ex, title="How many players and how many days?", minutes=7,
  prompt="The Cookie Cats team wants to test moving the first gate from level 30 to level 40. Use the control "
         "group (`version == 'gate_30'`) as the historical baseline.\n\n"
         "(a) Write a function `n_per_group(p1, mde)` for a two-sided two-proportion test with alpha = 0.05 and "
         "power = 0.80, using the normal approximation "
         "`n = (z_(1-alpha/2) + z_(power))^2 * (p1(1-p1) + p2(1-p2)) / mde^2` with `p2 = p1 + mde`.\n\n"
         "(b) Players needed per group to detect an absolute change of 1 percentage point (pp) in day-1 retention "
         "and in day-7 retention. Which metric needs more players, and why?\n\n"
         "(c) The game gets about 9,000 new installs a day (assumption). With a 50/50 split, how many days does the "
         "day-7 test need, and what duration would you actually run?\n\n"
         "(d) Say it to a PM in one sentence.\n\n"
         "Follow-ups: what changes with a 90/10 split? Why do you have to wait 7 extra days for a day-7 metric?",
  stub="def n_per_group(p1, mde, alpha=0.05, power=0.8):\n    pass\n\n# your code here",
  hint1="Signal: 'how many users' before the test. Method: sample size for two proportions (power analysis). "
        "Variance `p(1-p)` is largest at p = 0.5.",
  hint2="1. `z_a = stats.norm.ppf(1 - alpha/2)`, `z_b = stats.norm.ppf(power)`. 2. Plug into the formula, round up "
        "with `np.ceil`. 3. Baselines: `cats[cats.version=='gate_30'].retention_1.mean()` (and retention_7). "
        "4. Days = 2n / 9000, then round up to whole weeks.",
  solution='''def n_per_group(p1, mde, alpha=0.05, power=0.8):
    p2 = p1 + mde
    z_a, z_b = stats.norm.ppf(1 - alpha / 2), stats.norm.ppf(power)
    return int(np.ceil((z_a + z_b) ** 2 * (p1 * (1 - p1) + p2 * (1 - p2)) / mde ** 2))

ctl = cats[cats.version == "gate_30"]
p_r1, p_r7 = ctl.retention_1.mean(), ctl.retention_7.mean()
n_r1 = n_per_group(p_r1, -0.01)        # we fear a drop, but the test is two-sided
n_r7 = n_per_group(p_r7, -0.01)
print(f"baseline day-1 {p_r1:.4f}, day-7 {p_r7:.4f}")   # 0.4482, 0.1902
print("n per group day-1:", n_r1)                         # 38734
print("n per group day-7:", n_r7)                         # 23685
days = 2 * n_r7 / 9000
print(f"days of installs for day-7: {days:.1f}")          # 5.3
# 90/10 split: n_total for the same SE is larger by 1/(4 * 0.9 * 0.1) = 2.78x
print(f"90/10 inflation: {1 / (4 * 0.9 * 0.1):.2f}")     # 2.78''',
  why="Sample size grows with the metric variance `p(1-p)` and shrinks with the square of the MDE. Day-1 retention "
      "sits near 45%, where `p(1-p)` is close to its maximum 0.25 (0.247), while day-7 retention is 19% "
      "(variance about 0.154), so the same 1 pp change needs about 64% more players for day-1. Installs: 5.3 days "
      "of traffic for day-7, but run at least one full week (7 days) to cover weekday and weekend players, and "
      "then wait 7 more days so the last cohort can show its day-7 retention. Planned length: about 2 weeks."
      + pm("To detect a 1 point drop in 7-day retention we need about 24,000 players per group, which is one week "
           "of installs plus one week of waiting for the last players to reach day 7, so results in about 2 weeks.",
           [("90/10 split?", "The variance of the difference is `p(1-p)(1/n1 + 1/n2)`. For a fixed total it is "
             "smallest at 50/50; at 90/10 you need about 2.78 times as many users in total. Use unequal splits only "
             "to limit risk, and accept a longer test."),
            ("Why wait 7 days?", "A user who installs on the last day can only show day-7 retention 7 days later. "
             "Stopping earlier means the last cohorts have a truncated metric, which biases it downward."),
            ("One-sided test?", "It needs fewer users (z = 1.645 instead of 1.96), but you would miss a harm in the "
             "other direction. Most companies use two-sided tests by default.")]),
  complexity="O(1) arithmetic once the two baselines are computed.",
  mistakes="Using the relative MDE (1%) where the formula needs the absolute one (1 pp). Forgetting it is per group. "
           "Rounding down. Stopping on the day the sample size is reached without full weeks and without the day-7 "
           "maturity window.",
  learn=["stats-ab-design", "stats-power-mde"])

# ---------------------------------------------------------------- Q2
q(ex, title="Only some players ever see the change", minutes=7,
  prompt="The gate only matters for players who get far enough to meet it. Use `sum_gamerounds >= 30` in the "
         "control group as a proxy for 'reached the first gate' (an assumption: rounds are not levels).\n\n"
         "(a) What share of control players is 'triggered'? What is day-7 retention among triggered and "
         "non-triggered players?\n\n"
         "(b) Suppose the change lowers day-7 retention by 2 pp among triggered players and does nothing to the "
         "others. What is the effect on all players?\n\n"
         "(c) Using `n_per_group` from Q1 (or re-define it), compare the number of installs per group needed for "
         "(i) an analysis on all players and (ii) a triggered analysis (only players who reached the gate).\n\n"
         "(d) Say it to a PM.\n\n"
         "Follow-up: in the real test, can you define the trigger as 'played at least 30 rounds in the first 14 "
         "days'? Why or why not?",
  stub="# your code here",
  hint1="Signal: the treatment affects only a subset of users. Concept: dilution and triggered analysis. The "
        "overall effect is the triggered effect times the triggered share.",
  hint2="1. `trig = ctl.sum_gamerounds >= 30`; share = `trig.mean()`. 2. Overall effect = -0.02 * share. "
        "3. All-player n: `n_per_group(overall_baseline, overall_effect)`. 4. Triggered n: "
        "`n_per_group(triggered_baseline, -0.02)`, then installs = n / share.",
  solution='''ctl = cats[cats.version == "gate_30"]
trig = ctl.sum_gamerounds >= 30
share = trig.mean()
r7_trig, r7_not = ctl.retention_7[trig].mean(), ctl.retention_7[~trig].mean()
print(f"triggered share {share:.3f}, r7 triggered {r7_trig:.3f}, not {r7_not:.3f}")  # 0.373, 0.439, 0.043

effect_all = -0.02 * share
print(f"effect on all players: {effect_all * 100:.2f} pp")        # -0.75 pp

def n_per_group(p1, mde, alpha=0.05, power=0.8):
    p2 = p1 + mde
    z = stats.norm.ppf(1 - alpha / 2) + stats.norm.ppf(power)
    return int(np.ceil(z ** 2 * (p1 * (1 - p1) + p2 * (1 - p2)) / mde ** 2))

n_all = n_per_group(ctl.retention_7.mean(), effect_all)
n_trig = n_per_group(r7_trig, -0.02)
print("installs per group, all players:", n_all)                 # 42875
print("triggered players per group:", n_trig)                    # 9609
print("installs per group, triggered:", int(np.ceil(n_trig / share)))   # 25788''',
  why="Untriggered players add noise but no signal, so the effect is diluted to `0.373 * 2 = 0.75` pp while the "
      "variance stays almost the same. Analysing only triggered players needs about 40% fewer installs "
      "(25,788 vs 42,875 per group). The trigger must be something that happens *before* the treatment can act and "
      "is logged the same way in both arms, for example 'reached level 30' (the gate_40 players also pass level 30, "
      "they just do not meet a gate there)."
      + pm("Only about 37% of players ever reach the gate, so we will analyse those players; this cuts the needed "
           "installs by about 40% without hiding any effect, and we will still report the all-player number.",
           [("Trigger = 30 rounds in 14 days?", "No. Rounds played are measured *after* assignment and the gate "
             "itself can change them (gate_40 players may play more or fewer rounds). Conditioning on a post-treatment "
             "variable breaks randomisation. Use a trigger logged at the moment the two experiences start to differ "
             "(reaching level 30), recorded in both arms (counterfactual logging in control)."),
            ("What do you report?", "The triggered effect (most sensitive) and the diluted effect on all users "
             "(what the business gets): diluted = triggered effect * triggered share.")]),
  complexity="O(n) for the group means.",
  mistakes="Assuming dilution does not matter. Triggering on a metric the treatment can change. Forgetting to turn "
           "triggered users back into installs (divide by the share) when planning duration.",
  learn=["stats-ab-design", "stats-power-mde"])

# ---------------------------------------------------------------- Q3
q(ex, title="Design a test for a new comment ranking", minutes=7, kind="text",
  prompt="A short-video app wants to rank comments under each video by 'predicted reply probability' instead of "
         "by likes. The PM asks you to design the A/B test. In 6 to 8 bullet points cover: hypothesis, "
         "randomisation unit, primary metric, guardrails, sample size inputs, duration, and two risks specific to "
         "this feature. Then say the plan to the PM in two sentences.\n\n"
         "Follow-ups: (1) Comments are written by users who are themselves in the test. Is that a problem? "
         "(2) The PM wants to also change the comment box design in the same test. What do you say?",
  hint1="Signal: 'design the test'. Framework: hypothesis, unit, metrics (primary, secondary, guardrail), "
        "size and duration, risks (interference, novelty, logging).",
  hint2="1. Unit: user (not session, not comment view). 2. Primary: something the change should move directly "
        "(comment replies or comment engagement per user). 3. Guardrails: watch time, reports/blocks, latency. "
        "4. Size from baseline variance and an MDE the business cares about. 5. At least 1 to 2 full weeks. "
        "6. Risks: interference between users, novelty.",
  solution="""- **Hypothesis:** ranking by predicted reply probability raises conversation (replies) without hurting
  watch time or safety.
- **Unit:** user id (logged-in), so one person sees one ranking everywhere. Session or page-view units would let a
  user flip between rankings and would make the observations dependent.
- **Primary metric:** comment replies per user per day (or share of users who reply at least once). Secondary:
  comment likes, comment section opens, time in comments.
- **Guardrails:** total watch time per user, reports and blocks per 1,000 comments shown, comment-load latency,
  creator-side metrics (comments received).
- **Size:** baseline mean and standard deviation of replies per user from last month, MDE agreed with the PM
  (for example 2% relative), alpha 0.05, power 0.8. Replies per user is skewed, so plan for winsorizing or CUPED.
- **Duration:** at least 2 full weeks to cover weekly cycles and let novelty fade. Run an A/A check (or check SRM) on
  the first day.
- **Risk 1, interference:** treated users write replies that control users then see, so control is not clean
  (spillover usually shrinks the measured effect). Mitigation: cluster by community or video, or accept it and say
  the estimate is conservative.
- **Risk 2, ranking feedback loop:** comments that are ranked higher get more replies, which the model learns from.
  Train the model on data not produced by the treatment, or keep a holdout.

**Say it to a PM:** "We will randomise by user, judge the test on replies per user with watch time and reports as
safety checks, and run it for two full weeks; we need about N users per group to see a 2% change."

**Follow-ups:**
1. Yes, this is interference (a SUTVA violation). Replies created by treatment users show up for control users. If
   the effect is large, randomise at a cluster level (by creator or by video) so most conversations stay inside one
   arm, and compare.
2. Do not bundle it. If the metric moves you cannot tell which change caused it. Run two arms (ranking only, ranking
   plus new box) or a 2x2 factorial if traffic allows.""",
  why="Examiners grade structure: a clear unit, one primary metric tied to the hypothesis, guardrails that catch "
      "harm, and a sizing plan that names its inputs. Naming feature-specific risks (interference, feedback loops) "
      "is what makes the answer medium level instead of generic.",
  mistakes="Many primary metrics (multiple testing, no decision rule). Randomising by comment impression. Forgetting "
           "guardrails. Not mentioning duration in full weeks.",
  learn=["stats-ab-design", "stats-network-effects", "stats-case-framework"])

# ---------------------------------------------------------------- Q4 review
q(ex, title="What could this test detect?", minutes=5, review=True,
  prompt="The Cookie Cats test ended with 44,700 players in gate_30 and 45,489 in gate_40. Day-7 retention in "
         "control is about 19.0%.\n\n"
         "(a) With alpha = 0.05 (two-sided) and power 0.80, what is the minimum detectable effect (absolute, in pp) "
         "for day-7 retention? Use `MDE = (z_(1-alpha/2) + z_(power)) * sqrt(p(1-p)(1/n1 + 1/n2))`.\n\n"
         "(b) What was the power to detect a true drop of 0.82 pp (the size the test actually observed)?\n\n"
         "(c) Say it to a PM.\n\n"
         "Follow-up: a test with the same n shows a +0.3 pp change, p = 0.6. The PM says 'so there is no effect'. "
         "What do you answer?",
  stub="# your code here",
  hint1="Signal: n is fixed, find the smallest effect you could see. Method: invert the power formula (MDE).",
  hint2="1. `se = sqrt(p*(1-p)*(1/n1 + 1/n2))`. 2. `mde = (1.96 + 0.8416) * se`. "
        "3. Power for effect d: `norm.cdf(d/se - 1.96)` (ignore the tiny other tail).",
  solution='''n1, n2 = 44700, 45489
p = cats[cats.version == "gate_30"].retention_7.mean()
se = np.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
z_a, z_b = stats.norm.ppf(0.975), stats.norm.ppf(0.8)
print(f"SE of the difference: {se * 100:.3f} pp")              # 0.261 pp
print(f"MDE: {(z_a + z_b) * se * 100:.2f} pp")                  # 0.73 pp
d = 0.0082
power = stats.norm.cdf(d / se - z_a) + stats.norm.cdf(-d / se - z_a)
print(f"power for 0.82 pp: {power:.2f}")                        # 0.88''',
  why="With about 45,000 players per arm the standard error of the difference is 0.26 pp, so effects smaller than "
      "about 0.73 pp would often be missed. The observed 0.82 pp is just above that, and the power for an effect of "
      "that size is 0.88."
      + pm("This test was large enough to reliably catch a change of about three quarters of a point in 7-day "
           "retention; smaller changes could hide in the noise.",
           [("'No effect'?", "Not significant is not the same as no effect. Report the 95% CI: with SE 0.26 pp it is "
             "about +0.3 plus or minus 0.51 pp, so effects from -0.2 to +0.8 pp are all consistent with the data. "
             "If the business cares about effects that small, the test was underpowered for that question.")]),
  complexity="O(1).",
  mistakes="Using the per-group SE `sqrt(p(1-p)/n)` instead of the SE of the difference. Computing 'post-hoc power' "
           "from the observed effect and treating it as new evidence (it is a function of the p-value).",
  learn=["stats-power-mde"])

ex.save()
