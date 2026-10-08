import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam  # noqa: F401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _stats_hard_common import start, shown, PM

# Day 30 stats: light final check (3 short mixed questions) plus the day-before checklist.

INTRO = ("**Light day.** Three short questions (about 15 minutes) to check that the core tools come back fast, "
         "then the checklist for the day before the exam. No new material today. If something here feels "
         "slow, read the matching handbook section once and stop there. Rest is part of the plan.")

ex = start(30, intro=INTRO, extra="from scipy.stats import norm",
           data_doc="No dataset today. Everything fits in a few lines of numpy and scipy.")

# ---------------------------------------------------------------- Q1 sample size by hand
q1 = '''p1, p2 = 0.10, 0.105                        # baseline 10%, MDE 5% relative
za, zb = norm.ppf(0.975), norm.ppf(0.80)
n = (za + zb) ** 2 * (p1 * (1 - p1) + p2 * (1 - p2)) / (p2 - p1) ** 2
print(f"exact-ish: {n:,.0f} per group; rule of thumb 16 p(1-p) / delta^2: {16 * p1 * (1 - p1) / (p2 - p1) ** 2:,.0f}")
print(f"with 20,000 eligible users a day split 50/50: {2 * n / 20_000:.1f} days -> run 7 days (a full week)")
print(f"MDE if we only get 20,000 users per group: {(za + zb) * np.sqrt(2 * p1 * (1 - p1) / 20_000) / p1:.1%} relative")
# exact-ish: 57,760 per group; rule of thumb 16 p(1-p) / delta^2: 57,600
# with 20,000 eligible users a day split 50/50: 5.8 days -> run 7 days (a full week)
# MDE if we only get 20,000 users per group: 8.4% relative'''
ex.q("Five-minute sizing", minutes=5, kind="python", level="medium",
     prompt="Checkout conversion is 10%. The PM wants to detect a **5% relative** lift (to 10.5%), two-sided "
            "alpha 0.05, power 80%. 20,000 eligible users arrive per day.\n\n"
            "1. Users per group? Check your answer with the rule of thumb `16 p(1-p) / delta^2`.\n"
            "2. How many days should the test run?\n"
            "3. If the PM can only give 20,000 users per group, what lift can the test detect?" +
            PM + "explain the duration in one sentence.",
     hint1="Signal: 'how many users / how long'. Method: power and MDE for two proportions.",
     hint2="1. `n = (z_0.975 + z_0.8)^2 (p1 q1 + p2 q2) / (p2 - p1)^2`. 2. Days = `2n / daily users`, rounded "
           "up to whole weeks. 3. Invert: `MDE = (z_0.975 + z_0.8) sqrt(2 p q / n)`.",
     solution=q1,
     why="About 57.8k users per group (the rule of thumb gives 57.6k because `(1.96 + 0.84)^2` is about 7.85, so "
         "`2 x 7.85` is about 16). That is about 6 days of traffic, but tests should cover whole weeks to include "
         "weekday and weekend behaviour, so run 7 days (14 if novelty is a concern). With only 20k per group the "
         "smallest detectable lift is about 8.4% relative." + PM + "\"To reliably see a 5% lift we need about "
         "58,000 users per group, which is 6 days of traffic, so we run one full week to cover weekends.\"",
     mistakes="Using the relative MDE (0.05) as delta. Stopping on day 6 in the middle of a week. Forgetting that "
              "the variance uses p near 0.10, not 0.5.",
     learn=["stats-power-mde", "stats-ab-design"])
shown(ex)

# ---------------------------------------------------------------- Q2 rapid-fire
ex.q("Rapid fire: one line each", minutes=5, kind="text", level="medium",
     prompt="Answer each in one sentence, out loud, in under 20 seconds:\n\n"
            "1. The first thing you check when a metric drops.\n"
            "2. What a p-value is (and is not).\n"
            "3. When you randomize clusters instead of users.\n"
            "4. Why peeking at a fixed-horizon test is a problem.\n"
            "5. The condition a CUPED covariate must meet.\n"
            "6. What Simpson's paradox is, in one example.\n"
            "7. How you tell a novelty effect from a learning effect." +
            PM + "item 2, in words a PM would use.",
     hint1="Signal: recall. Method: one definition plus one consequence per item.",
     hint2="Data quality first; P(data this extreme | no effect); interference; repeated tests inflate false "
           "wins; measured before treatment; the mix flips the direction; new users and the time trend.",
     solution="""1. **Metric drop:** is the data right (pipeline, logging, definition change), then is it unusual
compared with normal variation and the calendar, before hunting causes.
2. **p-value:** the probability of data at least this extreme if there were no effect; it is **not** the
probability that the effect is real or that the null is true.
3. **Cluster randomization:** when units interfere (friends, shared supply or budget), so you randomize groups that
contain the interaction, and analyze at the cluster level.
4. **Peeking:** every look is another chance for noise to cross the threshold; daily looks with 1.96 can push false
wins from 5% to about 25%, so use a sequential design.
5. **CUPED:** the covariate must be measured before randomization (unaffected by treatment) and correlated with the
metric; the variance falls by about `rho^2`.
6. **Simpson's paradox:** a trend in every subgroup reverses in the total because the groups have different mixes;
for example phone customers churn more overall but less inside DSL, because all Fiber customers have phone.
7. **Novelty vs learning:** novelty decays over time and is absent for new users; learning grows over time. Plot the
lift by day since first exposure, and compare new and existing users.

**Say it to a PM:** "The p-value tells us how surprising this result would be if the change did nothing; a small
value means 'unlikely to be pure luck', not 'a 95% chance that it works'.\"""",
     why="Fast, exact definitions are the foundation examiners test before case questions; each answer here "
         "has a definition and a consequence.",
     learn=["stats-hypothesis-tests", "stats-ab-pitfalls", "stats-metric-drop"])

# ---------------------------------------------------------------- Q3 30-second readout
ex.q("The 30-second readout", minutes=5, kind="text", level="medium",
     prompt="You get this readout of a 2-week test of a new comment ranking (user-level randomization, SRM check "
            "passed):\n\n"
            "| Metric | Change | 95% CI |\n|---|---|---|\n"
            "| Comments per user (primary) | +3.1% | +1.9% to +4.3% |\n"
            "| Watch time per user | +0.1% | -0.3% to +0.5% |\n"
            "| Reports per 1k comments (guardrail) | -6.0% | -11.0% to -1.0% |\n"
            "| Day-7 retention | +0.2% | -0.4% to +0.8% |\n\n"
            "Write the 30-second summary for the PM: result, confidence, risks, decision." +
            PM + "this whole question is the PM sentence; keep it under 60 words.",
     hint1="Signal: a clean readout. Method: lead with the decision, then the main number with its range, then "
           "guardrails and one risk.",
     hint2="1. Primary up and clearly positive. 2. Guardrail improved. 3. Watch time and retention flat. 4. Risk: "
           "novelty over 2 weeks. 5. Decision: launch with a holdout.",
     solution="""**Model answer (about 55 words):** "I recommend launching. Comments per user rose 3.1%, and we are
confident it is between 2% and 4%. Reports per thousand comments fell 6%, so the extra comments are not toxic.
Watch time and retention did not change. The main risk is novelty after only two weeks, so we keep a 5% holdout
for a month to confirm."

**Why it works:** decision first, one number with its range in plain words, the guardrail that answers the obvious
worry, the neutral metrics in one sentence, and a concrete plan for the remaining risk.""",
     why="Examiners often end a case with 'summarize for the PM'. A short, ordered summary with numbers and a "
         "decision shows judgement more than any formula.",
     learn=["stats-launch-decisions", "stats-case-framework"])

ex.text("""---
## Checklist for the day before the exam

**Morning (60 to 90 minutes, then stop)**
- Redo only the open items in your mistake log, one pass, no new topics.
- Read the cheat sheets once: [stats tests](%(site)s#cheat-stats-tests), [A/B testing](%(site)s#cheat-ab-testing), [exam day](%(site)s#cheat-exam-day).
- Say the case framework out loud once: clarify, goal, metrics (primary, drivers, guardrails), design, analysis, decision.
- Say three formulas out loud: `SE = sqrt(p(1-p)/n)`, `n = 16 sd^2 / delta^2` per group, CUPED variance times `1 - rho^2`.

**Stories and questions**
- Two project stories in 90 seconds each: problem, what you did, the number that changed, what you learned.
- One story about a wrong analysis you caught (or made) and how you fixed it.
- Three questions for the examiner about how the team uses experiments and metrics.

**Logistics**
- Check the time zone, the link, camera, microphone and a quiet room; test the coding pad if there is one.
- Prepare paper and pen for formulas and a calculator you are allowed to use.
- Water, a light meal before, and a fixed stop time tonight.

**In the exam**
- Repeat the question in your own words and ask one or two clarifying questions before you compute.
- Name the method and its assumption before the number; give the number with its range; end with a decision.
- If you get stuck, say what you would check next. A clear partial plan scores better than silence.
- Every answer ends with the sentence you would say to a PM.

**Evening:** no studying after dinner. Sleep is worth more than one more topic.""" % {"site": __import__("libx").SITE})

ex.save()
