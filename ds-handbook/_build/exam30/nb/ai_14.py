import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _ai_mid_common import setup

# Day 14 AI mock exam. Review: trees-boosting, features-imbalance, unsupervised, gradient-descent,
# neural-networks, embeddings. 8 questions: rapid concept + short hands-on + one mini case.
INTRO = """**Mock exam rules.** One timer for the whole notebook: **30 minutes**. Run the setup cell first, then
start the timer. Answer the concept questions out loud (or in two or three written lines) and move on; do not polish.
Do not open any hint or solution until the 30 minutes are over. Then mark each question right, partly right or wrong,
and log everything that was not right.

Topics: trees and boosting, imbalanced data, unsupervised learning, gradient descent, neural networks, embeddings."""

ex = Exam(14, "ai", intro=INTRO)
setup(ex, '''import io, zipfile
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

bank_path = os.path.join(DATA, "bank_marketing.csv")
if not os.path.exists(bank_path):                 # UCI zip that contains another zip (see DATASETS.md)
    print("downloading bank marketing")
    outer = zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(
        "https://archive.ics.uci.edu/static/public/222/bank+marketing.zip").read()))
    inner = zipfile.ZipFile(io.BytesIO(outer.read("bank-additional.zip")))
    with open(bank_path, "wb") as f:
        f.write(inner.read("bank-additional/bank-additional-full.csv"))
bank = pd.read_csv(bank_path, sep=";")
num = ["age", "campaign", "pdays", "previous", "emp.var.rate", "cons.price.idx", "cons.conf.idx",
       "euribor3m", "nr.employed"]                               # no `duration`: it is only known after the call
Xb = bank[num].to_numpy(float)
yb = (bank["y"] == "yes").astype(int).to_numpy()
Xb_tr, Xb_te, yb_tr, yb_te = train_test_split(Xb, yb, test_size=0.3, random_state=0, stratify=yb)
scaler = StandardScaler().fit(Xb_tr)
Xb_tr, Xb_te = scaler.transform(Xb_tr), scaler.transform(Xb_te)

pg = pd.read_csv(data_path("penguins.csv", "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/penguins.csv"))
pg_feat = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
P4 = pg.dropna(subset=pg_feat)[pg_feat].to_numpy(float)
print("bank", Xb.shape, "positive share", round(yb.mean(), 3), "| penguins", P4.shape)''', data=True)

ex.text("""**Data:** `Xb_tr`, `Xb_te`, `yb_tr`, `yb_te` = UCI Bank Marketing (41,188 calls, 11.3% said yes to a term
deposit), 9 numeric features, standardized, 70/30 stratified split. `P4` = the 4 body measurements of 342 penguins
(not scaled).""")

# ---------------------------------------------------------------- Q1 RF vs GBM
ex.q("Two tree ensembles", minutes=3, kind="text",
     prompt="""In about 45 seconds: random forest versus gradient boosting. How is each built, what does each reduce
(bias or variance), what happens when you add more trees to each, and which one would you tune more carefully?""",
     hint1="Signal: tree ensembles. Pattern: bagging (parallel, deep trees, averages) versus boosting (sequential, "
           "shallow trees, fits residuals).",
     hint2="1. RF: bootstrap samples + random feature subsets, deep trees, average: reduces variance.\n2. GBM: each "
           "small tree fits the gradient of the loss (residuals) of the current ensemble, shrunk by a learning "
           "rate: reduces bias.\n3. More trees: RF does not overfit (it plateaus); GBM can overfit, so early "
           "stopping.\n4. GBM has more sensitive hyperparameters.",
     solution="""**Model answer (about 45 s):**

\"A random forest trains many deep trees in parallel, each on a bootstrap sample and with a random subset of features
at each split, and averages them. Deep trees have low bias and high variance; averaging de-correlated trees cuts the
variance. Adding trees never hurts accuracy, it just plateaus, so the number of trees is not a sensitive knob.

Gradient boosting builds shallow trees one after another. Each new tree fits the negative gradient of the loss of the
current ensemble, for squared error simply the residuals, and is added with a small learning rate. It mainly reduces
bias, step by step. More trees eventually overfit, so I use early stopping on a validation set, and I tune the learning
rate, depth, number of trees, and subsampling together. Boosting (XGBoost, LightGBM) usually wins on tabular data but
needs more careful tuning; a random forest is the robust baseline.\"""",
     why="The bias/variance view and the different behaviour when adding trees are the core of this classic question.",
     learn=["ai-trees-boosting", "ai-bias-variance"])

# ---------------------------------------------------------------- Q2 class weights
ex.q("Balanced class weights: what really changes?", minutes=4,
     prompt="""On the bank data, fit `LogisticRegression(max_iter=1000)` twice: without class weights and with
`class_weight="balanced"`. For each, print on the test set: PR AUC (`average_precision_score`), precision and recall at
threshold 0.5, and the mean predicted probability. In one sentence: what did class weights change and what did they
not change?""",
     hint1="Signal: imbalanced target (11% yes), \"class weights\". Pattern: reweighting shifts the scores and the "
           "effective threshold; ranking quality (PR AUC) barely moves; calibration is lost.",
     hint2="1. Fit both models, `predict_proba(Xb_te)[:, 1]`.\n2. `average_precision_score`, then threshold 0.5 for "
           "precision and recall.\n3. Compare `p.mean()` with the true positive rate 0.113.",
     solution="""from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, precision_score, recall_score

for cw in (None, "balanced"):
    m = LogisticRegression(max_iter=1000, class_weight=cw).fit(Xb_tr, yb_tr)
    p = m.predict_proba(Xb_te)[:, 1]
    pred = (p >= 0.5).astype(int)
    print(cw, "PR AUC", round(average_precision_score(yb_te, p), 3),
          "precision", round(precision_score(yb_te, pred), 3), "recall", round(recall_score(yb_te, pred), 3),
          "mean p", round(p.mean(), 3))
# None PR AUC 0.405 precision 0.683 recall 0.177 mean p 0.112
# balanced PR AUC 0.404 precision 0.255 recall 0.691 mean p 0.405""",
     why="""The ranking is almost the same (PR AUC 0.405 versus 0.404): class weights mostly move all scores up, which is
like choosing a lower threshold. At 0.5 the balanced model trades precision (0.683 to 0.255) for recall (0.177 to
0.691). And it breaks calibration: its average predicted probability is 0.405 while the real rate is 0.113, so its
scores can no longer be read as probabilities (for expected value or budgeting). The unweighted model is calibrated
(0.112). Usually better: train unweighted, then pick the threshold from the business cost of false positives and
negatives; use weights or resampling when the minority class is so rare that the model ignores it.""",
     complexity="Each fit is O(iterations * n * d), about a second here.",
     mistakes="Concluding that balanced weights \"improve the model\" from recall at 0.5 alone; reading weighted "
              "scores as probabilities; resampling before the train/test split.",
     learn=["ai-features-imbalance", "ai-classification-metrics"])

# ---------------------------------------------------------------- Q3 PCA
ex.q("How many dimensions are really there?", minutes=4,
     prompt="""Standardize `P4`, run PCA, and print the explained variance ratio of each component and the cumulative
share. How many components keep at least 90% of the variance? What would happen without standardizing, and why?""",
     hint1="Signal: \"how many dimensions keep most of the information\". Pattern: PCA explained variance ratio on "
           "standardized features.",
     hint2="1. `StandardScaler().fit_transform(P4)`.\n2. `PCA().fit(Z).explained_variance_ratio_`.\n3. `np.cumsum`, "
           "first index where it reaches 0.9, plus 1.",
     solution="""from sklearn.decomposition import PCA
Z = StandardScaler().fit_transform(P4)
ratio = PCA().fit(Z).explained_variance_ratio_
print(ratio.round(3), np.cumsum(ratio).round(3))
# [0.688 0.193 0.091 0.027] [0.688 0.882 0.973 1.   ]
print("components for 90%:", int(np.argmax(np.cumsum(ratio) >= 0.9)) + 1)    # components for 90%: 3

raw = PCA().fit(P4).explained_variance_ratio_
print("unscaled first component:", raw[0].round(4))                          # unscaled first component: 0.9999""",
     why="""The first component (69%) is overall body size: flipper length, body mass and bill length move together.
Two components keep 88.2%, so 90% needs 3 (97.3%). Without standardizing, PCA follows raw variance: body mass is in
grams (variance in the hundreds of thousands) while bills are in millimetres, so the first component is almost exactly
body mass and \"explains\" 99.99% of the variance. PCA, k-means and kNN all need scaled features; tree models
do not.""",
     complexity="O(n d^2 + d^3) for PCA via the covariance matrix; tiny here.",
     mistakes="Fitting the scaler or PCA on test data; reading component signs as meaningful (they can flip); using "
              "PCA before a tree model without a reason.",
     learn=["ai-unsupervised", "cheat-ml-models"])

# ---------------------------------------------------------------- Q4 momentum and Adam
ex.q("Optimizers in one minute", minutes=3, kind="text",
     prompt="""In about 45 seconds: what problem does momentum solve, what does Adam add on top, and why is AdamW the
default for transformers?""",
     hint1="Signal: optimizer comparison. Pattern: momentum = velocity (averaged gradients); Adam = momentum + "
           "per-parameter scaling by the RMS of gradients; AdamW = decoupled weight decay.",
     hint2="1. Plain GD zig-zags in narrow valleys and is slow in flat directions.\n2. Momentum averages gradients: "
           "oscillations cancel, consistent directions speed up.\n3. Adam divides by `sqrt(v_hat)`: every parameter "
           "gets a similar step size; bias correction early.\n4. AdamW: weight decay applied directly, not through "
           "the adaptive scaling.",
     solution="""**Model answer (about 45 s):**

\"Plain gradient descent struggles when the loss surface is badly conditioned: steep in some directions and flat in
others. With a learning rate small enough for the steep direction, progress along the flat one is very slow, and the
path zig-zags. Momentum keeps a running sum of past gradients, a velocity: the zig-zag components cancel and the
consistent direction accumulates, so it moves faster with less oscillation.

Adam combines momentum, a moving average `m` of gradients, with a moving average `v` of squared gradients, and divides
the step by `sqrt(v)`. Each parameter gets its own effective learning rate, which helps with sparse or badly scaled
gradients, and bias correction fixes the zero initialization at the start.

AdamW applies weight decay directly to the weights instead of adding an L2 term to the gradient, where Adam's scaling
would weaken it for parameters with large gradients. That makes regularization behave as intended, and it is the
standard for transformers, combined with warmup and a cosine decay schedule.\"""",
     why="Reviews day 11. A rapid, precise version of this answer is expected in any deep-learning screen.",
     learn=["ai-gradient-descent", "cheat-deep-learning"])

# ---------------------------------------------------------------- Q5 backprop by hand
ex.q("One neuron, one gradient", minutes=4,
     prompt="""A single neuron: `p = sigmoid(w . x + b)`, loss `L = -(y log p + (1 - y) log(1 - p))`.

Write `neuron_grad(x, w, b, y)` returning `(L, dL_dw, dL_db)`. For `x = [1, 2]`, `w = [0.5, -0.25]`, `b = 0.1`,
`y = 1`: `z = 0.1`, `p = 0.525`, the loss is 0.6444. Which way will one gradient step move each weight, and why?""",
     stub="""def neuron_grad(x, w, b, y):
    # your code here
    pass""",
     tests="""x1, w1 = np.array([1.0, 2.0]), np.array([0.5, -0.25])
check("loss", lambda: neuron_grad(x1, w1, 0.1, 1)[0], 0.644397, tol=1e-6)
check("dL/dw", lambda: neuron_grad(x1, w1, 0.1, 1)[1], [-0.475021, -0.950042], tol=1e-6)
check("dL/db", lambda: neuron_grad(x1, w1, 0.1, 1)[2], -0.475021, tol=1e-6)
check("label 0 flips the sign", lambda: neuron_grad(x1, w1, 0.1, 0)[2], 0.524979, tol=1e-6)""",
     hint1="Signal: gradient of a sigmoid neuron with log loss. Pattern: chain rule; the sigmoid and log loss "
           "combine to `dL/dz = p - y`.",
     hint2="1. `z = w @ x + b`, `p = 1 / (1 + exp(-z))`.\n2. `L = -(y log p + (1 - y) log(1 - p))`.\n"
           "3. `dz = p - y`; `dw = dz * x`; `db = dz`.",
     solution="""def neuron_grad(x, w, b, y):
    z = w @ x + b
    p = 1 / (1 + np.exp(-z))
    L = -(y * np.log(p) + (1 - y) * np.log(1 - p))
    dz = p - y
    return L, dz * x, dz

L, dw, db = neuron_grad(np.array([1.0, 2.0]), np.array([0.5, -0.25]), 0.1, 1)
print(round(L, 4), dw.round(4), round(db, 4))      # 0.6444 [-0.475 -0.95 ] -0.475""",
     why="""`dL/dp = -(y/p) + (1-y)/(1-p)` and `dp/dz = p(1-p)`; their product simplifies to `p - y` = 0.525 - 1 =
-0.475. Then `dL/dw = (p - y) x` and `dL/db = p - y`. All gradients are negative, so a step `w - lr * grad` increases
both weights and the bias, which raises z and therefore p, towards the label 1. The weight with the larger input (x2 =
2) gets twice the update: inputs scale their weights' gradients, one more reason to standardize features.""",
     complexity="O(d).",
     mistakes="Forgetting the minus sign of the loss; using `p(1 - p)` twice; writing `dw = (p - y) * w` instead of `x`.",
     learn=["ai-neural-networks", "ai-logistic-regression"])

# ---------------------------------------------------------------- Q6 scaling
ex.q("Which models care about feature scale?", minutes=2, kind="text",
     prompt="""In about 30 seconds: which of these need standardized features and why: gradient-boosted trees,
k-means, logistic regression with L2, a neural network, random forest, kNN, PCA?""",
     hint1="Signal: preprocessing. Pattern: distance-, variance- or gradient-based methods care about scale; "
           "threshold-based trees do not.",
     hint2="Trees split on thresholds of one feature at a time, so any monotonic rescaling gives the same splits.",
     solution="""**Model answer (about 30 s):**

\"Trees, both random forests and gradient boosting, do not need scaling: each split is a threshold on one feature, and
a monotonic rescaling gives the same ordering and the same splits. k-means, kNN and PCA need it, because they use
distances or variances, and a feature in large units would dominate. Logistic regression with L2 needs it because the
penalty treats all coefficients equally, so the units decide how much each feature is penalized; it also speeds up
gradient-based solvers. Neural networks need it for optimization: unscaled inputs give badly conditioned losses,
saturated activations and unstable gradients.\"""",
     why="Mixes trees, unsupervised and neural-network review in one quick question; examiners use it to see if "
         "you know why, not just a rule.",
     learn=["ai-features-imbalance", "ai-trees-boosting", "ai-unsupervised"])

# ---------------------------------------------------------------- Q7 dot vs cosine
ex.q("Dot or cosine for a user?", minutes=3,
     prompt="""A user vector `u = [1, 0.5]` and three item vectors: `A = [4, 1]`, `B = [1, 0.6]`, `C = [0.5, 1]`.
Write `rank_items(u, E, metric)` that returns the item indices sorted from best to worst score, with
`metric` either `"dot"` or `"cosine"`. Which item wins in each case, and which metric would you use for \"more like
your taste\" versus \"most likely to be clicked\"?""",
     stub="""def rank_items(u, E, metric="dot"):
    # your code here
    pass""",
     tests="""u0 = np.array([1.0, 0.5]); E0 = np.array([[4.0, 1.0], [1.0, 0.6], [0.5, 1.0]])
check("dot ranking", lambda: list(rank_items(u0, E0, "dot")), lambda r: r == [0, 1, 2])
check("cosine ranking", lambda: list(rank_items(u0, E0, "cosine")), lambda r: r == [1, 0, 2])""",
     hint1="Signal: ranking items for a user with embeddings. Pattern: dot product rewards vector length; cosine "
           "compares direction only.",
     hint2="1. Dot: `E @ u`.\n2. Cosine: `E @ u / (norm(E, axis=1) * norm(u))`.\n3. `np.argsort(-scores)`.",
     solution="""def rank_items(u, E, metric="dot"):
    s = E @ u
    if metric == "cosine":
        s = s / (np.linalg.norm(E, axis=1) * np.linalg.norm(u))
    return np.argsort(-s)

u0 = np.array([1.0, 0.5]); E0 = np.array([[4.0, 1.0], [1.0, 0.6], [0.5, 1.0]])
print((E0 @ u0).round(3))                                                              # [4.5 1.3 1. ]
print((E0 @ u0 / (np.linalg.norm(E0, axis=1) * np.linalg.norm(u0))).round(3))         # [0.976 0.997 0.8  ]""",
     why="""Dot product: A wins (4.5) because it is long, not because it matches best. Cosine: B wins (0.997 versus 0.976)
because its direction is closest to the user's. In trained recommenders, item vector length often encodes popularity
(day 13: length correlated 0.74 with rating count), so dot product suits predicting clicks, where popularity really
helps, and cosine suits \"similar to your taste\" lists and similar-item search. Many systems use the dot product for
retrieval and then control popularity in the ranker.""",
     complexity="O(n d).",
     mistakes="Normalizing only the items or only the user and calling it cosine (the user norm does not change the "
              "ranking, but the item norms do); sorting ascending.",
     learn=["ai-embeddings", "ai-recommenders"])

# ---------------------------------------------------------------- Q8 mini case: fake accounts
ex.q("Mini case: fake accounts on a video app", minutes=7, kind="text",
     prompt="""About 0.5% of new accounts on a short-video app are fake (bots used for spam and fake followers).
You have sign-up data (device, IP, email domain, time), the first 24 hours of behaviour (follows, likes, comments,
watch sessions) and a small set of accounts confirmed fake by a review team.

In about 4 minutes, out loud: the ML framing, the label and its problems, features, the model, how to handle the
imbalance, the metric and threshold, and what you do about new attack patterns the labels have never seen.""",
     hint1="Signal: rare adversarial positives, partial labels, tabular plus behaviour data. Pattern: supervised GBM on "
           "engineered features + unsupervised anomaly or cluster signals + precision-constrained threshold + "
           "monitoring for drift.",
     hint2="1. Framing: score each account at sign-up and after 24 h; decision = block, challenge (CAPTCHA, phone), or "
           "allow.\n2. Labels: reviewed accounts are biased toward what reviewers looked at; delayed; noisy.\n"
           "3. Features: velocity (actions per minute), device/IP sharing counts, graph features, behaviour "
           "embeddings.\n4. GBM with class weights or downsampled negatives; PR AUC, precision at fixed recall.\n"
           "5. Threshold by action cost; challenge in the grey zone.\n6. Unknown attacks: clustering of devices/IPs, "
           "isolation forest, sudden new clusters; red-team; retrain often.",
     solution="""**Model answer (about 4 minutes, key points):**

**Framing.** Binary classification at the account level, scored twice: at sign-up (only sign-up features, to stop
bots early) and after 24 hours (behaviour too). The output drives an action ladder: allow, add friction (phone
verification, CAPTCHA), limit actions, or ban. Friction is cheap for real users; a wrong ban is expensive.

**Labels.** Positives are accounts confirmed by reviewers, so they only cover attacks someone already looked at; labels
arrive late and some are wrong. Negatives are \"not reviewed\", which contains unknown fakes. I would add a random audit
sample to estimate the true rate and get unbiased evaluation data.

**Features.** Sign-up: device fingerprint, how many accounts share the device, IP or IP subnet in the last hour,
disposable email domain, sign-up hour, app version. Behaviour: actions per minute, follow/like ratios, share of actions
on a few target accounts, session length and watch completion (bots rarely watch), comment text similarity. Graph:
clusters of accounts following the same targets; embeddings of the account in the follow graph.

**Model.** Gradient-boosted trees on these tabular features: strong, handles missing values and mixed scales, fast to
serve, explainable with SHAP for the review team. Imbalance: keep all positives, downsample negatives (and correct the
probabilities), or use class weights; never evaluate on resampled data.

**Metric and threshold.** PR AUC offline and, more useful, recall at a fixed precision, for example 95% precision for
an automatic ban, a lower bar for friction. Choose thresholds per action from the cost of false positives (a real
creator banned) versus false negatives (spam reaching users).

**New attacks.** A supervised model only knows past patterns, and attackers adapt. Add unsupervised signals: sudden new
clusters of accounts sharing devices or behaviour, isolation-forest scores on behaviour features, spikes in sign-ups
from one subnet. Route high-anomaly, low-model-score accounts to review, so labels for new attacks arrive quickly. Then
retrain frequently, monitor the score distribution and precision on audited samples, and keep rules for emergencies.\"""",
     why="The mini case combines all the review topics: trees and boosting (the model), imbalance (positives at 0.5%), "
         "unsupervised learning (unknown attacks), embeddings (graph and behaviour). Score yourself on: action "
         "ladder, label bias, precision-constrained threshold, and a plan for new attacks.",
     learn=["ai-features-imbalance", "ai-trees-boosting", "ai-unsupervised", "ai-ml-system-design"])

ex.save()
