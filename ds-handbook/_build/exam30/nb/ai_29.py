"""Day 29 AI: one full ML/AI exam round (breadth questions plus an end-to-end case: evaluate an AI feature)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam  # noqa: F401
from _ai_hard_common import start, ask

INTRO = """**Full exam round (60 minutes).** This notebook is one ML/AI round as a big-tech company runs it:
about 15 minutes of breadth questions (Q1 to Q3), then a 45-minute case on one AI feature, evaluated end to end
(Q4 to Q7). Set one timer for 60 minutes. Speak your answers out loud as if the examiner were listening:
state assumptions, give numbers, and name trade-offs. Do not open hints or solutions until the hour is over;
then grade each part (full, partial, missed) and log the misses."""

SETUP = r'''from scipy import stats
from sklearn.metrics import roc_auc_score

def _t(name, got, want):
    good = got == want
    print(("PASS " if good else "FAIL ") + name + f" -> {got!r}" + ("" if good else f"   expected {want!r}"))

g = np.random.default_rng(29)

# ---- SIMULATED offline eval: 300 videos, comment summaries from prompt v1 and prompt v2, scored by a validated judge
n_vid = 300
base = g.normal(3.2, 0.8, n_vid)                                  # how easy each video's comments are to summarise
score_v1 = np.clip(np.round(base + g.normal(0, 0.6, n_vid)), 1, 5).astype(int)            # judge score 1 to 5
score_v2 = np.clip(np.round(base + 0.15 + g.normal(0, 0.6, n_vid)), 1, 5).astype(int)
risk = g.random(n_vid)
halluc_v1 = (risk < 0.12) | (g.random(n_vid) < 0.02)              # summary states something no comment says
halluc_v2 = (risk < 0.07) | (g.random(n_vid) < 0.02)
offline = pd.DataFrame({"score_v1": score_v1, "score_v2": score_v2, "halluc_v1": halluc_v1, "halluc_v2": halluc_v2})

# ---- SIMULATED A/B test: one row per user (randomised by user), 14 days
n_user = 10000
def _arm(lift):
    sessions = g.poisson(g.gamma(2.0, 4.0, n_user)) + 1                     # sessions per user (heavy users exist)
    per_session = g.gamma(4.0, (300 + lift) / 4.0, n_user)                # user's typical seconds per session
    watch = np.array([g.gamma(4.0, m / 4.0, s).sum() for m, s in zip(per_session, sessions)])
    return sessions, watch
s_c, w_c = _arm(0.0)
s_t, w_t = _arm(9.0)
ab = pd.DataFrame({"group": ["control"] * n_user + ["treatment"] * n_user,
                   "sessions": np.r_[s_c, s_t], "watch_s": np.r_[w_c, w_t]})
print("offline", offline.shape, " ab", ab.shape)'''

ex = start(29, intro=INTRO, extra=SETUP, title="Day 29: AI and ML (full exam round)", data_note="""The case data
is **simulated** (an exam gives you numbers on the whiteboard; here you compute them):
`offline` (one row per video: judge scores 1 to 5 and a hallucination flag for summaries from prompt v1 and prompt
v2, same 300 videos) and `ab` (one row per user in a 14-day A/B test: `group`, `sessions`, `watch_s` total watch
seconds).""")

# ================================================================== part 1: breadth
ex.text("## Part 1: breadth (about 15 minutes)")

ask(ex, title="Boosting versus one deep tree", minutes=5, kind="text",
    prompt=""""Why does gradient boosting usually beat a single deep decision tree, and which three
hyperparameters would you tune first?" Answer in about one minute.""",
    hint1="""Signal: bias-variance trade-off for tree ensembles.""",
    hint2="""Deep tree: low bias, high variance. Boosting: many shallow trees fitted to residuals, shrinkage. Tune
learning rate with number of trees (early stopping), depth or leaves, subsampling or regularisation.""",
    solution="""A single deep tree has low bias but high variance: small changes in the data change the splits, and
it memorises noise. Gradient boosting adds many **shallow** trees, each fitted to the current errors (the
negative gradient of the loss), with a small **learning rate**, so each tree corrects a little: bias falls step
by step while each weak learner keeps variance low. Row and column subsampling add randomness that reduces
variance further, and L2 penalties on leaf values shrink extreme predictions.

**Tune first:** (1) learning rate together with the number of trees, using early stopping on a validation set;
(2) tree complexity (max depth or number of leaves, min samples per leaf); (3) subsampling of rows and columns
(and L2 regularisation). Trade-off: a lower learning rate needs more trees (slower training and inference) but
usually generalises better.""",
    why="""Examiners check that you can explain the mechanism (sequential residual fitting, shrinkage) with the
bias-variance vocabulary and tune in a sensible order.""",
    learn=["ai-trees-boosting", "ai-bias-variance"])

ask(ex, title="1% positives: which curve and which numbers?", minutes=4, kind="text",
    prompt="""""Our fraud model has ROC AUC 0.95 and positives are 1% of transactions. The business asks if it is
good. What do you show them instead, and why? And what does calibration add?\"""",
    hint1="""Signal: class imbalance makes ROC look good because the false positive rate divides by a huge number of
negatives. Use precision-recall and decisions at a threshold.""",
    hint2="""PR curve and average precision; precision and recall at the operating threshold, translated to counts
and money; calibration for expected cost and thresholds.""",
    solution="""ROC AUC measures ranking, and the false positive rate divides by the huge number of negatives, so even
a small FPR hides many false alarms. With 1% fraud, FPR 2% at recall 80% means 1.98 false alarms for every 0.8
caught fraud: precision about 29%. So show the **precision-recall curve** (average precision; the random baseline
is 0.01, not 0.5) and, more important, the **operating point**: at the chosen threshold, how many transactions
are blocked or reviewed per day, how many are fraud, how much money is saved, and how many good customers are
hurt.

**Calibration** means a score of 0.2 really corresponds to a 20% fraud rate. It lets you set thresholds by
expected cost (block if `p * loss > cost of friction`), compare or combine models, and keep thresholds valid
after retraining. Check it with a reliability curve or the Brier score; fix it with Platt scaling or isotonic
regression on held-out data.""",
    why="""It tests class-imbalance thinking and the habit of translating metrics into business decisions.""",
    learn=["ai-classification-metrics", "ai-features-imbalance"])

ask(ex, title="Compute AUC without sklearn", minutes=6,
    prompt="""Write `auc(y, s)`: the probability that a random positive gets a higher score than a random negative,
counting ties as one half. Make it `O(n log n)` (use ranks), not a double loop. Example:
`auc([0, 0, 1, 1], [0.1, 0.4, 0.35, 0.8])` is 0.75.""",
    stub='''def auc(y, s):
    # your code here
    pass''',
    tests='''_t("example", auc([0, 0, 1, 1], [0.1, 0.4, 0.35, 0.8]), 0.75)
_t("ties count half", auc([0, 1], [0.5, 0.5]), 0.5)
yy = g.random(2000) < 0.1; ss = g.normal(yy * 1.0, 1)
_t("matches sklearn", round(auc(yy.astype(int), ss) or 0, 10), round(roc_auc_score(yy, ss), 10))''',
    hint1="""Signal: AUC equals the Mann-Whitney U statistic divided by `n_pos * n_neg`.""",
    hint2="""1. Average ranks of all scores (`stats.rankdata`, ties get the mean rank). 2. Sum of positive ranks
minus `n_pos * (n_pos + 1) / 2` is U. 3. Divide by `n_pos * n_neg`.""",
    solution='''def auc(y, s):
    y = np.asarray(y).astype(bool)
    r = stats.rankdata(s)                       # average ranks handle ties as one half
    n_pos, n_neg = y.sum(), (~y).sum()
    u = r[y].sum() - n_pos * (n_pos + 1) / 2
    return float(u / (n_pos * n_neg))

print(auc([0, 0, 1, 1], [0.1, 0.4, 0.35, 0.8]))   # 0.75''',
    why="""Of the 4 (positive, negative) pairs, 3 are ordered correctly (0.35 is below 0.4), so AUC = 3/4. The rank
formula counts the same pairs in `O(n log n)`. Saying "AUC is the probability a random positive outranks a random
negative" is the interpretation examiners expect; it also explains why AUC ignores calibration and the class
ratio.""",
    complexity="O(n log n) for the ranking.",
    mistakes="A double loop (O(n^2)); ordinal ranks that break ties arbitrarily; forgetting the ties-as-half rule.",
    learn=["ai-classification-metrics"])

# ================================================================== part 2: the case
ex.text("""## Part 2: the case (about 45 minutes)

**Examiner:** "Under popular videos there are thousands of comments. We want an AI summary at the top of the
comment section: three short bullet points saying what people are discussing. You own the evaluation, end to end:
from defining success to the launch decision.\"""")

ask(ex, title="Define success before building anything", minutes=10, kind="text",
    prompt="""Start the case: clarify the goal, define the primary metric, secondary metrics and guardrails, and
list the main risks of this feature. What does "a good summary" mean, concretely?""",
    hint1="""Signal: product framing for a generative feature. Value for viewers, effect on creators and the
community, and the specific failure modes of summarisation (hallucination, toxicity amplification, misleading).""",
    hint2="""Clarify scope (which videos, languages, refresh). Primary: engagement quality for viewers (comment
section time or session watch time). Guardrails: comments posted, reports, latency, cost. Quality rubric:
faithful, representative, safe, concise.""",
    solution="""**Clarify:** which videos (above 500 comments?), which languages, how often the summary refreshes,
whether creators can turn it off, and whether it is shown to all viewers or on tap.

**Goal:** help viewers understand the conversation quickly, so they stay engaged with the video and community,
without harming the comment ecosystem.

**Metrics:**
- Primary (user level): watch time per session (the app's core value), with comment-section engagement as a
  secondary signal. Alternative primary for a narrower goal: comment-section opens per viewer.
- Secondary: summary expand or tap rate, scroll depth in comments, likes on comments.
- Guardrails: **comments posted per viewer** (a summary can replace reading and posting), reports and
  "inaccurate summary" feedback, creator opt-out rate, latency of the comment section, cost per 1,000 views.

**Quality rubric for one summary:** (1) faithful: every bullet is supported by actual comments (no
hallucination); (2) representative: covers the main themes in proportion, not just the loudest; (3) safe: does
not repeat hate, harassment or personal data, does not amplify misinformation from the comments; (4) concise and
in the viewer's language.

**Risks:** hallucinated claims about a creator (reputation and legal risk), amplifying toxic or false comments,
manipulation (brigading to steer the summary), staleness after the discussion changes, cost at the scale of
billions of views (cache one summary per video, refresh on comment growth).""",
    why="""A strong case answer starts with scope, the user value, a primary metric plus guardrails that capture the
specific way this feature can hurt (fewer comments posted), and a concrete quality definition that later becomes
the judge rubric.""",
    learn=["ai-ml-system-design", "ai-llm-evaluation"])

ask(ex, title="Offline: is prompt v2 better than v1?", minutes=10,
    prompt="""The team compared two prompt versions on the same 300 videos (`offline`). A validated LLM judge
(kappa 0.72 against experts on this rubric) scored each summary from 1 to 5 and flagged hallucinations.

1. Mean judge score for each version and a **paired** test of the difference (paired t-test and Wilcoxon
   signed-rank). Why paired?
2. Hallucination rates and a McNemar exact test (a binomial test on the discordant videos).
3. Your recommendation, and two things you would check before trusting it.""",
    stub='''# your code here''',
    hint1="""Signal: two systems evaluated on the same items. Use paired tests (each video is its own control):
paired t or Wilcoxon for scores, McNemar for paired binary outcomes.""",
    hint2="""1. `d = score_v2 - score_v1`; `stats.ttest_rel`, `stats.wilcoxon`. 2. Discordant: `b = v1 only`,
`c = v2 only`; `stats.binomtest(c, b + c, 0.5)`. 3. Compare with an unpaired test to see why pairing matters.""",
    solution='''o = offline
d = o.score_v2 - o.score_v1
print(f"mean score v1 {o.score_v1.mean():.3f}  v2 {o.score_v2.mean():.3f}  diff {d.mean():+.3f}")
print(f"paired t p = {stats.ttest_rel(o.score_v2, o.score_v1).pvalue:.4f}   "
      f"Wilcoxon p = {stats.wilcoxon(o.score_v2, o.score_v1).pvalue:.4f}   "
      f"unpaired t p = {stats.ttest_ind(o.score_v2, o.score_v1).pvalue:.4f}")
b = int((o.halluc_v1 & ~o.halluc_v2).sum())      # v1 hallucinated, v2 did not
c = int((~o.halluc_v1 & o.halluc_v2).sum())      # v2 hallucinated, v1 did not
print(f"hallucination v1 {o.halluc_v1.mean():.3f}  v2 {o.halluc_v2.mean():.3f}  discordant b={b} c={c}  "
      f"McNemar p = {stats.binomtest(c, b + c, 0.5).pvalue:.4f}")
# mean score v1 3.200  v2 3.303  diff +0.103
# paired t p = 0.0343   Wilcoxon p = 0.0335   unpaired t p = 0.2067
# hallucination v1 0.120  v2 0.090  discordant b=15 c=6  McNemar p = 0.0784''',
    why="""v2 scores 0.10 points higher on average (3.30 versus 3.20). The paired t-test gives p = 0.034 and the
Wilcoxon test p = 0.034, but an unpaired t-test on the same numbers gives p = 0.21. **Why paired:** videos differ a
lot in how hard they are to summarise; pairing removes that video-to-video variation, so the same data has much
more power. Hallucinations fall from 12.0% to 9.0%: v2 fixes 15 videos and breaks 6. McNemar p = 0.078: a good
sign, but not conclusive with 300 videos (only the 21 discordant videos carry information).

**Recommendation:** v2 is better on quality and probably on hallucinations; move it to the online test, because
hallucination is the higher-risk metric, and grow the offline set to about 1,000 videos (focused on hard,
high-comment videos) to confirm it. **Check first:** (1) re-validate the judge on v2 outputs (a prompt change can
change the style the judge rewards, for example longer bullets); (2) slice by language and video category: an
average gain can hide a loss in one language. Also check the length of v2 summaries (length bias, day 23).""",
    complexity="O(n).",
    mistakes="Unpaired tests on paired data (throws away the pairing and loses power); a t-test on ordinal 1 to 5 "
             "scores without a rank-based check; trusting the judge without re-validating on the new prompt's "
             "outputs (judges can prefer their own style).",
    learn=["ai-llm-evaluation", "stats-choosing-a-test"])

ask(ex, title="Online: read the A/B test correctly", minutes=12,
    prompt="""v2 ran in a 14-day A/B test, randomised by **user** (`ab`). The primary metric is watch time per session
= total watch seconds / total sessions in each arm.

1. Compute the metric per arm and the relative lift.
2. Write `ratio_se(y, x)`: the delta-method standard error of `mean(y) / mean(x)` over users:
   `var = (var_y / mx**2 - 2 * my * cov_xy / mx**3 + my**2 * var_x / mx**4) / n` (sample variances, `ddof=1`).
3. 95% CI and p-value for the difference with the delta method. Check the control arm's delta-method SE
   against a bootstrap over users (500 resamples, `np.random.default_rng(0)`).
4. Why would treating each session as an independent observation be wrong here?""",
    stub='''def ratio_se(y, x):
    # your code here
    pass''',
    tests='''y_, x_ = ab.watch_s[ab.group == "control"].values, ab.sessions[ab.group == "control"].values
bt = np.random.default_rng(0)
boot = []
for _ in range(300):
    i = bt.integers(0, len(y_), len(y_))
    boot.append(y_[i].sum() / x_[i].sum())
se = ratio_se(y_, x_) or 0
_t("delta SE within 15% of bootstrap SE", bool(abs(se - np.std(boot)) / np.std(boot) < 0.15), True)''',
    hint1="""Signal: a ratio metric whose denominator (sessions) is random and the randomisation unit (user) is not
the analysis unit (session). Use the delta method or a user-level bootstrap.""",
    hint2="""1. Per arm: `y = watch_s`, `x = sessions` per user. 2. `my, mx = y.mean(), x.mean()`, `np.var(.., ddof=1)`,
`np.cov(y, x)[0, 1]`. 3. Difference of two independent ratios: `se_diff = sqrt(se_t**2 + se_c**2)`, z-test.""",
    solution='''def ratio_se(y, x):
    y, x = np.asarray(y, float), np.asarray(x, float)
    n, my, mx = len(y), y.mean(), x.mean()
    vy, vx, cxy = y.var(ddof=1), x.var(ddof=1), np.cov(y, x)[0, 1]
    return float(np.sqrt((vy / mx**2 - 2 * my * cxy / mx**3 + my**2 * vx / mx**4) / n))

res = {}
for grp in ("control", "treatment"):
    a = ab[ab.group == grp]
    res[grp] = (a.watch_s.sum() / a.sessions.sum(), ratio_se(a.watch_s, a.sessions))
(rc, sc), (rt, st) = res["control"], res["treatment"]
diff, se = rt - rc, np.sqrt(sc**2 + st**2)
print(f"watch per session: control {rc:.1f} s, treatment {rt:.1f} s, lift {rt / rc - 1:+.2%}")
print(f"diff {diff:+.2f} s, 95% CI [{diff - 1.96 * se:+.2f}, {diff + 1.96 * se:+.2f}], p = {2 * stats.norm.sf(abs(diff / se)):.4f}")

bt = np.random.default_rng(0)
a = ab[ab.group == "control"]
y_, x_ = a.watch_s.values, a.sessions.values
boot = [(lambda i: y_[i].sum() / x_[i].sum())(bt.integers(0, len(y_), len(y_))) for _ in range(500)]
print(f"control SE: delta {sc:.3f}  bootstrap over users {np.std(boot):.3f}")
# watch per session: control 299.0 s, treatment 308.9 s, lift +3.29%
# diff +9.85 s, 95% CI [+4.41, +15.29], p = 0.0004
# control SE: delta 1.897  bootstrap over users 1.917''',
    why="""Watch time per session is 299.0 s in control and 308.9 s in treatment (+3.29%); the difference is +9.85 s with
a 95% CI of +4.41 to +15.29 s (p = 0.0004), so the effect is significant. The delta-method SE for the control arm
(1.897) matches the bootstrap over users (1.917): the formula is right, and it is much cheaper to compute on
billions of rows.

**Why not treat sessions as independent:** users were randomised, not sessions. Sessions of the same user are
correlated (a heavy watcher has long sessions every time), so there are far fewer independent units than
sessions. Treating sessions as units makes the SE too small and gives false wins. Also, the denominator (sessions)
is random and can itself change with the treatment; if the feature changes how many sessions people have, the
ratio can move without anyone watching more, so always report the numerator and the denominator separately
(total watch time per user and sessions per user) next to the ratio.""",
    complexity="O(n) for the delta method; O(B n) for the bootstrap.",
    mistakes="Treating sessions as independent when users were randomised (SE too small, false wins); averaging "
             "per-user ratios when the metric is defined as a ratio of totals (different metric, gives light "
             "users the same weight as heavy users); forgetting the covariance term.",
    learn=["stats-ratio-metrics", "ai-llm-evaluation"])

ask(ex, title="The launch decision and the hardest follow-ups", minutes=13, kind="text",
    prompt="""The results: watch time per session +3.3% (95% CI about +1.5% to +5.1%, see Q6); comments **posted** per
viewer **-4%** (significant); reports of inaccurate summaries 0.3 per 1,000 summary views; cost within budget.
Make the launch call and defend it. Then answer the examiner's follow-ups:

- "Creators complain the summary makes their comment section look negative. What do you do?"
- "How would you know the long-term effect, since the test only ran 14 days?"
- "Someone organises 500 accounts to post the same claim so it appears in the summary. How do you stop it?\"""",
    hint1="""Signal: conflicting metrics. Weigh the primary win against a guardrail loss that matters for the
ecosystem (comments are content for others). Think about mechanism, segments and mitigations, not just
ship or no-ship.""",
    hint2="""Decision: do not ship to everyone as is; understand why posting drops (substitution), test a variant
(summary collapsed, a "join the conversation" prompt, only on large threads). Long term: holdout. Creators:
representativeness and controls. Brigading: weight by unique, trusted accounts, dedupe, rate limits.""",
    solution="""**Decision: not a full launch yet; iterate and launch partially.** Watch time is the primary metric and
it improved, but comments posted are content and a community signal: a 4% drop reduces what other viewers read,
creators' feedback loop and future engagement. The likely mechanism is substitution: viewers read the summary
instead of scrolling and replying. Steps: (1) look at segments: is the drop concentrated on small threads,
certain languages, or viewers who expanded the summary? (2) test variants that keep the benefit and invite
participation: a collapsed summary, a "join the discussion" link to the top comment for each bullet, showing it
only on threads above 1,000 comments; (3) agree with the product lead on the trade-off rate (how much watch
time is worth one comment) before the next readout, so the decision is not made after seeing the data.

**Creators and negativity.** Check representativeness: compare the sentiment mix of the summary with the
sentiment mix of a sample of comments (weighted by likes), measure it per creator, and fix the prompt or the
comment sampling if the summary over-weights negative comments. Give creators controls (turn off, report a
summary) and keep personal attacks and harassment out of the input entirely (filter comments by the
moderation models before summarising).

**Long-term effect.** Keep a long-term holdout (for example 2 to 5% of users without the feature for months) to
measure retention and posting over time; check the effect by week in the test for novelty or learning effects;
use surrogate metrics validated on past experiments.

**Brigading.** Summarise from a sample of comments weighted by unique, trusted accounts (account age, history,
not part of a coordinated cluster), deduplicate near-identical comments, down-weight sudden bursts, run the same
integrity signals as for spam, and never let a claim into the summary just because many accounts repeat it;
for factual claims about people or events, require higher thresholds or avoid stating them.""",
    why="""The final part of a case tests judgment: you respect the guardrail, explain the mechanism, propose a
better variant and a pre-agreed decision rule, and handle long-term and adversarial questions with concrete
measurements.""",
    learn=["ai-ml-system-design", "ai-llm-evaluation", "stats-launch-decisions"])

ex.save()
