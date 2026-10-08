"""Day 23 AI (hard): LLM evaluation (focus), agents and classification metrics (review)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam  # noqa: F401
from _ai_hard_common import start, ask

SETUP = r'''from scipy import stats
from math import comb

def _t(name, got, want):
    good = got == want
    print(("PASS " if good else "FAIL ") + name + f" -> {got!r}" + ("" if good else f"   expected {want!r}"))

rng = np.random.default_rng(23)

# ---- 1) SIMULATED pointwise grades: 500 chatbot answers graded pass/fail by a human expert and by an LLM judge.
n = 500
human = (rng.random(n) < 0.80).astype(int)                       # 1 = pass. About 80% of answers are fine
judge = np.where(human == 1, rng.random(n) < 0.93,               # judge passes 93% of the good answers
                              rng.random(n) < 0.45).astype(int)  # ...and also 45% of the bad ones (too lenient)
grades = pd.DataFrame({"human": human, "judge": judge})

# ---- 2) SIMULATED pairwise judgments: 400 pairs (answer A, answer B), each shown to the judge in both orders.
m = 400
truth_A = rng.random(m) < 0.5                                    # human preference: True = A is better
len_A = rng.integers(40, 400, m); len_B = rng.integers(40, 400, m)   # answer lengths in tokens
def _judge_pick_first(first_better, len_first, len_second):
    """Simulated judge: follows quality, but likes the first slot and likes longer answers."""
    logit = 1.6 * np.where(first_better, 1, -1) + 0.6 + 0.006 * (len_first - len_second)
    return rng.random(len(logit)) < 1 / (1 + np.exp(-logit))
ab = _judge_pick_first(truth_A, len_A, len_B)                    # order (A, B): True = judge picked A
ba = _judge_pick_first(~truth_A, len_B, len_A)                   # order (B, A): True = judge picked B
pairs = pd.DataFrame({"human_A": truth_A, "len_A": len_A, "len_B": len_B,
                      "judge_AB_picks_A": ab, "judge_BA_picks_B": ba})

# ---- 3) SIMULATED A/B test of "AI reply suggestions" (one row per user, 14 days)
N = 20000
ctl = pd.DataFrame({"group": "control", "replied": rng.random(N) < 0.300})
trt = pd.DataFrame({"group": "treatment", "replied": rng.random(N) < 0.309})
users = pd.concat([ctl, trt], ignore_index=True)
lat_ctl = rng.lognormal(np.log(180), 0.35, 30000)               # ms to show the reply box, control
lat_trt = rng.lognormal(np.log(195), 0.45, 30000)               # treatment waits for the suggestion model
suggestions_shown = 52000                                        # suggestions shown in treatment
flagged_unsafe = 9                                               # confirmed unsafe suggestions among them
print("grades", grades.shape, "pairs", pairs.shape, "users", users.shape)'''

ex = start(23, extra=SETUP, data_note="""All data today is **simulated** in the setup cell (there is no public
dataset of LLM judge versus human labels that fits in a notebook). Every table says what one row is:
`grades` (one answer graded by a human and by an LLM judge), `pairs` (one pair of answers judged in both orders),
`users` plus latency arrays (an A/B test of an AI feature). Simulated data still behaves like real data: noisy,
with biases you must find.""")

# ------------------------------------------------------------------ Q1 kappa
ask(ex, title="Can we trust the LLM judge?", minutes=6,
    prompt="""Your team wants to replace human graders with an LLM judge. In `grades`, 1 = pass, 0 = fail.

1. Write `cohen_kappa(a, b)` from scratch: `kappa = (p_o - p_e) / (1 - p_e)`, where `p_o` is the observed
   agreement and `p_e` the agreement expected by chance from the two raters' label rates. Check it against
   `sklearn.metrics.cohen_kappa_score`.
2. Report raw agreement and kappa for the judge. Then do the same for a lazy "judge" that passes everything.
3. Treat "fail" as the positive class: what are the judge's precision and recall for catching bad answers?
4. One sentence for the team: is the judge good enough to replace humans?""",
    stub='''def cohen_kappa(a, b):
    # your code here
    pass

# then use it on grades.human and grades.judge''',
    tests='''from sklearn.metrics import cohen_kappa_score
_t("matches sklearn", round(cohen_kappa(grades.human, grades.judge) or 0, 6), round(cohen_kappa_score(grades.human, grades.judge), 6))
_t("perfect", cohen_kappa([0, 1, 1, 0], [0, 1, 1, 0]), 1.0)
_t("lazy judge", cohen_kappa([0, 1, 1, 1], [1, 1, 1, 1]), 0.0)''',
    hint1="""Signal: two raters, categorical labels, and one label is much more common. Raw agreement is
inflated by the majority class; Cohen's kappa corrects for chance agreement. The "catching bad answers" part is
precision and recall with fail as the positive class.""",
    hint2="""1. `p_o = mean(a == b)`. 2. `p_e = sum over labels c of P(a = c) * P(b = c)`.
3. Lazy judge: `p_o` equals the pass rate, and `p_e` equals it too, so kappa is 0.
4. Fail recall = caught fails / all human fails; fail precision = true fails / all judge fails.""",
    solution='''from sklearn.metrics import cohen_kappa_score, precision_score, recall_score

def cohen_kappa(a, b):
    a, b = np.asarray(a), np.asarray(b)
    p_o = np.mean(a == b)
    labels = np.union1d(a, b)
    p_e = sum(np.mean(a == c) * np.mean(b == c) for c in labels)
    return float((p_o - p_e) / (1 - p_e)) if p_e < 1 else 1.0

h, j = grades.human.values, grades.judge.values
print("human pass rate", h.mean().round(3), " judge pass rate", j.mean().round(3))
print("agreement", np.mean(h == j).round(3), " kappa", round(cohen_kappa(h, j), 3),
      " sklearn", round(cohen_kappa_score(h, j), 3))
lazy = np.ones_like(h)
print("lazy judge: agreement", np.mean(h == lazy).round(3), " kappa", round(cohen_kappa(h, lazy), 3))
fail_h, fail_j = 1 - h, 1 - j
print("fail precision", round(precision_score(fail_h, fail_j), 3), " fail recall", round(recall_score(fail_h, fail_j), 3))
# human pass rate 0.798  judge pass rate 0.842
# agreement 0.852  kappa 0.5  sklearn 0.5
# lazy judge: agreement 0.798  kappa 0.0
# fail precision 0.671  fail recall 0.525''',
    why="""Raw agreement (85.2%) looks good, but a judge that passes everything already gets 79.8% because
most answers are fine. Kappa removes that chance agreement: 0.50 is only "moderate" (a common rule of thumb:
above 0.6 substantial, above 0.8 near-human). The fail-class view tells the real story: the judge catches only
52.5% of bad answers, and a third of its "fail" verdicts (precision 0.671) are good answers. It is too lenient.

**For the team:** "The judge agrees with experts 85% of the time, but most of that is easy passes; it misses about
half of the bad answers, so it can rank model versions but cannot replace human review of failures yet."

**Deep follow-ups.** *What is a good target?* Compare with human-human kappa on the same items; a judge cannot be
expected to beat the agreement between two experts. *How do you improve it?* A rubric with explicit fail criteria,
few-shot examples of borderline fails, ask for reasoning before the verdict, a stronger judge model, or
calibrate a threshold on a judge score instead of a binary verdict. *How many labels to validate?* Enough fails:
with 20% fails, 500 items give only about 100 fails, so the fail recall has a CI of about plus or minus 10
points. *Ordinal labels (1 to 5)?* Use weighted kappa (quadratic weights) so near-misses count partly.""",
    complexity="O(n).",
    mistakes="Reporting only raw agreement; computing kappa on the pass class only; treating kappa 0.5 as "
             "\"half right\" (it means halfway between chance and perfect); validating the judge on a different "
             "mix of answers than production (kappa depends on prevalence).",
    learn=["ai-llm-evaluation", "ai-classification-metrics"])

# ------------------------------------------------------------------ Q2 position bias
ask(ex, title="Does the order of the two answers change the verdict?", minutes=6,
    prompt="""In `pairs`, each pair was shown to the judge twice: as (A, B) and as (B, A).
`judge_AB_picks_A` is True when the judge chose A in the first order; `judge_BA_picks_B` is True when it chose B
in the swapped order (that is, it picked the answer in the first slot both times if both are True).

1. How often does the judge pick the first slot (pool both orders)? Is that different from 50% (binomial test)?
2. Consistency: in what share of pairs does the judge pick the same answer in both orders?
3. Accuracy against `human_A`: using only order (A, B), versus using only the pairs where both orders agree.
4. What would you ship as the evaluation protocol?""",
    stub='''# your code here''',
    hint1="""Signal: an LLM judge that sees answers in a fixed order. This is position bias; the standard test is to
swap the order and check consistency.""",
    hint2="""1. First-slot picks = `judge_AB_picks_A` plus `judge_BA_picks_B`, out of `2 * m` judgments.
2. Consistent when the judge picks A in order 1 AND does not pick B in order 2: `ab & ~ba` or `~ab & ba`.
3. Compare `ab == human_A` with the same check restricted to consistent pairs (and report their share).""",
    solution='''ab, ba, hA = pairs.judge_AB_picks_A.values, pairs.judge_BA_picks_B.values, pairs.human_A.values
first = ab.sum() + ba.sum()
total = 2 * len(pairs)
p = stats.binomtest(int(first), total, 0.5).pvalue
print("first slot picked", round(first / total, 3), " binomial p =", f"{p:.1e}")
consistent = ab != ba                         # picks A first time and A (not B) second time, or B both times
print("consistent share", round(consistent.mean(), 3))
print("accuracy, order AB only", round(np.mean(ab == hA), 3))
judge_A_both = ab & ~ba
print("accuracy on consistent pairs", round(np.mean(judge_A_both[consistent] == hA[consistent]), 3))
# first slot picked 0.581  binomial p = 4.9e-06
# consistent share 0.712
# accuracy, order AB only 0.785
# accuracy on consistent pairs 0.916''',
    why="""With no bias, the first slot would win 50% of the time; here it wins 58.1% (p = 4.9e-06), and the
judge flips its verdict on 28.8% of pairs when you swap the order. Accuracy from one order is 78.5%, while on the
71.2% of pairs where both orders agree it is 91.6%. Inconsistent verdicts are mostly noise from close pairs.

**Protocol to ship:** always judge both orders. Count a win only when both orders agree; count a flip as a tie
(or average the two probabilities if the judge gives scores). Report the tie rate next to the win rate, because
a model change that makes many pairs close shows up as ties, not as wins. Randomise the order in single-pass
evaluations so the bias at least cancels between models. **Follow-up: "is position bias the only one?"** No:
also verbosity (next question), self-preference (a judge favours outputs from its own model family) and
sensitivity to formatting such as markdown and lists. Validate against human labels whenever you change the judge
model or the prompt.""",
    complexity="O(m).",
    mistakes="Testing only one order (the bias is invisible); dropping inconsistent pairs without reporting how "
             "many (selection bias: they are the hard, close pairs); calling the bias small because accuracy "
             "looks fine.",
    learn=["ai-llm-evaluation"])

# ------------------------------------------------------------------ Q3 length bias
ask(ex, title="Does the judge reward longer answers?", minutes=6,
    prompt="""Use the order (A, B) judgments in `pairs`. The human preference `human_A` is the truth.

1. How often does the judge pick the longer answer? How often do the humans?
2. Look only at pairs where the human preferred the **shorter** answer. How often does the judge agree?
   Compare with pairs where the human preferred the longer one.
3. Fit a logistic regression: judge picks A ~ human prefers A + (len_A - len_B) / 100. Interpret the length
   coefficient as an odds ratio per 100 extra tokens.
4. How would you fix or control for this in an eval and in an online metric?""",
    stub='''# your code here''',
    hint1="""Signal: a confounded preference. Longer answers might be better, so you must condition on the
human verdict (stratify or regress) to separate "longer" from "better". This is verbosity (length) bias.""",
    hint2="""1. `longer_A = len_A > len_B`; judge picks longer = `ab == longer_A`.
2. Group by whether the human prefers the longer answer, compute judge agreement in each group.
3. `statsmodels.Logit(ab, X)` with `X = [const, human_A, dlen/100]`; `exp(coef)` is the odds ratio.""",
    solution='''import statsmodels.api as sm
ab, hA = pairs.judge_AB_picks_A.values, pairs.human_A.values
longer_A = (pairs.len_A > pairs.len_B).values
print("judge picks longer", round(np.mean(ab == longer_A), 3), " human picks longer", round(np.mean(hA == longer_A), 3))
human_longer = hA == longer_A
agree = ab == hA
print("judge agrees when human prefers SHORTER", round(agree[~human_longer].mean(), 3), f"(n={(~human_longer).sum()})")
print("judge agrees when human prefers LONGER ", round(agree[human_longer].mean(), 3), f"(n={human_longer.sum()})")
X = sm.add_constant(np.column_stack([hA.astype(float), (pairs.len_A - pairs.len_B).values / 100]))
fit = sm.Logit(ab.astype(float), X).fit(disp=0)
print("coef", fit.params.round(3), " odds ratio per 100 tokens", round(np.exp(fit.params[2]), 2),
      " p =", f"{fit.pvalues[2]:.1e}")
# judge picks longer 0.595  human picks longer 0.49
# judge agrees when human prefers SHORTER 0.686 (n=204)
# judge agrees when human prefers LONGER  0.888 (n=196)
# coef [-0.981  3.217  0.594]  odds ratio per 100 tokens 1.81  p = 1.9e-09''',
    why="""Humans pick the longer answer 49% of the time (length is not quality here), but the judge picks it
59.5% of the time. When the human prefers the shorter answer, the judge agrees only 68.6% of the time, versus
88.8% when the human prefers the longer one. Holding the human verdict fixed, each extra 100 tokens multiplies the
odds that the judge picks A by 1.81 (p = 1.9e-09). (The intercept -0.981 is the log-odds of picking A when the
human prefers B, with equal lengths.)

**Fixes.** In the prompt: tell the judge that length is not a criterion and to penalise padding. In the
analysis: report win rates stratified by length difference, or a length-controlled win rate (fit this same
regression and read the quality effect at zero length difference, the idea behind length-controlled
AlpacaEval). In training: if the judge feeds a reward model (RLHF), length bias becomes reward hacking, and the
policy learns to write longer answers. **Online:** watch answer length as a metric next to user satisfaction;
if satisfaction does not move while length grows, the judge is being gamed.""",
    complexity="O(m) plus a small logistic fit.",
    mistakes="Comparing judge and human length preference without conditioning on quality (longer may truly be "
             "better); controlling for length by truncating answers (changes the content); forgetting that the "
             "intercept here also carries the position bias from Q2.",
    learn=["ai-llm-evaluation", "ai-logistic-regression"])

# ------------------------------------------------------------------ Q4 A/B test with guardrails
ask(ex, title="Launch the AI reply suggestions?", minutes=8,
    prompt="""A 14-day A/B test of AI reply suggestions in a comment section (simulated, see setup). The
pre-registered plan:

- **Primary metric:** share of users who replied at least once (`users.replied`). Ship only if the lift is
  positive and significant at 5%.
- **Latency guardrail:** p95 time to show the reply box may rise by at most 60 ms (95% bootstrap CI upper bound
  of the p95 difference must be below 60). Arrays `lat_ctl`, `lat_trt`.
- **Safety guardrail:** the unsafe suggestion rate must be below 3 per 10,000 with 95% confidence
  (upper bound of an exact Clopper-Pearson interval). `flagged_unsafe` out of `suggestions_shown`.
- **Cost:** each suggestion uses 350 input and 40 output tokens. Assume illustrative prices of 0.15 USD per
  million input tokens and 0.60 USD per million output tokens. Report the cost per extra replying user.

Compute each piece and make the call.""",
    stub='''# your code here''',
    hint1="""Signal: one primary metric plus several guardrails with different statistics: a two-proportion z-test,
a bootstrap CI for a percentile difference, an exact binomial bound for a rare event, and unit economics.""",
    hint2="""1. z-test on `replied` by group; lift and 95% CI. 2. Bootstrap 1,000 resamples of each latency array,
`np.percentile(.., 95)` difference. 3. `stats.beta.ppf(0.95, k + 1, n - k)` is the one-sided upper bound.
4. Cost per suggestion times suggestions, divided by the extra repliers `(p_t - p_c) * N`.""",
    solution='''from statsmodels.stats.proportion import proportions_ztest
g = users.groupby("group").replied.agg(["sum", "count"])
pc, pt = g.loc["control", "sum"] / g.loc["control", "count"], g.loc["treatment", "sum"] / g.loc["treatment", "count"]
z, p = proportions_ztest(g.loc[["treatment", "control"], "sum"], g.loc[["treatment", "control"], "count"])
se = np.sqrt(pc * (1 - pc) / N + pt * (1 - pt) / N)
print(f"reply rate control {pc:.4f} treatment {pt:.4f} lift {pt - pc:+.4f} "
      f"CI [{pt - pc - 1.96 * se:+.4f}, {pt - pc + 1.96 * se:+.4f}] p = {p:.1e}")

b = np.random.default_rng(0)
diffs = [np.percentile(b.choice(lat_trt, lat_trt.size), 95) - np.percentile(b.choice(lat_ctl, lat_ctl.size), 95)
         for _ in range(1000)]
print(f"p95 latency diff {np.percentile(lat_trt, 95) - np.percentile(lat_ctl, 95):.1f} ms, "
      f"95% CI [{np.percentile(diffs, 2.5):.1f}, {np.percentile(diffs, 97.5):.1f}]")

upper = stats.beta.ppf(0.95, flagged_unsafe + 1, suggestions_shown - flagged_unsafe)
print(f"unsafe per 10k: {1e4 * flagged_unsafe / suggestions_shown:.2f}, one-sided 95% upper bound {1e4 * upper:.2f}")

cost_one = 350 * 0.15 / 1e6 + 40 * 0.60 / 1e6
extra_users = (pt - pc) * N
print(f"cost per suggestion {cost_one:.6f} USD, test cost {cost_one * suggestions_shown:.2f} USD, "
      f"per extra replying user {cost_one * suggestions_shown / extra_users:.3f} USD")
# reply rate control 0.3021 treatment 0.3184 lift +0.0163 CI [+0.0072, +0.0253] p = 4.4e-04
# p95 latency diff 89.4 ms, 95% CI [83.8, 93.8]
# unsafe per 10k: 1.73, one-sided 95% upper bound 3.02
# cost per suggestion 0.000077 USD, test cost 3.98 USD, per extra replying user 0.012 USD''',
    why="""**Read-out.** Primary: the reply rate rises from 30.2% to 31.8% (+1.6 points, CI +0.7 to +2.5, p below
0.001): a clear win. Latency: p95 rises by 89 ms (CI 84 to 94), above the 60 ms guardrail, so the guardrail
fails. Safety: 1.73 unsafe per 10k observed, but the 95% upper bound is 3.02, just above 3: we cannot yet
claim the rate is below the limit. Cost: about 0.012 USD per extra replying user, cheap.

**Decision:** do not launch as is, even though the primary metric won, because the plan said guardrails are
pass/fail. Next steps: (1) fix latency without hurting the effect: show the reply box immediately and stream
or insert the suggestion when ready, use a smaller or quantized model, cache frequent contexts; (2) add a
stricter safety filter and keep collecting data: at the same observed rate, about 26,000 more suggestions
(78,000 in total, 14 events) would bring the upper bound to about 2.8 per 10k; (3) rerun a short confirmation test.

**Deep follow-ups.** *Why a bootstrap for p95?* No simple formula for the standard error of a percentile
difference; the bootstrap is the standard tool (resample users or sessions, not requests, if requests are
clustered). *Why Clopper-Pearson?* With 9 events the normal approximation is poor; with 0 events use the rule
of three (upper bound about `3 / n`). *Novelty effect?* Check the lift by week; AI features often get curiosity
clicks early. *Network effect?* More replies cause more notifications for the authors in control too, so user
randomisation may underestimate the effect; consider cluster or post-level randomisation.""",
    complexity="O(B * n) for the bootstrap (B = 1,000).",
    mistakes="Testing p95 latency with a t-test on means (the tail moves, not the mean); calling 0 to 3 per 10k "
             "\"safe\" from the point estimate alone; reporting cost per suggestion instead of per unit of value; "
             "changing the decision rule after seeing the data.",
    learn=["ai-llm-evaluation", "ai-safety-cost"])

# ------------------------------------------------------------------ Q5 review: pass@k
ask(ex, title="Report agent reliability from repeated runs", minutes=5, review=True,
    prompt="""You ran an agent `n = 10` times on each of 5 tasks. Correct runs per task: `c = [10, 9, 6, 2, 0]`.

1. Write `pass_at_k(n, c, k)`: the chance that at least one of `k` runs drawn without replacement from the `n`
   is correct, `1 - C(n - c, k) / C(n, k)`.
2. Write `pass_all_k(n, c, k)`: the chance that all `k` drawn runs are correct, `C(c, k) / C(n, k)`.
3. Average both over the 5 tasks for `k = 1` and `k = 5`. Which one should a product team look at for an agent
   that acts on a user's behalf?""",
    stub='''def pass_at_k(n, c, k):
    # your code here
    pass

def pass_all_k(n, c, k):
    # your code here
    pass''',
    tests='''_t("pass@1 equals c/n", pass_at_k(10, 6, 1), 0.6)
_t("pass@5 with c=2", round(pass_at_k(10, 2, 5) or 0, 4), 0.7778)
_t("pass@k when c=0", pass_at_k(10, 0, 5), 0.0)
_t("pass^5 with c=9", round(pass_all_k(10, 9, 5) or 0, 4), 0.5)
_t("pass^5 with c=2", pass_all_k(10, 2, 5), 0.0)''',
    hint1="""Signal: several samples per task and a k-attempt metric. Use the unbiased combinatorial estimator
from the HumanEval paper (pass@k), and its mirror for reliability (pass^k: all k succeed).""",
    hint2="""1. `math.comb(a, b)` is 0 when `b > a`, which handles the edge cases for you.
2. Compute the two per task, then average across tasks.""",
    solution='''from math import comb

def pass_at_k(n, c, k):
    return 1 - comb(n - c, k) / comb(n, k)

def pass_all_k(n, c, k):
    return comb(c, k) / comb(n, k)

c_list = [10, 9, 6, 2, 0]
for k in (1, 5):
    a = np.mean([pass_at_k(10, c, k) for c in c_list])
    b = np.mean([pass_all_k(10, c, k) for c in c_list])
    print(f"k={k}: pass@k {a:.3f}  pass^k {b:.3f}")
# k=1: pass@k 0.540  pass^k 0.540
# k=5: pass@k 0.756  pass^k 0.305''',
    why="""With one try both metrics equal the average success rate (54%). With 5 tries, pass@5 rises to 75.6%
("can it ever solve it?", useful when a human or a test picks the best of k, like code generation with unit
tests), while pass^5 drops to 30.5% ("does it solve it every time?"). An agent that acts for users gets one shot
each time and is used again and again, so **reliability (pass^k) is the product metric**; a big gap between
pass@k and pass^k means the agent is capable but inconsistent, which points to sampling temperature, flaky tools
or ambiguous prompts. Task 4 (2 of 10) shows why: pass@5 is 0.78 but pass^5 is 0.""",
    complexity="O(1) per task with math.comb.",
    mistakes="Estimating pass@k as `1 - (1 - c/n) ** k` (biased, assumes sampling with replacement); "
             "reporting pass@k for a product where users get one try; too few runs per task (n = 1 tells you "
             "nothing about variance).",
    learn=["ai-agents", "ai-llm-evaluation"])

ex.save()
