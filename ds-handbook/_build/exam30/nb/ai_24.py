"""Day 24 AI (hard): ML system design case 1, feed ranking for a short-video app (focus);
recommenders and LLM evaluation (review)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libx import Exam  # noqa: F401
from _ai_hard_common import start, ask

SETUP = r'''def _t(name, got, want):
    good = got == want
    print(("PASS " if good else "FAIL ") + name + f" -> {got!r}" + ("" if good else f"   expected {want!r}"))

# Six candidate videos for one user request, with the ranker's predicted probabilities (made up).
cands = pd.DataFrame({
    "video":       ["v1", "v2", "v3", "v4", "v5", "v6"],
    "duration_s":  [15, 60, 180, 30, 45, 20],
    "p_finish":    [0.70, 0.35, 0.10, 0.55, 0.40, 0.60],
    "p_like":      [0.08, 0.05, 0.03, 0.12, 0.04, 0.06],
    "p_share":     [0.010, 0.004, 0.002, 0.030, 0.002, 0.020],
    "p_skip2s":    [0.15, 0.20, 0.30, 0.10, 0.40, 0.12],   # swiped away within 2 seconds
    "exp_watch_s": [12, 33, 70, 22, 21, 15],               # predicted watch time in seconds
})
print(cands)'''

ex = start(24, loads=("movielens",), extra=SETUP, data_note="""- `ratings` (MovieLens latest-small, real,
100,836 ratings by 610 users, 1996 to 2018): `userId`, `movieId`, `rating` (0.5 to 5), `timestamp` (unix seconds).
We use it as a stand-in for engagement logs (rating 4 or more = "the user liked it").
- `cands` (made up): six candidate videos with the ranker's predicted probabilities for one request.""")

# ------------------------------------------------------------------ Q1 the case (text)
ask(ex, title="Design the For You feed ranking", minutes=10, kind="text",
    prompt="""The examiner says: "Design the ranking system for the main feed of a short-video app (think
TikTok For You). 150M daily users, about 500M videos in the catalogue, 100M new videos a week." You have 10
minutes. Cover, in this order: **problem and metrics, data and labels, features, model (the whole funnel),
evaluation (offline and online), serving, monitoring.** Then be ready for the deep follow-ups listed in the
solution.""",
    hint1="""Signal: a large-scale recommendation problem with strict latency. The answer is a multi-stage funnel:
candidate generation (retrieval) then ranking then re-ranking, trained on implicit feedback with several
objectives.""",
    hint2="""1. Business goal: long-term engagement and retention, not clicks. Online metrics and guardrails.
2. Labels from implicit signals: watch time, finish, like, share, follow, fast skip, "not interested".
3. Funnel: retrieval (two-tower, co-engagement, follow graph, fresh content) to a few thousand; light ranker to a
few hundred; heavy multi-task ranker; re-rank for diversity, freshness and policy.
4. Offline: AUC or log loss per head, NDCG, time-based split. Online: A/B test with holdouts.
5. Serving: feature store, ANN index, latency budget. Monitoring: drift, calibration, feedback loops.""",
    solution="""**1. Problem and metrics**
- Goal: users find videos they enjoy and come back. North star: daily active users and long-term retention;
  the proxy for a session is total watch time and "satisfied views".
- Online metrics: watch time per user, finish rate, likes, shares, follows per user, 7-day retention in a
  long-running holdout. Guardrails: fast-skip rate, "not interested" and report rates, creator-side diversity
  (share of impressions to new creators), latency, crash rate.
- ML task: for each (user, video, context) predict several engagement probabilities, combine them into one score,
  rank.

**2. Data and labels**
- Impression logs (what was shown, position, context), engagement events (watch seconds, finish, replay, like,
  share, comment, follow, fast skip, "not interested"), video metadata, creator data, user profile.
- Labels per impression: `finish`, `like`, `share`, `follow`, `skip within 2s`, watch time (regression or bucketed).
  Watch time is biased toward long videos, so use completion ratio or watch-time percentile within a duration
  bucket.
- Pitfalls: exposure bias (only shown videos have labels), position bias, delayed labels (shares and follows
  arrive later), bots.

**3. Features**
- User: embedding learned from history, recent watch sequence (last 50 video ids), languages, device, time of day.
- Video: content embeddings (vision, audio, ASR text, caption), duration, age, creator, hashtags, sound.
- Video statistics: smoothed rates (finish rate, like rate) over 1 hour, 1 day, 7 days, with priors for new
  videos.
- Cross features: user's past engagement with this creator, sound or topic; similarity between user and video
  embeddings.
- All windowed counts must be computed "as of" impression time to avoid leakage.

**4. Model (the funnel)**
- **Candidate generation**, about 10 sources merged to a few thousand: two-tower retrieval (user tower, video
  tower, approximate nearest neighbours over 500M videos), item-to-item co-engagement from recent watches,
  followed creators, trending in region and language, and a fresh-content pool for new uploads.
- **Light ranker**: a small model (or a distilled two-tower score) cuts thousands to about 300.
- **Heavy ranker**: a multi-task deep model (shared bottom or mixture of experts, one head per objective,
  sequence features with attention over the user's recent watches). Score fusion:
  `score = w1 * p_finish + w2 * p_like + w3 * p_share + w4 * p_follow - w5 * p_skip`, weights tuned with online
  experiments.
- **Re-ranking**: diversity (no two videos in a row from the same creator or sound), freshness boost,
  exploration slots for new videos, policy filters (integrity scores, age rating).

**5. Evaluation**
- Offline: log loss and AUC per head, calibration, NDCG on time-split data (train on days 1 to 14, test on day 15),
  sliced by new users, new videos, regions.
- Online: A/B test on users, 1 to 2 weeks for novelty, primary watch time per user, guardrails as above; a
  long-term holdout (1% of users kept on an old model for months) to measure retention and feedback-loop effects.
  Interleaving for fast ranking comparisons.

**6. Serving**
- Peak QPS around 130k (see Q4). Latency budget about 200 ms p99: retrieval 40, feature fetch 30, light ranker 20,
  heavy ranker 60, re-rank and policy 10, network 40.
- Online feature store (low-latency key value store) plus streaming updates of video stats within minutes;
  ANN index refreshed often so new uploads appear quickly; GPU inference with batching for the heavy ranker.
- Prefetch the next page while the user watches; cache candidate lists per user for a few minutes.

**7. Monitoring**
- Data: feature drift (PSI), missing features, feature store freshness. Model: calibration per head, prediction
  distribution, online versus offline gaps. Product: dashboards for watch time, skips, reports, creator
  diversity. Retrain daily or continuously; roll out with canaries and automatic rollback.

**Deep follow-ups (TikTok style) with short answers**
- *Watch time favours long videos. Fix?* Predict completion or watch-time percentile within duration buckets, or
  weight the watch-time label; see Q2.
- *Feedback loop: the model only learns from what it showed.* Exploration slots (about 5% of impressions with
  randomised or uncertainty-based picks), log the propensity, use inverse propensity weighting, and keep a
  random-traffic dataset for unbiased evaluation.
- *Position bias in labels?* Add position as a training feature and set it to a constant at serving, or learn a
  separate position tower (shallow tower) whose output is dropped at serving.
- *Cold start for a new video?* Content embeddings put it near similar videos; a fresh pool gives it a fixed
  number of test impressions (for example 300 to 500) and promotes it to wider pools if early rates are good
  (a bandit over traffic tiers).
- *Cold start for a new user?* Popular-in-region plus fast exploration across topics; the first 10 to 20 swipes
  update the user embedding in real time from the session sequence.
- *How do you set the fusion weights?* They encode business trade-offs; tune them by online experiments or
  Bayesian optimisation with long-term retention as the target and guardrails as constraints. Heads must stay
  calibrated, or the weights mean nothing.
- *Short-term engagement versus long-term wellbeing?* Long-term holdouts, guardrails on "not interested" and late
  night sessions, diversity constraints, and metrics like "satisfied sessions" from surveys.""",
    why="""A strong answer is structured, starts from the business goal, uses a funnel because no heavy model can
score 500M videos in 200 ms, separates offline and online evaluation, and names the classic recommender biases
(exposure, position, popularity, duration) with concrete fixes. Examiners at short-video companies dig into
watch-time bias, cold start and feedback loops, so prepare those three in depth.""",
    learn=["ai-ml-system-design", "ai-recommenders"])

# ------------------------------------------------------------------ Q2 score fusion and watch-time bias
ask(ex, title="One score from many predictions", minutes=7,
    prompt="""The heavy ranker gives several predictions per candidate (table `cands`).

1. Rank the six videos by predicted watch time `exp_watch_s`. What kind of video wins?
2. Write `fuse(df, w)` that returns the list of video ids sorted by
   `w["finish"] * p_finish + w["like"] * p_like + w["share"] * p_share - w["skip"] * p_skip2s` (highest first).
   Use `W = {"finish": 1, "like": 3, "share": 20, "skip": 1}`.
3. Rank by watch time divided by duration (expected completion). Compare the three rankings.
4. Why are the share weight (20) and the like weight (3) so much bigger than the finish weight?""",
    stub='''def fuse(df, w):
    # your code here
    pass''',
    tests='''W = {"finish": 1, "like": 3, "share": 20, "skip": 1}
_t("fused ranking", fuse(cands, W), ["v4", "v6", "v1", "v2", "v5", "v3"])
_t("finish only", fuse(cands, {"finish": 1, "like": 0, "share": 0, "skip": 0}), ["v1", "v6", "v4", "v5", "v2", "v3"])''',
    hint1="""Signal: a multi-task ranker needs a single sort key. That is score fusion (a weighted sum of
calibrated predictions); raw watch time has a duration bias.""",
    hint2="""1. `sort_values("exp_watch_s", ascending=False)`. 2. Build the score column, sort descending, return
`video.tolist()`. 3. `exp_watch_s / duration_s`. 4. Think of how rare each event is and how much it is worth.""",
    solution='''W = {"finish": 1, "like": 3, "share": 20, "skip": 1}

def fuse(df, w):
    score = (w["finish"] * df.p_finish + w["like"] * df.p_like
             + w["share"] * df.p_share - w["skip"] * df.p_skip2s)
    return df.assign(score=score).sort_values("score", ascending=False).video.tolist()

c = cands.copy()
c["score"] = W["finish"] * c.p_finish + W["like"] * c.p_like + W["share"] * c.p_share - W["skip"] * c.p_skip2s
c["completion"] = c.exp_watch_s / c.duration_s
print("by watch time :", c.sort_values("exp_watch_s", ascending=False).video.tolist())
print("fused         :", fuse(cands, W))
print("by completion :", c.sort_values("completion", ascending=False).video.tolist())
print(c[["video", "duration_s", "exp_watch_s", "completion", "score"]].round(3).to_string(index=False))
# by watch time : ['v3', 'v2', 'v4', 'v5', 'v6', 'v1']
# fused         : ['v4', 'v6', 'v1', 'v2', 'v5', 'v3']
# by completion : ['v1', 'v6', 'v4', 'v2', 'v5', 'v3']
# (table) v3: 70 s expected watch but completion 0.389 and score -0.07; v4: score 1.41''',
    why="""Ranking by predicted watch time puts the 180-second video v3 first, although it has the lowest finish,
like and share rates and the highest fast-skip rate: long videos collect seconds just by being long. The fused
score puts v4 first (1.41: best like and share rates, fewest fast skips) and v3 last (-0.07). Completion
(watch time / duration) removes most of the duration effect and agrees with the fused ranking at the bottom
(v5, v3 last).

**Why the big weights for rare events:** the predictions are probabilities of events with very different base
rates and value. A share happens about 20 to 100 times less often than a finish, but it brings new viewers and is
a strong satisfaction signal, so its weight is large. Weights roughly mean "how many finishes is one share worth".
That only works if each head is **calibrated**: if the share head overestimates by 2x, its effective weight
doubles.

**Follow-ups.** *How are weights chosen?* Online experiments on the weight vector with long-term retention as the
target and guardrails as constraints. *Additive or multiplicative?* Some systems use
`p_finish ** a * (1 + p_like) ** b ...`; multiplicative fusion is less sensitive to the scale of one head. *How to
fix duration bias in training?* Predict completion or a watch-time quantile within duration buckets, or weight
the watch-time label by duration (as in YouTube's weighted logistic regression for watch time).""",
    complexity="O(n log n) for n candidates.",
    mistakes="Adding uncalibrated scores from different heads; ranking by raw watch time; setting weights once "
             "offline and never testing them online; forgetting negative signals (fast skip, not interested).",
    learn=["ai-ml-system-design", "ai-recommenders"])

# ------------------------------------------------------------------ Q3 offline eval with time split (review recommenders)
ask(ex, title="Why the offline score was too good", minutes=7, review=True,
    prompt="""A teammate evaluated a popularity recommender on `ratings` with a **random** 80/20 split and got
a good recall@10. You suspect the split. Build both evaluations and compare:

- **Random split:** each rating goes to test with probability 0.2 (`np.random.default_rng(0)`).
- **Temporal split per user:** sort each user's ratings by time; the last 20% (rank `>= int(0.8 * n_user)`) is test.

Model: rank movies by the number of ratings `>= 4` in train. For each user with at least one test rating `>= 4`,
recommend the top 10 movies they have not rated in train. Report users evaluated, mean recall@10, mean NDCG@10
and hit rate (share of users with at least one hit). Explain the gap.""",
    stub='''def evaluate(test_mask, K=10):
    # your code here
    pass''',
    hint1="""Signal: an offline metric for a system that will predict the future. The split must respect time
(temporal or "leave last out"), otherwise the model learns from the future: data leakage.""",
    hint2="""1. Sort by user and time, `cumcount()` per user for the rank, `transform("size")` for n.
2. Train popularity: `value_counts()` of liked movieIds in train.
3. Per user: skip seen movies, take 10, count hits, recall = hits / liked test items,
NDCG = DCG / ideal DCG with `1 / log2(position + 1)`.""",
    solution='''r = ratings.sort_values(["userId", "timestamp", "movieId"]).reset_index(drop=True)
r["rank"] = r.groupby("userId").cumcount()
r["n"] = r.groupby("userId").movieId.transform("size")
temporal = r["rank"] >= (0.8 * r["n"]).astype(int)
random_ = pd.Series(np.random.default_rng(0).random(len(r)) < 0.2)

def evaluate(test_mask, K=10):
    train, test = r[~test_mask], r[test_mask & (r.rating >= 4)]
    popular = train[train.rating >= 4].movieId.value_counts().index.to_numpy()[:3000]
    seen = train.groupby("userId").movieId.agg(set)
    truth = test.groupby("userId").movieId.agg(set)
    recall, ndcg = [], []
    for u, liked in truth.items():
        s = seen.get(u, set())
        top = [m for m in popular if m not in s][:K]
        hits = [m in liked for m in top]
        recall.append(sum(hits) / len(liked))
        dcg = sum(h / np.log2(i + 2) for i, h in enumerate(hits))
        idcg = sum(1 / np.log2(i + 2) for i in range(min(len(liked), K)))
        ndcg.append(dcg / idcg)
    return (len(truth), round(float(np.mean(recall)), 4), round(float(np.mean(ndcg)), 4),
            round(float(np.mean([x > 0 for x in recall])), 3))

print("random  (users, recall@10, ndcg@10, hit rate):", evaluate(random_))
print("temporal(users, recall@10, ndcg@10, hit rate):", evaluate(temporal))
# random  (users, recall@10, ndcg@10, hit rate): (597, 0.1046, 0.1653, 0.566)
# temporal(users, recall@10, ndcg@10, hit rate): (592, 0.0499, 0.0798, 0.328)''',
    why="""With a random split, popularity reaches recall@10 0.1046 and a 56.6% hit rate; with the temporal split the
same model gets 0.0499 and 32.8%: the random split roughly doubles the score. Why: (1) the random test set is
spread across each user's whole history, so the train set already contains the user's taste from "after" the
test events; (2) item popularity is computed partly from the future, so movies that become popular later look
predictable; (3) a real system always predicts the next items, which are harder (newer, more niche).

**Rule:** evaluate the way the model will be used: train on the past, test on the future (a global time cut
or "leave last N out" per user). Even the per-user temporal split here still leaks a little, because popularity
uses other users' ratings from after a given user's test period; a global time cut removes that too, but on
MovieLens it leaves very few users who appear on both sides, which is itself a lesson about cold start.
**Follow-up: "offline recall went up but the A/B test is flat. Why?"** Offline data only contains items the old
system showed (exposure bias), offline metrics ignore position and presentation, and the new model can change
user behaviour; trust the online test, and use offline metrics as a filter.""",
    complexity="O(R + U * P) where R = ratings, U = test users, P = popular items scanned per user.",
    mistakes="Random splits for a forecasting problem; recommending items the user already consumed (inflates "
             "or deflates the metric depending on the rule); dividing recall by K instead of the number of "
             "relevant items; comparing models evaluated on different user sets.",
    learn=["ai-recommenders", "ai-ml-system-design"])

# ------------------------------------------------------------------ Q4 capacity and latency math
ask(ex, title="How many machines does the ranker need?", minutes=6,
    prompt="""Back-of-the-envelope numbers the examiner expects you to compute out loud:

- 150M daily active users, 25 feed requests per user per day, peak traffic is 3 times the daily average.
- Each request: retrieval returns 3,000 candidates, the light ranker keeps 300 for the heavy ranker.
- Cost per candidate: light ranker 0.05 MFLOP, heavy ranker 20 MFLOP.
- One GPU server delivers 50 TFLOP/s in theory but only 30% of it in production (batching, memory).
- Keep 40% headroom (servers run at 60% of their capacity at peak).
- Video embeddings: 500M videos, 128 dimensions.

Compute: average and peak QPS; heavy-ranker FLOP/s at peak; servers needed; the FLOP/s if the heavy model scored
all 3,000 candidates (no light ranker); memory for the embedding table in float32, float16 and int8.""",
    stub='''# your code here''',
    hint1="""Signal: capacity planning. Everything is multiplication: traffic, then work per request, then work
per machine. The funnel exists because work per request explodes otherwise.""",
    hint2="""1. `avg_qps = DAU * requests / 86400`, `peak = 3 * avg`. 2. FLOP/s = peak * (3000 * light + 300 *
heavy). 3. Effective server = 50e12 * 0.3; servers = FLOP/s / (effective * 0.6), round up.
4. Memory = videos * dims * bytes per number.""",
    solution='''import math
dau, req, peak_factor = 150e6, 25, 3
avg_qps = dau * req / 86400
peak_qps = peak_factor * avg_qps
flops_req = 3000 * 0.05e6 + 300 * 20e6                  # light on 3,000, heavy on 300
flops_peak = peak_qps * flops_req
server = 50e12 * 0.30
servers = math.ceil(flops_peak / (server * 0.6))
no_funnel = peak_qps * 3000 * 20e6
print(f"avg QPS {avg_qps:,.0f}, peak QPS {peak_qps:,.0f}")
print(f"FLOP per request {flops_req:.3g}, peak FLOP/s {flops_peak:.3g}, servers {servers}")
print(f"heavy model on all 3,000: {no_funnel:.3g} FLOP/s, servers {math.ceil(no_funnel / (server * 0.6))}")
for name, b in [("float32", 4), ("float16", 2), ("int8", 1)]:
    print(f"embeddings {name}: {500e6 * 128 * b / 1e9:.0f} GB")
# avg QPS 43,403, peak QPS 130,208
# FLOP per request 6.15e+09, peak FLOP/s 8.01e+14, servers 89
# heavy model on all 3,000: 7.81e+15 FLOP/s, servers 869
# embeddings float32: 256 GB / float16: 128 GB / int8: 64 GB''',
    why="""About 43k QPS on average and 130k at peak. With the funnel each request costs 6.15e9 FLOP (almost all of it
the heavy ranker on 300 candidates), which is 8.0e14 FLOP/s at peak, so about **89 GPU servers**. Running the
heavy model on all 3,000 candidates would need about **869 servers**, almost 10 times more: this is why
recommenders use a cascade, and why the light ranker is trained to imitate the heavy one (distillation) so it
does not drop the videos the heavy model would like.

The embedding table is 256 GB in float32, 128 GB in float16 and 64 GB in int8. It does not fit in one GPU,
so ANN retrieval uses sharded indexes and compressed vectors (product quantization), and the full-precision
vectors are only used for a final re-score.

**Follow-up: "how do you cut cost by half?"** Smaller heavy ranker (distillation), fewer candidates to the heavy
stage (measure the recall loss of the light ranker), caching of user embeddings within a session, int8 or
float16 inference, and dynamic candidate counts (fewer at peak).""",
    complexity="O(1).",
    mistakes="Forgetting the peak factor; mixing up MFLOP and FLOP; using theoretical GPU throughput; no headroom "
             "for failover and traffic spikes; forgetting that the embedding table must be replicated per region.",
    learn=["ai-ml-system-design", "ai-safety-cost"])

# ------------------------------------------------------------------ Q5 review: weighted kappa
ask(ex, title="An LLM rates video titles on a 3-point scale", minutes=5, review=True,
    prompt="""To build a "title quality" feature for the ranker, an LLM rates titles as 0 = bad, 1 = ok, 2 = good.
Experts rated the same 300 titles. Confusion matrix (rows = expert, columns = LLM):

```
         LLM 0  LLM 1  LLM 2
exp 0      30     12      3
exp 1      10     80     25
exp 2       2     18    120
```

Write `weighted_kappa(cm, weights="quadratic")` from the confusion matrix (support `"linear"` too), using
`kappa_w = 1 - sum(w * O) / sum(w * E)` with disagreement weights `w_ij = (i - j) ** 2` (quadratic) or `|i - j|`
(linear), `O` the observed proportions and `E` the outer product of the row and column marginals. Compare with
unweighted kappa. Why is weighted kappa the right choice here?""",
    stub='''cm = np.array([[30, 12, 3], [10, 80, 25], [2, 18, 120]])

def weighted_kappa(cm, weights="quadratic"):
    # your code here
    pass''',
    tests='''cm = np.array([[30, 12, 3], [10, 80, 25], [2, 18, 120]])
from sklearn.metrics import cohen_kappa_score
yh = np.repeat([0, 0, 0, 1, 1, 1, 2, 2, 2], cm.ravel()); yl = np.repeat([0, 1, 2] * 3, cm.ravel())
for wt in ("quadratic", "linear"):
    _t(wt + " vs sklearn", round(weighted_kappa(cm, wt) or 0, 6), round(cohen_kappa_score(yh, yl, weights=wt), 6))''',
    hint1="""Signal: ordinal labels from two raters. Plain kappa treats "good vs ok" as wrong as "good vs bad";
weighted kappa gives partial credit by distance.""",
    hint2="""1. `O = cm / cm.sum()`. 2. `E = np.outer(O.sum(1), O.sum(0))`. 3. `i, j = np.indices(cm.shape)`;
`w = (i - j) ** 2` or `abs(i - j)`. 4. `1 - (w * O).sum() / (w * E).sum()`. Unweighted: `w = (i != j)`.""",
    solution='''cm = np.array([[30, 12, 3], [10, 80, 25], [2, 18, 120]])

def weighted_kappa(cm, weights="quadratic"):
    O = cm / cm.sum()
    E = np.outer(O.sum(axis=1), O.sum(axis=0))
    i, j = np.indices(cm.shape)
    w = {"quadratic": (i - j) ** 2, "linear": np.abs(i - j), "none": (i != j).astype(float)}[weights]
    return float(1 - (w * O).sum() / (w * E).sum())

print("accuracy", round(np.trace(cm) / cm.sum(), 3))
for wt in ("none", "linear", "quadratic"):
    print(wt, round(weighted_kappa(cm, wt), 3))
# accuracy 0.767
# none 0.616
# linear 0.666
# quadratic 0.724''',
    why="""Raw agreement is 76.7%. Unweighted kappa is 0.616, linear 0.666, quadratic 0.724: weighting gives partial
credit because most disagreements are one step apart (ok versus good), and only 5 of 300 titles are two steps
apart (bad versus good). For an ordinal scale that is the right view: calling a good title "ok" is a much smaller
error than calling it "bad". Quadratic weighting punishes big disagreements most and is the standard choice when
the score is used as a number (as a ranking feature).

**For the ranker:** before using the LLM rating as a feature, check agreement by slice (language, video
category), check that the rating is stable when the prompt or the LLM version changes (re-rate a fixed set and
compute kappa against the old ratings), and remember the online test decides: a feature with good kappa can still
add nothing if the ranker already captures title quality from engagement.""",
    complexity="O(c ** 2) for c classes.",
    mistakes="Using unweighted kappa for ordinal scales (too harsh); using quadratic weights for nominal "
             "categories (there is no order); forgetting that E uses the marginals of both raters.",
    learn=["ai-llm-evaluation"])

ex.save()
