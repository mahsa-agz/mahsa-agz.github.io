"""Day 25 AI (hard): ML system design case 2, harmful content moderation (focus); features and imbalance (review)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam  # noqa: F401
from _ai_hard_common import start, ask

SETUP = r'''from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, average_precision_score, brier_score_loss

def _t(name, got, want):
    good = got == want
    print(("PASS " if good else "FAIL ") + name + f" -> {got!r}" + ("" if good else f"   expected {want!r}"))

# ---- real data: SMS spam as a stand-in for "harmful posts" (spam = the violating class)
y_all = (sms.label == "spam").astype(int).values
txt_tmp, txt_te, y_tmp, y_te = train_test_split(sms.text, y_all, test_size=0.2, stratify=y_all, random_state=0)
txt_tr, txt_va, y_tr, y_va = train_test_split(txt_tmp, y_tmp, test_size=0.25, stratify=y_tmp, random_state=0)
vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)
X_tr, X_va, X_te = vec.fit_transform(txt_tr), vec.transform(txt_va), vec.transform(txt_te)
print("train / valid / test:", X_tr.shape[0], X_va.shape[0], X_te.shape[0], " spam rate", y_all.mean().round(4))

# ---- SIMULATED: one day of 1,000,000 posts with a classifier score; true labels are hidden from you
_rng = np.random.default_rng(25)
N_POSTS = 1_000_000
_truth = _rng.random(N_POSTS) < 0.004                               # true prevalence is unknown to the team
post_score = np.clip(np.where(_truth, _rng.beta(5, 2, N_POSTS), _rng.beta(1, 12, N_POSTS)), 0, 1)
def human_label(idx):
    """Pretend human review: returns the true labels of the posts at positions idx (costs money!)."""
    return _truth[idx].astype(int)'''

ex = start(25, loads=("sms",), extra=SETUP, data_note="""- `sms` (UCI SMS Spam Collection, real, 5,572
messages, 13.4% spam): `label` (ham/spam), `text`. We use spam as a stand-in for harmful posts: the class is rare,
adversarial and costly to miss. The setup splits it 60/20/20 (train, validation, test, stratified) and builds
TF-IDF features `X_tr, X_va, X_te` with labels `y_tr, y_va, y_te` (1 = spam).
- `post_score` (simulated): classifier scores for one day of 1,000,000 posts. The true labels are hidden; you can
only buy labels with `human_label(idx)`.""")

# ------------------------------------------------------------------ Q1 the case (text)
ask(ex, title="Design harmful content detection for a short-video app", minutes=10, kind="text",
    prompt="""The examiner says: "Design the system that detects harmful content (violence, hate, adult
content, self-harm, scams) in videos and comments for a short-video app with 200M uploads and comments a day."
You have 10 minutes. Cover **problem and metrics, data and labels, features, model, evaluation, serving and
the enforcement policy, monitoring.**""",
    hint1="""Signal: rare, adversarial, multi-class, multimodal classification with human reviewers in the loop.
The key ideas are prevalence as the north-star metric, precision/recall trade-offs per action, and a cascade
(cheap models first, humans last).""",
    hint2="""1. Metrics: prevalence of violating views (measured by sampling), precision per action, recall,
appeal overturn rate, reviewer load. 2. Labels: moderator decisions, user reports (noisy), policy experts for
golden sets. 3. Multimodal features plus uploader and behavioural signals. 4. Multi-label model per policy,
calibrated. 5. Thresholds by action: auto-remove, reduce reach, human review. 6. Monitoring: new attack patterns.""",
    solution="""**1. Problem and metrics**
- Goal: keep users from seeing harmful content while not removing legitimate content (free expression and
  creator trust).
- North star: **prevalence**, the share of *views* that land on violating content, measured by labelling a
  random (or stratified) sample of viewed content every day (see Q4). It counts what users actually see.
- Model metrics per policy: precision at the auto-action threshold (wrong removals hurt creators), recall
  (estimated from sampled data), PR-AUC. Operations: time to action, share removed before the first view, review
  queue size, appeal rate and overturn rate.

**2. Data and labels**
- Moderator decisions (good but biased toward what was flagged), user reports (noisy, sometimes abusive),
  expert-labelled golden sets per policy for evaluation, and random samples for unbiased prevalence and recall.
- Label noise: measure inter-rater agreement (kappa) per policy, use adjudication for disagreements, refresh
  guidelines; policies change, so labels have versions.

**3. Features**
- Content: video frames (vision embeddings), audio (speech to text, audio events), caption, hashtags, OCR of text
  on screen, comment text; multilingual text encoders.
- Context: uploader history (prior strikes, account age), upload behaviour (bursts, many accounts posting the
  same video), engagement velocity, report counts and reporter reliability, hash match against known bad media
  (perceptual hashes).

**4. Model**
- Cascade: (1) hash matching and rules (instant, near-perfect precision for known items); (2) a light multimodal
  model on every upload; (3) heavier per-policy models (multi-label, one head per policy, calibrated) on
  suspicious items; (4) human review for the uncertain band.
- An LLM with the written policy in the prompt can label borderline text cases and produce training data, but at
  200M items a day it is used on a small slice for cost reasons (see day 27).

**5. Evaluation**
- Offline: PR curves per policy and per language on the golden set; precision at the auto-remove threshold with
  a CI; recall estimated on random samples, not only on reported items.
- Online: A/B tests on enforcement changes, measuring prevalence (primary), creator appeals and overturns,
  user reports, engagement guardrails.

**6. Serving and enforcement policy**
- Score at upload (before distribution) and again as views grow (more signals arrive: reports, comments).
- Actions by score band: very high precision band auto-removes; middle band goes to human review, prioritised by
  `P(violation) * expected views * severity`; lower band reduces distribution (not recommended in feeds) until
  reviewed. Severity matters: self-harm and child safety get lower thresholds and fast escalation.
- Appeals feed back as labels.

**7. Monitoring**
- Adversaries adapt (misspellings, text in images, coded words): watch the report rate on items the model
  passed, new clusters of near-duplicate content, PSI on score distributions per language, precision of
  auto-actions from daily audits. Retrain often; keep rules for fast fixes while models catch up.

**Deep follow-ups**
- *Why not optimise accuracy?* With 0.4% prevalence, "allow everything" is 99.6% accurate.
- *How do you know recall if you only label flagged items?* You do not; label random or stratified samples of
  all content (Q4).
- *New language or new policy with few labels?* Multilingual encoders, translation, LLM-generated labels checked
  by experts, active learning on uncertain items.
- *Fairness?* Check false positive rates by language, dialect and creator group; dialects are often over-flagged
  by toxicity models.
- *Latency versus safety?* Hold distribution for very high-risk uploads (for example a new account posting a
  live stream) until a fast model has scored them.""",
    why="""Moderation exams test whether you measure the right thing (prevalence of views, not accuracy), know
that labels from flagged items are biased, design actions with different thresholds, and expect adversaries. The
model itself is the least interesting part.""",
    learn=["ai-ml-system-design", "ai-features-imbalance"])

# ------------------------------------------------------------------ Q2 base rates and queue size
ask(ex, title="How big is the review queue?", minutes=6,
    prompt="""200M new items a day, 0.2% of them violate policy. A classifier at threshold A has recall 90% and a
false positive rate (FPR) of 1%. At threshold B: recall 80%, FPR 0.1%. A reviewer handles 600 items per day.

Write `flag_stats(n, prevalence, recall, fpr, per_reviewer)` returning a dict with `flagged`, `true_pos`,
`precision`, `reviewers` (rounded up) and `missed` (violating items not flagged). Compare A and B. Which threshold
would you use for auto-removal and which for the review queue?""",
    stub='''def flag_stats(n, prevalence, recall, fpr, per_reviewer):
    # your code here
    pass''',
    tests='''a = flag_stats(200e6, 0.002, 0.90, 0.01, 600) or {}
_t("A flagged", round(a.get("flagged", 0)), 2356000)
_t("A precision", round(a.get("precision", 0), 4), 0.1528)
_t("A reviewers", a.get("reviewers"), 3927)
b = flag_stats(200e6, 0.002, 0.80, 0.001, 600) or {}
_t("B precision", round(b.get("precision", 0), 4), 0.6159)
_t("B missed", round(b.get("missed", 0)), 80000)''',
    hint1="""Signal: a rare positive class and a "small" false positive rate. Base rates: false positives come
from the huge negative class, so precision collapses. Work with counts, not rates.""",
    hint2="""1. positives = n * prevalence; true_pos = recall * positives; false_pos = fpr * (n - positives).
2. flagged = true_pos + false_pos; precision = true_pos / flagged. 3. reviewers = ceil(flagged / 600).""",
    solution='''import math

def flag_stats(n, prevalence, recall, fpr, per_reviewer):
    pos = n * prevalence
    tp = recall * pos
    fp = fpr * (n - pos)
    flagged = tp + fp
    return {"flagged": flagged, "true_pos": tp, "precision": tp / flagged,
            "reviewers": math.ceil(flagged / per_reviewer), "missed": pos - tp}

for name, rec, fpr in [("A", 0.90, 0.01), ("B", 0.80, 0.001)]:
    s = flag_stats(200e6, 0.002, rec, fpr, 600)
    print(name, {k: round(v, 4) if k == "precision" else round(v) for k, v in s.items()})
# A {'flagged': 2356000, 'true_pos': 360000, 'precision': 0.1528, 'reviewers': 3927, 'missed': 40000}
# B {'flagged': 519600, 'true_pos': 320000, 'precision': 0.6159, 'reviewers': 866, 'missed': 80000}''',
    why="""A 1% false positive rate sounds small, but it applies to 199.6M clean items: threshold A flags 2.36M items a
day, only 15.3% of them truly violating, and needs 3,927 reviewers. Threshold B flags 520k items with 61.6%
precision and needs 866 reviewers, but misses 80,000 violating items a day instead of 40,000.

**Policy:** neither threshold is good enough for automatic removal (you would wrongly remove 38% of what B
removes). Use a much higher threshold (precision 95 to 99%) for auto-removal, a middle band for human review
ordered by expected harm (`P(violation) * predicted views * severity`), and "reduce distribution" for the lower
band. **Follow-up: "we can only afford 1,000 reviewers."** Then the review band is fixed by capacity: take the
top 600,000 items a day by expected harm, and invest in the model (better precision means each reviewer removes
more harm), not only in more people.""",
    complexity="O(1).",
    mistakes="Reading FPR 1% as \"1% of flags are wrong\"; computing reviewers from the true positives only; "
             "forgetting that the missed items are the ones users see.",
    learn=["ai-classification-metrics", "ai-ml-system-design"])

# ------------------------------------------------------------------ Q3 two-tier thresholds on real data
ask(ex, title="Auto-remove, review, or allow", minutes=7,
    prompt="""Train a logistic regression (`C=10`, `max_iter=2000`) on `X_tr, y_tr`. Then set two thresholds on
the **validation** set:

- `t_high`: the lowest threshold whose validation precision is at least 0.99 (auto-remove band, `score >= t_high`).
- `t_low`: the highest threshold whose validation recall is at least 0.97 (review band, `t_low <= score < t_high`).

Apply them to the **test** set and report: share of spam auto-removed, precision of auto-removal, review
queue size (and how much of it is spam), spam missed (allowed). Why do we pick thresholds on validation and
report on test?""",
    stub='''# your code here''',
    hint1="""Signal: different actions need different precision. Use the precision-recall curve on held-out data
to choose operating points, one per action.""",
    hint2="""1. `p_va = model.predict_proba(X_va)[:, 1]`; `precision_recall_curve(y_va, p_va)` gives precision and
recall for each threshold (the arrays are one longer than thresholds: drop the last element).
2. `t_high = min(thr[prec >= 0.99])`, `t_low = max(thr[rec >= 0.97])`. 3. Bands on test, then counts.""",
    solution='''from sklearn.metrics import precision_recall_curve
model = LogisticRegression(C=10, max_iter=2000).fit(X_tr, y_tr)
p_va, p_te = model.predict_proba(X_va)[:, 1], model.predict_proba(X_te)[:, 1]
prec, rec, thr = precision_recall_curve(y_va, p_va)
prec, rec = prec[:-1], rec[:-1]                     # align with thresholds
t_high = thr[prec >= 0.99].min()
t_low = thr[rec >= 0.97].max()
print(f"t_high {t_high:.3f}  t_low {t_low:.3f}")
print(f"validation: precision at t_high {y_va[p_va >= t_high].mean():.3f}, recall at t_low {(p_va[y_va == 1] >= t_low).mean():.3f}")
auto = p_te >= t_high
review = (p_te >= t_low) & ~auto
allow = p_te < t_low
spam = y_te == 1
print(f"test spam {spam.sum()} of {len(y_te)}")
print(f"auto-removed: {auto.sum()} items, precision {y_te[auto].mean():.3f}, {auto[spam].mean():.1%} of spam")
print(f"review queue: {review.sum()} items ({review.mean():.1%} of all), {y_te[review].sum()} spam in it")
print(f"allowed spam (missed): {allow[spam].sum()}, ham sent to review or removed: {(~allow[~spam]).sum()}")
# t_high 0.483  t_low 0.243
# validation: precision at t_high 0.993, recall at t_low 0.973
# test spam 149 of 1115
# auto-removed: 130 items, precision 1.000, 87.2% of spam
# review queue: 14 items (1.3% of all), 5 spam in it
# allowed spam (missed): 14, ham sent to review or removed: 9''',
    why="""On validation, `t_high = 0.483` gives precision 0.993 and `t_low = 0.243` gives recall 0.973. On the test set the
auto-remove band catches 87.2% of the spam with no false removal (130 of 130 correct), and the review band is tiny
(14 items, 1.3% of traffic, 5 of them spam). But 14 spam messages fall below `t_low`, so test recall of the two
bands together is 135 / 149 = 90.6%, well under the 97% target. Thresholds chosen at extreme points of the PR curve
are unstable with about 150 positives; one or two messages move them.

**Why validation then test:** the thresholds are fitted parameters; choosing them on test and reporting on test
gives optimistic numbers. **What to say:** "with this data size, I would report test recall with a CI (here 135
of 149, a Wilson 95% CI of about 85% to 94%), get more labelled positives for threshold setting, and set `t_low` with a safety
margin." In production thresholds are re-checked often, because score distributions shift as spammers adapt.""",
    complexity="O(n log n) for the PR curve.",
    mistakes="Choosing thresholds on the test set (optimistic numbers); using 0.5 because it is the default; "
             "forgetting that test precision at a 0.99 target can land below 0.99 with few positives (report a CI).",
    learn=["ai-classification-metrics", "ai-ml-system-design"])

# ------------------------------------------------------------------ Q4 prevalence by stratified sampling
ask(ex, title="How much harmful content do users really see?", minutes=7,
    prompt="""Leadership asks for today's prevalence (share of the 1,000,000 posts in `post_score` that violate).
Labels cost money: you can label 1,000 posts with `human_label(idx)`.

1. Simple random sample (SRS) of 1,000 posts (`np.random.default_rng(1)`): estimate and 95% CI.
2. Stratified sample: 4 strata by score, `[0, 0.1)`, `[0.1, 0.3)`, `[0.3, 0.6)`, `[0.6, 1]`, 250 labels per
   stratum (`np.random.default_rng(2)`, sampling without replacement inside each stratum). Estimate
   `sum(N_h / N * p_h)` with `SE = sqrt(sum((N_h / N) ** 2 * p_h * (1 - p_h) / n_h))`.
3. Which design would you run every day, and why?""",
    stub='''# your code here''',
    hint1="""Signal: estimating a rare rate with a fixed labelling budget. Stratified sampling (oversample the
high-score strata, then weight back by stratum size) cuts the variance a lot when the score is informative.""",
    hint2="""1. SRS: `p = mean`, `se = sqrt(p(1-p)/n)`. 2. `edges = [0, .1, .3, .6, 1.0001]`; for each stratum get
its indices, `rng.choice(idx, 250, replace=False)`, label, `p_h`. 3. Weight by `N_h / N`.""",
    solution='''rng1 = np.random.default_rng(1)
idx = rng1.choice(N_POSTS, 1000, replace=False)
y = human_label(idx)
p_srs = y.mean(); se_srs = np.sqrt(p_srs * (1 - p_srs) / len(y))
print(f"SRS: {p_srs:.4f} +/- {1.96 * se_srs:.4f}  ({y.sum()} positives found)")

rng2 = np.random.default_rng(2)
edges = [0, 0.1, 0.3, 0.6, 1.0001]
est, var = 0.0, 0.0
for lo, hi in zip(edges[:-1], edges[1:]):
    members = np.where((post_score >= lo) & (post_score < hi))[0]
    lab = human_label(rng2.choice(members, 250, replace=False))
    w, ph = len(members) / N_POSTS, lab.mean()
    est += w * ph
    var += w ** 2 * ph * (1 - ph) / 250
    print(f"stratum [{lo}, {min(hi, 1)}): N_h={len(members):>7,}  p_h={ph:.3f}")
print(f"stratified: {est:.4f} +/- {1.96 * np.sqrt(var):.4f}")
print(f"true prevalence (unknown in real life): {human_label(np.arange(N_POSTS)).mean():.4f}")
# SRS: 0.0030 +/- 0.0034  (3 positives found)
# stratum [0, 0.1): N_h=713,625  p_h=0.000
# stratum [0.1, 0.3): N_h=268,615  p_h=0.000
# stratum [0.3, 0.6): N_h= 14,699  p_h=0.088
# stratum [0.6, 1): N_h=  3,061  p_h=1.000
# stratified: 0.0044 +/- 0.0005
# true prevalence (unknown in real life): 0.0040''',
    why="""Simple random sampling finds only 3 violating posts in 1,000, so the estimate is 0.30% plus or minus 0.34% (the
interval even crosses zero): useless for a daily dashboard. Stratified sampling with the same budget gives
0.44% plus or minus 0.05%, about 7 times narrower, close to the true 0.40%. It works because the classifier score
concentrates the positives: almost all of them sit in the two top strata (1.8% of posts), which get half of the
labels; the weights `N_h / N` undo the oversampling.

**Run the stratified design daily**, with three cautions: (1) the two low strata had 0 positives in 250 labels, so
their contribution to the SE is shown as 0, which is too optimistic (rule of three: each could hide up to 1.2%,
weighted by its size); give those strata a share of the budget forever, because that is where the misses live;
(2) if the classifier changes, the strata change, but the estimate stays unbiased as long as weights match the
design; (3) prevalence should be weighted by **views**, not posts: sample views (or weight posts by views),
because one viral harmful video matters more than a thousand unseen ones.""",
    complexity="O(N) to assign strata, plus the labelling cost (the real constraint).",
    mistakes="Averaging the labels of the stratified sample without weights (massively overestimates, because the "
             "high-score strata are oversampled); estimating prevalence from flagged items only; a stratum with "
             "p_h = 0 still has uncertainty (use a Wilson or rule-of-three bound there).",
    learn=["ai-ml-system-design", "stats-confidence-intervals"])

# ------------------------------------------------------------------ Q5 review: class weights and calibration
ask(ex, title="Class weights made the scores lie", minutes=6, review=True,
    prompt="""On the spam data (13.4% spam), fit three logistic regressions (`C=10`, `max_iter=2000`) on
`X_tr, y_tr`:

1. plain; 2. `class_weight="balanced"`; 3. trained on all spam plus a random 20% of ham
   (`np.random.default_rng(5)`), then corrected with `p = s * q / (s * q + 1 - q)` where `s = 0.2` and `q` is the
   model's score.

For each, on the test set, report average precision (PR-AUC), mean predicted probability (compare with the
real spam rate) and the Brier score. Which numbers change and which do not? When does it matter?""",
    stub='''# your code here''',
    hint1="""Signal: reweighting or resampling the classes changes the base rate the model sees. Ranking quality
barely moves, but probabilities shift (miscalibration). Undersampling has a closed-form prior correction.""",
    hint2="""1. Three fits. 2. `average_precision_score`, `p.mean()` versus `y_te.mean()`, `brier_score_loss`.
3. Correction derivation: undersampling negatives by `s` multiplies the odds by `1 / s`, so true odds = `s * q / (1 - q)`.""",
    solution='''plain = LogisticRegression(C=10, max_iter=2000).fit(X_tr, y_tr)
bal = LogisticRegression(C=10, max_iter=2000, class_weight="balanced").fit(X_tr, y_tr)
rng5 = np.random.default_rng(5)
keep = (y_tr == 1) | (rng5.random(len(y_tr)) < 0.2)
down = LogisticRegression(C=10, max_iter=2000).fit(X_tr[keep], y_tr[keep])
s = 0.2
q = down.predict_proba(X_te)[:, 1]
scores = {"plain": plain.predict_proba(X_te)[:, 1], "balanced": bal.predict_proba(X_te)[:, 1],
          "downsampled raw": q, "downsampled corrected": s * q / (s * q + 1 - q)}
print(f"real spam rate in test {y_te.mean():.4f}")
for name, p in scores.items():
    print(f"{name:22s} AP {average_precision_score(y_te, p):.4f}  mean p {p.mean():.4f}  "
          f"mean p on ham {p[y_te == 0].mean():.4f}  Brier {brier_score_loss(y_te, p):.4f}")
# real spam rate in test 0.1336
# plain                  AP 0.9673  mean p 0.1274  mean p on ham 0.0231  Brier 0.0170
# balanced               AP 0.9663  mean p 0.1576  mean p on ham 0.0462  Brier 0.0169
# downsampled raw        AP 0.9668  mean p 0.2013  mean p on ham 0.0994  Brier 0.0249
# downsampled corrected  AP 0.9668  mean p 0.1130  mean p on ham 0.0242  Brier 0.0236''',
    why="""Ranking quality (average precision) is almost the same for all four models (0.966 to 0.967): reweighting and
resampling do not make the model better at ordering messages. What changes is the **probability scale**. The plain
model's mean score (0.127) is close to the real spam rate (0.134). Balanced weights push it to 0.158 and double the
average score of clean messages (0.023 to 0.046). Training on 20% of the ham pushes the mean to 0.201 (clean
messages average 0.099); the prior correction brings it back (0.113, with clean messages at 0.024). The Brier score
barely moves for balanced weights here because most messages are easy (scores near 0 or 1); the shift lives in the
uncertain middle, where decisions are made.

**When it matters:** whenever the score is used as a probability: expected-cost decisions, prevalence estimates
from scores, a fixed threshold reused after retraining, or fusing several models (like the feed ranker's heads).
**What to do:** prefer the plain model plus a tuned threshold; if you downsample for speed (common in ads and
feeds), apply the prior correction or recalibrate (Platt or isotonic) on data with the real class mix.""",
    complexity="O(nnz) per fit for sparse TF-IDF.",
    mistakes="Using balanced weights and then reading scores as probabilities (for expected cost, prevalence or "
             "fusion with other models); resampling before the train/test split (test no longer reflects reality); "
             "thinking class weights fix a ranking problem.",
    learn=["ai-features-imbalance", "ai-classification-metrics"])

ex.save()
